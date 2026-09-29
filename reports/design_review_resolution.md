# Resolución documental de revisión independiente

El snapshot original y sus hallazgos se preservan en `research_independent_review.md`. Las correcciones se limitan a documentos de propuesta y matrices; no se ejecutó el plan.

|Hallazgo|Cambio concreto|Evidencia a releer|Estado de corrección|
|---|---|---|---|
|RIR-01 HIGH|Último máximo nativo con precisión completa; callback y retención/hash antes y después de stripping; pruebas de bytes y empate|SPEC §7; TASK-04|RESUELTO EN DISEÑO; relectura independiente realizada|
|RIR-02 HIGH|Variables antes de pip/imports, rutas efectivas comprobadas en hijo y bloqueo por escape|SPEC §4; entorno y TASK-01|IMPLEMENTED_IN_DESIGN; ejecución futura pendiente|
|RIR-03 MEDIUM|Entorno reconstruido común 8.4.52; 8.4.39 histórico conservado y REVIEW-09 actualizado|SPEC §7; TASK-01; matriz REVIEW|IMPLEMENTED_IN_DESIGN|
|RIR-04 MEDIUM|DER-001/002 enlazados desde CLAIM-004/005/009; alcance snapshot local|derived_evidence_registry.csv; claim matrix|CORRECTED_DOCUMENTARY_TRACEABILITY|
|RIR-05 MEDIUM|CLAIM-031 parcialmente soportado; no acredita cajas originales. DATA-006 es localización mango|claim matrix; REVIEW-11|CORRECTED_DOCUMENTARY_SCOPE|
|RIR-06 MEDIUM|Lectura completa y corrección de texto pegado, conservando comandos y cifras|SPEC; plan; risk register|CORRECTED_PROSE|

El estado de corrección no significa que el método esté implementado o validado en ejecución. La relectura independiente se registra por separado y no se sustituye por esta respuesta del autor del diseño.

## Relectura independiente, 2026-09-18

`reports/research_independent_rereview.md` confirma la resolución documental de RIR-01–06. Se corrigieron además la correspondencia de IDs M2 para intervalos, dos rutas locales y dos expresiones ambiguas. No quedan hallazgos HIGH/MEDIUM de diseño pendientes; falta completar la entrega del informe de validación documental, en preparación en ese snapshot. Nada de esto valida la implementación futura ni reemplaza la revisión científica adversarial final.
