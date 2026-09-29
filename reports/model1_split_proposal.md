# Propuesta de partición M1 — TASK-03

Algoritmo único de la SPEC §6, seed 42, objetivo [0.7, 0.15, 0.15], sin barrido de semillas.

| split | imágenes | grupos | inst. Enfermo | inst. Saludable | grupos con Enfermo | grupos con Saludable |
|---|---|---|---|---|---|---|
| train | 439 | 8 | 526 | 937 | 1 | 8 |
| valid | 113 | 93 | 30 | 169 | 9 | 84 |
| test | 117 | 98 | 26 | 166 | 15 | 84 |

Imágenes que cambian de split: 304 de 669.
`requires_retraining`: true

`test_history`:
```json
{
  "new_test_images": 117,
  "previously_in_historical_train": 89,
  "previously_in_historical_valid": 21,
  "previously_in_historical_test": 7,
  "note": "The published M1 weights were trained on the historical train split, so they cannot be evaluated as a holdout on the new test. Retraining is required."
}
```

Manifiesto: `data/manifests/model1_clean_manifest.csv`, SHA256 `dd9431dd7bbc00c6117baf6a0f6cf49eff8bc55f144016b4a98dbdea049ecf5f`.

Estado: **CONGELADA**. La revisión de puerta de la ronda 6 (`reports/amendments/gate-review-exp-r01.md`, parte B) reprodujo los bytes del manifiesto y la aceptó como entrada de EXP-R01.
