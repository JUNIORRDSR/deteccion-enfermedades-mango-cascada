"""TASK-07: cascade ground truth contract and joint scoring (SPEC section 9).

No disease-specific ground truth exists on the same scenes/fruits the detector
was evaluated on: DATA-001 (SemilleroTI-Mangos) labels Enfermo/Saludable boxes
on scene images; DATA-005 (Mango-vision DatasetMango_YOLO_cls) labels the four
diseases plus Saludable, but on fruit-centred crops from a different source,
with zero detection boxes. The classifier's own output is never ground truth.
State stays BLOCKED_BY_GROUND_TRUTH until an independent annotation arrives
matching the schema below; this module ships the schema, the validator and the
scorer such a study would need, with no invented accuracy in the meantime.

Primary success per diseased fruit is a JOINT event, never a product of two
marginal rates: one-to-one detection (IoU >= threshold, matching reused from
src.evaluation.evaluate.match) AND the cascade's final label equal to the
specific disease. Undetected fruits, M1 routing a diseased fruit to "healthy"
(so M2 never runs) and M2 abstentions are all failures of that same event and
all stay inside the recall denominator.
"""

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from src.evaluation.evaluate import match
from src.evaluation.provenance import InvalidInput, authorized_root, check_output, sanitize_text

DISEASES = ('Antracnosis', 'Cancro_bacteriano', 'Costras', 'Podredumbre_Extremo_tallo')
HEALTHY = 'Saludable'
AMBIGUOUS_LABELS = ('AMBIGUOUS', 'UNDIAGNOSED')
ALLOWED_DISEASE_LABELS = (*DISEASES, HEALTHY, *AMBIGUOUS_LABELS)
ABSTAIN = 'ABSTAIN'
ALLOWED_PREDICTED_LABELS = (*DISEASES, HEALTHY, ABSTAIN)
HEALTH_STATUSES = ('healthy', 'diseased')
INDEPENDENT = 'INDEPENDENT_ADJUDICATED'
ADJUDICATION_STATUSES = (INDEPENDENT, 'PENDING_ADJUDICATION', 'MODEL_ASSISTED')
REJECTED_DIAGNOSTIC_METHOD = 'model_prediction'
REQUIRED_GT_FIELDS = ('image_id', 'fruit_id', 'bbox_xyxy', 'disease_label', 'healthy_or_diseased',
                      'adjudication_status', 'annotator_id', 'diagnostic_method', 'date',
                      'group_id', 'source')
M2_DEFAULT_THRESHOLD = 0.4  # predefined candidate (SPEC section 9); never optimised on test.


def _bbox_ok(value) -> bool:
    return (isinstance(value, list) and len(value) == 4
            and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in value)
            and value[2] > value[0] and value[3] > value[1])


def _date_ok(value) -> bool:
    if not isinstance(value, str) or len(value) != 10:
        return False
    try:
        year, month, day = value.split('-')
        return len(year) == 4 and len(month) == len(day) == 2 and 1 <= int(month) <= 12 \
            and 1 <= int(day) <= 31
    except ValueError:
        return False


def validate_ground_truth(rows: list[dict]) -> None:
    """SPEC section 9 annotation schema. Raises ValueError('CODE:fruit_id') before use.

    Allowed labels are the four diseases and Saludable; AMBIGUOUS/UNDIAGNOSED are kept
    (never dropped) but score_cascade reports them outside the diagnostic denominator with
    an explicit count. diagnostic_method == 'model_prediction' is never accepted: a model's
    own output can never stand in for independently adjudicated ground truth.
    """
    seen_fruit: set[tuple] = set()
    for row in rows:
        where = row.get('fruit_id', 'UNKNOWN') if isinstance(row, dict) else 'UNKNOWN'
        if not isinstance(row, dict) or set(REQUIRED_GT_FIELDS) - set(row):
            raise ValueError(f'SCHEMA:{where}')
        if row['diagnostic_method'] == REJECTED_DIAGNOSTIC_METHOD:
            raise ValueError(f'MODEL_PREDICTION_REJECTED:{where}')
        image_id = row['image_id']
        if not (isinstance(image_id, str) and len(image_id) == 64
                and all(c in '0123456789abcdef' for c in image_id)):
            raise ValueError(f'BAD_IMAGE_ID:{where}')
        fruit_key = (image_id, row['fruit_id'])
        if not row['fruit_id'] or not isinstance(row['fruit_id'], str) or fruit_key in seen_fruit:
            raise ValueError(f'DUPLICATE_OR_MISSING_FRUIT_ID:{where}')
        seen_fruit.add(fruit_key)
        if not _bbox_ok(row['bbox_xyxy']):
            raise ValueError(f'BAD_BBOX:{where}')
        if row['disease_label'] not in ALLOWED_DISEASE_LABELS:
            raise ValueError(f'BAD_DISEASE_LABEL:{where}')
        if row['healthy_or_diseased'] not in HEALTH_STATUSES:
            raise ValueError(f'BAD_HEALTHY_OR_DISEASED:{where}')
        if row['disease_label'] in DISEASES and row['healthy_or_diseased'] != 'diseased':
            raise ValueError(f'INCONSISTENT_HEALTH_STATUS:{where}')
        if row['disease_label'] == HEALTHY and row['healthy_or_diseased'] != 'healthy':
            raise ValueError(f'INCONSISTENT_HEALTH_STATUS:{where}')
        if row['adjudication_status'] not in ADJUDICATION_STATUSES:
            raise ValueError(f'BAD_ADJUDICATION_STATUS:{where}')
        for field in ('annotator_id', 'diagnostic_method', 'group_id', 'source'):
            if not isinstance(row[field], str) or not row[field]:
                raise ValueError(f'MISSING_{field.upper()}:{where}')
        if not _date_ok(row['date']):
            raise ValueError(f'BAD_DATE:{where}')


def _check_prediction(row: dict) -> None:
    if not isinstance(row, dict) or 'image_id' not in row:
        raise ValueError('PREDICTION_SCHEMA:missing image_id')
    where = row.get('image_id', 'UNKNOWN')
    if not _bbox_ok(row.get('bbox_xyxy')):
        raise ValueError(f'PREDICTION_BAD_BBOX:{where}')
    if row.get('predicted_label') not in ALLOWED_PREDICTED_LABELS:
        raise ValueError(f'PREDICTION_BAD_LABEL:{where}')


def _by_image(rows: list[dict]) -> dict:
    grouped = defaultdict(list)
    for row in rows:
        grouped[row['image_id']].append(row)
    return grouped


def score_cascade(gt: list[dict], pred: list[dict], iou_threshold: float = 0.5) -> dict:
    """SPEC section 9. Never multiplies detection recall by classification accuracy.

    Matching runs over every GT fruit in an image (any adjudication status) so a
    prediction that lands on a not-yet-adjudicated or ambiguous fruit is excluded from
    metrics rather than miscounted as an extra false positive.
    """
    validate_ground_truth(gt)
    for row in pred:
        _check_prediction(row)

    excluded_non_independent = sum(1 for g in gt if g['adjudication_status'] != INDEPENDENT)
    ambiguous_count = sum(1 for g in gt if g['adjudication_status'] == INDEPENDENT
                          and g['disease_label'] in AMBIGUOUS_LABELS)

    gt_by_image, pred_by_image = _by_image(gt), _by_image(pred)
    tp: Counter = Counter()
    fp: Counter = Counter()
    outcomes = []

    def _score_extra(predictions, indices) -> None:
        for p_idx in indices:
            label = predictions[p_idx]['predicted_label']
            if label in DISEASES:
                fp[label] += 1

    for image_id, image_gt in gt_by_image.items():
        image_pred = pred_by_image.get(image_id, [])
        result = match([{'xyxy': g['bbox_xyxy']} for g in image_gt],
                       [{'xyxy': p['bbox_xyxy']} for p in image_pred], iou_threshold)
        matched = {m['gt']: m['pred'] for m in result['matches']}
        for g_idx, g in enumerate(image_gt):
            p_idx = matched.get(g_idx)
            predicted_label = image_pred[p_idx]['predicted_label'] if p_idx is not None else None
            if g['adjudication_status'] != INDEPENDENT or g['disease_label'] in AMBIGUOUS_LABELS:
                continue  # matched or not, this fruit can never produce a metric
            if g['disease_label'] == HEALTHY:
                outcome = ('success' if predicted_label == HEALTHY else
                          'undetected' if predicted_label is None else 'misdiagnosed_as_diseased')
                if predicted_label in DISEASES:
                    fp[predicted_label] += 1
            elif predicted_label is None:
                outcome = 'undetected'
            elif predicted_label == HEALTHY:
                outcome = 'm1_predicted_healthy'
            elif predicted_label == ABSTAIN:
                outcome = 'm2_abstained'
            elif predicted_label == g['disease_label']:
                outcome = 'success'
                tp[predicted_label] += 1
            else:
                outcome = 'wrong_diagnosis'
                if predicted_label in DISEASES:
                    fp[predicted_label] += 1
            outcomes.append({'image_id': image_id, 'fruit_id': g['fruit_id'],
                             'truth': g['disease_label'], 'predicted': predicted_label,
                             'outcome': outcome})
        _score_extra(image_pred, result['unmatched_pred'])
    for image_id, image_pred in pred_by_image.items():
        if image_id not in gt_by_image:
            _score_extra(image_pred, range(len(image_pred)))

    diseased = [o for o in outcomes if o['truth'] in DISEASES]
    successes = sum(o['outcome'] == 'success' for o in diseased)
    denominator = len(diseased)

    detected_diseased = [o for o in diseased if o['outcome'] != 'undetected']
    conditional_correct = sum(o['outcome'] == 'success' for o in detected_diseased)
    routed_to_m2 = [o for o in detected_diseased if o['outcome'] != 'm1_predicted_healthy']
    abstained = sum(o['outcome'] == 'm2_abstained' for o in routed_to_m2)

    per_disease_precision = {}
    for disease in DISEASES:
        denom = tp[disease] + fp[disease]
        per_disease_precision[disease] = {
            'tp': tp[disease], 'fp': fp[disease],
            'precision': tp[disease] / denom if denom else None, 'precision_denominator': denom}

    return {
        'joint_recall': {'successes': successes, 'denominator': denominator,
                         'value': successes / denominator if denominator else None},
        'per_disease_precision': per_disease_precision,
        'excluded': {'non_independent_count': excluded_non_independent,
                    'ambiguous_or_undiagnosed_count': ambiguous_count},
        'secondary': {
            'conditional_classification_given_detected': {
                'correct': conditional_correct, 'denominator': len(detected_diseased),
                'accuracy': conditional_correct / len(detected_diseased)
                           if detected_diseased else None},
            'm2_abstention_rate': {
                'abstained': abstained, 'denominator': len(routed_to_m2),
                'rate': abstained / len(routed_to_m2) if routed_to_m2 else None}},
        'outcomes': outcomes,
    }


def _read_jsonl(path: Path) -> list[dict]:
    rows = []
    for number, line in enumerate(Path(path).read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise InvalidInput(f'{path.name} line {number}: not JSON: {error}') from None
        if not isinstance(row, dict):
            raise InvalidInput(f'{path.name} line {number}: not an object')
        rows.append(row)
    return rows


def check_availability(inventory_path: Path) -> dict:
    """Reads the legacy inventory (TASK-02 manifest) and shows why DATA-001/DATA-005
    cannot be joined into disease-specific ground truth for the current corpora."""
    with Path(inventory_path).open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    by_dataset = defaultdict(list)
    for row in rows:
        by_dataset[row['dataset_id']].append(row)
    summary = {}
    for dataset_id in ('DATA-001', 'DATA-005'):
        members = by_dataset.get(dataset_id, [])
        summary[dataset_id] = {
            'n_rows': len(members),
            'class_names': sorted({m['class_names'] for m in members}),
            'sample_relative_path': members[0]['relative_path'] if members else None,
            'has_boxes': any(m.get('box_count', '0') not in ('', '0') for m in members)}
    return summary


def format_availability_assessment(summary: dict, inventory_path: Path) -> str:
    d1, d5 = summary['DATA-001'], summary['DATA-005']
    return f"""# Evaluación de disponibilidad de ground truth de cascada — BLOCKED_BY_GROUND_TRUTH

Fuente: `{inventory_path}` (inventario congelado en TASK-02).

## Hallazgo

No existe, para el corpus actual, ninguna escena/fruto con ground truth de
enfermedad específica adjudicado independientemente que coincida con las
imágenes usadas para evaluar el detector M1. Por lo tanto **no se calcula
ninguna métrica de la cascada** (recall conjunto, precisión por enfermedad,
clasificación condicional ni tasa de abstención) en esta edición: el estado
declarado por la SPEC §9 se mantiene, `BLOCKED_BY_GROUND_TRUTH`.

## Evidencia

- **DATA-001** (corpus del detector, `SemilleroTI-Mangos/docs/MangosDataset`):
  {d1['n_rows']} filas, clases {d1['class_names']}, con cajas
  (`has_boxes={d1['has_boxes']}`). Ejemplo de ruta: `{d1['sample_relative_path']}`.
  Etiqueta binaria Enfermo/Saludable por caja, nunca la enfermedad específica.
- **DATA-005** (corpus del clasificador, `Mango-vision/DatasetMango_YOLO_cls`):
  {d5['n_rows']} filas, clases {d5['class_names']}, sin cajas de detección
  (`has_boxes={d5['has_boxes']}`). Ejemplo de ruta: `{d5['sample_relative_path']}`.
  Imágenes centradas en el fruto de origen distinto (Mango-vision, no
  SemilleroTI-Mangos): no son las mismas escenas ni los mismos frutos que
  DATA-001, y no traen caja para emparejar con una detección M1.

Ningún archivo de `{inventory_path}` vincula un `image_id` de DATA-001 con un
`image_id` de DATA-005 sobre el mismo fruto físico. Sin esa correspondencia no
hay unidad de análisis fruto-a-fruto que sostenga un recall conjunto: la salida
del clasificador tampoco puede sustituir esa anotación (`diagnostic_method`
`model_prediction` queda rechazado por `validate_ground_truth`).

## Qué se entrega en su lugar

El esquema (`data/manifests/cascade_annotation_schema.json`), el validador
(`validate_ground_truth`) y el evaluador (`score_cascade`) quedan implementados
y probados con fixtures sintéticos (`tests/test_cascade.py`); no se produce
ningún CSV de accuracy porque no hay entrada real que anotar. Ver
`reports/cascade_protocol.md` para el protocolo que un estudio futuro con GT
independiente debería seguir antes de ejecutar esta rama.
"""


def _write_score(path: Path, result: dict) -> None:
    path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-availability', action='store_true')
    parser.add_argument('--annotations', type=Path)
    parser.add_argument('--predictions', type=Path)
    parser.add_argument('--inventory', type=Path,
                        default=Path('data/manifests/legacy_dataset_inventory.csv'))
    parser.add_argument('--iou-threshold', type=float, default=0.5)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()

    root = authorized_root()
    destination = check_output(root, args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)

    if args.check_availability:
        summary = check_availability(args.inventory)
        destination.write_text(format_availability_assessment(summary, args.inventory),
                               encoding='utf-8')
        print(f'wrote {destination}: BLOCKED_BY_GROUND_TRUTH, no metrics produced')
        return 0

    if not args.annotations or not args.predictions:
        parser.error('--annotations and --predictions are required without --check-availability')
    gt = _read_jsonl(args.annotations)
    pred = _read_jsonl(args.predictions)
    result = score_cascade(gt, pred, args.iou_threshold)
    _write_score(destination, result)
    print(f'wrote {destination}')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, InvalidInput, OSError) as error:
        print(sanitize_text(str(error)), file=sys.stderr)
        sys.exit(2)
