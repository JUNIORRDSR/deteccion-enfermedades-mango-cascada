# Informe final de validación — revisión mayor ALBUS26-116

**Fecha:** 2026-09-28, actualizado el 2026-09-29 tras las pasadas 2g y 2h · **Plazo editorial:** 30-09-2026 · **Rama:** `revision/execute-approved-plan` (local) · **Protocolo:** `ALBUS26-116-PROTOCOL-001`, commit `7d0f998`, JSON `6d5aa3ff…c8b`, intacto.

**Estado de entrega: pendiente de la decisión de los autores.** Todas las tareas del plan están ejecutadas. El manuscrito, la carta y la evidencia son coherentes entre sí y con los artefactos. Falla un criterio de cierre del plan (TASK-10, «cero hallazgos HIGH/MEDIUM abiertos»), así que la revisión no se declara DONE. La revisión adversarial final recomienda rechazar. Deja abiertos 4 HIGH y 2 MEDIUM que ningún cambio de texto resuelve, porque exigen datos nuevos o una re-adjudicación documentada. Enviar el manuscrito así es decisión de los autores.

**Candidato final:**

- DOCX `manuscript/source/Articulo_Mango_ALBUS_revision.docx`, SHA-256 `f16115958d081467283089639b9f5f7a901acca2a835e20c364c55be016395ed` (pasada 2h).
- PDF `manuscript/output/Articulo_Mango_ALBUS_revision.pdf`, SHA-256 `86bd462910f09b41d4a9920f30bd1022d0a26c98e56fcb30653e233222120b28`, 16 páginas.
- Carta: `docs/response_to_reviewers.md`, que no se publica.

## Gates

| Gate | Estado | Evidencia |
|---|---|---|
| A — repositorio entendido | SATISFIED | `reports/source_verification.json`; inventario, genealogía y matrices de la primera fase |
| B — diseño aprobado | SATISFIED | DECISION-027: freeze verificado (`reports/amendments/freeze_verification.json`) |
| C — plan aprobado | SATISFIED | DECISION-027 |
| D — datos validados | SATISFIED_WITH_DECLARED_LIMIT | Ver el detalle bajo la tabla |
| E — experimentos validados | SATISFIED para EXP-R01, EXP-V01, EXP-R02 y EXP-R03; BLOCKED para la Raspberry Pi 4 (hardware) y la métrica de la cascada (verdad de terreno) | Auditoría A (`reports/execution/task-05-execution-audit.md`): válido, reproducción byte a byte; `reports/reproduction_check.md`: 6 salidas idénticas en un clon limpio |
| F — claims validados | SATISFIED | Ver el detalle bajo la tabla |
| G — manuscrito validado | SATISFIED | 165 cifras recalculadas desde sus artefactos sin incidencias (`reports/manuscript_consistency.json`); 22 referencias y 22 claves citadas, sin huecos; render de 16 páginas revisado página a página (`reports/execution/render_review.md`) |
| H — respuesta validada | SATISFIED | Los 18 REVIEW tienen respuesta, con las ubicaciones del render final y las cifras escritas desde los artefactos. Estados: RESUELTO, con límites declarados en REVIEW-01; BLOQUEADO (REVIEW-08, REVIEW-12/13); RESPUESTA RAZONADA (REVIEW-11) |
| I — revisión adversarial final | NOT SATISFIED | Ver el detalle bajo la tabla |

**Gate D.** El manifiesto del detector está congelado (`dd9431dd…`) y `MangoDHDS_clean` se comprobó reejecutando el detector de duplicados. Límites declarados:

- la adjudicación visual se hizo primero con apoyo de agentes de IA, de fiabilidad limitada, y después la revisó manualmente una integrante del equipo, sin registro caso a caso (DECISION-040);
- queda un cluster de entrenamiento del Modelo 2 con dos etiquetas;
- `reports/protocol_compliance.json` lo registra en AMENDMENT-03.

**Gate F.** Las 50 afirmaciones del manuscrito enviado tienen destino final: REPLACED 13, SUPPORTED 10, RETIRED 8, REFORMULATED 7, QUALIFIED 6 y CORRECTED 6. Ninguna queda pendiente. `reports/editorial_claim_audit.csv` recoge 28 decisiones de lenguaje y `reports/editorial_audit.md` las explica.

**Gate I.** La revisión se ejecutó y recomienda rechazar (6 HIGH, 8 MEDIUM). La pasada 2f corrige o declara lo que el texto puede resolver. Quedan abiertos los HIGH H-01 (la revisión manual posterior no tiene registro caso a caso ni fue una re-adjudicación externa con ciego efectivo), H-03, H-04 y H-05, y los MEDIUM M-02 y M-03 en su parte de adjudicación y reentrenamiento (`reports/editorial_audit.md`, sección 7). Nadie volvió a revisar las pasadas 2f y 2g.

## Revisiones independientes

Todas las revisiones independientes de esta rama las hicieron modelos de IA en sesiones separadas de la que ejecutó el trabajo, no personas:

- las revisiones de cada tarea y de las enmiendas;
- la auditoría A de la ejecución;
- las rondas 1 y 2 de la auditoría B;
- la revisión adversarial final.

Sus informes están en `reports/execution/`, `reports/amendments/` y `reports/final_adversarial_review.md`. La adjudicación visual de la auditoría de fuga del detector se hizo primero con apoyo de agentes de IA y después la revisó manualmente una integrante del equipo, como declara la Sección 3.3.1 del manuscrito.

## Verificaciones finales

| Comprobación | Orden | Resultado |
|---|---|---|
| Suite completa | `.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"` | 397 pruebas, OK |
| Fuentes heredadas | `python -m src.evaluation.provenance --source-manifest provenance/source_manifest.csv --source-locations provenance/source_locations.csv --root-mapping configs/root_mapping.json --out reports/legacy_final_verification.json` | 11137 archivos, 0 discrepancias, salida 0 |
| Git de los repositorios heredados | `python provenance/commands/task10/legacy_git_check.py` | 14 de 14 salidas iguales al estado inicial |
| Portabilidad | `python provenance/commands/task10/portability_check.py` | 6 de 6 comprobaciones (`reports/portability_check.json`) |
| Reproducción en clon limpio | `powershell -File provenance/commands/task10/reproduce_frozen.ps1` | 6 salidas idénticas byte a byte en el HEAD `cc19e94`; los commits posteriores sólo cambian el manuscrito, la carta y los informes, no las entradas de la evaluación |
| Cifras del manuscrito | `python -m src.evaluation.document_checks --docx … --claims … --metrics artifacts/metrics --out reports/manuscript_consistency.json` | 165 cifras, 0 incidencias, sin lenguaje sin revisar |
| Citas del DOCX | `python provenance/commands/task09/check_citations.py` | 22 entradas y 22 claves citadas |
| Cumplimiento del protocolo | `reports/protocol_compliance.json` | AMENDMENT-01, 02 y 04 a 07 SATISFIED; 03 y 008 SATISFIED_WITH_DECLARED_LIMIT; 009 WITHDRAWN |

`reports/bibliography_check.json` sigue listando `dane2023` y `vanderheijden2022`. Son dos referencias del manuscrito enviado que la auditoría bibliográfica retiró, y quedan en `reports/citation_links.csv` como registro.

## Publicación

El repositorio público `https://github.com/JUNIORRDSR/deteccion-enfermedades-mango-cascada` está conectado como `origin`. Los autores publicaron el 2026-09-29 la release v1.0.0, con el estado de la pasada 2f, cuyo manuscrito aún no describe la revisión manual posterior de la adjudicación. La versión 1.0.1, con las pasadas 2g y 2h, queda preparada en la rama local `publicacion` y la etiqueta `v1.0.1`. Es un commit hijo del `main` publicado, así que su subida no reescribe la 1.0.0. El manuscrito cita la 1.0.1. Además del código y la evidencia, incluye los pesos de los dos modelos y se publica bajo la licencia AGPL-3.0. Se dejaron fuera, por decisión de los autores, la correspondencia de la revisión por pares, la carta de respuesta, el texto de las versiones anteriores del manuscrito y la plantilla de la revista. El manuscrito lo cita como Villa Bastidas et al. (2026).

## Qué falta para cerrar la revisión según el plan

1. **Registro de la revisión manual** de la auditoría del detector: las decisiones por candidato y cualquier desacuerdo con la adjudicación asistida por IA. Para cerrar H-01 del todo, una re-adjudicación de las 35 unidades y los 47 pares por personas ajenas al entrenamiento y con un ciego efectivo. Si cambia algún grupo, hay que rehacer la partición, reentrenar y evaluar en datos nuevos, porque la prueba actual ya se usó.
2. **Un conjunto externo**, con caja y diagnóstico adjudicados para los mismos frutos y confirmación fitopatológica. Sin él no se miden la cascada, la validez de las etiquetas ni la generalización.
3. **Adjudicación con experto** del cluster de entrenamiento del Modelo 2 con dos etiquetas, y reentrenamiento con muestreo por grupos.
4. **Una revisión independiente de las pasadas 2f y 2g.**
