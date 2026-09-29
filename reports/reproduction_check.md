# Reproducción fresca de los resultados congelados (TASK-10)

**Fecha:** 2026-09-28 · **HEAD reproducidos:** `c74f829b1a671d2f62e12db6459b03d66d49e421` y, tras las pasadas 2e, `cc19e9451aa81c40f50d8cbca203e88dcd9f5137` · **Orden:** `provenance/commands/task10/reproduce_frozen.ps1` · **Registro:** `reports/reproduction_check.log` (segunda ejecución; la primera queda en el historial de git).

Las dos ejecuciones dan el mismo resultado. Los commits posteriores a `cc19e94` sólo cambian el manuscrito, la carta y los informes, no las entradas de la evaluación.

## Método

Un clon limpio del HEAD, dentro del proyecto (`ALBUS26_major_revision/.repro/final`, borrado al terminar), con `core.autocrlf=false` como la rama de trabajo y un enlace de directorio al mismo `.venv` aprobado. Se borraron seis salidas comprometidas y se regeneraron con las órdenes literales del protocolo, sin elegir ningún parámetro:

1. `python -m src.evaluation.evaluate --model-id model1 --config configs/evaluation_frozen.json --split test --run-dir experiments/model1/EXP-R02`
2. `python -m src.statistics.intervals --predictions experiments/model1/EXP-R02/predictions.jsonl --groups data/manifests/model1_clean_manifest.csv --seed 42 --resamples 2000 --out artifacts/metrics/model1_intervals.json`
3. `python -m src.statistics.intervals --predictions experiments/model2/EXP-R03/predictions.jsonl --groups data/manifests/model2_frozen_manifest.csv --seed 42 --resamples 2000 --out artifacts/metrics/model2_intervals.json`

Cada orden pasó la puerta de inferencia aprobada (instantánea de `inference_approval` versión 10) antes de leer datos. No se repitió ninguna inferencia: la puntuación reconstruye las predicciones desde el intento definitivo de Kaggle ya comprometido.

## Resultado

| Salida | SHA-256 comprometido | Regenerado |
|---|---|---|
| `experiments/model1/EXP-R02/metrics.json` | `5c38381b…8774` | idéntico |
| `experiments/model1/EXP-R02/predictions.jsonl` | `a4de90cf…303d` | idéntico |
| `experiments/model1/EXP-R02/predictions.jsonl.sha256` | `51d2c111…142f` | idéntico |
| `experiments/model1/EXP-R02/prediction_provenance.json` | `42817fd7…7efc` | idéntico |
| `artifacts/metrics/model1_intervals.json` | `1d2192a3…3851` | idéntico |
| `artifacts/metrics/model2_intervals.json` | `03c922cb…3043` | idéntico |

Las seis salidas coinciden byte a byte, así que la tolerancia de 1e-6 del plan no llega a usarse. La auditoría independiente A (`reports/execution/task-05-execution-audit.md`, sección 3) reprodujo además, en otro clon, la puntuación de validación, la congelación del umbral, la sensibilidad del Modelo 2 y la derivación de la Tabla 4, también byte a byte.

## Incidencia registrada

El primer intento se detuvo antes de leer datos: el clon se creó con la configuración del sistema (`core.autocrlf=true`), que cambia los finales de línea al extraer, y la puerta rechazó el protocolo congelado porque su huella no coincidía (`88e982a9…` frente a `6d5aa3ff…`). Es el comportamiento esperado de la puerta. Se repitió con `core.autocrlf=false`, la configuración local de la rama de trabajo.
