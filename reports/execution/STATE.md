# Estado de la revisión ALBUS26-116 — punto de reanudación

**Fecha:** 2026-09-28 · **Plazo editorial:** 30-09-2026 · **Rama:** `revision/execute-approved-plan` (local) · **Worktree:** `ALBUS26_major_revision/.worktrees/execution` · **Publicación:** `https://github.com/JUNIORRDSR/deteccion-enfermedades-mango-cascada` (remoto `origin`, un commit, versión 1.0.0).

Protocolo congelado `ALBUS26-116-PROTOCOL-001` (commit `7d0f998`, JSON `6d5aa3ff…c8b`), intacto.

## Resultados congelados

| experimento | resultado | artefactos |
|---|---|---|
| EXP-V01 v2 | mAP@0,5 0,889 (113 imágenes); umbral congelado 0,35 (F2 Enfermo 0,884) | `experiments/model1/EXP-V01/`, `configs/evaluation_frozen.json` (`96a5991`) |
| EXP-R02 v1 | prueba única, retrospectiva: mAP@0,5 0,807 [0,677; 0,887]; sensibilidad Enfermo 0,577 [0,273; 0,735] | `experiments/model1/EXP-R02/`, `artifacts/metrics/model1_intervals.json`, TEST-ACCESS-004 |
| EXP-R03 | M2 local, 219 imágenes: exactitud 0,909 [0,869; 0,946]; sensibilidad a duplicados < 1 punto | `experiments/model2/EXP-R03/`, `artifacts/metrics/model2_*`, TEST-ACCESS-005 |
| TASK-06 | CPU local: mediana extremo a extremo 239,4 ms (p95 777,7 ms) | `reports/benchmark_report.md`, `artifacts/metrics/benchmark_summary.json` |

## Revisiones

- Auditoría A (`reports/execution/task-05-execution-audit.md`): resultados válidos, reproducción byte a byte.
- Auditoría B, ronda 1 (4 HIGH, 6 MEDIUM): corregidos en la pasada 2d.
- Auditoría B, ronda 2 (2 HIGH, 5 MEDIUM): corregidos en la pasada 2e.
- Revisión adversarial final (`reports/final_adversarial_review.md`): recomienda rechazar, con 6 HIGH y 8 MEDIUM. La pasada 2f corrige o declara lo que el texto puede resolver. Quedan abiertos 4 HIGH y 2 MEDIUM que exigen datos nuevos o revisión humana (`reports/editorial_audit.md`, sección 7).

## Decisiones de los autores del 2026-09-28

- Declarar ya que la adjudicación visual la hicieron agentes de IA; la re-adjudicación humana queda como trabajo futuro.
- Mantener el título.
- Publicar un único commit del estado final, con autor noreply, los pesos de los dos modelos y licencia AGPL-3.0. Quedan fuera el dictamen, la carta, las versiones anteriores del manuscrito y la plantilla de la revista.

## Estado

TASK-01 a TASK-10 están ejecutadas; `docs/final_validation_report.md` recoge los gates A a I. El gate I no está satisfecho y la revisión no se declara DONE. Enviar así el manuscrito es decisión de los autores.

## Hallazgos técnicos

- El MCP de Kaggle no monta entradas: los kernels de predicción se lanzan desde el editor web con Import Notebook (DECISION-038/039).
- La puerta de inferencia rechaza código sin seguimiento, así que cada script va a commit antes de ejecutarse.
- Un clon para reproducir necesita `core.autocrlf=false` y un enlace al mismo `.venv`; al borrarlo, hay que quitar primero el enlace con `rmdir`.
- `python-docx` sólo está en el Python del sistema; el `.venv` no debe cambiar.
- En la terminal Bash de este equipo, los heredocs con texto largo fallan: los scripts van a un archivo.
