# Independent Audit B, Round 2 — TASK-09 results pass

**Manuscript:** ALBUS26-116  
**Audit date:** 2026-09-28  
**Candidate audited:** `manuscript/source/Articulo_Mango_ALBUS_revision.docx`, SHA-256 `c8c5654c6855299157459757877184c8ae637ea5e6201ea2c3596367171a0773`  
**Rendered candidate:** `manuscript/output/Articulo_Mango_ALBUS_revision.pdf`, SHA-256 `f0618a04359499953c875ad1fc28d31b9247097ea4897385b6667fb43d337a1e`, 16 pages  
**Audit type:** independent read-only research-methodology and scientific-reporting re-review  
**Repository changes made by this audit:** this report only

## Verdict

**No. Apart from CLAIM-042 and the unfinished TASK-10, the manuscript and response letter still should not be submitted as they stand.** The central numerical results remain valid: the M1 and M2 point estimates and intervals, the new M2 duplicate-sensitivity paragraph, the confusion counts, and the CPU benchmark reconcile with their artifacts at the printed precision. No retracted detector result is presented as current.

The remaining blockers are reporting defects rather than failed computations. I found **2 open HIGH** and **5 open MEDIUM** findings. The two HIGH findings are an unsupported comparative efficiency/edge-compatibility claim in Section 3.4 and an unsupported causal societal-impact forecast in the conclusion. The MEDIUM findings concern a residual unqualified retrospective-test statement, incomplete numerical checking presented as broad coverage, inaccurate/incomplete final claim dispositions, unqualified “clean” leakage shorthand, and a response-letter header that contradicts the known pending publication claim. Two LOW presentation/metadata findings also remain.

## Authority and method

I applied the immutable protocol, design, TASK-09/TASK-10 plan, and decision log. In particular:

- the current tests must be reported as internal retrospective evaluations, never as newly pristine prospective holdouts;
- operational groups are the maximum known dependence unit, not demonstrated biological independence;
- checkpoint, threshold, and other scientific choices may not be selected on test;
- leakage statements must name the tested protocol and limits rather than claim universal cleanliness; and
- descriptive latency without a prior comparator cannot support a comparative efficiency claim.

I compared the DOCX before and after pass 2d in memory from Git blobs, read the final DOCX with `python-docx`, reconciled artifacts and JSON values without regenerating scientific outputs, rendered the committed PDF to temporary PNGs outside the worktree, inspected all 16 pages, and reran the final DOCX citation checker read-only (`21 entries, 21 cited keys`, no missing or uncited entry).

## 1. Round 1 findings B-01 through B-13

| ID | Round 2 status | Exact final text or evidence | Assessment |
|---|---|---|---|
| B-01 | **CLOSED** | Section 1 now says: “Para el productor rural promedio, las técnicas de laboratorio son costosas, lentas y requieren infraestructura especializada raramente disponible en zonas rurales (Venbrux et al., 2023).” | The unsupported premise that visual inspection is inherently late is gone. The remaining temporal statement in 5.4 is explicitly “una hipótesis por comprobar, no un resultado.” |
| B-02 | **CLOSED** | Section 3.3.2: “Con imágenes casi idénticas repartidas entre particiones, las métricas de validación y de prueba no miden sólo la generalización a frutos no vistos y pueden sobreestimarla (Kapoor & Narayanan, 2023); este trabajo no cuantificó ese efecto en el corpus de clasificación.” | This removes “severa,” memorization as a demonstrated mechanism, and the claim that the old metric was merely a memorization indicator. |
| B-03 | **CLOSED** | Section 4.2.3: “Este trabajo no analizó la causa de esa confusión; la similitud visual de las lesiones, la resolución de entrada y el número de ejemplos por clase son hipótesis por comprobar.” Section 6.1: “comprobar si más datos, mayor resolución de entrada o módulos de atención local la reducen queda como trabajo futuro” and “una posible saturación del sensor bajo luz intensa, que este trabajo no midió”. | The observed confusion remains separate from the untested explanations and remedies. Light saturation is now expressly unmeasured. |
| B-04 | **CLOSED** | Table 8 now says “Evaluar más datos, mayor resolución o atención local.” | The unsupported exact recommendation of 320 px is gone. |
| B-05 | **PARTIALLY CLOSED** | Correct additions include “una evaluación interna retrospectiva sobre imágenes ya publicadas,” “no una prueba prospectiva,” and retrospective qualifications in 4.2.3, the conclusion, and REVIEW-03. However, Section 3.7 still says “La validación sirvió sólo para elegir el checkpoint y el umbral; la prueba se evaluó una sola vez, con ambos fijados” without the required status, and REVIEW-04 calls it “El test nuevo”. | The manuscript and letter are much clearer, but one methods summary and one response still allow a pristine/new-holdout reading. See R2-03. |
| B-06 | **CLOSED** | Section 4.1.2: “Validación y prueba son disjuntas de entrenamiento por grupo de origen, y este trabajo no identificó la causa de la diferencia entre ambas.” | It states only the documented group separation and disclaims causal attribution. |
| B-07 | **CLOSED** | Section 4.2.3 reports 219 images, 208 unique SHA-256 values, 11 repeated files, both prespecified sensitivity estimands, 2,000 paired group resamples, seed 42, all point estimates, all 95% intervals, and all paired delta intervals. | Every value, sign, interval endpoint, and displayed rounding matches `artifacts/metrics/model2_sensitivity.json`; details are in Section 3 below. |
| B-08 | **PARTIALLY CLOSED** | `reports/manuscript_consistency.json` truthfully records `"checked_numbers": 124` and no mismatch among those entries. `reports/editorial_audit.md` documents exclusions for Tables 4, 5, and 7, Figures 4–7, methods/data figures, and historical figures. | Coverage is improved, but not complete or fully scoped: at least 19 displayed interval endpoints in 5.1, 6.1, and 7 are outside the checker even though those sections are described as covered. See R2-04. |
| B-09 | **PARTIALLY CLOSED** | The matrix has 50 rows and final columns; `reports/editorial_audit.md` exists. The matrix makes CLAIM-042 the sole `PENDING_AUTHOR` row. | CLAIM-035 and CLAIM-049 have false final-status labels, CLAIM-014 is not fully reflected in all final wording/locations, and the two open HIGH claims are absent from the matrix. See R2-05 and R2-06. |
| B-10 | **PARTIALLY CLOSED** | Literal searches find no `[PENDIENTE]`, `BORRADOR`, or `DRAFT`. REVIEW-10 and REVIEW-14/15 now have final dispositions and their stated sections exist. The title is “Respuesta al dictamen — ALBUS26-116”. | The header says “Ninguna acción pendiente se describe como hecha,” while the manuscript says the code is published and the repository records that as pending CLAIM-042. See R2-07. |
| B-11 | **OPEN** | In the final PDF, Figure 5’s lower-right panel has overlay text clipped at the right boundary; Figure 7’s 16-box panel uses very small labels. | This remains LOW because it does not alter the underlying counts, but the labels are not all comfortably readable. See R2-08. |
| B-12 | **CLOSED** | Figure 3 visibly uses comma decimals, including “mAP@0,5:0,95 = 0,761”. REVIEW-05 now reports the historical Wilson interval as `[0,578; 0,957]`. | Decimal punctuation is correct for current Spanish results. Decimal points that remain are literal software versions, DOI/URL text, or the exact YOLO annotation tuple `cls 0.5 0.5 1.0 1.0`; the reviewer’s original `0.846` remains only inside the attributed comment. |
| B-13 | **CLOSED** | Figures 1 and 2 are byte-identical to their source PNGs. They are 2418 × 1803 and 2559 × 1515 pixels and are placed at 6 inches wide, approximately 403 and 427 ppi. | Both comfortably exceed 300 ppi at their final placed size. |

## 2. Every body paragraph changed or added by pass 2d

The binary DOCX diff contains 18 changed or inserted body paragraphs. Each final paragraph is quoted below exactly.

### Abstract

> Resumen: Las enfermedades del mango causan pérdidas de producción, y su diagnóstico convencional depende de la inspección visual o del laboratorio, costosos o poco accesibles para el productor rural colombiano. Este trabajo presenta un sistema de detección visual automatizada de signos de enfermedad en frutos de mango, organizado como una cascada de dos modelos YOLO: un detector YOLO26n que localiza frutos y los clasifica como Enfermo o Saludable, y un clasificador YOLO11n-cls que asigna a cada fruto detectado una de cuatro patologías o Saludable. Una auditoría de fuga de datos mostró que la partición publicada del corpus del detector (669 imágenes de terceros) no era independiente: un mismo montaje de fotografías aparecía en entrenamiento y en prueba. El detector se reentrenó con una partición por grupos de origen; el checkpoint y el umbral de decisión se fijaron en validación antes de evaluar una sola vez la prueba (117 imágenes, 98 grupos), una evaluación interna retrospectiva sobre imágenes ya publicadas. En ella, el detector alcanza un mAP@0,5 de 0,807 [0,677; 0,887] y una sensibilidad para Enfermo de 0,577 [0,273; 0,735], con el intervalo de confianza del 95 % por grupo entre corchetes. El clasificador, evaluado también de forma retrospectiva sobre la partición limpia de MangoDHDS (219 imágenes), alcanza una exactitud de 0,909 [0,869; 0,946] y un macro-F1 de 0,909 [0,869; 0,945]. No hay verdad de terreno conjunta para medir la cascada completa, y el sistema no se validó en cultivos de la región. Se publican el protocolo de auditoría y su código.

**Judgment:** the numerical and retrospective statements are correct and proportionate. “partición limpia” is an unqualified leakage shorthand (R2-06), and the last sentence is the known pending CLAIM-042. Otherwise, the paragraph introduces no new causal, temporal, or test-selection claim.

### Section 1

> Dentro del sector, el cultivo de mango ocupa un lugar relevante por su valor económico y exportador, pero también por su vulnerabilidad a enfermedades fúngicas y bacterianas como la Antracnosis (causada por Colletotrichum gloeosporioides), el Cancro bacteriano, las Costras y la Podredumbre del extremo del tallo (Dofuor et al., 2023), además de la Cenicilla (Pseudoidium anacardii, antes Oidium mangiferae; Iqbal et al., 2024).

**Judgment:** supported terminology/capitalization correction; no new result claim.

> El diagnóstico convencional de estas patologías se basa en inspección visual humana o, en su defecto, en técnicas de laboratorio como la reacción en cadena de la polimerasa (PCR) o la microscopía (Khakimov et al., 2022; Buja et al., 2021). Para el productor rural promedio, las técnicas de laboratorio son costosas, lentas y requieren infraestructura especializada raramente disponible en zonas rurales (Venbrux et al., 2023). La consecuencia agronómica es una dependencia excesiva de la aplicación preventiva masiva de agroquímicos, con los costos económicos y ambientales que ello implica (Ciofini et al., 2022).

**Judgment:** the unsupported temporal premise was removed. The remaining general claims are attributed; no early-detection premise is adopted as a result of this study.

### Sections 3.2.2 and 3.3.2

> Se utilizó el conjunto MangoDHDS (Barhate et al., 2025), en su versión 1 de Mendeley Data, bajo licencia CC BY 4.0. El corpus original contiene 1500 imágenes distribuidas uniformemente en cinco clases (300 imágenes por clase): Anthracnose (Antracnosis), Bacterial Canker (Cancro bacteriano), Scab (Costras), Stem End Rot (Podredumbre del extremo del tallo) y Healthy (Saludable, utilizada como control de calidad del detector binario).

**Judgment:** supported by the dataset inventory and reference record; capitalization is corrected.

> Con imágenes casi idénticas repartidas entre particiones, las métricas de validación y de prueba no miden sólo la generalización a frutos no vistos y pueden sobreestimarla (Kapoor & Narayanan, 2023); este trabajo no cuantificó ese efecto en el corpus de clasificación.

**Judgment:** supported and proportionate. It describes the dependence risk, uses “pueden,” cites the general methodological source, and expressly disclaims a quantified corpus-specific effect.

### Section 3.5

> Para la segunda etapa se utiliza la variante de clasificación de YOLO (YOLO11n-cls) sobre MangoDHDS_clean. La razón de emplear la modalidad clasificación —y no detección— se justifica por la naturaleza del corpus: sus etiquetas son de imagen completa (en formato YOLO, cajas cls 0.5 0.5 1.0 1.0), de modo que cualquier entrenamiento como detector colapsaría a clasificación de imagen completa.

**Judgment:** supported by `data/audits/model2/membership_clean_vs_cls.json` (`full_image_boxes_in_data004 = 1500`) and the dataset archaeology. The decimal points are literal machine-format tokens, not prose-formatted result decimals. The paragraph no longer attributes the derived YOLO boxes to the original publisher.

### Sections 4.1.2 and 4.2.3

> El checkpoint de la época 91 y el umbral 0,35 (F2 de Enfermo en validación = 0,884) se fijaron antes de evaluar la prueba una sola vez (EXP-R02). Es una evaluación interna retrospectiva, no una prueba prospectiva: sus imágenes eran públicas y parte de ellas estaba en el entrenamiento histórico (Sección 3.3.1). La prueba tiene 117 imágenes, 98 grupos de origen y 192 instancias: 26 Enfermo y 166 Saludable. La Tabla 5 da cada métrica con su intervalo de confianza del 95 %, obtenido con 2000 remuestras bootstrap de los grupos de origen (semilla 42).

**Judgment:** fully supported by the selection record, access chronology, manifest, M1 metrics, and interval artifact. It correctly distinguishes the current validation-only selection from the historical exposure.

> Frente a validación, el mAP@0,5 baja de 0,889 a 0,807 [0,677; 0,887], y la caída se concentra en la clase Enfermo. Su sensibilidad pasa de 0,867 en validación a 0,577 [0,273; 0,735] en prueba, mientras que la de Saludable apenas cambia (0,846 frente a 0,867 [0,800; 0,931]). Es el resultado contrario al que se busca en este dominio, donde un fruto enfermo sin detectar cuesta más que una falsa alarma. La prueba tiene solo 26 instancias Enfermo en 15 grupos de origen, así que el intervalo de esa sensibilidad es ancho; aun así, su extremo superior queda por debajo del valor de validación. El umbral se eligió en validación, lo que vuelve optimistas las cifras de esa partición. Validación y prueba son disjuntas de entrenamiento por grupo de origen, y este trabajo no identificó la causa de la diferencia entre ambas.

**Judgment:** all values are correct. The final sentence fixes B-06 and avoids attributing the change to unseen montages or another untested cause. The statement about false-negative cost is the declared operating objective, not an empirical cost estimate.

> La evaluación se realizó sobre las 219 imágenes de la partición de prueba, en la que no se detecta contaminación entre particiones bajo el protocolo especificado (SHA-256 y pHash con Hamming < 5); esas imágenes forman 203 grupos de similitud, que son la unidad de los intervalos. El modelo alcanza una exactitud top-1 de 0,909 [0,869; 0,946] y un macro-F1 de 0,909 [0,869; 0,945], distribuidos según la Tabla 7. Como en el Modelo 1, es una evaluación interna retrospectiva: la versión anterior del manuscrito ya informó resultados sobre esta partición.

**Judgment:** supported and protocol-compliant. It bounds the leakage conclusion to the named protocol, calls the groups similarity groups rather than biologically independent units, and declares the retrospective status.

> La prueba tiene 219 imágenes pero 208 SHA-256 distintos: 11 imágenes repiten exactamente a otra de la misma partición. Los dos análisis de sensibilidad fijados en el protocolo usan las mismas predicciones y las mismas 2000 remuestras de grupos (semilla 42). Con una imagen por SHA-256, la exactitud es 0,904 [0,862; 0,943] y el macro-F1 0,906 [0,865; 0,943]; con peso 1 por cluster, 0,901 [0,857; 0,941] y 0,904 [0,862; 0,942]. Frente al análisis principal, la exactitud cambia -0,48 [-0,83; -0,22] y -0,72 [-1,24; -0,33] puntos porcentuales, y el macro-F1 -0,30 [-0,60; -0,09] y -0,50 [-0,95; -0,17], con el intervalo pareado del 95 % entre corchetes.

**Judgment:** fully supported. Section 3 below gives the unrounded reconciliation.

> De los 20 errores, los más frecuentes son: 6 imágenes de Cancro bacteriano clasificadas como Costras; 6 imágenes de Costras clasificadas como Cancro bacteriano; 2 imágenes de Costras clasificadas como Antracnosis (Figura 6). El intercambio entre Cancro bacteriano y Costras reúne la mayor parte de los errores, en las dos direcciones, y coincide con los F1 más bajos de la Tabla 7 (0,831 [0,736; 0,911] y 0,837 [0,743; 0,915]). Este trabajo no analizó la causa de esa confusión; la similitud visual de las lesiones, la resolución de entrada y el número de ejemplos por clase son hipótesis por comprobar. Saludable y Podredumbre del extremo del tallo alcanzan F1 de 0,976 [0,937; 1,000] y 0,976 [0,935; 1,000].

**Judgment:** counts and intervals match the artifacts. The possible explanations are explicitly hypotheses; no causal result is asserted.

### Sections 5.2 and 5.3

> La separación entre detección binaria y clasificación multiclase resulta justificada por la naturaleza de los datos disponibles. Un único modelo entrenado directamente sobre los cinco diagnósticos (cuatro enfermedades y Saludable) habría requerido un corpus con anotaciones simultáneas de caja y diagnóstico, que no se encontró entre los conjuntos públicos de mango revisados. La cascada permite explotar el conjunto de detección en campo abierto y el conjunto de clasificación en condiciones controladas. El costo es la propagación de errores: un fruto enfermo que el Modelo 1 no detecta nunca recibe diagnóstico, así que el desempeño de la cascada no es el producto de los desempeños de cada modelo. La métrica que lo mide es la proporción de frutos enfermos que reciben a la vez una detección emparejada (IoU ≥ 0,5) y la enfermedad correcta, sobre todos los frutos enfermos, detectados o no. Calcularla exige verdad de terreno conjunta, con caja y diagnóstico adjudicados para los mismos frutos, que ninguno de los dos conjuntos tiene. La métrica y su evaluador quedan definidos, pero su valor no se informa.

**Judgment:** the count of diagnoses and the limited corpus-search wording are corrected. The error-propagation statement follows mechanically from the implemented cascade, and the missing joint ground truth is stated rather than replaced with an invented result.

> Las dos auditorías de fuga son relevantes por dos motivos. En el corpus del detector, casi todas las instancias Enfermo de la prueba publicada procedían de un montaje cuyas demás imágenes estaban en entrenamiento (Sección 3.3.1), y en el de clasificación había pares casi duplicados repartidos entre particiones (Sección 3.3.2). Primero, muestran por qué conviene auditar el particionamiento antes de utilizar un conjunto público. Segundo, sugieren que las métricas reportadas en trabajos previos que hayan usado las particiones originales podrían estar sesgadas al alza y deberían interpretarse con cautela. El protocolo de regeneración (hash perceptual, union-find y estratificación) y su código se publican para que pueda aplicarse a otros conjuntos.

**Judgment:** the detector and classifier leaks are both represented, and “podrían” is proportionate. The final publication sentence remains CLAIM-042 and is not true until the author publishes/cites the repository or changes the sentence.

### Section 6.1

> La tercera limitación, y la de mayor peso para el uso previsto, es la baja sensibilidad del detector para Enfermo en prueba (0,577 [0,273; 0,735]), estimada con solo 26 instancias en 15 grupos de origen. La cuarta es la confusión entre Cancro bacteriano y Costras en el clasificador, con F1 de 0,831 [0,736; 0,911] y 0,837 [0,743; 0,915]: comprobar si más datos, mayor resolución de entrada o módulos de atención local la reducen queda como trabajo futuro. La quinta es la decisión deliberada de operar solo sobre el canal RGB de la cámara disponible, sin explotar la morfología accesible por profundidad estéreo. La sexta es el desbalance entre las clases del detector: hay muchas más instancias Saludable que Enfermo, lo que puede sesgar el entrenamiento hacia Saludable y deja la estimación de Enfermo en prueba con poca precisión. Quedan dos limitaciones operativas: una posible saturación del sensor bajo luz intensa, que este trabajo no midió, y la ausencia de mediciones en hardware de borde, pues la latencia en Raspberry Pi 4 no se midió. Finalmente, el sistema aún carece de un conjunto de prueba out-of-distribution externo, anotado de forma independiente, condición necesaria para sostener las afirmaciones de generalización en producción.

**Judgment:** result values are correct; remedies and light saturation are explicitly untested; no Raspberry Pi result is implied. The paragraph does not call the operational groups biologically independent.

### Conclusion and data availability

> Este trabajo presentó el diseño y la implementación de un sistema de visión por computador para la detección visual automatizada de signos de enfermedad en frutos de mango, estructurado como una cascada de dos modelos YOLO especializados. El detector binario YOLO26n, reentrenado con una partición por grupos de origen y evaluado una sola vez, de forma retrospectiva, sobre 117 imágenes de prueba de 98 grupos, alcanza un mAP@0,5 de 0,807 [0,677; 0,887] y una sensibilidad para Enfermo de 0,577 [0,273; 0,735]. El clasificador YOLO11n-cls, evaluado de forma retrospectiva sobre la partición limpia de MangoDHDS, alcanza una exactitud de 0,909 [0,869; 0,946] y un macro-F1 de 0,909 [0,869; 0,945]. Entre corchetes se dan los intervalos de confianza del 95 % por grupo.

**Judgment:** metrics and retrospective labels are correct. “partición limpia” remains unqualified leakage shorthand (R2-06).

> Como contribución metodológica, se identificaron y mitigaron fugas de datos en las particiones publicadas de los dos corpus: en el del detector, un mismo montaje fotográfico repartido entre entrenamiento y prueba, sustituido por una partición por grupos de origen; en el del clasificador, pares casi duplicados entre particiones, eliminados con un procedimiento reproducible basado en hash perceptual y union-find que regenera el conjunto con estratificación por clase, sin contaminación entre particiones detectada bajo el protocolo especificado (SHA-256, pHash con distancia de Hamming < 5 y agrupamiento por cluster). Esta auditoría es relevante para investigadores futuros que utilicen los mismos corpus y, en general, para la práctica de validación de calidad sobre conjuntos públicos en agricultura.

**Judgment:** supported and properly bounded to the tested protocol. “Mitigaron” is justified as cross-partition relations detected by that procedure being coassigned; the sentence does not claim universal independence.

> El detector también se ofrece como servicio web local basado en FastAPI con persistencia SQLite, pensado para operar sin conectividad permanente a internet; la cascada completa se ejecuta por línea de comandos (Sección 3.6). El siguiente paso prioritario es validar el sistema contra un conjunto de prueba externo anotado en campo, condición indispensable para sostener su aplicabilidad en producción agronómica real. La incorporación futura de información tridimensional (RGB-D) mediante la cámara Intel RealSense D435 y el despliegue edge sobre Raspberry Pi 4 con cuantización INT8 son las extensiones naturales que consolidarían el enfoque dentro del paradigma de Agricultura 4.0 como motor de sostenibilidad alimentaria en Colombia.

**Judgment:** the first sentence correctly limits the web service to the detector and the CLI to the full cascade; the external-test sentence is appropriate. The final sentence is an unsupported causal/impact forecast and fails this audit (R2-02).

> Los conjuntos empleados en este trabajo son de acceso público bajo licencia CC BY 4.0: mangoUnhealty v2 (Jairos Workspace, 2026), del que proceden las imágenes de entrenamiento del Modelo 1 y las reproducidas en las Figuras 5 y 7, y MangoDHDS (Barhate et al., 2025), base del Modelo 2. El procedimiento de deduplicación que genera MangoDHDS_clean se describe en la Sección 3 y es reproducible con semilla fija. De forma independiente, el equipo publicó en Roboflow Universe el conjunto Mango Disease (DANNs Workspace, 2026) (1019 imágenes, cinco clases, CC BY 4.0); dicho conjunto no interviene en los modelos ni en los resultados aquí reportados y queda disponible para trabajos futuros.

**Judgment:** locations, roles, counts, and non-use of the independent dataset agree with the repository records. No result is attributed to that dataset.

### Other pass-2d changes

| Item | Exact final content | Audit |
|---|---|---|
| Running header | “Villa Bastidas et al. \| Detección y clasificación de enfermedades en mango” | Present on PDF pages 2–16. |
| Table 2 | “5·10⁻⁴” | Correct typography and visible in the PDF. |
| Table 8 | “Detector limitado a 669 imágenes” | Correct and supported. |
| Table 8 | “Evaluar más datos, mayor resolución o atención local” | Appropriate future evaluation wording; no efficacy claim. |
| Table 8 | “Posible saturación del sensor (no medida)” / “Evaluar parasol y normalización” | Correctly marked unmeasured and prospective. |
| Figures 1–3 | Embedded media hashes equal their source PNG hashes | Figures 1–2 exceed 300 ppi at placement; Figure 3 uses decimal commas. |

## 3. M2 duplicate-sensitivity reconciliation

The new paragraph exactly matches `artifacts/metrics/model2_sensitivity.json`:

| Quantity | Artifact value | Manuscript | Audit |
|---|---:|---:|---|
| Images / unique SHA-256 / redundant files | 219 / 208 / 11 | 219 / 208 / 11 | Correct |
| Operational groups | 203 | 203 in the surrounding paragraph | Correct; not called biological independence |
| Resamples / seed | 2000 / 42 | 2000 / 42 | Correct |
| Exact-SHA accuracy | 0.903846; CI [0.861905, 0.942857] | `0,904 [0,862; 0,943]` | Correct |
| Exact-SHA macro-F1 | 0.906425; CI [0.864593, 0.943032] | `0,906 [0,865; 0,943]` | Correct |
| Cluster-weighted accuracy | 0.901478; CI [0.857143, 0.940887] | `0,901 [0,857; 0,941]` | Correct |
| Cluster-weighted macro-F1 | 0.904460; CI [0.861582, 0.942311] | `0,904 [0,862; 0,942]` | Correct |
| Exact-SHA accuracy delta | -0.482965 pp; CI [-0.828448, -0.216449] | `-0,48 [-0,83; -0,22]` | Correct sign and rounding |
| Cluster-weighted accuracy delta | -0.719797 pp; CI [-1.242330, -0.329175] | `-0,72 [-1,24; -0,33]` | Correct sign and rounding |
| Exact-SHA macro-F1 delta | -0.304836 pp; CI [-0.601999, -0.090504] | `-0,30 [-0,60; -0,09]` | Correct sign and rounding |
| Cluster-weighted macro-F1 delta | -0.501382 pp; CI [-0.951587, -0.172271] | `-0,50 [-0,95; -0,17]` | Correct sign and rounding |

The shared resampling claim is also supported: the interval and delta records use the same 2,000 group-bootstrap draws and the same draws hash.

## 4. Claim-evidence matrix

The matrix structurally contains 50 original rows plus `final_status`, `final_location`, and `final_evidence`. Most dispositions correspond to the final DOCX, and CLAIM-042 is the only row labeled `PENDING_AUTHOR`. The following dispositions are not fully true:

1. **CLAIM-035 is labeled `SUPPORTED`, but the submitted claim contained Cancro F1 `0.832` and the final table correctly reports `0,831`.** Under the matrix’s own definitions, this is `CORRECTED`, not `SUPPORTED`.
2. **CLAIM-049 is labeled `RETIRED`, but only its temporal half was retired.** Section 1 still says, with attribution, “los modelos de aprendizaje profundo superan a los métodos tradicionales.” The final evidence itself admits that this half remains. The row should be split or labeled `REFORMULATED`/`QUALIFIED`, not `RETIRED`.
3. **CLAIM-014 is only partly qualified in the final presentation.** Sections 3.3.1, 3.3.2, 4.2.3, and the bounded conclusion use acceptable protocol-limited wording, but the abstract and the first conclusion paragraph use “partición limpia de MangoDHDS” without the stated protocol limit, and Section 4.2.1 says “El conjunto limpio”.

The matrix also omits the current Section 3.4 efficiency/edge claim and the conclusion’s sustainability-impact claim, so it cannot support `reports/editorial_audit.md`’s broader assertion that no material unsupported final claim remains. CLAIM-042 is isolated correctly inside the matrix, editorial audit, render review, and state report, but not consistently in the response-letter header.

## 5. Editorial audit and render-review audit

### `reports/editorial_audit.md`

Supported statements:

- the DOCX and PDF hashes are correct;
- the registry contains 124 entries and all 124 registered checks pass;
- latency comes from `benchmark_summary.json`, whose source hash matches the raw CSV;
- the status-count table exactly reflects the CSV as written;
- figures/tables generated from artifacts and checked in Round 1 retain the same values; and
- the stated pass-2d typography, terminology, figure, header, and service-scope changes are present.

Unsupported or overstated statements:

- Section 1 says the registry covers 5.1, 6.1, and the conclusion without disclosing that it checks only selected values at those anchors. It omits at least five displayed interval endpoints in 5.1, six in 6.1, and eight in the conclusion.
- The B-05 resolution row is incomplete because Section 3.7 and REVIEW-04 retain the wording identified in R2-03.
- The claim-destination section inherits the false CLAIM-035 and CLAIM-049 labels and misses the two HIGH claims.
- The B-10 resolution row overlooks the response-header contradiction around CLAIM-042.

### `reports/execution/render_review.md`

The record is otherwise supported: hashes, 16-page count, page contents, section/table/figure order, cross-references, 21 alphabetized references, and the page placements agree with the committed PDF. Its two B-11 caveats are real. No table, caption, or reference entry is cut across a page boundary. The only additional render-level issue found is incorrect PDF author metadata: the PDF `/Author` is `Luis Camacho`, who is not a manuscript author (R2-09).

## 6. Response letter

### Checks that pass

- No literal placeholder remains, and the heading no longer calls the document a draft.
- All current M1, M2, interval, sensitivity-delta, and benchmark metrics match the artifacts and manuscript.
- The historical `33` images, `11/13`, `0.846`, and `145 ms` appear only in reviewer/historical context and are not presented as current results.
- The Wilson interval `[0,578; 0,957]` recomputes correctly.
- Every stated manuscript section/table location exists.
- REVIEW-10 accurately describes the removal of the temporal premise and the current qualified future hypothesis.
- REVIEW-14/15 accurately describes the terminology, decimal-comma, Figure 3, and render work; the LOW Figure 5/7 readability caveats remain documented in the render review.
- REVIEW-08 and REVIEW-12/13 remain honestly blocked rather than being described as validated.

### Checks that fail

- REVIEW-04 says “El test nuevo tiene 117 imágenes…” without saying this is a newly defined **internal retrospective** partition, not a new prospective holdout. This compounds the unqualified Section 3.7 sentence (R2-03).
- The header says “Ninguna acción pendiente se describe como hecha.” The manuscript says “Se publican el protocolo de auditoría y su código” and “su código se publican”, while CLAIM-042 records that publication as pending. The header therefore makes a false blanket statement (R2-07).

## 7. Global leftover scan

- **Retracted numbers:** none is presented as current in the DOCX. Historical values in the letter are explicitly attributed to the reviewer or the old version.
- **`?TEST?`, `TEST`, and “test independiente”:** no current own claim remains. The only “sin fuga” phrase in the letter is the reviewer’s comment; the correct limiting negation remains in Section 3.3.1.
- **Temporal/early detection:** no active result claims early or presymptomatic detection. Section 5.4 says earlier detection than RGB is an untested hypothesis.
- **Selection on test:** no checkpoint, threshold, architecture, or remedy is selected on the current test. The manuscript correctly requires new data for any future threshold adjustment.
- **Groups:** no operational group is called a biologically independent unit or an effective sample size.
- **Efficiency:** cited literature statements about real-time YOLO are attributed. The own Section 3.4 statement about a favorable speed/precision/memory balance and edge compatibility remains unsupported (R2-01).
- **Leakage:** protocol-bounded statements are correct, but “partición limpia” / “El conjunto limpio” remain semantically unqualified (R2-06).
- **Causal/impact language:** the Cancro–Costras and light-saturation explanations are now hypotheses. The conclusion’s sustainability-impact forecast remains unsupported (R2-02).
- **Decimal punctuation:** current Spanish results in prose, tables, and Figures 1–7 use decimal commas. Remaining points occur in software versions, DOI/URL strings, the literal YOLO tuple, or an exact historical reviewer quotation.
- **Figure text:** Figures 1–2 reflect the actual architecture and data sources; Figure 3 uses comma decimals; Figures 4 and 6 match their confusion artifacts; Figures 5 and 7 use the frozen samples and saved predictions. Figure 5’s lower-right labels and Figure 7’s dense panel remain a LOW readability issue.

## 8. Open findings

| ID | Severity | Location and exact wording | Consequence | Resolution criterion |
|---|---|---|---|---|
| R2-01 | **HIGH** | Section 3.4: “La variante nano fue seleccionada por su equilibrio entre velocidad de inferencia, precisión sobre objetos medianos y huella de memoria compatible con despliegue en hardware de borde.” | This is the comparative efficiency/edge claim that CLAIM-001 and AMENDMENT-06 say was retired. There is no prior comparison across variants, object sizes, memory use, or edge hardware; the single-CPU benchmark cannot establish it. | Replace it with a neutral factual reason (for example, that the nano variant was the chosen model) or provide a prespecified comparative analysis and actual memory/hardware evidence. Add the final disposition to the claim/editorial audits. |
| R2-02 | **HIGH** | Conclusion: “La incorporación futura de información tridimensional (RGB-D) mediante la cámara Intel RealSense D435 y el despliegue edge sobre Raspberry Pi 4 con cuantización INT8 son las extensiones naturales que consolidarían el enfoque dentro del paradigma de Agricultura 4.0 como motor de sostenibilidad alimentaria en Colombia.” | It predicts that two unimplemented, unevaluated extensions would consolidate the approach and make it a driver of national food sustainability. No experiment, causal chain, or cited impact evidence supports that conclusion. | Remove the consolidation/sustainability effect or recast the items strictly as untested future engineering work without an impact claim; map the final claim and evidence. |
| R2-03 | **MEDIUM** | Section 3.7: “La validación sirvió sólo para elegir el checkpoint y el umbral; la prueba se evaluó una sola vez, con ambos fijados.” REVIEW-04: “El test nuevo tiene 117 imágenes…” | These isolated statements can still imply a newly pristine holdout, despite historical exposure, contrary to the frozen reporting rule and the original B-05 criterion. | In Section 3.7 state that both reported test evaluations are internal retrospective evaluations; in REVIEW-04 replace “test nuevo” with “nueva partición interna retrospectiva” or equivalent. Keep the no-test-selection statement. |
| R2-04 | **MEDIUM** | `reports/editorial_audit.md`: “El registro `manuscript/numbers.json` contiene 124 cifras del texto y de las leyendas: … 5.1, 6.1, la conclusión…” | A local typo in at least 19 displayed interval endpoints in those named sections would not fail the checker, yet the documented exclusions do not disclose that partial within-paragraph coverage. The `no issues` report can still be mistaken for comprehensive coverage. | Register every displayed material result at every repeated anchor, or state exactly that only selected point estimates/one endpoint are checked in 5.1, 6.1, and 7 and list the unchecked repetitions. Regenerate the consistency report. |
| R2-05 | **MEDIUM** | Matrix: CLAIM-035 `SUPPORTED`; CLAIM-049 `RETIRED`; CLAIM-014 `QUALIFIED`. | The status semantics are false for a corrected `0,832 → 0,831`, a two-part claim whose second half remains, and leakage wording that is not qualified at every final occurrence. The matrix also omits R2-01 and R2-02. | Mark CLAIM-035 `CORRECTED`; split or relabel CLAIM-049; reconcile CLAIM-014 with every final occurrence; add dispositions for the two current material claims; recheck all 50 rows and update the editorial audit counts. |
| R2-06 | **MEDIUM** | Abstract and conclusion: “partición limpia de MangoDHDS”; Section 4.2.1: “El conjunto limpio”. | This shorthand can be read as an absolute leakage-cleanliness claim even though the test contains 11 redundant files and the protocol permits only “no cross-partition contamination detected under the specified procedure.” | Use the identifier `MangoDHDS_clean` as a name and/or repeat the protocol-bounded wording; do not use an unqualified cleanliness adjective as a scientific conclusion. Synchronize CLAIM-014 and the letter if wording changes. |
| R2-07 | **MEDIUM** | Response header: “Ninguna acción pendiente se describe como hecha.” Manuscript: “Se publican el protocolo de auditoría y su código” / “su código se publican”. | The letter asserts there is no such pending-as-done action while CLAIM-042 records exactly one. The pending claim is isolated elsewhere but not consistently in the submission letter. | Publish and cite the repository, or soften both manuscript sentences; until then, make the letter header expressly identify CLAIM-042 as the sole pending author action. |
| R2-08 | **LOW** | PDF Figures 5 and 7. | Figure 5’s lower-right overlay is clipped at the right boundary, and Figure 7’s densest panel has very small labels. Underlying samples and metrics remain valid. | Regenerate or relayout until all overlays are inside their panels and readable at normal PDF scale, then update the page review. |
| R2-09 | **LOW** | PDF metadata: `/Author = Luis Camacho`; listed authors are Daniela Villa Bastidas, Jorge Solano Romero, and Marvin Molina-Cárdenas. | The submission PDF carries incorrect author metadata even though the visible author line is correct. | Set the DOCX/PDF author metadata to the listed authors or remove it, rerender, and verify the final PDF metadata and hash. |

## 9. What remains before submission, in order

1. **Resolve R2-01 through R2-07 and decide CLAIM-042 before another final render.**  
   **Done when:** a semantic scan finds no unsupported efficiency, edge-compatibility, causal-impact, temporal, or unqualified leakage claim; every test summary says internal retrospective; the matrix and letter agree; and CLAIM-042 is either fulfilled with a citation or softened everywhere.

2. **Complete numerical and claim traceability on the exact candidate.**  
   **Done when:** every material repeated result is registered or explicitly listed as outside scope; the consistency report passes; all 50 claim dispositions and locations are true; the two new material claims have explicit dispositions; and `reports/editorial_audit.md` states the exact coverage.

3. **Regenerate the DOCX/PDF pair and repeat the full render review.**  
   **Done when:** hashes identify the same final pair; all 16 (or the new stable count of) pages are inspected; R2-08 and R2-09 are closed or explicitly accepted as LOW; figures remain at adequate resolution; numbering, cross-references, references, terminology, and decimal punctuation pass.

4. **Synchronize the response letter to that final render.**  
   **Done when:** the literal placeholder search returns zero; the header states the real CLAIM-042 status; every result equals its artifact/manuscript; every location points to the final section/page; and REVIEW-10 and REVIEW-15 still describe what the final PDF shows.

5. **Rerun TASK-09 gates after all text/render changes.**  
   **Done when:** document checks, citation checks, source-versus-embedded figure hashes, number/claim audits, and the page checklist all pass against the same DOCX/PDF hashes.

6. **Complete TASK-10 on the post-fix package.** Existing portability, legacy, protocol, and reproduction records are useful but predate this Round 2 closure and cannot be the final gate.  
   **Done when:** the complete test suite, freeze/amendment/access audit, legacy integrity, portability, protocol compliance, and clean-environment reproduction all pass against the final package; protocol compliance no longer calls AMENDMENT-06/07 satisfied while R2-01/R2-06 are open.

7. **Obtain the required fresh final adversarial review.** `reports/final_adversarial_review.md` is currently absent.  
   **Done when:** the independent reviewer inspects the final candidate and reports zero open HIGH and zero open MEDIUM; any fixes trigger the affected checks again.

8. **Replace the stale first-phase final report and finish the delivery record.** `docs/final_validation_report.md` still says no experiments or manuscript edits were executed; README finalization is also pending.  
   **Done when:** the final validation report, README, gate matrix, response letter, package inventory, and hashes all describe the final candidate and no later file change invalidates them.

## 10. Finding count and submission gate

| Severity | Open |
|---|---:|
| HIGH | **2** |
| MEDIUM | **5** |
| LOW | 2 |

**Submission gate:** **FAIL.** The results themselves remain numerically valid, but the manuscript and response letter are not submission-ready, even when CLAIM-042 and unfinished TASK-10 are set aside, until HIGH = 0 and MEDIUM = 0.
