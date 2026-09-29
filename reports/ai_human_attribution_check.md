# Control de atribución IA/humano

**Generado por:** `provenance/commands/task09/attribution_check.py` sobre el manuscrito tras la pasada 2g y los documentos que describen el estado actual.

**Términos buscados:** IA, inteligencia artificial, Claude, agente/agentes, humano/humana, revisión manual o «manualmente», revisión visual y adjudicación. En los documentos en inglés también se buscan AI y human.

**Apariciones en documentos actuales:** 72. **Sin justificación:** 0.

## Apariciones en el manuscrito y en los documentos actuales

| Archivo | Sección | Frase | Justificación |
|---|---|---|---|
| manuscrito (DOCX) | 1. Introducción | El diagnóstico convencional de estas patologías se basa en inspección visual humana o, en su defecto, en técnicas de laboratorio como la reacción en cadena de la polimerasa (PCR) o la microscopía (Khakimov et al., 2022; | Diagnóstico convencional por personas; no se refiere a esta auditoría. |
| manuscrito (DOCX) | 3.3.1 Detector binario (Modelo 1) | y revisión visual de cada candidato. | Nombra el criterio de la auditoría; su autoría está en la misma frase o en la siguiente. |
| manuscrito (DOCX) | 3.3.1 Detector binario (Modelo 1) | La primera adjudicación se hizo con apoyo de agentes de IA: | Uso real de IA en la adjudicación inicial: `data/audits/model1/blinding_log.json` y `supplementary_blinding_log.json` nombran a los agentes. |
| manuscrito (DOCX) | 3.3.1 Detector binario (Modelo 1) | dos instancias separadas (Claude Opus y Claude Sonnet) juzgaron cada candidato sin ver la partición, la clase ni el nombre de archivo, y una tercera (Claude Haiku) resolvió los desacuerdos; | Uso real de IA en la adjudicación inicial: `data/audits/model1/blinding_log.json` y `supplementary_blinding_log.json` nombran a los agentes. |
| manuscrito (DOCX) | 3.3.1 Detector binario (Modelo 1) | Dos generadores adicionales, pHash invariante a la rotación y similitud de embedding ImageNet con un horizonte fijado antes de ver los resultados, propusieron 47 pares más, adjudicados con el mismo protocolo (el tercer agente fue otra instancia de Claude Opus): | Uso real de IA en la adjudicación inicial: `data/audits/model1/blinding_log.json` y `supplementary_blinding_log.json` nombran a los agentes. |
| manuscrito (DOCX) | 3.3.1 Detector binario (Modelo 1) | Los agentes mostraron una fiabilidad limitada: | Uso real de IA en la adjudicación inicial: `data/audits/model1/blinding_log.json` y `supplementary_blinding_log.json` nombran a los agentes. |
| manuscrito (DOCX) | 3.3.1 Detector binario (Modelo 1) | Posteriormente, una integrante del equipo revisó manualmente los candidatos. | Revisión manual posterior, declarada por los autores (DECISION-040). No tiene registro caso a caso, así que no se le atribuyen resultados ni protocolo. |
| manuscrito (DOCX) | 3.3.1 Detector binario (Modelo 1) | Los grupos de la partición proceden de las decisiones registradas de la adjudicación, de modo que la partición y los intervalos dependen de ellas. | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| manuscrito (DOCX) | 3.3.1 Detector binario (Modelo 1) | Cada grupo une duplicados, casi duplicados y relaciones adjudicadas, y el montaje completo forma un único grupo, porque ninguna fuente verificable permite separar sus fotografías. | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| manuscrito (DOCX) | 4.2.1 Auditoría de fuga sobre el corpus público | se conservaron las dos etiquetas sin adjudicarlas. | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| manuscrito (DOCX) | 5.2 Sobre la cascada como decisión de diseño | Calcularla exige verdad de terreno conjunta, con caja y enfermedad adjudicadas para los mismos frutos, que ninguno de los dos conjuntos tiene. | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| manuscrito (DOCX) | 6.1 Limitaciones identificadas | La agrupación del corpus del detector depende de una adjudicación visual apoyada inicialmente en agentes de IA de fiabilidad limitada y revisada después por una integrante del equipo (Sección 3.3.1). | Revisión manual posterior, declarada por los autores (DECISION-040). No tiene registro caso a caso, así que no se le atribuyen resultados ni protocolo. |
| docs/response_to_reviewers.md | REVIEW-01 — Auditoría de duplicados en mangoUnhealty v2 | Revisión visual de cada candidato, primero con apoyo de agentes de IA: | Uso real de IA en la adjudicación inicial: `data/audits/model1/blinding_log.json` y `supplementary_blinding_log.json` nombran a los agentes. |
| docs/response_to_reviewers.md | REVIEW-01 — Auditoría de duplicados en mangoUnhealty v2 | dos instancias separadas (Claude Opus y Claude Sonnet) y una tercera (Claude Haiku) para los desacuerdos, con un ciego impuesto por instrucción y no por control de acceso. | Uso real de IA en la adjudicación inicial: `data/audits/model1/blinding_log.json` y `supplementary_blinding_log.json` nombran a los agentes. |
| docs/response_to_reviewers.md | REVIEW-01 — Auditoría de duplicados en mangoUnhealty v2 | Posteriormente, una integrante del equipo revisó manualmente los candidatos. | Revisión manual posterior, declarada por los autores (DECISION-040). No tiene registro caso a caso, así que no se le atribuyen resultados ni protocolo. |
| docs/response_to_reviewers.md | REVIEW-01 — Auditoría de duplicados en mangoUnhealty v2 | Seis cruzan de train a validation, y los agentes confirmaron cinco como casi duplicados. | Uso real de IA en la adjudicación inicial: `data/audits/model1/blinding_log.json` y `supplementary_blinding_log.json` nombran a los agentes. |
| docs/response_to_reviewers.md | REVIEW-01 — Auditoría de duplicados en mangoUnhealty v2 | Los 6 que llegan al test lo son para ambos agentes, así que el umbral de 5 deja pasar contaminación. | Uso real de IA en la adjudicación inicial: `data/audits/model1/blinding_log.json` y `supplementary_blinding_log.json` nombran a los agentes. |
| docs/response_to_reviewers.md | REVIEW-01 — Auditoría de duplicados en mangoUnhealty v2 | Sus 47 pares se adjudicaron con el mismo protocolo: | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| docs/response_to_reviewers.md | REVIEW-01 — Auditoría de duplicados en mangoUnhealty v2 | dos agentes en instancias separadas y un tercero, otra instancia de Claude Opus, para los 38 desacuerdos. | Uso real de IA en la adjudicación inicial: `data/audits/model1/blinding_log.json` y `supplementary_blinding_log.json` nombran a los agentes. |
| docs/response_to_reviewers.md | REVIEW-01 — Auditoría de duplicados en mangoUnhealty v2 | Los seis controles de consistencia, que comparan con decisiones anteriores y no con una verdad biológica, salieron bien para ambos agentes. | Uso real de IA en la adjudicación inicial: `data/audits/model1/blinding_log.json` y `supplementary_blinding_log.json` nombran a los agentes. |
| docs/response_to_reviewers.md | REVIEW-01 — Auditoría de duplicados en mangoUnhealty v2 | `data/audits/model1/` (pares candidatos, clusters, adjudicaciones, resolución y registro de cegamiento); | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| docs/response_to_reviewers.md | REVIEW-01 — Auditoría de duplicados en mangoUnhealty v2 | Con SHA-256, pHash bajo el umbral, revisión visual de candidatos y agrupamiento conservador por origen no se detecta contaminación entre conjuntos. | Nombra el criterio de la auditoría; su autoría está en la misma frase o en la siguiente. |
| docs/response_to_reviewers.md | REVIEW-01 — Auditoría de duplicados en mangoUnhealty v2 | La adjudicación visual se apoyó primero en agentes de IA de fiabilidad limitada (controles positivos fallidos y desacuerdos frecuentes) y después la revisó manualmente una integrante del equipo; | Revisión manual posterior, declarada por los autores (DECISION-040). No tiene registro caso a caso, así que no se le atribuyen resultados ni protocolo. |
| docs/response_to_reviewers.md | REVIEW-01 — Auditoría de duplicados en mangoUnhealty v2 | los grupos de la partición proceden de las decisiones registradas de la adjudicación. | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| docs/response_to_reviewers.md | REVIEW-02 — Partición por secuencia o grupo de origen | duplicados, casi duplicados, relaciones adjudicadas y el montaje completo como un único grupo, porque no hay una fuente verificable que permita separar sus fotografías. | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| docs/response_to_reviewers.md | REVIEW-02 — Partición por secuencia o grupo de origen | Consideramos una alternativa que separaba el montaje por identidad visual y la retiramos tras una revisión metodológica hecha por un agente de IA distinto del que ejecutó el trabajo. | Revisión metodológica hecha por un modelo de IA distinto del que ejecutó el trabajo, y así se declara. |
| docs/response_to_reviewers.md | REVIEW-12 y REVIEW-13 — Errores acumulados y métrica de la cascada completa | cada fruto enfermo con su caja y su diagnóstico específico adjudicado. | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| README.md | Contenido | \| `data/manifests/`, `data/audits/` \| Manifiestos congelados con el SHA-256 de cada imagen, pares candidatos, adjudicaciones y grupos \| | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| README.md | Uso de IA | ## Uso de IA | Título de la sección del README que declara el uso de IA. |
| README.md | Uso de IA | La adjudicación visual de la auditoría de fuga del detector se hizo primero con apoyo de agentes de IA (Claude); | Uso real de IA en la adjudicación inicial: `data/audits/model1/blinding_log.json` y `supplementary_blinding_log.json` nombran a los agentes. |
| README.md | Uso de IA | Después, una integrante del equipo revisó manualmente los candidatos (Sección 3.3.1 del manuscrito). | Revisión manual posterior, declarada por los autores (DECISION-040). No tiene registro caso a caso, así que no se le atribuyen resultados ni protocolo. |
| README.md | Uso de IA | Esa revisión manual no tiene un registro caso a caso en el repositorio (DECISION-040 en `docs/research/decision_log.md`). | Revisión manual posterior, declarada por los autores (DECISION-040). No tiene registro caso a caso, así que no se le atribuyen resultados ni protocolo. |
| README.md | Uso de IA | La ejecución de la revisión se hizo con asistentes de IA de programación, bajo la dirección de los autores. | Declaración general del uso de asistentes de IA en la ejecución de la revisión. |
| docs/final_validation_report.md | Informe final de validación — revisión mayor ALBUS26-116 | Deja abiertos 4 HIGH y 2 MEDIUM que ningún cambio de texto resuelve, porque exigen datos nuevos o una re-adjudicación documentada. | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| docs/final_validation_report.md | Gates | - la adjudicación visual se hizo primero con apoyo de agentes de IA, de fiabilidad limitada, y después la revisó manualmente una integrante del equipo, sin registro caso a caso (DECISION-040); | Revisión manual posterior, declarada por los autores (DECISION-040). No tiene registro caso a caso, así que no se le atribuyen resultados ni protocolo. |
| docs/final_validation_report.md | Gates | Quedan abiertos los HIGH H-01 (la revisión manual posterior no tiene registro caso a caso ni fue una re-adjudicación externa con ciego efectivo), H-03, H-04 y H-05, y los MEDIUM M-02 y M-03 en su parte de adjudicación y reentrenamiento (`reports/editorial_audit.md`, sección 7). | Revisión manual posterior, declarada por los autores (DECISION-040). No tiene registro caso a caso, así que no se le atribuyen resultados ni protocolo. |
| docs/final_validation_report.md | Revisiones independientes | Todas las revisiones independientes de esta rama las hicieron modelos de IA en sesiones separadas de la que ejecutó el trabajo, no personas: | Las revisiones independientes de la rama las hicieron modelos de IA, y así se declara. |
| docs/final_validation_report.md | Revisiones independientes | La adjudicación visual de la auditoría de fuga del detector se hizo primero con apoyo de agentes de IA y después la revisó manualmente una integrante del equipo, como declara la Sección 3.3.1 del manuscrito. | Revisión manual posterior, declarada por los autores (DECISION-040). No tiene registro caso a caso, así que no se le atribuyen resultados ni protocolo. |
| docs/final_validation_report.md | Publicación | Los autores publicaron el 2026-09-29 la release v1.0.0, con el estado de la pasada 2f, cuyo manuscrito aún no describe la revisión manual posterior de la adjudicación. | Revisión manual posterior, declarada por los autores (DECISION-040). No tiene registro caso a caso, así que no se le atribuyen resultados ni protocolo. |
| docs/final_validation_report.md | Qué falta para cerrar la revisión según el plan | **Registro de la revisión manual** de la auditoría del detector: | Revisión manual posterior, declarada por los autores (DECISION-040). No tiene registro caso a caso, así que no se le atribuyen resultados ni protocolo. |
| docs/final_validation_report.md | Qué falta para cerrar la revisión según el plan | las decisiones por candidato y cualquier desacuerdo con la adjudicación asistida por IA. | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| docs/final_validation_report.md | Qué falta para cerrar la revisión según el plan | Para cerrar H-01 del todo, una re-adjudicación de las 35 unidades y los 47 pares por personas ajenas al entrenamiento y con un ciego efectivo. | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| docs/final_validation_report.md | Qué falta para cerrar la revisión según el plan | **Un conjunto externo**, con caja y diagnóstico adjudicados para los mismos frutos y confirmación fitopatológica. | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| docs/final_validation_report.md | Qué falta para cerrar la revisión según el plan | **Adjudicación con experto** del cluster de entrenamiento del Modelo 2 con dos etiquetas, y reentrenamiento con muestreo por grupos. | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| reports/execution/STATE.md | Revisiones | Quedan abiertos 4 HIGH y 2 MEDIUM que exigen datos nuevos o una re-adjudicación documentada (`reports/editorial_audit.md`, sección 7). | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| reports/execution/STATE.md | Decisiones de los autores del 2026-09-28 | - Declarar que la adjudicación visual se apoyó primero en agentes de IA. | Uso real de IA en la adjudicación inicial: `data/audits/model1/blinding_log.json` y `supplementary_blinding_log.json` nombran a los agentes. |
| reports/execution/STATE.md | Decisiones de los autores del 2026-09-28 | El 2026-09-29 los autores añadieron que después una integrante del equipo revisó manualmente los candidatos (DECISION-040, sin registro caso a caso); | Revisión manual posterior, declarada por los autores (DECISION-040). No tiene registro caso a caso, así que no se le atribuyen resultados ni protocolo. |
| reports/editorial_audit.md | 1. Trazabilidad de las cifras | el primero de 3.3.1, con los recuentos de la adjudicación de `data/audits/model1/blinding_log.json`; | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| reports/editorial_audit.md | 1. Trazabilidad de las cifras | - en 3.3.1, los 38 desacuerdos entre los 47 pares suplementarios y los 7 sobre si existía relación (`data/audits/model1/supplementary_adjudications.csv`); | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| reports/editorial_audit.md | 2. Lenguaje | Cubren eficiencia, temporalidad, prevalencia, fuga, latencia, impacto, la adjudicación por IA, la cronología de la partición y dos afirmaciones de la literatura. | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| reports/editorial_audit.md | 7. Revisión adversarial final | declarar ya la adjudicación por IA, mantener el título y publicar el repositorio con los pesos bajo AGPL-3.0. | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| reports/editorial_audit.md | 7. Revisión adversarial final | Lo que exige datos nuevos o una re-adjudicación documentada queda abierto y declarado. | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| reports/editorial_audit.md | 7. Revisión adversarial final | \| H-01 adjudicación por agentes de IA presentada como revisores independientes \| HIGH \| Declarada en 3.3.1 y en REVIEW-01: | Uso real de IA en la adjudicación inicial: `data/audits/model1/blinding_log.json` y `supplementary_blinding_log.json` nombran a los agentes. |
| reports/editorial_audit.md | 7. Revisión adversarial final | La pasada 2g añade la revisión manual posterior de una integrante del equipo, declarada por los autores sin registro caso a caso (ED-25, DECISION-040). | Revisión manual posterior, declarada por los autores (DECISION-040). No tiene registro caso a caso, así que no se le atribuyen resultados ni protocolo. |
| reports/editorial_audit.md | 7. Revisión adversarial final | Sigue abierta la re-adjudicación externa con ciego efectivo que pide el revisor \| | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| reports/editorial_audit.md | 7. Revisión adversarial final | Abierta la adjudicación con experto \| | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| reports/editorial_audit.md | 7. Revisión adversarial final | Quedan abiertos cuatro HIGH, que dependen de datos nuevos o de una re-adjudicación documentada (H-01 en su parte de re-adjudicación externa, H-03, H-04 y H-05), y dos MEDIUM en su parte de adjudicación y reentrenamiento (M-02 y M-03). | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| reports/execution/render_review.md | Revisión del render del manuscrito | \| 4 \| 3.2.1 a 3.3.2 \| 3.3.1 describe primero la adjudicación asistida por agentes de IA, con su ciego por instrucción y su fiabilidad limitada, y después la revisión manual de una integrante del equipo. | Revisión manual posterior, declarada por los autores (DECISION-040). No tiene registro caso a caso, así que no se le atribuyen resultados ni protocolo. |
| reports/execution/render_review.md | Revisión del render del manuscrito | \| 13 \| 5, 5.1 a 5.4, 6 e inicio de 6.1 \| 5.2 habla de «las cinco clases» y de «caja y enfermedad adjudicadas». | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| reports/execution/render_review.md | Revisión del render del manuscrito | \| 14 \| Fin de 6.1, Tabla 8 y 6.2 \| 6.1 añade la limitación de la adjudicación y remite a 3.3.1. | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| reports/protocol_compliance.json | AMENDMENT-03 | "data/audits/model1/adjudications.csv", "data/audits/model1/adjudication_resolution.csv", | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| reports/protocol_compliance.json | AMENDMENT-03 | "data/audits/model1/supplementary_adjudications.csv", "reports/execution/task-02-audit-report.md"], | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| reports/protocol_compliance.json | AMENDMENT-03 | ["the A, B and C passes were Claude agents in separate instances, not human reviewers; | Uso real de IA en la adjudicación inicial: `data/audits/model1/blinding_log.json` y `supplementary_blinding_log.json` nombran a los agentes. |
| reports/protocol_compliance.json | AMENDMENT-03 | there is no case-by-case record of that review and the frozen groups come from the recorded AI-assisted adjudication", | Revisión manual posterior, declarada por los autores (DECISION-040). No tiene registro caso a caso, así que no se le atribuyen resultados ni protocolo. |
| reports/protocol_compliance.json | AMENDMENT-03 | "an external re-adjudication with effective blinding is still open (reports/final_adversarial_review.md, H-01)"] | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |
| reports/editorial_claim_audit.csv | ED-21 | ED-21 Sección 3.3.1 revisores independientes revisión visual ciega de cada candidato por dos revisores independientes, con un tercero en caso de desacuerdo OWN data/audits/model1/blinding_log.json y supplementary_blinding_log.json: | Registro de la decisión de la pasada 2f; ED-25 la sustituye y se conserva como historia. |
| reports/editorial_claim_audit.csv | ED-21 | los revisores fueron agentes Claude; | Registro de la decisión de la pasada 2f; ED-25 la sustituye y se conserva como historia. |
| reports/editorial_claim_audit.csv | ED-21 | agentes de IA nombrados, ciego por instrucción, sin revisión humana, controles fallidos y desacuerdos declarados REVIEW-01 | Registro de la decisión de la pasada 2f; ED-25 la sustituye y se conserva como historia. |
| reports/editorial_claim_audit.csv | ED-25 | carta REVIEW-01 sin revisión humana ninguna de estas decisiones la revisó una persona OWN Declaración de los autores del 2026-09-29 (DECISION-040): | Cita el texto antiguo que la decisión ED-25 sustituye. |
| reports/editorial_claim_audit.csv | ED-25 | una integrante del equipo revisó manualmente los candidatos después de la adjudicación asistida por IA; | Revisión manual posterior, declarada por los autores (DECISION-040). No tiene registro caso a caso, así que no se le atribuyen resultados ni protocolo. |
| reports/editorial_claim_audit.csv | ED-25 | adjudicación inicial asistida por agentes de IA y revisión manual posterior por una integrante del equipo; | Revisión manual posterior, declarada por los autores (DECISION-040). No tiene registro caso a caso, así que no se le atribuyen resultados ni protocolo. |
| reports/editorial_claim_audit.csv | ED-25 | los grupos proceden de las decisiones registradas de la adjudicación REVIEW-01 | Decisión sobre candidatos o etiquetas; quién adjudicó se declara en 3.3.1 y en REVIEW-01. |

## Registros históricos (no se modifican)

Estos archivos registran lo que ocurrió en cada fecha: quién adjudicó, qué decía el texto en cada pasada y qué señalaron las revisiones. Corregirlos para que coincidan con la descripción actual falsearía la historia. La descripción actual está en el manuscrito, la carta y DECISION-040.

| Archivo | Apariciones |
|---|---:|
| `data/audits/model1/adjudication_resolution.csv` | 29 |
| `data/audits/model1/adjudications.csv` | 107 |
| `data/audits/model1/blinding_log.json` | 6 |
| `data/audits/model1/candidate_pairs.csv` | 54 |
| `data/audits/model1/embedding_candidates.csv` | 40 |
| `data/audits/model1/rotation_candidates.csv` | 7 |
| `data/audits/model1/supplementary_adjudications.csv` | 161 |
| `data/audits/model1/supplementary_blinding_log.json` | 6 |
| `data/audits/model1/supplementary_packets/a/Q-18834d4a32.png` | 22 |
| `data/audits/model1/supplementary_packets/a/Q-2741318ce1.png` | 5 |
| `data/audits/model1/supplementary_packets/a/Q-2e146be0ef.png` | 17 |
| `data/audits/model1/supplementary_packets/a/Q-36376b2fb3.png` | 9 |
| `data/audits/model1/supplementary_packets/a/Q-397ccb0854.png` | 16 |
| `data/audits/model1/supplementary_packets/a/Q-398b647a1f.png` | 5 |
| `data/audits/model1/supplementary_packets/a/Q-3aa756b6ee.png` | 5 |
| `data/audits/model1/supplementary_packets/a/Q-3cbacbd917.png` | 29 |
| `data/audits/model1/supplementary_packets/a/Q-3dac37c801.png` | 5 |
| `data/audits/model1/supplementary_packets/a/Q-43c5055635.png` | 7 |
| `data/audits/model1/supplementary_packets/a/Q-44531a45cd.png` | 9 |
| `data/audits/model1/supplementary_packets/a/Q-446a406aa6.png` | 2 |
| `data/audits/model1/supplementary_packets/a/Q-45d90e3a3c.png` | 11 |
| `data/audits/model1/supplementary_packets/a/Q-48014bb4bc.png` | 11 |
| `data/audits/model1/supplementary_packets/a/Q-4d5f5a8a54.png` | 6 |
| `data/audits/model1/supplementary_packets/a/Q-4f065e0e41.png` | 14 |
| `data/audits/model1/supplementary_packets/a/Q-5209ad1750.png` | 6 |
| `data/audits/model1/supplementary_packets/a/Q-54285e62dc.png` | 3 |
| `data/audits/model1/supplementary_packets/a/Q-56e1815809.png` | 9 |
| `data/audits/model1/supplementary_packets/a/Q-5b8343b2c6.png` | 6 |
| `data/audits/model1/supplementary_packets/a/Q-5d1bb04703.png` | 5 |
| `data/audits/model1/supplementary_packets/a/Q-5ee715d969.png` | 13 |
| `data/audits/model1/supplementary_packets/a/Q-61bea59cd7.png` | 18 |
| `data/audits/model1/supplementary_packets/a/Q-6894111bc5.png` | 6 |
| `data/audits/model1/supplementary_packets/a/Q-6b5c957f60.png` | 12 |
| `data/audits/model1/supplementary_packets/a/Q-7613c2c185.png` | 43 |
| `data/audits/model1/supplementary_packets/a/Q-7b85feb20b.png` | 10 |
| `data/audits/model1/supplementary_packets/a/Q-7d27f686e8.png` | 53 |
| `data/audits/model1/supplementary_packets/a/Q-7f0d5c3136.png` | 7 |
| `data/audits/model1/supplementary_packets/a/Q-8132faceca.png` | 9 |
| `data/audits/model1/supplementary_packets/a/Q-867f6f5f6b.png` | 7 |
| `data/audits/model1/supplementary_packets/a/Q-86f2616362.png` | 8 |
| `data/audits/model1/supplementary_packets/a/Q-8a0fb6a51c.png` | 12 |
| `data/audits/model1/supplementary_packets/a/Q-9690c79165.png` | 15 |
| `data/audits/model1/supplementary_packets/a/Q-96b31e25de.png` | 13 |
| `data/audits/model1/supplementary_packets/a/Q-9cf69beab0.png` | 2 |
| `data/audits/model1/supplementary_packets/a/Q-9d88c91220.png` | 10 |
| `data/audits/model1/supplementary_packets/a/Q-a880206883.png` | 7 |
| `data/audits/model1/supplementary_packets/a/Q-aa16632f5f.png` | 5 |
| `data/audits/model1/supplementary_packets/a/Q-aa6fdcc39d.png` | 3 |
| `data/audits/model1/supplementary_packets/a/Q-aab252e6e0.png` | 25 |
| `data/audits/model1/supplementary_packets/a/Q-adef5d1ddc.png` | 6 |
| `data/audits/model1/supplementary_packets/a/Q-b1338de687.png` | 8 |
| `data/audits/model1/supplementary_packets/a/Q-b87f9617d1.png` | 2 |
| `data/audits/model1/supplementary_packets/a/Q-d7902f7f35.png` | 19 |
| `data/audits/model1/supplementary_packets/a/Q-d921a2ef78.png` | 13 |
| `data/audits/model1/supplementary_packets/a/Q-dd3776b341.png` | 11 |
| `data/audits/model1/supplementary_packets/a/Q-e3649651d0.png` | 7 |
| `data/audits/model1/supplementary_packets/a/Q-ec844a0321.png` | 9 |
| `data/audits/model1/supplementary_packets/a/Q-eeed15c1a3.png` | 4 |
| `data/audits/model1/supplementary_packets/a/Q-f6b9fdad1f.png` | 18 |
| `data/audits/model1/supplementary_packets/a/Q-fa2fe27239.png` | 4 |
| `data/audits/model1/supplementary_packets/a/Q-ff9ba74408.png` | 31 |
| `data/audits/model1/supplementary_packets/b/Q-0119983bf1.png` | 6 |
| `data/audits/model1/supplementary_packets/b/Q-056cd7d4dc.png` | 7 |
| `data/audits/model1/supplementary_packets/b/Q-0c5331b4f7.png` | 7 |
| `data/audits/model1/supplementary_packets/b/Q-0cb670a691.png` | 53 |
| `data/audits/model1/supplementary_packets/b/Q-114e496cd0.png` | 2 |
| `data/audits/model1/supplementary_packets/b/Q-15e6213bf9.png` | 5 |
| `data/audits/model1/supplementary_packets/b/Q-1d8bf1fa4d.png` | 6 |
| `data/audits/model1/supplementary_packets/b/Q-1ec3d4e552.png` | 25 |
| `data/audits/model1/supplementary_packets/b/Q-29901c6d31.png` | 29 |
| `data/audits/model1/supplementary_packets/b/Q-2ae2596570.png` | 13 |
| `data/audits/model1/supplementary_packets/b/Q-2d4e04edc5.png` | 13 |
| `data/audits/model1/supplementary_packets/b/Q-2da3e31b8b.png` | 6 |
| `data/audits/model1/supplementary_packets/b/Q-3006456b4c.png` | 9 |
| `data/audits/model1/supplementary_packets/b/Q-34bbdb0f9e.png` | 9 |
| `data/audits/model1/supplementary_packets/b/Q-36f319be0e.png` | 3 |
| `data/audits/model1/supplementary_packets/b/Q-3e376b8090.png` | 6 |
| `data/audits/model1/supplementary_packets/b/Q-422b30ec74.png` | 4 |
| `data/audits/model1/supplementary_packets/b/Q-45a99fc2fc.png` | 10 |
| `data/audits/model1/supplementary_packets/b/Q-45b512a9c5.png` | 18 |
| `data/audits/model1/supplementary_packets/b/Q-49a617f4c9.png` | 7 |
| `data/audits/model1/supplementary_packets/b/Q-51f0eb9022.png` | 22 |
| `data/audits/model1/supplementary_packets/b/Q-52d83f4f02.png` | 3 |
| `data/audits/model1/supplementary_packets/b/Q-59414cb3aa.png` | 8 |
| `data/audits/model1/supplementary_packets/b/Q-59ea79413d.png` | 4 |
| `data/audits/model1/supplementary_packets/b/Q-5bbc0616f3.png` | 13 |
| `data/audits/model1/supplementary_packets/b/Q-5dedc04b85.png` | 15 |
| `data/audits/model1/supplementary_packets/b/Q-69db94ceea.png` | 9 |
| `data/audits/model1/supplementary_packets/b/Q-74b43b765e.png` | 6 |
| `data/audits/model1/supplementary_packets/b/Q-79648f45f4.png` | 43 |
| `data/audits/model1/supplementary_packets/b/Q-8df7efa413.png` | 2 |
| `data/audits/model1/supplementary_packets/b/Q-910f387828.png` | 31 |
| `data/audits/model1/supplementary_packets/b/Q-9138e63631.png` | 5 |
| `data/audits/model1/supplementary_packets/b/Q-9f4be1596a.png` | 12 |
| `data/audits/model1/supplementary_packets/b/Q-a012fada5d.png` | 17 |
| `data/audits/model1/supplementary_packets/b/Q-a4edc5ecac.png` | 9 |
| `data/audits/model1/supplementary_packets/b/Q-a8cda11c84.png` | 11 |
| `data/audits/model1/supplementary_packets/b/Q-ae7f010c41.png` | 11 |
| `data/audits/model1/supplementary_packets/b/Q-afc0f0153c.png` | 5 |
| `data/audits/model1/supplementary_packets/b/Q-b02a343358.png` | 16 |
| `data/audits/model1/supplementary_packets/b/Q-b06ac9b832.png` | 7 |
| `data/audits/model1/supplementary_packets/b/Q-b2d2f02265.png` | 5 |
| `data/audits/model1/supplementary_packets/b/Q-bbdc0c1806.png` | 19 |
| `data/audits/model1/supplementary_packets/b/Q-c1873875b9.png` | 11 |
| `data/audits/model1/supplementary_packets/b/Q-c5548aec97.png` | 14 |
| `data/audits/model1/supplementary_packets/b/Q-d09e7b335e.png` | 2 |
| `data/audits/model1/supplementary_packets/b/Q-d8a7915f49.png` | 18 |
| `data/audits/model1/supplementary_packets/b/Q-e3e88f0cc8.png` | 12 |
| `data/audits/model1/supplementary_packets/b/Q-e64098536f.png` | 7 |
| `data/audits/model1/supplementary_packets/b/Q-ef068b7b9e.png` | 5 |
| `data/audits/model1/supplementary_packets/b/Q-f08d4f95ac.png` | 8 |
| `data/audits/model1/supplementary_packets/b/Q-f0b93c7df3.png` | 5 |
| `data/audits/model1/supplementary_packets/b/Q-f9cbd51188.png` | 10 |
| `data/audits/model1/supplementary_packets/b/Q-fb51b76f93.png` | 9 |
| `data/audits/model1/supplementary_relations.csv` | 47 |
| `data/audits/model1/supplementary_resolution.csv` | 115 |
| `reports/execution/task-02-audit-report.md` | 18 |
| `reports/final_adversarial_review.md` | 30 |
| `reports/execution/task-09-results-audit-round2.md` | 2 |
| `reports/amendments/amendment-008-independent-rereview.md` | 1 |
| `reports/amendments/amendment-008-independent-review-round7.md` | 1 |
| `reports/amendments/amendment-008-independent-review-round8.md` | 1 |
| `reports/amendments/amendment-009-independent-review.md` | 25 |
| `reports/amendments/delta-3990fa7-2e9b009.diff` | 43 |
| `reports/amendments/delta-3990fa7-963b03e.diff` | 42 |
| `reports/amendments/fix-963b03e-2e9b009.diff` | 6 |
| `reports/amendments/gate-review-exp-r01.md` | 11 |
| `reports/amendments/independent_delta_review.md` | 2 |
| `reports/amendments/plan_self_review.md` | 1 |
| `docs/research/decision_log.md` | 27 |
| `provenance/commands/task09/revise_pass2f.py` | 45 |
| `provenance/commands/task02/correct_audit_report.py` | 14 |
| `provenance/commands/task02/finalize_adjudication.py` | 7 |
| `provenance/commands/task02/record_supplementary.py` | 19 |
| `provenance/commands/task02/supplementary_candidates.py` | 6 |
| `docs/superpowers/plans/2026-09-17-albus26-major-revision.md` | 12 |
| `docs/superpowers/specs/2026-09-17-albus26-major-revision-design.md` | 14 |
