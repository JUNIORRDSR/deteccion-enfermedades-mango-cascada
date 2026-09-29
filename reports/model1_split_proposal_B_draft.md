# Propuesta de partición M1 — TASK-03

Algoritmo único de la SPEC §6, seed 42, objetivo [0.7, 0.15, 0.15], sin barrido de semillas.

| split | imágenes | grupos | inst. Enfermo | inst. Saludable | grupos con Enfermo | grupos con Saludable |
|---|---|---|---|---|---|---|
| train | 464 | 464 | 409 | 898 | 250 | 247 |
| valid | 102 | 87 | 86 | 187 | 50 | 46 |
| test | 103 | 90 | 87 | 187 | 48 | 52 |

Imágenes que cambian de split: 297 de 669.
`requires_retraining`: true

`test_history`:
```json
{
  "new_test_images": 103,
  "previously_in_historical_train": 74,
  "previously_in_historical_valid": 23,
  "previously_in_historical_test": 6,
  "note": "The published M1 weights were trained on the historical train split, so they cannot be evaluated as a holdout on the new test. Retraining is required."
}
```

Manifiesto: `data/manifests/model1_clean_manifest_B_draft.csv`, SHA256 `fbfe99b956b5838de9b53e5c733a579b9bbd7af95116dff9ee6715ad1657545f`.

Estado: **PROPUESTA**. La congelación se revisa antes de TASK-04.
