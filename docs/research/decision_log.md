# Registro de decisiones inicial

Fecha de registro: 2026-09-17, zona America/Bogota. Historial de investigación/documentación. Las entradas iniciales se conservan; decisiones posteriores pueden supersederlas explícitamente. La autorización condicional del 18-09-2026 no equivale a gate satisfecho antes de revisión fresca y freeze.

|DECISION-ID|timestamp|question|available_evidence|decision|alternatives|rationale|risk_if_wrong|affected_artifacts|
|---|---|---|---|---|---|---|---|---|
|DECISION-001|2026-09-17|Dónde escribir sin alterar fuentes|Preflight: contenedor sin Git; dos repos internos, uno dirty|Escribir solo ALBUS26_major_revision; no inicializar Git ni crear worktree|Crear worktree tras autorización|La tarea documental no modifica repos internos; un worktree no incluiría los documentos externos ni untracked|Confundir aislamiento documental con aislamiento Git|repository_initial_state;README|
|DECISION-002|2026-09-17|Cuál PDF fue sometido|Confirmación explícita del usuario en esta conversación; hash SRC del PDF raíz|Articulo_Mango_ALBUS.pdf es el sometido, HIGH por testimonio+identidad binaria|Inferir por v9 o paginación|El usuario confirma directamente; diferencias de páginas del dictamen se registran|No hay comprobante CMT binario local|genealogy;SPEC|
|DECISION-003|2026-09-17|Fuente editable|Comparación texto PDF/DOCX y siete imágenes; genealogía|Proponer DOCX ALBUS como canónico; copiar solo tras gate|Recrear desde LaTeX v9; reescribir desde cero|Correspondencia de contenido superior y plantilla oficial Word|Recrear altera contenido/maquetación accidentalmente|SPEC;TASK-09|
|DECISION-004|2026-09-17|Cómo tratar métricas recuperadas|CSV, matrices, pesos y logs existentes|OBSERVED/PARTIALLY_SUPPORTED, nunca REPRODUCED por leerlos|Declarar reproducible por tener checkpoint|Falta ejecución fresca y vínculo inmutable de entradas|Dar confianza excesiva a números históricos|experiment_registry;claim matrix|
|DECISION-005|2026-09-17|Qué significa ausencia de SHA duplicado|DATA-001 tiene 669 hashes únicos y 432 nombres sakit_mp4|No inferir independencia; auditar secuencia/pHash tras aprobación|Declarar split limpio|Hash identifica bytes; no identidad de fruto/escena|Fuga no detectada|REVIEW-01/02;SPEC|
|DECISION-006|2026-09-17|Umbral perceptual y agrupamiento futuro|Legacy usa pHash64 Hamming<5; secuencias sin mapa verificable|Proponer candidatos <5, bandas exploratorias 5..10 sin consultar métricas; conservar relaciones separadas; grupo conservador de video si no hay metadata|Asumir todos frames independientes; optimizar umbral por test|Se fija criterio antes de entrenar y explicita costo de agrupar ambiguos|Sobreagrupación puede dejar pocos grupos; subagrupación preserva fuga|TASK-02/03;methodology_decisions|
|DECISION-007|2026-09-17|Modelo/checkpoint para comparación val/test|best.pt metadata coincide métricas época137; pico mAP50 época95|Reportar validación del checkpoint elegido; máximos históricos separados; revisar R máximo omitido época1|Elegir máximo de cada métrica como un solo modelo|Evita selección retrospectiva y comparaciones incompatibles|Confundir selección por fitness con máximo mAP50|TASK-04/05;claim matrix|
|DECISION-008|2026-09-17|Incertidumbre futura|13 instancias Enfermo; correlación por imagen/secuencia; repetidos M2|CI95%; Wilson sólo con Bernoulli independiente justificado; bootstrap por unidad de independencia máxima conocida|Bootstrap por bbox; Wilson automático de13 cajas|Dependencia reduce n efectivo; intervalo no corrige sesgo de muestreo|CI demasiado estrecho; remuestras sin clase|TASK-05;SPEC|
|DECISION-009|2026-09-17|Ground truth cascada|Detector binario; classifier por imagen; propio etiqueta mango y polígonos|BLOCKED_BY_GROUND_TRUTH para métricas de enfermedad conjunta; entregar protocolo/evaluador futuro|Usar M2 como verdad; multiplicar recalls marginales|Ambos métodos fabricarían evidencia|El revisor puede requerir colección nueva|TASK-07;response draft|
|DECISION-010|2026-09-17|Latencia Raspberry Pi|PDF afirma <5 y >5; logs raw/hardware no identificados|Medir sólo con equipo real o retirar claim como resultado|Simular ARM; trasladar CPUWindows|No existe evidencia para concluir cumplimiento edge|La revisión pierde resultado de despliegue, correctamente|REVIEW-08;TASK-06|
|DECISION-011|2026-09-17|APA7 vs normas ALBUS|Plantilla oficial Full Papers SHA6c6418b6… exige APA; dictamen pide APA7|Compatibles en estilo general; verificar detalle durante edición, sin conversión destructiva|Mantener IEEE; convertir sin consultar plantilla|Respeta fuente primaria y dictamen|Ambigüedades particulares se registran antes de resolver|TASK-08/09;external_sources|
|DECISION-012|2026-09-17|API descrita vs código|api/inference→core/vision→YOLO; CLI→core/cascade→M1/M2|Corregir descripción a dos rutas separadas después de gate; no ampliar app para justificar paper|Integrar API nueva|Código nuevo no prueba que integración existía en experimento histórico|Descripción editorial inexacta si hay versión externa faltante|CLAIM-039;TASK-09|
|DECISION-013|2026-09-17|Fallos durante investigación|Agentes interrumpidos por límite de uso; parser bbox señaló polígonos|Retomar archivos guardados; revisar formato antes de llamar corrupta la etiqueta|Repetir arqueología; descartar anotaciones|Limitación de parser no es defecto de datos; no hubo experimento nuevo|Inventario subcuenta objetos|dataset report;verification|
|DECISION-014|2026-09-17|Aprobación de SPEC y plan|Solicitud explícita §§0,41,42|Preparar ambos y sus revisiones antes de pedir aprobación conjunta|Pausas adicionales genéricas de skills|Instrucción específica del usuario prevalece|Confundir continuar investigación con aprobar experimentos|README;SPEC;plan|

Histórico del 17-09-2026: «Continua» reanudó la primera fase y entonces no sustituía aprobación de SPEC+plan. La autorización posterior se registra abajo; no borrar este contexto.


## Decisiones tras revisión independiente

|ID|Fecha|Pregunta y evidencia|Decisión propuesta|Alternativa y riesgo|Artefactos|
|---|---|---|---|---|---|
|DECISION-015|2026-09-17|RIR-01: guardado nativo sobrescribe best en empate y CSV pierde precisión|Usar último máximo nativo con fitness sin redondear y hashes antes/después de stripping|Primera época requeriría retención distinta; se evita declarar pesos inexistentes|SPEC §7; TASK-04|
|DECISION-016|2026-09-17|RIR-02/03: versión inconsistente y cachés globales|Un entorno reconstruido 8.4.52, preservando metadata histórica 8.4.39; redirección antes de instalar/importar y prueba en hijo|Dos entornos añadirían coste sin recuperar las dependencias M1 desconocidas; compatibilidad nueva aún no probada|SPEC §4/7; TASK-01|
|DECISION-017|2026-09-17|RIR-04/05: YAML no prueba conteos ni cajas originales|Registrar DER-001/002/003, enlazar conteos locales y moderar CLAIM-031|No elevar observación de layout derivado a procedencia original|claim matrix; derived_evidence_registry|

## Enmiendas vinculantes del usuario — 2026-09-18

La solicitud adjunta «Texto pegado.txt» aprueba conceptualmente SPEC y plan, condicionando TASK-01 a incorporar y verificar siete enmiendas mediante diff exacto, self-reviews y revisión independiente fresca sin HIGH/MEDIUM abiertos. **Estado al editar este registro: PENDING_FRESH_REVIEW; GATE B/C no declarados satisfechos.** El coordinador añadirá una entrada nueva con reporte/hash del delta, hallazgos cerrados, commits, freeze y timestamp cuando se cumplan las condiciones; no reinterpretar esta tabla como aprobación efectiva ni inicio de TASK-01.

|ID|Fecha|Enmienda / decisión vinculante|Alternativa descartada y motivo|REVIEW ↔ TASK / evidencia esperada|
|---|---|---|---|---|
|DECISION-018|2026-09-18|AMENDMENT-01 supersede DECISION-001 y prohibiciones operativas antiguas: Git nuevo exclusivo, baseline exacto `3990fa7c79b77224675449b9bb676e650c47bbaf`, commit administrativo `c0463636d2288ba3370d34914c27e47b11a5e30f`, rama/worktree de ejecución y commits locales pequeños autorizados. Legacy archivos y .git intactos, sin push/merge externo/publicación, grandes por manifests/hashes sin LFS innecesario|Usar Git legacy o incluir corpus gigante violaría aislamiento. Tool app no selecciona repo anidado desde cwd sin Git: fallback git worktree documentado dentro de raíz autorizada|REVIEW-09 y todos (procedencia) ↔ preflight, TASK-01/10; `reports/amendments/pre_execution_integrity.json`, ledger y verificación final con GIT_OPTIONAL_LOCKS=0|
|DECISION-019|2026-09-18|AMENDMENT-02: freeze inmutable anterior a TASK-01/nuevas observaciones, commit+SHA de SPEC/plan y reglas completas; `test_observed_before_freeze=true` por evidencia histórica ya leída. Enmiendas posteriores append-only con test observado, impacto y reviewer; bugs de efecto científico también se registran|No llamar preregistro prospectivo a arqueología retrospectiva; no reescribir silenciosamente protocolo ni usar TDD para eludir gate científico|REVIEW-01/02/03/05/07/09 ↔ preflight, TASK-01/10; `provenance/protocol_freeze.{md,json}`, test_access_log y PROTOCOL-AMENDMENT-XXX|
|DECISION-020|2026-09-18|AMENDMENT-03: dos pasadas A/B independientes para candidatos relevantes con juicio visual; IDs opacos y sin resultados/métricas/consecuencias/primera revisión, ocultar split/rutas/clases cuando posible; grande≥10, decisiones originales y desacuerdo separado, registro por par o cluster con cobertura|Mayoría de agentes no es ground truth biológico; procedencia documental prevalece. No N² visual redundante de un video conocido|REVIEW-01/02 ↔ TASK-02/03/10; paquetes ciegos, adjudications, resolution y blinding log|
|DECISION-021|2026-09-18|AMENDMENT-04: principal M2 image-weighted; exact-SHA-dedup menor image_id con GT consistente y cluster-weighted peso1/tamaño; confusión ponderada y cinco clases fijas, deltas respecto principal, bootstrap group_id máximo disponible y draws pareados, CI bloqueado por insuficiencia conforme SPEC|No reentrenar automáticamente por duplicados intra-split ni elegir estimando por resultados. Counts de clusters no demuestran independencia biológica|REVIEW-02/04/05/09 ↔ TASK-02/05/09/10; duplicate_structure, model2_sensitivity, confusiones/draws/reporte|
|DECISION-022|2026-09-18|AMENDMENT-05: entorno con identidad Python/pip/índices/config/report/check/JSON/wheel-build/hashes, OS/CPU/RAM/GPU/driver/CUDA y whitelist env sin secretos; sidecar SRC-ID+logical_root+logical_path separado de local_absolute_path. Root mapping legacy_corpus/external_mail/revision; preservar manifests originales|Pins no aseguran mismos bytes; padre del worktree no es legacy. Redactar userinfo/tokens/queries sensibles conservando host. Hash no disponible se informa, no se inventa|REVIEW-09/17 ↔ TASK-01/10; environment, root_mapping/source_locations, portability_check|
|DECISION-023|2026-09-18|AMENDMENT-06: auditar DETECCIÓN TEMPRANA y EFICIENTE en título/resumen/contribuciones/conclusión; neutralizar eficiente por defecto porque el benchmark previsto es descriptivo y no fija criterio operacional comparativo previo|No añadir benchmark retrospectivo para salvar un adjetivo. Mantener eficiente sólo con definición previa y criterio verificable o comparador adecuado|REVIEW-07/08/10/14 ↔ TASK-06/09/10; editorial_claim_audit y claim-evidence|
|DECISION-024|2026-09-18|AMENDMENT-07: conclusiones de contaminación detectada limitadas a forma/algoritmo/parámetros/origen/secuencia/límites/relaciones no excluidas; normalizar todos los claims propios activos|No dataset libre de fuga, independencia universal ni clean sin duplicados. Citas históricas atribuibles permanecen sin adoptarse como conclusiones|REVIEW-01/02/04/14 ↔ TASK-02/03/09/10; audit_report, editorial_claim_audit, response|
|DECISION-025|2026-09-18|Supersede DECISION-014 en aprobación: cumplida revisión fresca sin HIGH/MEDIUM y freeze, registrar B/C=SATISFIED y ejecutar TASK-01→10 con implementador fresco, revisión de SPEC/calidad por tarea, TDD, debugging y verificación fresca; no nueva aprobación ordinaria. Detención global sólo por las cinco condiciones del usuario, reproducidas en SPEC §11|Bloqueos conocidos Pi/GT/M1 histórico exacto no detienen ramas independientes ni autorizan afirmar D/E satisfechos. Sin revisión fresca no hay aprobación efectiva|Todos REVIEW ↔ preflight/TASK-01..10; self-reviews, reporte independiente, registro posterior de cumplimiento, freeze y ledger|

La edición de enmiendas es documental: no ejecuta auditorías nuevas, inferencias, entrenamiento ni TASK-01. El reporte de integridad fresco lo produce/verifica el coordinador; este registro no reemplaza su evidencia ni la futura revisión independiente.

## DECISION-026 — Cumplimiento de la aprobación condicional

Registro: 2026-09-19T21:22:02.083075+00:00. La integración y revisión exigidas por el usuario están satisfechas. El revisor fresco `/root/amendment_delta_review` emitió PASS de cumplimiento y calidad; ADR-LOW-01 fue corregido y vuelto a revisar; HIGH=0, MEDIUM=0, LOW=0 abiertos. Reportes originales y de cierre: `reports/amendments/independent_delta_review.md` y `independent_delta_rereview.md`. Delta exacto final contra baseline: `reports/amendments/delta-3990fa7-2e9b009.diff`, SHA256 `2cda88c86b1a9e03293d7ae1a56d15423b106fa5d449ccb216c89ec7a720400c`. SPEC y plan coinciden con sus commits y los 141 archivos del baseline con la primera fase; cobertura REVIEW18/TASK10/AMENDMENT7 verificada. Fuentes11137 sin diferencias y estado Git legacy igual al inicial, con exclusiones documentadas. Evidencia estructurada: `reports/amendments/conditional_approval_fulfilled.json`.

Se registra la aprobación ya concedida por el usuario, sin solicitar otra autorización. La ejecución aún espera la creación y verificación del snapshot inmutable; después del freeze B/C=SATISFIED y comienza TASK-01. No se ha creado entorno ni producido nueva observación experimental. Las anotaciones PENDING de SPEC/plan son el estado histórico del candidato revisado; el estado efectivo se registra aquí y en el freeze/ledger, sin reescribir esos documentos congelados.

## DECISION-027 — Freeze verificado; GATE B/C satisfechos

2026-09-20T03:52:41.583330+00:00: snapshot `ALBUS26-116-PROTOCOL-001` creado antes de TASK-01, commit `7d0f9985cce73740cfa2ae26154971b55282ad52`, JSON SHA256 `6d5aa3ff47cba97f8ecd0dd15683bb96f0d53146f3af1ce1e95bf24cec7cbc8b`. `reports/amendments/freeze_verification.json` registra verificación de reglas, documentos completos, commits y hashes, creación exclusiva y ausencia de nuevas observaciones. Comprobación fresca posterior al commit: sidecars y documentos siguen idénticos y checkout limpio. GATE B=SATISFIED; GATE C=SATISFIED. Se habilita ejecución secuencial TASK-01→10 bajo las condiciones aprobadas, sin alterar snapshots.

## DECISION-028 — Autorización de Kaggle y enmienda 008 v2

Registro: 2026-09-22T14:26:04.338678+00:00. El usuario autorizó el 2026-09-21 usar el MCP de Kaggle para el entrenamiento y el análisis pesado, lo que satisface la regla de detención global 1 por acción externa. El cambio de sede es material, así que se tramita como PROTOCOL-AMENDMENT-008 y no como una decisión operativa.

La versión 1 fue rechazada por revisión independiente con 6 HIGH y 3 MEDIUM. Dos hallazgos factuales se verificaron y eran errores propios: ART-005 ya identificaba el args.yaml histórico, y la fila de hardware de EXP-001 marca el 2xT4 como afirmado por el PDF y no verificado, no como observado. Al verificarlos se encontró evidencia nueva que refuerza la enmienda: el campo dataset de EXP-001 apunta a /kaggle/input/datasets/jairoall/mangodataset/data.yaml, de modo que el entrenamiento histórico ya se ejecutó en Kaggle. Kaggle es la sede original, no una sede nueva, y eso procede de la configuración guardada del run.

La versión 2 cierra los nueve hallazgos y queda en PROPOSED_V2, pendiente de revisión independiente fresca. Hasta entonces no se ejecuta nada en Kaggle ni se sube ningún dato. Evidencia: provenance/protocol_amendments/PROTOCOL-AMENDMENT-008-kaggle-compute.{md,json} y reports/amendments/amendment-008-review-response.md.

## DECISION-029 — Corrección: la sede histórica NO está verificada

Registro: 2026-09-22T14:50:10.096572+00:00. Esta decisión **corrige a DECISION-028**, que afirmaba que el entrenamiento histórico «ya se ejecutó en Kaggle» y lo trataba como observado. La revisión independiente de la versión 2 de PROTOCOL-AMENDMENT-008 lo marcó como N-01 HIGH y tiene razón.

Lo verificable es que hay rutas con forma de Kaggle embebidas en la configuración guardada: el campo dataset de EXP-001, los train_args del checkpoint decodificado estáticamente y la cadena /kaggle/working/runs/detect/train-2. Eso es procedencia de CONFIGURACIÓN, no de EJECUCIÓN autenticada. El propio repositorio registra como ausentes el notebook original, el manifiesto histórico, la invocación, el entorno y el log de hardware, y la arqueología de experimentos ya advertía que una ruta almacenada en código no prueba que esos bytes se usaran en una ejecución histórica.

Clasificación vigente: rutas con forma de Kaggle CIRCUNSTANCIALES; sede de ejecución histórica UNVERIFIED. Promoverla exigiría identificador autenticado de kernel o notebook, versión de dataset adjunta o log de plataforma.

Es el error simétrico del que la versión 1 cometió con el 2xT4: allí se dio por observado lo que el PDF sólo afirmaba; aquí se dio por observada una sede que la configuración sólo sugiere. La enmienda se sostiene sin ese argumento: lo que la sostiene es la ausencia medida de GPU local, el presupuesto medido en Kaggle y la autorización del usuario. La sede histórica deja de usarse como justificación.

La enmienda pasa a PROPOSED_V3. Sigue sin autorizar ninguna ejecución ni subida.

## DECISION-030 — Entrenar M1 en CPU local es viable; corrige una afirmación no medida

Registro: 2026-09-22T17:54:30.109838+00:00. PROTOCOL-AMENDMENT-008 v1 afirmaba que entrenar YOLO 150 épocas en la CPU local «no es una alternativa científica viable en tiempo razonable». Esa afirmación nunca se midió. Medida ahora con una sonda no científica (reports/execution/cpu_capacity_probe.json), sólo con imágenes de train y valid, modelo descartado: 336 s por época de mediana y 355 s de máximo, validación incluida, en el AMD Ryzen 5 7520U. 150 épocas: 14,8 h de cota superior y unas 20 h con el factor de seguridad 1,35. Con el split real, de unas 443 imágenes de entrenamiento, algo menos.

Es viable dentro del plazo del 30 de septiembre. El plan congelado ya dice en TASK-04 «Proponer CPU si es el único dispositivo disponible», así que entrenar en CPU no requiere ninguna enmienda. Kaggle sigue siendo más rápido, pero su ruta tiene bloqueos abiertos: revisión independiente de la enmienda, scopes de API con datasets.get denegado, y el prerrequisito de licencia antes de cualquier subida. La elección de sede corresponde al usuario.

Anomalía declarada de la sonda: registró cuatro tiempos para tres épocas; la callback de fin de época se disparó una vez más. Las estimaciones usan el máximo, así que quedan del lado conservador.

## DECISION-031 — Agrupamiento B del montaje y sede Kaggle, decididos por el usuario

Registro: 2026-09-22T19:24:12.850540+00:00. Ante la regla de detención global 4/5 de la SPEC §11, se presentaron al usuario dos decisiones con sus consecuencias por escrito. Primera: agrupar el montaje sakit_mp4 como un solo grupo (opción A, regla congelada) o por identidad visual (opción B, enmienda). Segunda: entrenar M1 en CPU local, medida en unas 15 h, o en Kaggle.

El usuario eligió **B** y **Kaggle**. B se tramita como PROTOCOL-AMENDMENT-009, que declara que el coordinador conocía el tamaño de test de A antes de proponer B. Kaggle sigue sujeta a PROTOCOL-AMENDMENT-008, todavía no aprobada, y a sus prerrequisitos abiertos: revisión independiente, scopes de escritura del conector, origen por imagen de DATA-001 antes de subir y custodio para la fase de test. La vía de CPU local queda medida y autorizada por el plan congelado como alternativa si esos prerrequisitos no se cierran a tiempo para el plazo del 30 de septiembre; activarla también es decisión del usuario.

## DECISION-032 — Partición primaria A; enmienda 009 retirada

Registro: 2026-09-23T03:30:18.329646+00:00. Esta decisión **sustituye la elección de B de DECISION-031**. El 2026-09-22 el usuario pidió revisar la revisión adversarial de Codex de la enmienda 009 y continuar de forma autónoma. La revisión (5 HIGH, 4 MEDIUM) se verificó punto por punto y se acepta.

La SPEC §5 congelada resuelve el caso sin enmienda: el montaje sin fuente verificable se agrupa entero y, si eso deja un test poco informativo, se declara la insuficiencia en vez de partir el grupo. B como análisis primario queda descartada. La SPEC §11 (regla 5) exige consultar al usuario ante una enmienda que cambie la interpretación primaria; volver a la regla congelada no es una enmienda.

Estado: PROTOCOL-AMENDMENT-009 WITHDRAWN. Comprobación residual SUPERSEDED y no aplicada. Respuestas conservadas fuera del repositorio con estos SHA256: revisor A (107/107) `885c433c6159ef9b8f998c443e55995e78dbb954d889952356d23d2da22b79a5`, revisor B (83/107) `31bc7461fb70e2907e137a2e28a95421042364e5b840fc66a3e06889f44f5224`. El coordinador conoció el recuento agregado de A (controles 4/4, 69 de 103 consultas marcadas), no las decisiones de B. Ninguno de esos datos afecta a A.

Consecuencia declarada: en A todo Enfermo de entrenamiento procede de un solo grupo (el montaje) y el test tiene pocos grupos con Enfermo. El test mide generalización desde el montaje hacia otras fuentes; su incertidumbre se informa por grupo, sin fabricar independencia.

## DECISION-033 — Kaggle como sede única; datos desde el commit público

Registro: 2026-09-23T03:30:18.329646+00:00. El usuario ordenó el 2026-09-22 que todo entrenamiento y procesamiento se haga en Kaggle. La alternativa de CPU local de DECISION-030 deja de ser el plan de respaldo. El cambio de sede sigue necesitando PROTOCOL-AMENDMENT-008 aprobada.

Capacidad observada hoy por el MCP: cuota semanal de GPU de 108.000 s, 0 usados, renovación 2026-09-26; `datasets.get` sobre el dataset privado del usuario ya responde. El MCP no expone creación de datasets.

Ruta de datos sin subir nada: el corpus DATA-001 está versionado en el repositorio público `DANN-MAGE/SemilleroTI-Mangos`, commit `98614804dd967e19a77af9fc58c27364d2e43bc9`. Verificado contra el manifiesto: 669/669 imágenes idénticas byte a byte. De las 669 etiquetas, 465 son idénticas y 204 difieren sólo por la conversión LF→CRLF de `core.autocrlf=true` en la copia local; ninguna difiere en contenido. El checkpoint base `yolo26n.pt` tiene en la release oficial `ultralytics/assets` v8.4.0 el digest `sha256:9b09cc8bf347f0fc8a5f7657480587f25db09b34bf33b0652110fb03a8ad4fef` y 5.544.453 bytes. El mismo mecanismo reproduce el hash registrado de ART-004 (`c62d41bf…bd7`). Kaggle descarga ambos y verifica cada byte contra estos hashes antes de entrenar.

## DECISION-034 — Adjudicación suplementaria de los 47 candidatos pendientes

Registro: 2026-09-23T03:30:18.329646+00:00. El repositorio ya contiene 47 pares en estado `PENDING_ADJUDICATION`: 7 de pHash invariante a rotación y 40 del ranking de embedding ART-004, con horizonte fijado antes de ver resultados. Con la partición A, 27 de ellos cruzan splits. La SPEC §5 dice que un caso visual sin dos pasadas bloquea el agrupamiento que depende de él, así que la partición A no se congela hasta adjudicarlos.

Se adjudican los 47, crucen o no, para que el split no dirija la revisión. El contrato es el de §5: dos revisores ciegos de familias distintas y tercera adjudicación separada en caso de desacuerdo. Se añaden 6 controles de consistencia contra decisiones ya adjudicadas (3 relacionados, 3 no relacionados, uno de ellos un par similar en pHash). Miden acuerdo con el registro previo, no verdad biológica. Los pares bajo los horizontes quedan como riesgo residual declarado; el par conocido de mismo fruto en fotos distintas ocupaba el puesto 765 del ranking global, así que el horizonte de 40 no tiene recall demostrado para esa relación. Script: `provenance/commands/task02/supplementary_candidates.py`; clave: `data/audits/model1/supplementary_key.json`.

## DECISION-035 — Partición A congelada y sonda de capacidad

Registro: 2026-09-23T19:30:00+00:00. La adjudicación suplementaria terminó conforme a la SPEC §5: dos pasadas ciegas y tercera adjudicación separada de los 38 desacuerdos, sin pendientes. De los 47 pares, 37 quedan relacionados y 10 no. Los controles de consistencia salieron 6/6 para ambos revisores.

Con esas relaciones, el algoritmo único de la SPEC §6 y el montaje como un solo grupo, la partición A queda así: entrenamiento 439 imágenes en 8 grupos; validación 113 en 93; prueba 117 en 98, con 15 grupos que llevan Enfermo (26 instancias). La regla de bloqueo no se activa. Manifiesto `dd9431dd…`, registro de congelación en `data/manifests/model1_clean_manifest.freeze.json`, pendiente de revisión independiente.

Sonda de capacidad `KAGGLE-CAPACITY-001` (no científica): el intento 1 abortó en la descarga porque transcribí a mano mal la cadena de split del kernel. `select()` lo detectó antes de construir ningún modelo, y el hash del código ejecutado difiere del renderizado, que es lo que debía ocurrir. Se conservan recibo y registro del intento en `attempt1/`. La cadena viaja ahora codificada por rachas. El intento 2 se lanzó con la misma regla de proyección, fijada en el código antes de medir.


## DECISION-036 — Entorno local de inferencia y paquete pi_heif

Registro: 2026-09-28. Al fijar el entorno local de inferencia se halló que el `.venv` difiere de `provenance/environment/reconstructed_freeze.txt`. Contiene además `pi_heif==1.4.0`, instalado el 2026-09-25 a las 17:33 con `uv`, y no hay ninguna orden de esta revisión que lo instalara. Ultralytics 8.4.52 lo instala por sí mismo: `ultralytics/utils/patches.py` sustituye `PIL.Image.open` y, cuando una apertura falla, llama a `check_requirements("pi-heif")` para leer HEIC/HEIF. Sólo interviene en imágenes que PIL no abre. Las 669 imágenes de M1 y las 1.500 de M2 son JPG, así que no cambia ningún píxel ni ningún resultado.

Se declara como desviación del entorno reconstruido y no se desinstala, para no cambiar el entorno a mitad de la revisión. El entorno real queda fijado en `provenance/environment/inference_environment.txt` (43 distribuciones, generado por `authority.environment_lines`). Ese archivo es una autoridad de la instantánea de inferencia, M1 y M2. `approved_inference` exige que el intérprete sea el `.venv` de esta copia y que sus paquetes coincidan con el registro. EXP-R03 guarda su SHA256 en `run_record.json`. Responde a la sonda de la revisión de TASK-05 de la ronda 7, que instaló un Ultralytics sustituto en otro entorno.


## DECISION-037 — Aprobación de la inferencia por el investigador principal

Registro: 2026-09-28. La puerta de inferencia de TASK-05 (enmienda 008 §5.1) pasó por doce rondas de revisión independiente. Las rondas 6 a 12 cerraron HIGH-04, NEW-HIGH-01, NEW-HIGH-03, NEW-HIGH-06, NEW-HIGH-07, NEW-LOW-01 y NEW-LOW-02, y todas las rutas concretas de NEW-HIGH-05 que encontraron: cargador de arranque, código sin versionar o con mayúsculas en la extensión, repositorio incrustado, marcas del índice de git, cachés del `.venv` y `RECORD` reescritos. Cada ronda halló después una ruta más estrecha de manipulación local del `.venv` o del checkout en esta máquina, y ninguna mostró un efecto en el entorno aprobado.

La ronda 12 (`reports/execution/task-05-independent-review-round12.md`) dejó abierta una sola ruta: un `python._pth` colocado en `.venv\Scripts` que añade un directorio externo. Se rechaza desde el commit `42270fa` (registro del intérprete base y lista de `sys.path` permitida), pero ninguna ronda independiente lo revisó: la ronda 13 se detuvo por decisión del investigador.

Decisión: el investigador principal aprueba la inferencia para la instantánea exacta de §5.1 y ordena ejecutar la secuencia congelada (EXP-V01, congelación del umbral, EXP-R02, EXP-R03, intervalos y sensibilidad M2) para no comprometer el plazo editorial. La aprobación queda en `inference_approval` del JSON de la enmienda, con este riesgo residual declarado: la corrección de la ronda 12 no tiene revisión independiente, y otras manipulaciones locales de esta máquina quedan como limitación declarada, no como efecto observado. Todas las comprobaciones de `authority.py` siguen activas en cada orden; un cambio posterior en cualquier autoridad de la instantánea vuelve a bloquear la inferencia.


## DECISION-038 — Adjuntar la salida de EXP-R01 desde el editor web de Kaggle

Registro: 2026-09-28. EXP-V01 v1 (`experiments/model1/EXP-V01/v1`) falló en la etapa `start`: `/kaggle/input` estaba vacío y el trabajo rechazó antes de instalar, descargar o construir el modelo. La reconciliación lo clasifica como reintentable ("failed before any model output").

Causa: `save_notebook` del MCP de Kaggle no monta fuentes de datos. Se comprobó con un kernel privado no científico, `jorgesolanodev/albus26-attach-probe` (versiones 1 a 3, CPU, sin internet), que solo lista `/kaggle/input` y calcula el hash de un `selected.pt` si aparece. Se probaron `kernelDataSources`, `kernelDataSourcesSetter`, y también un dataset público (`uciml/iris`) por `datasetDataSources` y `datasetDataSourcesSetter`. En todas las variantes `/kaggle/input` quedó vacío. El probe no leyó datos del corpus ni el checkpoint. En esta máquina no hay CLI de Kaggle ni credenciales, y no se crean.

Decisión: el investigador principal adjunta la salida del kernel `albus26-m1-exp-r01` desde el editor web de Kaggle, como única entrada, y lanza "Save & Run All" sin editar el código ni la configuración. Así la versión 2 del kernel corresponde al intento v2 (`8c479cc`), cuya fuente es idéntica byte a byte a la de v1 (`e70e79e0…`). La vía manual no afecta la integridad: el trabajo exige una sola entrada con un solo `selected.pt` cuyo SHA256 coincida con el sellado, y la verificación local compara el hash de la fuente ejecutada, el payload y los archivos descargados. EXP-R02 necesitará la misma entrada; su procedimiento se registrará antes de renderizarlo.


## DECISION-039 — Fuente ejecutada desde el editor web de Kaggle

Registro: 2026-09-28. Al preparar EXP-V01 v2 según DECISION-038 se comprobó en el kernel no científico `jorgesolanodev/albus26-attach-probe` que el editor web de Kaggle, en modo Script, guarda cada versión con una línea `# %% [code]` antes del texto. Los hashes se calcularon localmente antes de cada ejecución:

- Versión 5, enviada por el MCP: se ejecuta el texto tal cual (`2a25832e…`), pero sin entrada montada.
- Versión 6, guardada desde el editor: se ejecuta `# %% [code]` más el mismo texto (`722a7410…`), con la salida de EXP-R01 montada en `/kaggle/input/notebooks/jorgesolanodev/albus26-m1-exp-r01/run/weights/selected.pt`. Su SHA256, `0648da3f…`, es el checkpoint sellado.
- Versión 7: se cargó un archivo local con File > Import Notebook y se guardó desde el editor. Se ejecuta exactamente `# %% [code]` más ese archivo (`38a9b499…`).

El MCP no puede montar entradas (DECISION-038) ni fijar un borrador sin crear una versión, porque el tipo `InterActive` devuelve error. Por eso ninguna vía ejecuta a la vez el texto renderizado y la entrada, y la comparación sellada de la fuente ejecutada rechazaría toda versión guardada desde el editor.

Decisión: `evaluate.executed_source` acepta como fuente ejecutada exactamente dos textos, el kernel renderizado o el mismo kernel precedido de la única línea `# %% [code]`, y rechaza cualquier otro. `verify_kaggle_run.reconcile` y `evaluate.rebuild_predictions` lo usan en lugar de la igualdad directa. `kaggle_job.py` no cambia, de modo que el render de EXP-V01 v2 (`8c479cc`) sigue siendo la renderización aprobada de su payload. Las pruebas cubren ambas formas aceptadas y las rechazadas (otra marca, marca doble, otro texto, recibo sin hash). La suite completa pasa: 395 pruebas.

Procedimiento para EXP-V01 v2 y EXP-R02: en el editor del kernel, File > Import Notebook con el `kernel.py` renderizado del intento; Add Input con la salida de `albus26-m1-exp-r01` como única entrada; Save Version > Save & Run All. Así el borrador queda fijado por construcción y no depende de lo que el editor tuviera antes.

Consecuencia: cambian `src/evaluation/evaluate.py` y `provenance/commands/task04/verify_kaggle_run.py`, que están en la instantánea m1 de la enmienda 008 §5.1. La inferencia M1 queda bloqueada hasta que el investigador principal apruebe la nueva instantánea. La instantánea m2 no cambia.

Aprobación: el investigador principal aprobó la inferencia para la nueva instantánea m1 en el chat de la sesión el 2026-09-28 y autorizó regenerar el JSON de la enmienda (`inference_approval` versión 10). Queda como riesgo residual que este cambio no tuvo revisión independiente.
