"""Figures 4-7 from the committed results (TASK-09 pass 2c). M1 is never run here; only fig7
runs M2 on crops of saved validation boxes, as the command-line cascade does.

fig4: M1 detection confusion on the test set, from experiments/model1/EXP-R02/metrics.json;
      (b) normalises the true-class rows only (a background row has no ground truth).
fig5: saved EXP-R02 detections at the frozen operating point drawn on test images chosen
      with seed 42 among images with at least one ground-truth box; no new inference.
fig6: M2 confusion on the test set, from experiments/model2/EXP-R03/predictions.jsonl.
fig7: the cascade on validation images, from the saved EXP-V01 boxes (see fig7).
Pixel sizes equal those of the figures they replace, so the DOCX extents stay valid.
"""

import csv
import json
import random
import sys
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
FIGURES = ROOT / 'manuscript/figures'
NAMES = {'Enfermo': 'Enfermo', 'Saludable': 'Saludable', 'background': 'Fondo'}
M2_LABELS = {'Antracnosis': 'Antracnosis', 'Cancro_bacteriano': 'Cancro bacteriano',
             'Costras': 'Costras', 'Podredumbre_Extremo_tallo': 'Podredumbre ext. tallo',
             'Saludable': 'Saludable'}


def _matrix(ax, matrix, labels, title, fmt):
    shown = [[v if v is not None else 0 for v in row] for row in matrix]
    ax.imshow(shown, cmap='Blues')
    top = max(max(row) for row in shown)  # the colormap scales to the global maximum
    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            text = '—' if value is None else format(value, fmt).replace('.', ',')
            ax.text(j, i, text, ha='center', va='center', fontsize=11,
                    color='white' if value is not None and top and value > 0.6 * top else '#222222')
    ax.set_xticks(range(len(labels)), labels, fontsize=10)
    ax.set_yticks(range(len(labels)), labels, fontsize=10)
    ax.set_xlabel('Predicción')
    ax.set_ylabel('Verdad')
    ax.set_title(title, fontweight='bold')


def fig4(out: Path) -> None:
    metrics = json.loads((ROOT / 'experiments/model1/EXP-R02/metrics.json').read_text(encoding='utf-8'))
    cm = metrics['detection_confusion']
    labels = [NAMES[n] for n in cm['labels']]
    counts = [[int(v) for v in row] for row in cm['matrix']]
    rows = [[v / sum(row) if sum(row) else None for v in row] for row in counts[:-1]]
    rows.append([None] * len(labels))
    fig, (a, b) = plt.subplots(1, 2, figsize=(27.85 / 2.5, 13.91 / 2.5), dpi=250)
    _matrix(a, counts, labels, '(a) Conteos absolutos', 'd')
    _matrix(b, rows, labels, '(b) Proporción por fila verdadera', '.2f')
    threshold = f"{metrics['threshold']:.2f}".replace('.', ',')
    fig.suptitle(f'Modelo 1, conjunto de prueba (IoU ≥ 0,5; umbral {threshold})',
                 fontweight='bold', fontsize=13)
    fig.tight_layout()
    fig.savefig(out, dpi=250)
    plt.close(fig)


def fig5(out: Path, n: int = 9) -> None:
    """A seed-42 sample, not a selection: each title gives true and detected counts."""
    from PIL import Image, ImageDraw, ImageFont
    metrics = json.loads((ROOT / 'experiments/model1/EXP-R02/metrics.json').read_text(encoding='utf-8'))
    threshold = metrics['threshold']
    records = [json.loads(line) for line in (ROOT / 'experiments/model1/EXP-R02/predictions.jsonl')
               .read_text(encoding='utf-8').splitlines()]
    legacy = Path(json.loads((ROOT / 'configs/root_mapping.json').read_text(encoding='utf-8'))
                  ['legacy_corpus'])
    rows = {r['image_id']: r for r in csv.DictReader(
        open(ROOT / 'data/manifests/model1_clean_manifest.csv', encoding='utf-8'))}
    candidates = sorted(r['image_id'] for r in records if r['gt'])
    chosen = sorted(random.Random(42).sample(candidates, n))
    by_id = {r['image_id']: r for r in records}
    fig, axes = plt.subplots(3, 3, figsize=(18.21 / 2.5, 19.0 / 2.5), dpi=250)
    colours = {0: (220, 60, 50), 1: (46, 160, 67)}
    names = ('Enfermo', 'Saludable')
    for ax in axes.flat:
        ax.axis('off')
    for ax, image_id in zip(axes.flat, chosen):
        record = by_id[image_id]
        kept = [d for d in record['detections'] if d['score'] >= threshold]
        image = Image.open(legacy / rows[image_id]['path']).convert('RGB')
        draw = ImageDraw.Draw(image)
        width = max(2, image.width // 150)
        font = ImageFont.load_default(size=max(12, image.width // 22))
        for det in kept:
            label = f"{names[det['class_id']]} {det['score']:.2f}".replace('.', ',')
            x1, y1 = det['xyxy'][:2]
            draw.rectangle(det['xyxy'], outline=colours[det['class_id']], width=width)
            anchor = 'lb' if y1 > font.size else 'lt'  # inside the box at the top edge
            x = max(0, min(x1, image.width - draw.textlength(label, font=font)))  # never past the edge
            box = draw.textbbox((x, y1), label, font=font, anchor=anchor)
            draw.rectangle(box, fill=colours[det['class_id']])
            draw.text((x, y1), label, fill='white', font=font, anchor=anchor)
        ax.imshow(image)
        count = lambda boxes, c: sum(b['class_id'] == c for b in boxes)  # noqa: E731
        ax.set_title(f"Real E {count(record['gt'], 0)} · S {count(record['gt'], 1)}\n"
                     f"Detectado E {count(kept, 0)} · S {count(kept, 1)}", fontsize=7)
    fig.tight_layout()
    fig.savefig(out, dpi=250)
    plt.close(fig)


def fig7(out: Path, n: int = 9) -> None:
    """The cascade on VALIDATION images (seed 42 among images with a ground-truth box): the
    saved EXP-V01 boxes at the frozen threshold, cropped, classified by ART-002 and drawn by
    src/cascade/runtime.py exactly as the command-line cascade does. M1 is not run again."""
    import hashlib
    from types import SimpleNamespace

    import torch
    from ultralytics import YOLO
    from ultralytics.engine.results import Boxes

    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from src.cascade import runtime
    from src.evaluation import predict_model2
    threshold = json.loads((ROOT / 'configs/evaluation_frozen.json').read_text(encoding='utf-8'))[
        'threshold']
    records = [json.loads(line) for line in (ROOT / 'experiments/model1/EXP-V01/predictions.jsonl')
               .read_text(encoding='utf-8').splitlines()]
    legacy = Path(json.loads((ROOT / 'configs/root_mapping.json').read_text(encoding='utf-8'))
                  ['legacy_corpus'])
    weights = legacy / predict_model2.ART002_PATH
    assert hashlib.sha256(weights.read_bytes()).hexdigest() == \
        predict_model2.M2_CONTRACT['weights_sha256'], 'ART-002 differs from the frozen weights'
    classifier = YOLO(str(weights))
    rows = {r['image_id']: r for r in csv.DictReader(
        open(ROOT / 'data/manifests/model1_clean_manifest.csv', encoding='utf-8'))}
    candidates = sorted(r['image_id'] for r in records if r['gt'])
    chosen = sorted(random.Random(42).sample(candidates, n))
    by_id = {r['image_id']: r for r in records}
    fig, axes = plt.subplots(3, 3, figsize=(19.22 / 2.5, 20.0 / 2.5), dpi=250)
    for ax in axes.flat:
        ax.axis('off')
    for ax, image_id in zip(axes.flat, chosen):
        frame = runtime.decode(runtime.read_file(legacy / rows[image_id]['path']))
        kept = [d for d in by_id[image_id]['detections'] if d['score'] >= threshold]
        data = torch.tensor([[*d['xyxy'], d['score'], d['class_id']] for d in kept]).reshape(-1, 6)
        items = runtime.classify_crops(frame, SimpleNamespace(boxes=Boxes(data, frame.shape[:2])),
                                       classifier, 0.4, 224, 'cpu')
        ax.imshow(runtime.annotate(frame, items)[:, :, ::-1])
        ax.set_title(f'{len(items)} caja(s) del Modelo 1', fontsize=7)
    fig.tight_layout()
    fig.savefig(out, dpi=250)
    plt.close(fig)


def fig6(out: Path) -> None:
    records = [json.loads(line) for line in (ROOT / 'experiments/model2/EXP-R03/predictions.jsonl')
               .read_text(encoding='utf-8').splitlines()]
    order = records[0]['class_names']
    index = {name: i for i, name in enumerate(order)}
    counts = [[0] * len(order) for _ in order]
    for r in records:
        counts[index[r['truth']]][index[r['pred']]] += 1
    rows = [[v / sum(row) if sum(row) else None for v in row] for row in counts]
    labels = [M2_LABELS[n] for n in order]
    fig, (a, b) = plt.subplots(1, 2, figsize=(29.54 / 2.5, 14.86 / 2.5), dpi=250)
    _matrix(a, counts, labels, '(a) Conteos absolutos', 'd')
    _matrix(b, rows, labels, '(b) Proporción por fila verdadera', '.2f')
    for ax in (a, b):
        plt.setp(ax.get_xticklabels(), rotation=30, ha='right', rotation_mode='anchor')
    fig.suptitle(f'Modelo 2, prueba de MangoDHDS_clean (n = {len(records)})', fontweight='bold',
                 fontsize=13)
    fig.tight_layout()
    fig.savefig(out, dpi=250)
    plt.close(fig)


if __name__ == '__main__':
    wanted = sys.argv[1:] or ['fig4', 'fig5', 'fig6', 'fig7']
    targets = {'fig4': 'fig4_confusion_m1.png', 'fig5': 'fig5_detecciones.png',
               'fig6': 'fig6_confusion_m2.png', 'fig7': 'fig7_cascada_validacion.png'}
    FIGURES.mkdir(parents=True, exist_ok=True)
    for name in wanted:
        globals()[name](FIGURES / targets[name])
        print(name, FIGURES / targets[name])
