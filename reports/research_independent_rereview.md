# Relectura independiente del diseño — ALBUS26-116

Fecha: 2026-09-18. Alcance exclusivamente documental: correcciones RIR-01–06, SPEC, plan, matrices e informe ejecutivo. Se conserva `research_independent_review.md`. No se ejecutaron modelos, pHash, particiones, entrenamiento, benchmarks ni builds; no se modificaron las propuestas. Resolver un hallazgo de diseño no demuestra que su implementación futura funcione ni supera gates experimentales.

Raíz de las rutas siguientes: `C:/Users/junio/Downloads/mango-vision/ALBUS26_major_revision/`. **S** designa `docs/superpowers/specs/2026-09-17-albus26-major-revision-design.md`; **P**, `docs/superpowers/plans/2026-09-17-albus26-major-revision.md`; **E**, `reports/first_phase_executive_report.md`.

## Snapshot revisado

| Documento | SHA256 |
|---|---|
| S | `0e471f11c9d70b1a2f12db1c9cdfe4823e0b4ec417eba95caf91b1e21596cc61` |
| P | `a4a44b0fc694590da78c2f257d27ecaaf2245ab428184fdb952f15f27d2b8508` |
| `docs/research/claim_evidence_matrix.csv` | `19943624048bc3f42caf529c8f5c6e52b9d24f52cad8610cdfa35f9f8c8a802f` |
| `docs/research/reviewer_matrix.md` | `da91ca3b30f6ec2c614c9e775b705c9a08648ca0b026bbd39840f9f66cad85db` |
| `provenance/derived_evidence_registry.csv` | `03bd5e9d6272857f50fbe1d834258d71321c254c68078e4edfc458bb65c40b71` |
| E | `1c36657c379776930026e1eb981ca1e13b648bc5d27ed5b18737bb3ad7fdaf61` |

## Resolución de los seis hallazgos iniciales

| Hallazgo | Estado documental | Evidencia actual |
|---|---|---|
| RIR-01, checkpoint y redondeo | RESUELTO EN DISEÑO | S §7 y P TASK-04 adoptan última época máxima, fitness sin redondear, callback después del guardado, vínculo época/hash y conservación antes/después de stripping. Las pruebas propuestas comprueban bytes y valores que colapsan al redondear. |
| RIR-02, escrituras del runtime | RESUELTO EN DISEÑO | S §4 y P:35–56/97 fijan configuración, caches y temporales antes de importar; requieren comprobación en proceso hijo de las rutas efectivas y rechazo previo si falta aislamiento. No se ha ejecutado esa comprobación. |
| RIR-03, versiones contradictorias | RESUELTO EN DISEÑO | S §7 y P TASK-01 coinciden en 8.4.52 reconstruida; conservan 8.4.39 como metadata histórica M1 y exigen enmienda ante incompatibilidad. REVIEW-09 reconoce la versión recuperada. |
| RIR-04, evidencia de conteos | RESUELTO DOCUMENTALMENTE | CLAIM-004/005/009 enlazan DER-001/002 y limitan soporte al snapshot local. Se comprobaron existencia y SHA256 de DER-001/002/003 contra su registro: coinciden. |
| RIR-05, cajas originales/clase propia | RESUELTO DOCUMENTALMENTE | CLAIM-031 pasa a PARTIALLY_SUPPORTED y distingue cajas derivadas de origen no verificado; REVIEW-11 describe DATA-006 como localización de una clase `mango`. |
| RIR-06, texto pegado | RESUELTO EN LO SUSTANTIVO | La relectura de TASK-02–10 ya permite distinguir precondiciones, acciones y límites. Quedan expresiones menores señaladas abajo, sin el patrón general anterior. |

La nueva congelación M2 tiene salida y comando explícitos (P:154/180/185). TASK-05 ahora separa validación, congelación del punto operativo y test (P:254/261–265), y exige rechazar predicciones de test como entrada a selección. Estos cambios mejoran el contrato; permanece el enlace de grupos M2 descrito a continuación.

## Hallazgos del snapshot inicial de esta relectura

Los estados de esta sección fueron comprobados nuevamente después de su corrección; el cierre vigente figura al final.

### RIRR-01 — MEDIUM — Los intervalos M2 reciben IDs de otra representación

P:143 genera `data/audits/model2/clusters.csv` auditando DATA-004 y reutilizando SRC-ID (P:133). P:185 congela DATA-005 para evaluar clasificación, pero P:268 entrega los clusters DATA-004 a los intervalos de predicciones DATA-005. Los archivos tienen identidades distintas aunque sus bytes coincidan: `An111.jpg` es SRC-003465 en DATA-004 y SRC-006467 en DATA-005, ambos con SHA256 `479bcffac126ce640c1a7c0336574ce84084283c0fc70c5d541d750a4abe6865` según `data/manifests/legacy_dataset_inventory.csv`.

**Impacto:** una unión por image_id puede fallar o perder registros; inferir grupos sólo desde hash tampoco conserva necesariamente la multiplicidad de copias. El freeze nuevo incluye grupos, pero el comando posterior no lo utiliza.

**Criterio de corrección:** transferir explícitamente la asignación DATA-004→DATA-005 durante freeze, preservando nombre, hash, clase y multiplicidad; usar `data/manifests/model2_frozen_manifest.csv` como entrada de grupos de intervalos. Exigir que cada predicción tenga exactamente una asignación y que ninguna quede descartada silenciosamente. Basta una prueba con dos SRC-ID distintos para la misma imagen y copias repetidas.

### RIRR-02 — MEDIUM — Referencias locales de entrega todavía incompletas

Se comprobaron los 39 enlaces locales de E mediante `Test-Path`; dos no existen en el snapshot:

- E:27 enlaza `../Mango-vision/src/data_prep/make_cls_layout.py`; el archivo comprobado está en `../Mango-vision/src/training/make_cls_layout.py` (SRC-009665).
- La entrega enlaza `docs/final_validation_report.md`, todavía ausente. Puede ser un documento en preparación, pero no debe presentarse como evidencia entregada antes de crearse y revisarse.

Además, S:9 cita `decision_log.md` aunque declara resolver rutas desde la raíz del workspace; el archivo existente está en `docs/research/decision_log.md`.

**Criterio de corrección:** corregir las dos rutas erróneas y producir/verificar el informe de validación documental antes de entregar su enlace, o indicar explícitamente que está pendiente. Repetir la comprobación de enlaces del ejecutivo después de los cambios; los archivos científicos futuros del plan no deben confundirse con entregables actuales faltantes.

### RIRR-03 — LOW — Dos expresiones aún describen mal el objeto o el intervalo

- E:15 dice «carpetas v4–v6». La genealogía y el inventario describen los ZIP v4/v5/v6; esas carpetas no son las fuentes comparadas. Sustituir por «paquetes ZIP v4–v6».
- P:250 escribe «rejilla .05..95». S:77 fija inequívocamente 0.05 a 0.95. Escribir ambos extremos completos evita que la instrucción operativa parezca terminar en 95.

## Verificaciones y límite del dictamen

Se leyeron las propuestas corregidas y las 17 respuestas del ejecutivo, contrastando sus afirmaciones principales con genealogía, registros EXP/ART, matriz CLAIM e inventario de datasets. Los 50 claims tienen enlaces SRC/DER que resuelven en los registros actuales. Las tres evidencias DER existen y sus hashes registrados coinciden. El ejecutivo mantiene `reproduced=NO`, separa aritmética de reproducción y deja explícitos los bloqueos de GT/hardware; no se encontró otra afirmación mayor sin sustento en esta relectura.

Los seis hallazgos originales están resueltos a nivel documental; no quedan hallazgos HIGH de aquella revisión. Ninguna conclusión de este informe autoriza ejecutar el plan, acredita independencia biológica de datos o declara terminada la revisión científica.

## Comprobación final de las correcciones de esta relectura

Se releyeron las líneas modificadas, sin aceptar la descripción del coordinador como prueba. Snapshot final:

| Documento | SHA256 final |
|---|---|
| S | `beeaec22060d5865839bf6da9e2bcc93d0a7c5af0676a5f9e92c00348d5d69ca` |
| P | `9cf27f53ca2b3b3ec0e7ba5b581cb9b0622b958865d964368897fb988a54af58` |
| E | `cde7f60648acec2735a139aa59dc3000174b502e3bf5c859f207ca2326ea57b1` |

- **RIRR-01: RESUELTO EN DISEÑO.** P:180 exige transferencia DATA-004→DATA-005 por nombre/hash/clase/split con multiplicidad y ambos SRC; P:268 usa el manifiesto M2 congelado, exige unión total y única y añade rechazo de SRC ajenos y prueba de copias con hash igual. No se ha implementado ni ejecutado esa prueba.
- **RIRR-02: rutas erróneas RESUELTAS; un entregable PENDIENTE.** El enlace a `src/training/make_cls_layout.py` ahora existe y S:9 apunta al registro real de decisiones. La nueva comprobación encontró 38 de 39 enlaces locales existentes. Sólo `docs/final_validation_report.md` sigue ausente y el coordinador informa que está en preparación. Su existencia, contenido y enlace deben verificarse al preparar la entrega final; no se presenta aquí como evidencia ya leída.
- **RIRR-03: RESUELTO DOCUMENTALMENTE.** E:15 identifica paquetes ZIP y P:250 usa 0.05..0.95, consistente con S:77.

**Conclusión vigente:** no se identifican hallazgos HIGH o MEDIUM de diseño pendientes en SPEC/plan después de estas correcciones. Queda la precondición de entrega del informe de validación documental enlazado. La resolución es exclusivamente documental; aprobación humana y gates científicos/experimentales siguen pendientes.
