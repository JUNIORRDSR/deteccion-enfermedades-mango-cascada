"""TASK-04: retrain M1 from the official base checkpoint on the frozen clean split.

Verified in the installed Ultralytics 8.4.52 (engine/trainer.py, utils/metrics.py):
- detection fitness is mAP@0.5:0.95 only, weights [0, 0, 0, 1];
- best.pt is written when best_fitness == fitness, so on a tie the LAST epoch wins,
  which is the frozen rule;
- on_model_save fires after the native save;
- trainer.fitness is ROUNDED to 5 decimals (engine/validator.py:267), found by the local
  smoke run. The unrounded value the SPEC requires lives in trainer.validator.metrics.
  The native save condition still keeps the bytes of the unrounded maximum: that epoch's
  rounded fitness equals the running rounded maximum, so it is always a candidate.

`run_training` is independent of the repository layout, so the same function can
run locally on CPU or inside a Kaggle notebook once PROTOCOL-AMENDMENT-008 allows it.
"""

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

FROZEN = {'epochs': 150, 'patience': 100, 'batch': 16, 'imgsz': 640, 'seed': 0,
          'optimizer': 'auto'}
TRAINED_M1_SHA256 = '595fa3ea9b0670f63289529bde3333124ff1179588b52fbe16c9c454b6e488de'


class RunRejected(Exception):
    """An input or record that must stop the run rather than be worked around."""


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def prepare_run(config: dict, manifest: Path, run_dir: Path) -> dict:
    """All checks happen before any scientific import."""
    manifest = Path(manifest)
    sidecar = manifest.with_suffix(manifest.suffix + '.sha256')
    if not sidecar.is_file():
        raise RunRejected(f'manifest sidecar missing: {sidecar}')
    declared = sidecar.read_text(encoding='ascii').split()[0]
    actual = _sha(manifest)
    if actual != declared:
        raise RunRejected(f'manifest hash {actual} differs from its frozen sidecar {declared}')
    for key, value in FROZEN.items():
        if config.get(key) != value:
            raise RunRejected(f'{key} is {config.get(key)!r}; the frozen protocol fixes {value!r}')
    base_declared = config.get('base_checkpoint_sha256', '')
    if base_declared == TRAINED_M1_SHA256:
        raise RunRejected('the base checkpoint is the trained M1 weight; a changed split must '
                          'start from the official base, never from weights that saw its members')
    base = Path(config['base_checkpoint'])
    if not base.is_file() or _sha(base) != base_declared:
        raise RunRejected(f'base checkpoint bytes do not match the declared hash: {base}')
    Path(run_dir).mkdir(parents=True, exist_ok=False)
    return {'experiment_id': config['experiment_id'], 'manifest': str(manifest),
            'manifest_sha256': actual, 'base_checkpoint': str(base),
            'base_checkpoint_sha256': base_declared, 'config': dict(config),
            'command': ' '.join(sys.argv)}


def select_checkpoint(records: list[dict]) -> dict:
    """Maximum unrounded fitness; the last epoch wins a tie. Bytes must match."""
    if not records:
        raise RunRejected('no checkpoint records to select from')
    for record in records:
        path = Path(record['checkpoint_path'])
        if not path.is_file():
            raise RunRejected(f"checkpoint missing for epoch {record['epoch']}: {path}")
        if _sha(path) != record['sha256']:
            raise RunRejected(f"checkpoint hash changed for epoch {record['epoch']}: {path}")
        if not math.isfinite(float(record['fitness'])):
            raise RunRejected(f"non-finite fitness at epoch {record['epoch']}")
    return max(records, key=lambda r: (float(r['fitness']), int(r['epoch'])))


def append_record(path: Path, record: dict) -> None:
    """One JSON line flushed to disk now, so a cut run keeps every finished epoch."""
    with Path(path).open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(record) + '\n')
        stream.flush()
        os.fsync(stream.fileno())


def epoch_record(trainer) -> dict:
    """Base-1 epoch with UNROUNDED fitness and metrics from the validator's DetMetrics."""
    exact = trainer.validator.metrics
    fitness = float(exact.fitness)
    return {'epoch': trainer.epoch + 1, 'fitness': fitness, 'fitness_repr': repr(fitness),
            'fitness_native_rounded': float(trainer.fitness),
            'metrics': {k: float(v) for k, v in exact.results_dict.items()}}


def run_training(config: dict, data_yaml: Path, run_dir: Path, device: str) -> dict:
    """Train once; record every epoch and keep the bytes of every candidate best."""
    from ultralytics import YOLO

    candidates_dir = run_dir / 'weights' / 'candidates'
    candidates_dir.mkdir(parents=True, exist_ok=True)
    all_epochs, candidates = [], []

    def on_model_save(trainer):
        record = epoch_record(trainer)
        all_epochs.append(record)
        append_record(run_dir / 'epoch_records.jsonl', record)
        if trainer.best_fitness == trainer.fitness:  # new best or a tie, on the rounded value
            target = candidates_dir / f"epoch{record['epoch']:03d}.pt"
            shutil.copyfile(trainer.best, target)
            candidates.append({**record, 'checkpoint_path': str(target), 'sha256': _sha(target)})

    model = YOLO(config['base_checkpoint'])
    model.add_callback('on_model_save', on_model_save)
    model.train(data=str(data_yaml), epochs=config['epochs'], patience=config['patience'],
                batch=config['batch'], imgsz=config['imgsz'], seed=config['seed'],
                optimizer=config['optimizer'], device=device, deterministic=True,
                project=str(run_dir), name='train', exist_ok=False, save=True, plots=True,
                workers=config.get('workers', 2))
    finite = [r for r in all_epochs if math.isfinite(r['fitness'])]
    if len(finite) != len(all_epochs):
        raise RunRejected('a saved epoch had a non-finite fitness; the run cannot be validated')
    chosen = select_checkpoint(candidates)
    global_max = max(all_epochs, key=lambda r: (r['fitness'], r['epoch']))
    if (chosen['epoch'], chosen['fitness']) != (global_max['epoch'], global_max['fitness']):
        raise RunRejected('the selected candidate does not match the global maximum over all epochs')
    shutil.copyfile(chosen['checkpoint_path'], run_dir / 'weights' / 'selected.pt')
    return {'selected_epoch': chosen['epoch'], 'selected_fitness_repr': chosen['fitness_repr'],
            'selected_sha256': chosen['sha256'], 'epochs_recorded': len(all_epochs),
            'candidates_kept': len(candidates), 'selected_metrics': chosen['metrics']}


def build_view(root: Path, manifest: Path, legacy: Path, run_id: str) -> Path:
    """Train and valid only. The test split is never copied into the training view."""
    from src.evaluation.provenance import check_output
    view = check_output(root, root / 'data' / 'derived' / f'model1_clean_{run_id}',
                        allow_directory=True)
    if view.exists():
        raise RunRejected(f'derived view already exists: {view}')
    rows = list(csv.DictReader(open(manifest, encoding='utf-8')))
    for row in rows:
        if row['proposed_split'] == 'test':
            continue
        split = 'train' if row['proposed_split'] == 'train' else 'val'
        for kind, relative in (('images', row['logical_path']), ('labels', row['label'])):
            target = view / kind / split / Path(relative).name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(legacy / relative, target)
    (view / 'data.yaml').write_text(
        f'path: {view.as_posix()}\ntrain: images/train\nval: images/val\n'
        "nc: 2\nnames: ['Enfermo', 'Saludable']\n", encoding='utf-8')
    return view


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--run-dir', type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding='utf-8'))
    record = prepare_run(config, args.manifest, args.run_dir)  # before any scientific import

    from src.evaluation.provenance import (
        authorized_root, configure_environment, lock_ultralytics, verify_environment,
    )
    root = authorized_root()
    configure_environment(root)
    verify_environment(root)
    os.environ['YOLO_OFFLINE'] = 'true'
    legacy = Path(json.loads((root / 'configs/root_mapping.json').read_text(encoding='utf-8'))
                  ['legacy_corpus'])
    view = build_view(root, args.manifest, legacy, config['experiment_id'])
    from ultralytics import SETTINGS, __version__
    import torch
    lock_ultralytics(SETTINGS, root)

    run_dir = args.run_dir
    (run_dir / 'command.txt').write_text(record['command'] + '\n', encoding='utf-8')
    (run_dir / 'dataset_manifest.sha256').write_text(
        f"{record['manifest_sha256']}  {Path(record['manifest']).name}\n", encoding='ascii')
    (run_dir / 'config.json').write_text(json.dumps(config, indent=2) + '\n', encoding='utf-8')
    (run_dir / 'environment.json').write_text(json.dumps({
        'python': sys.version, 'platform': platform.platform(), 'ultralytics': __version__,
        'torch': torch.__version__, 'cuda_available': torch.cuda.is_available(),
        'device': config['device'], 'gpus': [torch.cuda.get_device_name(i)
                                             for i in range(torch.cuda.device_count())],
        'venue': config.get('venue', 'local'), 'amendments': config.get('amendments', [])},
        indent=2) + '\n', encoding='utf-8')
    result = run_training(config, view / 'data.yaml', run_dir, config['device'])
    after = _sha(args.manifest)
    if after != record['manifest_sha256']:
        raise RunRejected('the manifest changed during the run')
    (run_dir / 'metrics.json').write_text(json.dumps({**result, 'test_evaluated': False},
                                                     indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except RunRejected as error:
        print(f'REJECTED: {error}', file=sys.stderr)
        sys.exit(2)
