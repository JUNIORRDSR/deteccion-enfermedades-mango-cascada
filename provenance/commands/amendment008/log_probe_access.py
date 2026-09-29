"""Append the Kaggle probe to the test access log (it hashed test bytes, no inference)."""

import csv
from pathlib import Path

LOG = Path(__file__).resolve().parents[3] / 'provenance/test_access_log.csv'

rows = list(csv.DictReader(open(LOG, encoding='utf-8')))
if not any(r['access_id'] == 'TEST-ACCESS-003' for r in rows):
    rows.append({
        'access_id': 'TEST-ACCESS-003', 'recorded_at': '2026-09-23T04:10:00+00:00',
        'observed_period': '2026-09-23', 'access_type': 'INTEGRITY_CHECK_NO_INFERENCE',
        'evidence': 'experiments/model1/KAGGLE-PROBE-001/receipt.json;kaggle kernel 135462618 v1',
        'new_inference': 'false', 'selection_permitted': 'false',
        'notes': ('Sonda de Kaggle sin modelo: descargó y hasheó las 669 imágenes, incluidas las '
                  'de test, para verificar la fuente pública; ninguna predicción, métrica ni '
                  'visualización.')})
    with LOG.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
print(len(rows))
