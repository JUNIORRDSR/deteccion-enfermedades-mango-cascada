# Self-review de SPEC — enmiendas 2026-09-18

Alcance: lectura de la solicitud vinculante y revisión documental del delta respecto del baseline `3990fa7c79b77224675449b9bb676e650c47bbaf`. No constituye revisión independiente ni aprobación efectiva; GATE B/C siguen PENDING_FRESH_REVIEW hasta evidencia del coordinador. No se ejecutó TASK-01 ni ciencia. El freeze se crea después de la revisión fresca satisfactoria, antes de TASK-01.

|Enmienda|SPEC|REVIEW ↔ TASK|Resultado del self-review|
|---|---|---|---|
|AMENDMENT-01|§4.1,11|09/todos ↔ preflight,01,10|Git exclusivo y baseline exacto, exclusiones administrativas separadas, worktree fallback documentado; candidatos locales y revisión BASE..HEAD; legacy read-only con OPTIONAL_LOCKS=0; prohibiciones externas mantenidas|
|AMENDMENT-02|§4.2,11|01,02,03,05,07,09 ↔ preflight,01,10|Commits/SHA, reglas completas, test histórico ya observado, snapshot append-only y desviación científica también por bugs; no nueva observación antes del freeze|
|AMENDMENT-03|§5|01,02 ↔02,03,10|A/B independientes y ciegos, paquetes separados, grande≥10, cobertura de candidatos, registro por par/cluster y resolución separada; no consenso biológico|
|AMENDMENT-04|§5,7|02,04,05,09 ↔02,05,09,10|Principal por imagen, secundarios SHA/cluster explícitos, confusión float y cinco clases fijas, deltas pareados y reglas undefined/CI; no retrain automático|
|AMENDMENT-05|§4.1,4.3,6|09,17 ↔01,10|Identidad de runtime e instalación con límites de hashes/builds, secrets redactados, roots explícitos y manifests originales preservados|
|AMENDMENT-06|§8,10|07,08,10,14 ↔06,09,10|Audita eficiente y temprana en cuatro ubicaciones; neutral por defecto, criterio previo/comparador requerido para mantener eficiente|
|AMENDMENT-07|§5,6,10,11|01,02,04,14 ↔02,03,09,10|Conclusiones limitadas a contaminación detectada y protocolo; límites de independencia, duplicados intra-split y relaciones no excluidas explícitos|

Contradicciones corregidas: prohibiciones anteriores de Git/commits/worktree; interpretación de `../` desde worktree; gate de aprobación antigua; detención de todo el trabajo ante bloqueo experimental; revisión limitada antes a críticos/altos; remuestreo M2 por cluster cuando existe grupo de dependencia mayor. Las cinco paradas globales del usuario permanecen exhaustivas; D/E conservan estado verdadero en ramas bloqueadas.

Coherencia estadística revisada documentalmente: los tres estimandos operan sobre mismas predicciones y clases, sus pesos/denominadores son explícitos, draws compartidos mantienen pares y multiplicidad, y falta de clase no se convierte en cero ni exclusión silenciosa. n clusters/grupos no se presenta como independencia biológica demostrada. La sensibilidad no decide qué resultado primario reportar.

Límites pendientes, no defectos ocultos: compatibilidad del entorno propuesto, grupos biológicos, GT conjunto, Pi y reproducción histórica exacta necesitan evidencia de ejecución/fuentes. No se declaran resueltos. La revisión independiente fresca aún debe evaluar el delta y sus efectos; este self-review no autoriza ejecutar tareas.
