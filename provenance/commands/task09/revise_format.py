"""TASK-09, REVIEW-14/15: decimal comma and Spanish labels where no new result is involved.

The manuscript writes decimals with a comma (pass 2b onwards); version numbers (8.4.52,
CUDA 12.8), the YOLO label literal «cls 0.5 0.5 1.0 1.0» and reference titles keep their dots.
Hyperparameter labels of Tables 2 and 3 go to Spanish with the Ultralytics argument in
parentheses, so the configuration stays reproducible. Result paragraphs are left to pass 2c.
Table 2's augmentation row lists what EXP-R01 applied (run/train/args.yaml and the job log):
erasing and randaugment are classification-only in Ultralytics (ClassificationDataset) and
never reached the detector, while the Albumentations transforms and close_mosaic did.
Table 3's row follows ART-002's train_args, trained with Ultralytics 8.4.52, whose
classify_augmentations applies RandomResizedCrop(scale=(1 - scale, 1)), the flip, RandAugment
and RandomErasing, and skips ColorJitter when RandAugment is on.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import docx  # noqa: E402
from docx_edit import cell_text, replace, sha  # noqa: E402

DOCX = ROOT / 'manuscript/source/Articulo_Mango_ALBUS_revision.docx'
T2, T3 = 1, 2  # python-docx indices of Tablas 2 y 3
LABELS = {
    T2: {'Paciencia (early stopping)': 'Paciencia (patience)',
         'Batch size': 'Tamaño de lote (batch)',
         'Learning rate (lr0 / lrf)': 'Tasa de aprendizaje (lr0 / lrf)',
         'Momentum': 'Momento (momentum)',
         'Weight decay': 'Decaimiento de pesos (weight_decay)',
         'Warmup epochs': 'Épocas de calentamiento (warmup_epochs)',
         'Pre-entrenamiento': 'Preentrenamiento'},
    T3: {'Batch size': 'Tamaño de lote (batch)'},
}
VALUES = {
    T2: {'Tasa de aprendizaje (lr0 / lrf)': ('0.001667 (auto) / 0.01', '0,001667 (auto) / 0,01'),
         'Momento (momentum)': ('0.9 (auto)', '0,9 (auto)'),
         'Aumentación': ('Mosaic 1.0, HSV 0.015/0.7/0.4, flip H p=0.5, scale 0.5, translate 0.1, '
                         'erasing 0.4, randaugment',
                         'mosaic 1,0 (sin mosaico en las 10 últimas épocas); HSV 0,015/0,7/0,4; '
                         'fliplr 0,5; scale 0,5; translate 0,1; Albumentations: Blur, MedianBlur, '
                         'ToGray y CLAHE, p = 0,01 cada una'),
         'Tiempo total': ('≈ 18.7 min (sesión completa)', '≈ 18,7 min (sesión completa)')},
    T3: {'Arquitectura': ('YOLO11n-cls (1.5M params)', 'YOLO11n-cls (1,5 M parámetros)'),
         'lr0 (auto)': ('≈ 0.0011', '≈ 0,0011'),
         'Aumentación': ('flip H, ajuste brillo/contraste, RandomResizedCrop, randaugment',
                         'RandomResizedCrop (escala 0,5–1); fliplr 0,5; RandAugment; '
                         'RandomErasing p = 0,4; sin ajuste de color, que Ultralytics desactiva '
                         'con RandAugment')},
}


def main() -> int:
    before = sha(DOCX)
    d = docx.Document(DOCX)
    for table, mapping in LABELS.items():
        labels = [row.cells[0].text for row in d.tables[table].rows]
        for old, new in mapping.items():
            cell_text(d, table, labels.index(old), 0, new)
    for table, mapping in VALUES.items():
        labels = [row.cells[0].text for row in d.tables[table].rows]
        for label, (old, new) in mapping.items():
            row = labels.index(label)
            if d.tables[table].cell(row, 1).text != old:
                raise SystemExit(f'{label}: expected {old!r}, found {d.tables[table].cell(row, 1).text!r}')
            cell_text(d, table, row, 1, new)
    replace(d, '(1.5 M parámetros)', '(1,5 M parámetros)')
    replace(d, 'transferido desde pesos pre-entrenados en ImageNet', 'transferido desde pesos '
            'preentrenados en ImageNet')
    replace(d, '(exactitud top-1 en validación = 0.935)', '(exactitud top-1 en validación = 0,935)')
    d.save(DOCX)
    docx.Document(DOCX)
    log = ROOT / 'manuscript/source/edit_log.json'
    entries = json.loads(log.read_text(encoding='utf-8'))
    entries.append({'pass': 'format', 'script': 'provenance/commands/task09/revise_format.py',
                    'before_sha256': before, 'after_sha256': sha(DOCX)})
    log.write_text(json.dumps(entries, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(entries[-1], indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
