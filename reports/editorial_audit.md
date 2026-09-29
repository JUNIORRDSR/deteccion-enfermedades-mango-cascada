# Auditoría editorial del manuscrito (TASK-09)

**Fecha:** 2026-09-28 · **Manuscrito:** `manuscript/source/Articulo_Mango_ALBUS_revision.docx` tras la pasada 2f (SHA-256 `d177dd9d2d944b021f3977ecf37271e235f7fcdfd2af8a48d2ce0f0af0397b1b`) · **Responde a:** la auditoría B, ronda 1 (`reports/execution/task-09-results-audit.md`, hallazgos B-08 y B-09) y ronda 2 (`reports/execution/task-09-results-audit-round2.md`, hallazgos R2-04 y R2-05), y a la revisión adversarial final (`reports/final_adversarial_review.md`).

## 1. Trazabilidad de las cifras

El registro `manuscript/numbers.json` contiene 165 cifras y se genera con `provenance/commands/task09/make_numbers.py`. `src.evaluation.document_checks` vuelve a calcular cada una desde su artefacto y exige que aparezca, con coma decimal y el redondeo indicado, en el único párrafo que contiene su ancla. El resultado está en `reports/manuscript_consistency.json`: 165 cifras comprobadas, sin incidencias.

Párrafos cubiertos: el resumen; el primero de 3.3.1, con los recuentos de la adjudicación de `data/audits/model1/blinding_log.json`; 4.1.1, con las métricas de validación del evaluador del artículo; 4.1.2 y el párrafo que lo lee; 4.1.3; 4.1.5; 4.2.3, con el análisis de sensibilidad y el párrafo de los errores del Modelo 2; 5.1; 6.1; la conclusión; y las leyendas de las Tablas 4, 5 y 7 y de las Figuras 4 y 5. En cada uno se registra cada valor de resultado impreso, con los dos extremos de cada intervalo, más los recuentos de imágenes, grupos e instancias y los parámetros del bootstrap (2000 remuestras, semilla 42). En 4.1.5 se registran también la media, la desviación típica, el mínimo y el máximo de la latencia.

En esos párrafos quedan sin registrar, a propósito:

- Recuentos derivados, comprobados contra su artefacto el 2026-09-28. Los que añadió la pasada 2f los escribe `provenance/commands/task09/revise_pass2f.py` desde los artefactos, y `manuscript/source/edit_log.json` guarda sus valores:
  - las 669 imágenes del corpus del detector, que son las filas de `data/manifests/model1_clean_manifest.csv`;
  - las 11 imágenes repetidas, 219 − 208 en `artifacts/metrics/model2_sensitivity.json`;
  - los 20 errores del Modelo 2, la suma fuera de la diagonal de la matriz de confusión de ese mismo archivo;
  - en 3.3.1, los 38 desacuerdos entre los 47 pares suplementarios y los 7 sobre si existía relación (`data/audits/model1/supplementary_adjudications.csv`);
  - en 4.1.1, el mAP@0,5 de 0,905 y el mAP@0,5:0,95 de 0,761 del registro de entrenamiento en la época 91 (`experiments/model1/EXP-R01/v1/run/train/results.csv`);
  - en 4.1.5, las 32 imágenes, los 28 grupos, las 3 con Enfermo y los 0 a 2 frutos detectados del conjunto medido (`artifacts/metrics/benchmark_raw_pool.csv` y `benchmark_raw.csv`);
  - en 4.2.1, los SHA-256 distintos de entrenamiento (986 de 1064) y de validación (206 de 217) y el único cluster con etiquetas distintas (`data/manifests/model2_frozen_manifest.csv`).
- Los números que no son resultados: los nombres de modelo (YOLO26n, YOLO11n), «mAP@0,5», «95 %», «SHA-256», los números de sección, tabla y figura, y la configuración del equipo y del protocolo del benchmark en 4.1.5.

La latencia sale de `artifacts/metrics/benchmark_summary.json`, escrito por `provenance/commands/task06/summarize_benchmark.py` desde `artifacts/metrics/benchmark_raw.csv` con la misma función `summarize` del benchmark.

Quedan fuera del registro, con su fuente:

- Las celdas de las Tablas 4, 5 y 7 y las Figuras 4 a 7. Las escriben celda a celda `results_tables.py` y `figures_results.py` desde los mismos artefactos. La auditoría B comprobó todos sus valores (secciones 1 y 4 de su informe de la ronda 1).
- Las cifras de datos y métodos (Tablas 1, 2, 3 y 6 y la Sección 3). Las fijaron las pasadas 1 a 2b desde los manifiestos congelados y los registros de EXP-R01 y ART-002.
- Las cifras históricas que el texto presenta como tales, por ejemplo las 13 instancias Enfermo de la prueba publicada.

## 2. Lenguaje

`reports/editorial_claim_audit.csv` recoge 24 decisiones, de ED-01 a ED-24. Cubren eficiencia, temporalidad, prevalencia, fuga, latencia, impacto, la adjudicación por IA, la cronología de la partición y dos afirmaciones de la literatura. Desde la pasada 2e, `document_checks` también busca «limpio» o «limpia» usado como veredicto de fuga. No encuentra ninguna coincidencia léxica sin revisar. La única coincidencia revisada es la negación de 3.3.1: «No se afirma que el conjunto esté libre de fuga».

La búsqueda por palabras no basta, así que las pasadas 2d, 2e y 2f añadieron una revisión semántica.

La pasada 2d:

- retiró la premisa de que la inspección visual es tardía (B-01);
- declaró las dos pruebas como evaluaciones internas retrospectivas (B-05);
- convirtió en hipótesis las explicaciones causales no ensayadas: la memorización por la fuga del corpus de clasificación (B-02), la confusión Cancro bacteriano–Costras, la resolución y la saturación bajo luz intensa (B-03, B-04), y la diferencia entre validación y prueba (B-06).

La pasada 2e:

- retiró de 3.4 la justificación de la variante nano por un equilibrio de velocidad, memoria y hardware de borde que no se midió (R2-01, ED-18);
- dejó RGB-D y Raspberry Pi 4 como trabajo futuro no evaluado, sin pronóstico de consolidación ni de sostenibilidad (R2-02, ED-19);
- declaró también en 3.7 que las dos pruebas son evaluaciones internas retrospectivas, y en la carta, en REVIEW-04 (R2-03);
- sustituyó «partición limpia» y «conjunto limpio» por el nombre MangoDHDS_clean y la redacción limitada al protocolo (R2-06, ED-20);
- alineó 6.1 con 3.5: el corpus de clasificación sólo tiene etiquetas de imagen completa (CLAIM-031).

La pasada 2f responde a la revisión adversarial final (sección 7).

## 3. Claims del manuscrito original

`docs/research/claim_evidence_matrix.csv` conserva las 50 filas y sus columnas de auditoría. Las columnas `final_status`, `final_location` y `final_evidence` dan su destino en el texto revisado (`provenance/commands/task09/claims_final.py`):

| Estado final | Claims |
|---|---:|
| REPLACED | 13 |
| SUPPORTED | 10 |
| RETIRED | 8 |
| REFORMULATED | 7 |
| QUALIFIED | 6 |
| CORRECTED | 6 |

La pasada 2e corrigió cuatro destinos:

- CLAIM-035 pasa a CORRECTED, porque el F1 de Cancro bacteriano era 0,832 y es 0,831.
- CLAIM-049 pasa a REFORMULATED: su mitad temporal se retiró y la ventaja del aprendizaje profundo se conserva, atribuida y sin «consistentemente».
- CLAIM-014 cubre ahora también el resumen y 4.2.1.
- CLAIM-031 cubre ahora también 6.1.

Las dos afirmaciones que la ronda 2 encontró fuera de la matriz caen en claims existentes. La eficiencia de la variante nano de 3.4 corresponde a CLAIM-001, retirado. La extensión RGB-D de la conclusión corresponde a CLAIM-043, reformulado.

Ningún claim queda UNVERIFIED ni UNSUPPORTED sin destino, ni pendiente de los autores. CLAIM-042 pasó a SUPPORTED en la pasada 2f: el resumen, 3.6, 5.3 y la disponibilidad de datos citan el repositorio público (Villa Bastidas et al., 2026), con el código, los manifiestos, los pesos de los dos modelos y la evidencia bajo licencia AGPL-3.0.

## 4. Afirmaciones nuevas de resultados

| Afirmación | Ubicación | Evidencia |
|---|---|---|
| Umbral 0,35 elegido en validación por F2 de Enfermo, antes de la prueba | 3.7; 4.1.2 | `configs/evaluation_frozen.json` (commit `96a5991`); auditoría A, sección 4 |
| Prueba del Modelo 1 evaluada una sola vez, como evaluación interna retrospectiva | Resumen; 3.7; 4.1.2; 7 | `provenance/test_access_log.csv` (TEST-ACCESS-004); `experiments/model1/EXP-R02/account_kernels_*.json` |
| mAP@0,5 y sensibilidad para Enfermo en prueba, con IC por grupo | Resumen; 4.1.2; Tabla 5; 5.1; 6.1; 7 | `experiments/model1/EXP-R02/metrics.json`; `artifacts/metrics/model1_intervals.json` |
| El detector deja pasar más frutos enfermos de los que marca en falso | 5.1 | Matriz de detección de EXP-R02 (11 frente a 4); precisión mayor que sensibilidad |
| El error dominante es la falta de detección | 4.1.3 | Matriz de detección de EXP-R02 (Figura 4) |
| Exactitud y macro-F1 del Modelo 2, y su cambio con deduplicación y ponderación por cluster | Resumen; 4.2.3; Tabla 7; 7 | `artifacts/metrics/model2_intervals.json`; `artifacts/metrics/model2_sensitivity.json` |
| Latencia en CPU por etapa y de extremo a extremo | 4.1.5 | `reports/benchmark_report.md`; `artifacts/metrics/benchmark_summary.json` |

La auditoría A (`reports/execution/task-05-execution-audit.md`) reprodujo byte a byte los artefactos de las cinco primeras filas y validó el registro de la latencia.

## 5. Hallazgos de la auditoría B, ronda 1

| Hallazgo | Resolución |
|---|---|
| B-01 premisa temporal en la introducción | Retirada (pasada 2d) |
| B-02 sobreestimación «severa» y memorización | Limitado a la dependencia demostrada, con cita (pasada 2d) |
| B-03 explicación de la confusión Cancro–Costras y saturación por luz | Declaradas hipótesis no ensayadas (pasada 2d) |
| B-04 «resolución 320 px» | Sustituido por «Evaluar más datos, mayor resolución o atención local» |
| B-05 estado retrospectivo de las pruebas | Declarado en el resumen, 4.1.2, 4.2.3 y la conclusión (pasada 2d) y en 3.7 (pasada 2e); la carta, en REVIEW-03 y REVIEW-04 |
| B-06 «montajes que el modelo no vio» | Sustituido por la separación documentada por grupos, sin atribuir causa |
| B-07 sensibilidad a duplicados del Modelo 2 | Nuevo párrafo en 4.2.3 con las tres estimaciones y los cambios con IC pareado |
| B-08 alcance del registro de cifras | 156 cifras y alcance exacto en la sección 1 (pasada 2e) |
| B-09 matriz de claims y esta auditoría | Secciones 3 y 4, con los destinos corregidos en la pasada 2e |
| B-10 carta desactualizada | Ubicaciones del render final; el encabezado nombra CLAIM-042 como única acción pendiente |
| B-11 etiquetas apretadas en las Figuras 5 y 7 | Figura 5 sin etiquetas fuera del panel (pasada 2e); los solapes entre etiquetas de escenas densas quedan como bajo aceptado |
| B-12 punto decimal en la Figura 3 y en la carta | Figura 3 regenerada con coma decimal; carta en la pasada final |
| B-13 resolución de las Figuras 1 y 2 | Regeneradas a 300 ppp con el mismo tamaño físico |

Otros cambios de la revisión del render de la pasada 2d: encabezado de página rellenado, fuga del detector mencionada en 5.3 y la conclusión, alcance del servicio web en la conclusión, cinco diagnósticos en 5.2 (CLAIM-041), etiquetas de imagen completa en 3.5 (CLAIM-031), mayúsculas de los nombres de enfermedad, «5·10⁻⁴» en la Tabla 2, «669 imágenes» en la Tabla 8 y «las Figuras 5 y 7».

## 6. Hallazgos de la auditoría B, ronda 2

| Hallazgo | Severidad | Resolución (pasada 2e, `provenance/commands/task09/revise_pass2e.py`) |
|---|---|---|
| R2-01 eficiencia y borde de la variante nano en 3.4 | HIGH | «La variante nano es la del run histórico; este trabajo no comparó variantes de otro tamaño.» ED-18; CLAIM-001 |
| R2-02 pronóstico de sostenibilidad en la conclusión | HIGH | «…quedan como trabajo futuro; este estudio no evaluó ninguno de los dos.» ED-19; CLAIM-043 |
| R2-03 3.7 y REVIEW-04 sin estado retrospectivo | MEDIUM | 3.7 declara las dos pruebas evaluaciones internas retrospectivas; REVIEW-04 habla de «la nueva partición interna de prueba, evaluada de forma retrospectiva» |
| R2-04 cobertura parcial del registro de cifras | MEDIUM | 32 cifras más (extremos de intervalos en 4.2.3, 5.1, 6.1 y 7; recuentos de 4.1.3; parámetros del bootstrap); alcance exacto en la sección 1 |
| R2-05 destinos de CLAIM-035, CLAIM-049 y CLAIM-014 | MEDIUM | Sección 3 |
| R2-06 «partición limpia» y «conjunto limpio» | MEDIUM | MangoDHDS_clean como nombre y redacción limitada al protocolo; `document_checks` detecta desde ahora «limpio/limpia» |
| R2-07 encabezado de la carta frente a CLAIM-042 | MEDIUM | El encabezado nombra CLAIM-042 como única acción pendiente; la decisión sigue siendo de los autores |
| R2-08 Figura 5 cortada y Figura 7 densa | LOW | Figura 5 regenerada sin etiquetas fuera del panel; la Figura 7 es el dibujo del propio script de línea de comandos y se acepta como bajo |
| R2-09 autor en los metadatos del PDF | LOW | Autor del DOCX y del PDF igual a la línea de autores del manuscrito |

La revisión del render de la pasada 2e (`reports/execution/render_review.md`) añadió además que ningún título quede solo al pie de una página.

## 7. Revisión adversarial final

La revisión (`reports/final_adversarial_review.md`) recomienda rechazar. Encontró 6 HIGH, 8 MEDIUM y 2 LOW. La pasada 2f (`provenance/commands/task09/revise_pass2f.py`) corrige o declara lo que el texto puede resolver, con las decisiones de los autores del 2026-09-28: declarar ya la adjudicación por IA, mantener el título y publicar el repositorio con los pesos bajo AGPL-3.0. Lo que exige datos nuevos o revisión humana queda abierto y declarado.

| Hallazgo | Severidad | Estado tras la pasada 2f |
|---|---|---|
| H-01 adjudicación por agentes de IA presentada como revisores independientes | HIGH | Declarada en 3.3.1 y en REVIEW-01: modelos, ciego por instrucción, sin revisión humana, controles fallidos y desacuerdos (ED-21). Abierta la re-adjudicación humana que pide el revisor |
| H-02 regla de partición «fijada antes de ver los datos» | HIGH | Corregido en 3.3.1 y REVIEW-02: se fijó el 20-09-2026, antes de construir los grupos y después de conocer los datos (ED-22) |
| H-03 sin estándar diagnóstico para las etiquetas | HIGH | Declarado en 6.1; el título se mantiene por decisión de los autores. Abierto: exige etiquetas con confirmación fitopatológica |
| H-04 un único origen Enfermo en entrenamiento y sensibilidad baja | HIGH | Ya declarado en 3.2.1, 3.3.1 y 6.1. Abierto: exige datos nuevos |
| H-05 sin verdad de terreno conjunta y cambio de dominio del clasificador | HIGH | El cambio de dominio se declara en 5.2 y REVIEW-12/13. Abierto: exige un conjunto con caja y diagnóstico en campo |
| H-06 código «publicado» sin publicar; inferencia no reproducible | HIGH | Repositorio público con el código, los manifiestos, las predicciones y los pesos de los dos modelos, citado en el resumen, 3.6, 5.3 y la disponibilidad de datos (CLAIM-042) |
| M-01 pruebas retrospectivas | MEDIUM | Ya declarado; el revisor lo reconoce |
| M-02 cluster de entrenamiento con etiquetas Cancro bacteriano y Costras | MEDIUM | Declarado en 4.2.1. Abierta la adjudicación con experto |
| M-03 duplicados en entrenamiento y validación del Modelo 2 | MEDIUM | Declarado en 4.2.1 con sus recuentos. Abierto el reentrenamiento con muestreo por grupos |
| M-04 dos evaluadores de validación | MEDIUM | 4.1.1 da las dos cifras, las diferencias conocidas (lotes rectangulares y FP16 frente a imagen a imagen en FP32) y lo que no se comprobó |
| M-05 intervalos condicionales | MEDIUM | Declarado en 3.7 y REVIEW-05 |
| M-06 umbral de 0,4 sin validar | MEDIUM | Declarado en 3.1 |
| M-07 latencia incompleta | MEDIUM | 4.1.5 y REVIEW-07 dan media, desviación típica, mínimo, máximo y composición del conjunto medido |
| M-08 afirmaciones de la literatura | MEDIUM | Suavizadas en la Sección 1 y en 2.2 (ED-23, ED-24) |
| L-01 URL móvil de Ultralytics y pie de plantilla | LOW | Ultralytics citado por la etiqueta v8.4.52; el pie lo completa la revista |
| L-02 blancos y etiquetas densas | LOW | Aceptado; la pasada 2f además impide que una tabla se corte entre páginas |

Quedan abiertos cuatro HIGH, que dependen de datos nuevos o de revisión humana (H-01 en su parte de re-adjudicación, H-03, H-04 y H-05), y dos MEDIUM en su parte de adjudicación y reentrenamiento (M-02 y M-03). Ningún cambio de texto los resuelve. Enviar así el manuscrito es una decisión de los autores, que el informe final registra.
