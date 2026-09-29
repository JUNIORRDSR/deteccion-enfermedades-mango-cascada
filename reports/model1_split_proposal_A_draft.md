# Propuesta de partición M1 — TASK-03

Algoritmo único de la SPEC §6, seed 42, objetivo [0.7, 0.15, 0.15], sin barrido de semillas.

| split | imágenes | grupos | inst. Enfermo | inst. Saludable | grupos con Enfermo | grupos con Saludable |
|---|---|---|---|---|---|---|
| train | 445 | 14 | 526 | 942 | 1 | 14 |
| valid | 110 | 103 | 29 | 169 | 14 | 90 |
| test | 114 | 108 | 27 | 161 | 10 | 98 |

Imágenes que cambian de split: 304 de 669.
`requires_retraining`: true

`test_history`:
```json
{
  "new_test_images": 114,
  "previously_in_historical_train": 85,
  "previously_in_historical_valid": 24,
  "previously_in_historical_test": 5,
  "note": "The published M1 weights were trained on the historical train split, so they cannot be evaluated as a holdout on the new test. Retraining is required."
}
```

Manifiesto: `data/manifests/model1_clean_manifest_A_draft.csv`, SHA256 `aabb435227ab432c3a4b8b4fd45a474de2ac2e8114d49da858acc8dcacd283e2`.

Estado: **BORRADOR** previo a la adjudicación suplementaria (DECISION-034); conservado por MEDIUM-01 de la revisión de la enmienda 009. Generado con `split.py --audit data/audits/model1 --seed 42 --ratios 0.70 0.15 0.15` sin opciones de la enmienda.
