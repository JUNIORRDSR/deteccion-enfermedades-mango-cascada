# Auditoría final de texto (fase 1)

**Fecha:** 2026-09-29 · **Candidato auditado:** `manuscript/source/Articulo_Mango_ALBUS_revision.docx` tras la pasada 2f (SHA-256 `d177dd9d2d944b021f3977ecf37271e235f7fcdfd2af8a48d2ce0f0af0397b1b`), la carta `docs/response_to_reviewers.md` y los documentos que describen el estado actual.

**Alcance:** limpieza de texto, atribución IA/humano y consistencia. No se cambia el experimento, los modelos, las particiones ni ningún número validado.

## Fuente de verdad sobre la revisión visual

- **Adjudicación asistida por IA (documentada).**
  - `data/audits/model1/blinding_log.json` y `supplementary_blinding_log.json` nombran a los revisores A, B y C como instancias de Claude (Opus, Sonnet, Haiku y una segunda de Opus).
  - Los mismos registros guardan los controles: los dos agentes de la primera ronda no reconocieron ninguno de los 2 controles positivos.
  - `adjudications.csv` y `supplementary_adjudications.csv` muestran los desacuerdos: 14 de 35 unidades y 38 de 47 pares.
  - La partición congelada (`data/manifests/model1_clean_manifest.csv`, 2026-09-23) se construyó con las decisiones registradas en `adjudication_resolution.csv` y `supplementary_resolution.csv`.
- **Revisión manual posterior (declarada por los autores el 2026-09-29).**
  - Una integrante del equipo revisó manualmente los candidatos.
  - No existe en el repositorio ni en la carpeta del proyecto un registro caso a caso de esa revisión. No hay decisiones por candidato, fecha, alcance ni acuerdo con la adjudicación asistida. Una búsqueda de archivos y de términos lo confirmó.
  - Por eso el texto la describe sin resultados ni protocolo, y se registra como declaración de los autores (DECISION-040).

## Tabla de hallazgos

Categorías de la última columna:

- **B:** afirmación desactualizada.
- **C:** trazabilidad histórica, que no se modifica.
- **D:** redacción que se mejora.

| ID | Archivo/sección | Texto actual | Problema | Fuente de verdad | Cambio propuesto | Categoría |
|---|---|---|---|---|---|---|
| TC-01 | DOCX, 3.3.1 | «…y revisión visual de cada candidato por dos agentes de IA en instancias separadas (Claude Opus y Claude Sonnet), con un tercero (Claude Haiku)…; ese ciego se impuso por instrucción, no por control de acceso, y ninguna de estas decisiones la revisó una persona.» | AI_ATTRIBUTION, HUMAN_REVIEW: la última cláusula ya no es cierta | Registros de cegamiento; declaración de los autores | Se conservan los agentes, el ciego por instrucción y la fiabilidad limitada. Se retira «ninguna… la revisó una persona». Se añade que después una integrante del equipo revisó manualmente los candidatos y que los grupos proceden de las decisiones registradas de la adjudicación | B + D |
| TC-02 | DOCX, 3.3.1 | «La fiabilidad de esta adjudicación es limitada… Como esas decisiones definen los grupos, la partición y los intervalos heredan su error.» | SCIENTIFIC_WORDING: los hechos son correctos, pero el tono es defensivo | Registros de cegamiento | Mismos hechos y cifras (2 controles, 14 de 35, 38 de 47, 7), en redacción descriptiva | D |
| TC-03 | DOCX, 6.1 | La limitación de la adjudicación sólo aparece en 3.3.1 | CONSISTENCY: la sección de limitaciones no la menciona | 3.3.1 | Una frase en 6.1 que remite a 3.3.1 | D |
| TC-04 | Carta, REVIEW-01, punto 3 | «…y ninguna decisión la revisó una persona.» | HUMAN_REVIEW desactualizado | Declaración de los autores | Primero adjudicación asistida por IA; después, revisión manual por una integrante del equipo | B |
| TC-05 | Carta, REVIEW-01, límite declarado | «La adjudicación visual la hicieron agentes de IA, sin revisión humana… la re-adjudicación por personas queda como trabajo futuro.» | HUMAN_REVIEW desactualizado | Ídem | Adjudicación asistida por IA con fiabilidad limitada y revisión manual posterior; los grupos proceden de las decisiones registradas | B |
| TC-06 | Carta, REVIEW-01, estado | «RESUELTO PARCIALMENTE: … sin revisión humana.» | STALE_TEXT | Ídem | «RESUELTO, con los límites declarados» | B |
| TC-07 | README, «Uso de IA» | «…la hicieron agentes de IA (Claude) sin revisión humana…» | HUMAN_REVIEW desactualizado | Ídem | Adjudicación asistida por IA y revisión manual posterior, sin registro caso a caso | B |
| TC-08 | `docs/final_validation_report.md` (gates D, H e I; «Revisiones independientes»; «Qué falta») | «sin revisión humana», «RESUELTO PARCIALMENTE (REVIEW-01…)», «Adjudicación humana de las 35 unidades…» | HUMAN_REVIEW, STALE_TEXT | Ídem | Actualizar al estado declarado; el pendiente pasa a registrar la revisión manual y, para cerrar H-01 del todo, una re-adjudicación externa | B |
| TC-09 | `reports/execution/STATE.md` | «la re-adjudicación humana queda como trabajo futuro» | STALE_TEXT | Ídem | Actualizar | B |
| TC-10 | `reports/editorial_audit.md`, sección 7 | H-01: «sin revisión humana… Abierta la re-adjudicación humana» | STALE_TEXT | Ídem | Actualizar la fila y el párrafo final | B |
| TC-11 | `reports/protocol_compliance.json`, AMENDMENT-03 | «human re-adjudication is open» | STALE_TEXT | Ídem | Revisión manual posterior declarada, sin registro caso a caso | B |
| TC-12 | `reports/execution/render_review.md`, página 4 | «…la ausencia de revisión humana…» | STALE_TEXT | Ídem | Se regenera con el render nuevo | B |
| TC-13 | `reports/editorial_claim_audit.csv`, ED-21 | Decisión de la pasada 2f: «sin revisión humana» | Registro de una decisión pasada | Ídem | No se reescribe; se añade ED-25, que la sustituye | C |
| TC-14 | `data/audits/model1/*` (registros de cegamiento, respuestas, adjudicaciones), `reports/execution/task-02-audit-report.md`, `reports/final_adversarial_review.md`, auditorías B, `reports/amendments/*`, `provenance/commands/task09/revise_pass2f.py`, `manuscript/source/edit_log.json`, `docs/research/decision_log.md` | Menciones a reviewer-A/B/C, Claude, «revisores independientes» y «sin revisión humana» | Trazabilidad histórica de lo que ocurrió y de lo que se escribió en cada fecha | — | Sin cambios; `decision_log.md` recibe una entrada nueva (DECISION-040) | C |
| TC-15 | DOCX, 3.6 | «…marca como «Desconocido» un diagnóstico con confianza inferior a 0,4» | SCIENTIFIC_WORDING: la salida del sistema es una clasificación visual, no un diagnóstico | 6.1 (etiquetas visuales de terceros) | «una clasificación» | D |
| TC-16 | DOCX, 4.2.4 | «…no evidencia diagnósticos correctos.» | SCIENTIFIC_WORDING | Ídem | «no demuestra que las clases asignadas sean correctas» | D |
| TC-17 | DOCX, fuente de la Figura 7 | «El diagnóstico fino proviene del Modelo 2…» | SCIENTIFIC_WORDING | Ídem | «La clase de enfermedad la asigna el Modelo 2…» | D |
| TC-18 | DOCX, 5.2 | «los cinco diagnósticos…», «caja y diagnóstico», «nunca recibe diagnóstico», «resulta justificada», «explotar» | SCIENTIFIC_WORDING, EDITORIAL | Ídem | «las cinco clases», «caja y enfermedad», «nunca recibe una clase de enfermedad», «responde a», «usar» | D |
| TC-19 | DOCX, justificación de la cascada (3.1) | «el corpus que permite entrenar localización fiable en campo abierto» | OVERCLAIM: la sensibilidad para Enfermo en prueba es 0,577 | Tabla 5 | «el corpus con cajas en escenas de campo abierto» | D |
| TC-20 | DOCX, 5.4 | «consolidar primero la cascada RGB con métricas estables» | OVERCLAIM: las métricas del detector no son estables entre validación y prueba | 4.1.2 | «consolidar primero la cascada RGB» | D |
| TC-21 | DOCX, resumen | «…costosos o poco accesibles para el productor rural colombiano.» | OVERCLAIM y CONSISTENCY: la Sección 1 ya no sostiene la parte rural | Sección 1 (Venbrux et al., 2023) | «…o de técnicas de laboratorio que requieren equipos y personal especializados» | D |
| TC-22 | DOCX, 2.4 | «El presente trabajo documenta y mitiga uno de tales casos sobre un corpus público de mango», tras la frase de Padilla et al. | STALE_TEXT (el trabajo audita dos corpus) y CONSISTENCY (la referencia queda separada de su antecedente) | 3.3.1 y 3.3.2 | La frase pasa tras la de Kapoor y Narayanan, con «los dos corpus públicos de mango»; la de Padilla se simplifica | D |
| TC-23 | DOCX, 3.3.2 | «reveló una anomalía significativa. Aplicando el hashing perceptual…» | EDITORIAL: «significativa» sugiere una prueba estadística | Tabla 6 | Una sola frase con los mismos números | D |
| TC-24 | DOCX, 3.3.2 | «Una reejecución independiente reproduce exactamente los 76 pares» | AI_ATTRIBUTION: «independiente» sugiere un revisor externo; fue una nueva ejecución del código | `reports/execution/task-02-audit-report.md` | «Una nueva ejecución del detector de duplicados en esta revisión reproduce…» | D |
| TC-25 | DOCX, Sección 1 | «…han emergido en la última década como herramientas con alto potencial diagnóstico…»; «Adicionalmente, en Kapoor y Narayanan (2023) se documenta…» | EDITORIAL: frases infladas y pasivas | Citas existentes | Redacción directa, sin cambiar las citas | D |
| TC-26 | DOCX, 3.5 | «La razón de emplear la modalidad clasificación —y no detección— se justifica por…» | EDITORIAL: redundante | — | «Se usa la modalidad de clasificación, y no la de detección, por…» | D |
| TC-27 | DOCX, 6.2 | «Será la métrica honesta de desempeño en producción.» | EDITORIAL | — | «Con ese conjunto podrá medirse el desempeño en condiciones de producción.» | D |
| TC-28 | DOCX, Tabla 8 | «Cajas sintéticas en MangoDHDS» | CONSISTENCY con 3.5 y 6.1 («etiquetas de imagen completa») | 3.5 | «Etiquetas de imagen completa en MangoDHDS» | D |
| TC-30 | Figura 1, flecha del Modelo 2 (hallado en la fase 3, al revisar el render) | «diagnóstico» | SCIENTIFIC_WORDING, igual que TC-15 a TC-18 | Ídem | «clase»; `figures.py` regenera la figura con el mismo tamaño y la Figura 2 queda idéntica byte a byte | D |
| TC-29 | DOCX, agradecimientos o declaración de uso de IA | El manuscrito declara la IA sólo en la adjudicación (3.3.1); el README declara además el uso de asistentes de IA en la ejecución, el código y la edición | AI_ATTRIBUTION: posible requisito de la revista | Política de ALBUS, no verificada | **No se aplica.** La declaración general de uso de IA es una afirmación de los autores y depende de la política de la revista; queda propuesta en el informe final | Decisión de los autores |

## Revisado y conservado sin cambios

- Las cifras de M1 y M2, las matrices, los intervalos, la latencia y los recuentos de duplicados. `reports/manuscript_consistency.json` las recalcula todas: 165 cifras.
- Las limitaciones de 3.3.1, 4.1.2, 4.2.1, 5.2 y 6.1.
- «No se afirma que el conjunto esté libre de fuga» (3.3.1): es la negación revisada del lenguaje de fuga, ED-17.
- «Estas cifras no son comparables con las de la versión anterior del manuscrito» (5.1) y «la versión anterior del manuscrito ya informó resultados sobre esta partición» (4.2.3). Distinguen resultados históricos de actuales y la carta los necesita.
- El título, por decisión de los autores del 2026-09-28.
- «inspección visual humana» (Sección 1) se refiere al diagnóstico convencional, no a esta auditoría.
