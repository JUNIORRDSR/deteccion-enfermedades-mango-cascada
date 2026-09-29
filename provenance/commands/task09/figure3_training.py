"""Figure 3 from EXP-R01 (TASK-09): training and validation curves of the retrained M1.

Reads experiments/model1/EXP-R01/v1/run/train/results.csv (Ultralytics per-epoch log) and the
committed selection record; marks the SELECTED epoch, chosen by the maximum unrounded
validation mAP50-95 (the frozen rule), not the maximum mAP50. The DFL loss of YOLO26 stays
below 0.016 in every epoch and is left out; the caption says so. Same pixel size as the figure it replaces, so the DOCX extent stays valid.
"""

import csv
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / 'experiments/model1/EXP-R01'
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'manuscript/figures/fig3_entrenamiento.png'
NAVY, TEAL, CORAL, VIOLET = '#1b365d', '#1d8a7a', '#e8795e', '#7b5ea7'


def main() -> int:
    rows = list(csv.DictReader(open(RUN / 'v1/run/train/results.csv', encoding='utf-8')))
    rows = [{k.strip(): float(v) for k, v in r.items()} for r in rows]
    selection = json.loads((RUN / 'selection_record.json').read_text(encoding='utf-8'))
    best = selection['selected_epoch']
    epoch = [r['epoch'] for r in rows]
    fig, (a, b) = plt.subplots(1, 2, figsize=(28.19 / 2.5, 10.21 / 2.5), dpi=250)
    for key, label, color, style in (('train/box_loss', 'entren. box', NAVY, '-'),
                                     ('train/cls_loss', 'entren. cls', TEAL, '-'),
                                     ('val/box_loss', 'valid. box', NAVY, '--'),
                                     ('val/cls_loss', 'valid. cls', TEAL, '--')):
        a.plot(epoch, [r[key] for r in rows], style, color=color, linewidth=1.3, label=label)
    a.set_title('(a) Pérdidas de entrenamiento y validación', fontweight='bold')
    a.set_xlabel('Época')
    a.set_ylabel('Pérdida')
    a.grid(alpha=0.3)
    a.legend(fontsize=8, ncol=2)
    for key, label, color in (('metrics/mAP50(B)', 'mAP@0,5', TEAL),
                              ('metrics/mAP50-95(B)', 'mAP@0,5:0,95', NAVY),
                              ('metrics/precision(B)', 'Precisión', CORAL),
                              ('metrics/recall(B)', 'Sensibilidad', VIOLET)):
        b.plot(epoch, [r[key] for r in rows], color=color, linewidth=1.3, label=label)
    chosen = next(r for r in rows if int(r['epoch']) == best)
    b.plot([best], [chosen['metrics/mAP50-95(B)']], marker='*', markersize=14, color=NAVY,
           markeredgecolor='white', zorder=5)
    b.annotate(f'época seleccionada {best}\nmAP@0,5:0,95 = '
               f'{chosen["metrics/mAP50-95(B)"]:.3f}'.replace('.', ','),
               xy=(best, chosen['metrics/mAP50-95(B)']), xytext=(best - 55, 0.45),
               fontsize=8.5, color=NAVY, arrowprops={'arrowstyle': '->', 'color': NAVY})
    b.set_ylim(0, 1)
    b.set_title('(b) Métricas sobre el conjunto de validación', fontweight='bold')
    b.set_xlabel('Época')
    b.set_ylabel('Valor')
    b.grid(alpha=0.3)
    b.legend(fontsize=8, loc='lower right')
    comma = FuncFormatter(lambda value, _: f'{value:g}'.replace('.', ','))  # audit B, B-12
    for axis in (a.yaxis, b.yaxis):
        axis.set_major_formatter(comma)
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=250)
    print(OUT, best, chosen['metrics/mAP50-95(B)'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
