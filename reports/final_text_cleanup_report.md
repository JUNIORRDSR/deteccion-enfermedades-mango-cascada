# Informe final de la limpieza de texto y de la atribución IA/humano

**Fecha:** 2026-09-29 · **Pasada:** 2g (`provenance/commands/task09/revise_pass2g.py`) · **Auditoría previa:** `reports/final_text_cleanup_audit.md` (TC-01 a TC-30) · **Candidato:** DOCX `f16115958d081467283089639b9f5f7a901acca2a835e20c364c55be016395ed`, PDF `86bd462910f09b41d4a9920f30bd1022d0a26c98e56fcb30653e233222120b28`, 16 páginas (pasada 2h, que sólo cambia la versión citada del repositorio).

Esta pasada no cambia el experimento, los modelos, las particiones ni ningún resultado. El informe no declara que el artículo esté científicamente terminado. Sólo comprueba que la limpieza editorial y la descripción de la revisión (primero con IA, después humana) son coherentes y están respaldadas por la evidencia disponible.

## Cambios realizados

- **Atribución de la revisión visual** (3.3.1, 6.1, carta REVIEW-01, README y documentos de estado):
  - la primera adjudicación se describe como asistida por agentes de IA;
  - se añade la revisión manual posterior de una integrante del equipo;
  - se retira «ninguna de estas decisiones la revisó una persona».
- **Salida del sistema.** «Clasificación» o «clase de enfermedad» sustituye a «diagnóstico» en 3.6, 4.2.4, 5.2, la fuente de la Figura 7 y la flecha de la Figura 1. «Diagnóstico» queda sólo para el diagnóstico convencional o experto.
- **Dos sobreafirmaciones retiradas:** «localización fiable en campo abierto» (3.1) y «métricas estables» (5.4). El resumen ya no atribuye el costo del laboratorio al «productor rural colombiano», que la Sección 1 no sostiene.
- **Texto desactualizado.** La Sección 2.4 decía «uno de tales casos sobre un corpus público», separado de su antecedente; ahora habla de los dos corpus, tras la cita de Kapoor y Narayanan.
- **Redacción más directa**, sin cambiar citas:
  - la frase inicial sobre visión por computador;
  - la de Kapoor y Narayanan (2023);
  - 3.3.2, sin «anomalía significativa» y sin «reejecución independiente»;
  - 3.5 y 6.2.
- **Tabla 8:** «Etiquetas de imagen completa en MangoDHDS», como 3.5 y 6.1.
- **Registros:**
  - DECISION-040 en `docs/research/decision_log.md`;
  - ED-25 a ED-28 en `reports/editorial_claim_audit.csv`;
  - CLAIM-031 y CLAIM-041 en la matriz de claims;
  - AMENDMENT-03 en `reports/protocol_compliance.json`.

## Atribución IA/humano

El texto final describe el proceso así (Sección 3.3.1):

> La primera adjudicación se hizo con apoyo de agentes de IA: dos instancias separadas (Claude Opus y Claude Sonnet) juzgaron cada candidato sin ver la partición, la clase ni el nombre de archivo, y una tercera (Claude Haiku) resolvió los desacuerdos; ese ciego se impuso por instrucción, no por control de acceso. […] Los agentes mostraron una fiabilidad limitada: […] Posteriormente, una integrante del equipo revisó manualmente los candidatos. Los grupos de la partición proceden de las decisiones registradas de la adjudicación, de modo que la partición y los intervalos dependen de ellas.

Qué respalda cada parte:

- **El uso de IA y su fiabilidad** están documentados en `data/audits/model1/`: registros de cegamiento, respuestas y adjudicaciones. Se conservan sin cambios.
- **La revisión manual posterior** la declararon los autores el 2026-09-29 (DECISION-040). No hay un registro caso a caso de ella en el repositorio ni en la carpeta del proyecto. Por eso el texto no le atribuye decisiones, protocolo, fecha, número de revisores ni grado de acuerdo, y no presenta los grupos como validados por ella.
- **Los grupos de la partición congelada** son los de la adjudicación registrada. Así lo dice el texto, porque es lo que muestran los artefactos.
- **Lo que no se afirma:** que el conjunto esté libre de fuga, que haya independencia biológica, que exista validación fitopatológica, ni que la revisión humana haya encontrado todas las relaciones.

`reports/ai_human_attribution_check.md` lista las 71 apariciones finales de los términos de IA y revisión humana, con su justificación: ninguna queda sin justificar. También lista los 137 archivos históricos que se conservan como ocurrieron.

## Resultados

Las métricas científicas no se modificaron. `provenance/commands/task09/validate_pass2g.py 7bed50c` compara todos los números del texto y las tablas con el candidato de la pasada 2f: son idénticos, sin contar las referencias a secciones añadidas («Sección 3.3.1», «Sección 3.7»). La pasada 2h sólo cambia dos dígitos, los de la versión citada del repositorio (1.0.0 → 1.0.1); el mismo script frente a la pasada 2g confirma que es la única diferencia numérica.

`reports/manuscript_consistency.json` recalcula las 165 cifras registradas desde sus artefactos, sin incidencias. Siguen iguales:

- **M1:** mAP@0,5 de 0,807 [0,677; 0,887] y sensibilidad para Enfermo de 0,577 [0,273; 0,735] en prueba.
- **M2:** exactitud de 0,909 [0,869; 0,946] y macro-F1 de 0,909 [0,869; 0,945].
- Las matrices de confusión, la latencia y los recuentos de duplicados.

## Limitaciones

Las limitaciones reales siguen visibles. El script de validación comprueba 20 frases del texto y las encuentra todas:

- la baja sensibilidad de M1 para Enfermo;
- el único origen Enfermo en entrenamiento;
- las pruebas retrospectivas;
- la falta de verdad de terreno conjunta y de validación en campo;
- el cambio de dominio del clasificador;
- el umbral de 0,4 sin validar;
- los intervalos condicionales;
- la fuga no descartada;
- la adjudicación asistida por IA de fiabilidad limitada, con su revisión manual posterior;
- las etiquetas de terceros sin confirmación fitopatológica;
- el cluster de M2 con dos etiquetas y los duplicados de entrenamiento y validación;
- los dos evaluadores de validación;
- la latencia sin escenas densas;
- la Raspberry Pi no medida;
- la falta de prueba externa.

La pasada añade además una limitación en 6.1 sobre la adjudicación.

## Archivos modificados

- `manuscript/source/Articulo_Mango_ALBUS_revision.docx`, `manuscript/output/Articulo_Mango_ALBUS_revision.pdf` y `manuscript/source/edit_log.json`.
- `manuscript/figures/fig1_cascada.png` y `provenance/commands/task09/figures.py` (flecha «clase»; la Figura 2 queda idéntica byte a byte).
- `docs/response_to_reviewers.md`, `README.md`, `docs/final_validation_report.md`, `docs/research/decision_log.md` (DECISION-040) y `docs/research/claim_evidence_matrix.csv`.
- `reports/editorial_audit.md`, `reports/editorial_claim_audit.csv`, `reports/protocol_compliance.json`, `reports/execution/STATE.md`, `reports/execution/render_review.md` y `reports/manuscript_consistency.json`.
- `provenance/commands/task09/claims_final.py`.
- Nuevos:
  - `provenance/commands/task09/revise_pass2g.py`, `validate_pass2g.py` y `attribution_check.py`;
  - `reports/final_text_cleanup_audit.md`, `reports/ai_human_attribution_check.md` y este informe.

Los registros históricos no se modificaron: registros de cegamiento, respuestas y adjudicaciones, auditorías, revisiones y scripts de pasadas anteriores.

## Validaciones ejecutadas

| Validación | Resultado |
|---|---|
| Lectura completa del manuscrito antes y después de la pasada | PASS |
| Cifras recalculadas desde sus artefactos (`document_checks`, 165 cifras) | PASS |
| Números del texto y las tablas idénticos a la pasada 2f (`validate_pass2g.py`) | PASS |
| Referencias y citas en ambos sentidos (`check_citations.py`, 22 y 22) | PASS |
| Render nuevo del PDF (16 páginas) | PASS |
| Inspección visual de todas las páginas (`reports/execution/render_review.md`) | PASS |
| Sin redacción de «sin revisión humana» en el manuscrito ni en los documentos actuales | PASS |
| Sin contradicciones sobre la participación de IA (`reports/ai_human_attribution_check.md`, 71 apariciones justificadas) | PASS |
| M1 y M2 conservan exactamente sus resultados | PASS |
| Ninguna limitación real desapareció (20 de 20) | PASS |
| Metadatos de autor del PDF | PASS |
| Suite completa de pruebas (397 pruebas) | PASS |

## Pendiente de los autores

1. **Registro de la revisión manual.** Si existe un registro de las decisiones de la integrante del equipo, conviene añadirlo a `data/audits/model1/`. Cualquier desacuerdo con la adjudicación asistida debe declararse, porque los grupos de la partición proceden de esta última.
2. **Declaración general de uso de IA (TC-29, no aplicada).** El manuscrito declara la IA en la adjudicación. No declara su uso en la programación, la ejecución de los análisis, las revisiones metodológicas ni la edición del texto, que el README sí menciona. Si la política de ALBUS lo pide, una redacción posible para Agradecimientos o para una sección propia: «Los autores usaron asistentes de IA (Claude y Codex) para programar y ejecutar los análisis, para revisiones metodológicas internas y para editar el texto; los autores revisaron el contenido y son responsables de él.» Es una declaración de los autores y no se añadió sin su confirmación.
3. **Publicación.** La release v1.0.0 ya publicada tiene el estado de la pasada 2f, cuyo manuscrito aún no describe la revisión manual posterior. La pasada 2h cambia sólo la cita del manuscrito a la versión 1.0.1: la referencia y el encabezado de la carta. La rama local `publicacion` y la etiqueta `v1.0.1` preparan esa versión como commit hijo del `main` publicado, y la subida la hacen los autores.
