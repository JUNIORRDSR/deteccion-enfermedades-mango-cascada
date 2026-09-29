"""NON-SCIENTIFIC local CPU throughput probe for TASK-04 capacity.

The frozen plan (TASK-04) says to propose CPU when it is the only available
device. The Kaggle amendment was motivated by the claim that local CPU training
was not viable in reasonable time, a claim that was never measured. This probe
measures it.

Rules, mirroring configs/capacity_plan.json:
- only train and valid images of the CURRENT split are used; test is never read;
- the model is built from the architecture file, no pretrained weights, no download;
- the probe model and its metrics are discarded and never reported, only timings;
- the first epoch is warm-up and excluded from the estimate.
"""

import json
import os
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.evaluation.provenance import (  # noqa: E402
    authorized_root, check_output, configure_environment, lock_ultralytics, verify_environment,
)

EPOCHS = 3


def build_view(root: Path, legacy: Path) -> tuple[Path, int]:
    """Copy train and valid only. Ultralytics writes label caches next to the labels,
    so training straight from the legacy tree would write into it."""
    import csv
    view = check_output(root, root / 'data/derived/probe_m1', allow_directory=True)
    if view.exists():
        shutil.rmtree(view)
    rows = [r for r in csv.DictReader(open(root / 'data/manifests/legacy_dataset_inventory.csv',
                                           encoding='utf-8-sig'))
            if r['dataset_id'] == 'DATA-001' and r['split'] in ('train', 'valid')]
    for row in rows:
        split = 'train' if row['split'] == 'train' else 'val'
        for kind, relative in (('images', row['relative_path']), ('labels', row['label_path'])):
            source = legacy / relative
            target = view / kind / split / Path(relative).name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    if any(r['split'] == 'test' for r in rows):
        raise SystemExit('test image in the probe view')
    (view / 'data.yaml').write_text(
        f'path: {view.as_posix()}\ntrain: images/train\nval: images/val\n'
        "nc: 2\nnames: ['Enfermo', 'Saludable']\n", encoding='utf-8')
    return view, len(rows)


def main() -> int:
    root = authorized_root()
    configure_environment(root)
    verify_environment(root)
    os.environ['YOLO_OFFLINE'] = 'true'
    legacy = Path(json.loads((root / 'configs/root_mapping.json').read_text(encoding='utf-8'))
                  ['legacy_corpus'])
    view, n_images = build_view(root, legacy)

    from ultralytics import SETTINGS, YOLO
    import torch
    lock_ultralytics(SETTINGS, root)
    torch.set_num_threads(os.cpu_count() or 1)

    epoch_times: list[float] = []
    state = {'start': None}

    def on_epoch_start(trainer):
        state['start'] = time.perf_counter()

    def on_fit_epoch_end(trainer):  # after the validation pass, so val overhead is included
        epoch_times.append(time.perf_counter() - state['start'])

    runs = check_output(root, root / 'experiments/probes', allow_directory=True)
    model = YOLO('yolo26n.yaml')
    model.add_callback('on_train_epoch_start', on_epoch_start)
    model.add_callback('on_fit_epoch_end', on_fit_epoch_end)
    started = time.perf_counter()
    model.train(data=str(view / 'data.yaml'), epochs=EPOCHS, imgsz=640, batch=16, device='cpu',
                seed=0, pretrained=False, workers=2, plots=False, save=False, exist_ok=False,
                project=str(runs), name=f'cpu_probe_{int(time.time())}', verbose=False)
    wall = time.perf_counter() - started

    measured = epoch_times[1:]  # first epoch is warm-up
    per_epoch = sorted(measured)[len(measured) // 2] if measured else None
    upper = max(measured) if measured else None
    report = {
        'kind': 'NON_SCIENTIFIC_THROUGHPUT_PROBE',
        'device': 'cpu', 'torch_threads': torch.get_num_threads(),
        'processor': 'AMD Ryzen 5 7520U with Radeon Graphics (provenance/environment/cpu_topology_probe.json)',
        'images_train_plus_val': n_images, 'test_images_read': 0,
        'epochs_run': EPOCHS, 'warmup_epochs_excluded': 1,
        'epoch_seconds_all': [round(t, 1) for t in epoch_times],
        'per_epoch_seconds_median': round(per_epoch, 1) if per_epoch else None,
        'per_epoch_seconds_upper': round(upper, 1) if upper else None,
        'projected_150_epochs_hours_upper': round(upper * 150 / 3600, 2) if upper else None,
        'projected_150_epochs_hours_with_safety_1_35':
            round(upper * 150 * 1.35 / 3600, 2) if upper else None,
        'wall_seconds_total': round(wall, 1),
        'model_retained': False, 'metrics_reported': False,
        'note': ('Timings only. The probe model and its metrics are discarded. The real split '
                 'will have about 443 training images instead of 502, so this over-estimates.'),
    }
    shutil.rmtree(runs, ignore_errors=True)
    out = check_output(root, root / 'reports/execution/cpu_capacity_probe.json')
    out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
