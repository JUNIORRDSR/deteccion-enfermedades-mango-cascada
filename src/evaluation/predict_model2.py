"""EXP-R03: the single test evaluation of the EXISTING M2 classifier (ART-002), no retraining.

Frozen before running: weights by hash, membership by the committed model2_frozen_manifest.csv
and its sidecar, 224 px, top-1 without rejection. Images are read by Ultralytics from the file
path (its own input contract), not by the legacy gallery's BGR->RGB conversion. Classes are
mapped by NAME from model.names, never by folder order. Local venue: the M2 data and weights
are not on any public source Kaggle can read, and this is seconds of CPU (SPEC section 7).
"""

import argparse
import csv
import datetime
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ART002_SHA256 = 'e277717e6ca9d7f308d22697550a5a4e80613929acb68eeb790f3304ebfdb08e'
ART002_PATH = 'Mango-vision/models/clasificador_enfermedad.pt'  # legacy_corpus, configs/inputs.json
# The committed frozen M2 membership (TASK-03); any other manifest is refused.
M2_MANIFEST = 'data/manifests/model2_frozen_manifest.csv'
M2_MANIFEST_SHA256 = 'cd4f0d0e428fc3015268b7df541bf705261893c4b5cba0a7ef274e17d0680d92'
CLASS_NAMES = ('Antracnosis', 'Cancro_bacteriano', 'Costras', 'Podredumbre_Extremo_tallo',
               'Saludable')
# What EXP-R03 is; the run record is written from it and every consumer checks it field by
# field (TASK-05 round-3 MEDIUM-01).
M2_CONTRACT = {'experiment_id': 'EXP-R03', 'manifest': M2_MANIFEST,
               'manifest_sha256': M2_MANIFEST_SHA256, 'weights_sha256': ART002_SHA256,
               'predictions': 'experiments/model2/EXP-R03/predictions.jsonl', 'imgsz': 224,
               'rule': 'top-1 without rejection', 'input_contract': 'Ultralytics file-path loader',
               'class_names': list(CLASS_NAMES), 'ultralytics': '8.4.52',
               'config': 'configs/evaluation_frozen.json', 'dependencies_outside_checkout': True,
               'environment': 'provenance/environment/inference_environment.txt'}


class RunRejected(Exception):
    """An input that must stop the run rather than be worked around."""


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def classification_record(row: dict, probs: list[float], names: dict[int, str]) -> dict:
    """One prediction line; truth and prediction by class name; top-1 without rejection."""
    if sorted(names.values()) != sorted(CLASS_NAMES):
        raise RunRejected(f'model classes {sorted(names.values())} differ from the frozen names')
    if row['class_name'] not in CLASS_NAMES:
        raise RunRejected(f"unknown truth class {row['class_name']!r}")
    by_name = {names[i]: float(p) for i, p in enumerate(probs)}
    top = max(range(len(probs)), key=lambda i: (probs[i], -i))  # exact tie: first model index
    return {'image_id': row['image_id'], 'sha256': row['sha256'], 'cluster_id': row['cluster_id'],
            'group_id': row['group_id'], 'split': row['split'], 'truth': row['class_name'],
            'pred': names[top], 'probs': {name: by_name[name] for name in CLASS_NAMES},
            'class_names': [names[i] for i in range(len(names))]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--weights', type=Path, required=True)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.manifest, args.weights, args.run_dir, config=args.config)))
    return 0


def run(manifest: Path, weights: Path, run_dir: Path, config: Path | None = None) -> dict:
    """EXP-R03 once. Also reached by the frozen command `evaluate --model-id model2`. Before any
    test byte is read, inference must be approved for the committed M2 snapshot (which also
    verifies the interpreter, the import system and every installed file) and the config must
    be the M1 operating-point freeze, validated as M1 validates it (TASK-05 round 7). After the
    imports, Ultralytics and torch must come from recorded files of the interpreter."""
    from src.evaluation import authority, evaluate
    from src.evaluation.provenance import (
        authorized_root, check_output, configure_environment, lock_ultralytics, verify_environment,
    )
    root = authorized_root()
    try:
        authority.approved_inference(root, 'm2')
    except authority.NotApproved as error:
        raise RunRejected(str(error)) from None
    if not config or Path(config).resolve() != (root / M2_CONTRACT['config']).resolve():
        raise RunRejected(f"EXP-R03 needs the committed {M2_CONTRACT['config']}")
    try:
        evaluate.sealed_config(root / M2_CONTRACT['config'], root / evaluate.M1_MANIFEST, root)
    except evaluate.RunRejected as error:
        raise RunRejected(f'EXP-R03 needs the frozen M1 operating point: {error}') from None
    configure_environment(root)
    verify_environment(root)
    manifest, weights = Path(manifest), Path(weights)
    declared = manifest.with_suffix('.csv.sha256').read_text(encoding='ascii').split()[0]
    if (manifest.resolve() != (root / M2_MANIFEST).resolve()
            or _sha(manifest) != declared or declared != M2_MANIFEST_SHA256):
        raise RunRejected('only the committed frozen M2 manifest is accepted')
    if _sha(weights) != ART002_SHA256:
        raise RunRejected('weights are not ART-002')
    if Path(run_dir).resolve() != (root / M2_CONTRACT['predictions']).parent.resolve():
        raise RunRejected('EXP-R03 runs only into ' + str(Path(M2_CONTRACT['predictions']).parent))
    run = check_output(root, Path(run_dir), allow_directory=True)
    run.mkdir(parents=True, exist_ok=False)  # one evaluation: an existing run dir stops here
    legacy = Path(json.loads((root / 'configs/root_mapping.json').read_text(encoding='utf-8'))
                  ['legacy_corpus'])
    rows = [r for r in csv.DictReader(open(manifest, encoding='utf-8'))
            if r['split'] == 'test']
    for r in rows:
        if _sha(legacy / r['path']) != r['sha256']:
            raise RunRejected(f"image bytes differ from the manifest: {r['image_id']}")

    import os
    os.environ['YOLO_OFFLINE'] = 'true'
    import torch
    import ultralytics
    from ultralytics import SETTINGS, YOLO, __version__
    try:
        runtime_modules = authority.check_imported('ultralytics', 'torch')
    except authority.NotApproved as error:
        raise RunRejected(str(error)) from None
    if __version__ != M2_CONTRACT['ultralytics'] or ultralytics.__version__ != __version__:
        raise RunRejected(f"Ultralytics must be {M2_CONTRACT['ultralytics']}")
    lock_ultralytics(SETTINGS, root)
    model = YOLO(str(weights))
    names = {int(k): v for k, v in model.names.items()}
    records = []
    for r in sorted(rows, key=lambda r: r['image_id']):
        result = model.predict(str(legacy / r['path']), imgsz=224, device='cpu', verbose=False)[0]
        records.append(classification_record(r, result.probs.data.tolist(), names))
    predictions = run / 'predictions.jsonl'
    predictions.write_text(''.join(json.dumps(x, sort_keys=True) + '\n' for x in records),
                           encoding='utf-8', newline='\n')
    (run / 'predictions.jsonl.sha256').write_text(f'{_sha(predictions)}  predictions.jsonl\n',
                                                  encoding='ascii')
    (run / 'run_record.json').write_text(json.dumps({
        **{k: M2_CONTRACT[k] for k in ('experiment_id', 'weights_sha256', 'manifest_sha256',
                                       'imgsz', 'rule', 'input_contract')},
        'model_names': names, 'ultralytics': __version__, 'torch': torch.__version__,
        'python': sys.version, 'dependencies_outside_checkout': True,
        'runtime_sha256': authority.runtime_identity(), 'runtime_modules': runtime_modules,
        'environment': M2_CONTRACT['environment'],
        'environment_sha256': _sha(root / M2_CONTRACT['environment']),
        'images': len(records), 'predictions_sha256': _sha(predictions),
        'recorded_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'config': M2_CONTRACT['config'], 'config_sha256': _sha(config),
        'producer': 'src/evaluation/predict_model2.py', 'producer_sha256': _sha(Path(__file__)),
        'command': ' '.join(sys.argv)}, indent=2) + '\n', encoding='utf-8')
    return {'images': len(records), 'predictions_sha256': _sha(predictions)}


if __name__ == '__main__':
    try:
        sys.exit(main())
    except RunRejected as error:
        print(f'REJECTED: {error}', file=sys.stderr)
        sys.exit(2)
