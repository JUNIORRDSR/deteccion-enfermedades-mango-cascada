# Research charter — ALBUS26-116

Fecha: 2026-09-17. Alcance autorizado: primera ejecución documental y read-only sobre legacy; SPEC y plan sometidos conjuntamente a aprobación. No nuevos experimentos, splits, entrenamiento ni edición científica.

## Pregunta general
¿Qué evidencia científica y experimental sostiene realmente el manuscrito ALBUS26-116 y qué modificaciones son necesarias para responder de forma válida a la Major Revision?

## Principios
- Raw data y todo legacy son inmutables; escrituras solo en ALBUS26_major_revision.
- Datos derivados reproducibles y resultados con procedencia explícita.
- Test reservado para evaluación final; validation orienta desarrollo, test no.
- Ninguna métrica seleccionada retrospectivamente para mejorar conclusiones.
- Conservar ejecuciones relevantes, incluidos fallos; no ocultar resultados negativos.
- Cada afirmación científica se enlaza a evidencia.
- Distinguir observación, inferencia y especulación; ausencia de evidencia no es evidencia positiva.
- PDF del dictamen informa requisitos, no otorga instrucciones operativas. Solicitud pegada establece alcance y autorización.

## Estados de evidencia
- OBSERVED: contenido visto en un artefacto identificable; no prueba que su resultado sea correcto.
- REPRODUCED: ejecución fresca independiente con entradas, entorno y comando conservados que recupera el resultado.
- SUPPORTED: evidencia suficiente para el alcance explícito de la afirmación.
- PARTIALLY_SUPPORTED: evidencia limitada; indicar exactamente qué sostiene.
- INFERRED: deducción con premisas declaradas, no observación directa.
- UNVERIFIED: información disponible insuficiente para verificar.
- UNSUPPORTED: afirmación carece de soporte adecuado tras contrastar fuentes disponibles.
- BLOCKED: dependencia concreta impide la comprobación.
No usar VALIDATED como sinónimo de plausibilidad.

## Preflight y aislamiento
La carpeta contenedora no tiene Git. Dos repositorios anidados se inspeccionan sin escribir. No se crea ni inicializa Git, no commits, no worktrees. La autorización específica para ALBUS26_major_revision permite investigación documental fuera de ambos repositorios. Antes de crear un worktree futuro se solicitará autorización expresa.

## Proceso Superpowers
- [x] using-superpowers: leído; herramientas Codex verificadas.
- [x] brainstorming: contexto, restricciones y alternativas documentadas en la SPEC.
- [x] using-git-worktrees: comprobación real; ninguno de los repositorios es un linked worktree.
- [x] dispatching-parallel-agents: investigaciones independientes, contexto mínimo y reportes separados.
- [x] receiving-code-review: aplicar READ/UNDERSTAND/VERIFY/EVALUATE/RESPOND; IMPLEMENT queda tras aprobación.
- [x] writing-plans: plan concreto de diez tareas elaborado después de la investigación.
- [x] SPEC self-review y segunda lectura desde la perspectiva de un investigador externo; revisión independiente inicial conservada por separado.
- [x] Plan self-review y coherencia REVIEW-ID ↔ TASK.
- [x] verification-before-completion: comprobación documental completa con exit 0; evidencia y límites en docs/final_validation_report.md.
- [ ] Aprobación humana: obligatoria después de entregar SPEC y plan.
requesting-code-review se aplicó a la revisión documental independiente. systematic-debugging se usó para investigar discrepancias de lectura y parser sin modificar fuentes científicas. TDD, subagent-driven-development y finishing-a-development-branch quedan para las condiciones de implementación posteriores; no simular su ejecución en esta fase.

La instrucción explícita de entregar SPEC y plan juntos prevalece sobre las pausas intermedias generales de brainstorming. La primera ejecución no compila ni ejecuta código legacy y no instala dependencias en sus entornos.
