# Self-review del plan — enmiendas 2026-09-18

Revisión documental de cobertura, contratos y orden. Estado: listo para revisión independiente fresca del delta; ninguna TASK ejecutada, ningún gate marcado satisfecho por el autor. Los tests descritos son entregables futuros TDD, no evidencia de ejecución actual.

|Enmienda|REVIEW|TASK / preflight|Contrato, check y salida comprobados en el plan|
|---|---|---|---|
|AMENDMENT-01|09/todos|Preflight,01,10|Baseline/hashes, Git exclusivo y candidato BASE..HEAD, commits de fixes y cierre después de revisión; lectura Git legacy sin locks y comparación inicial/final|
|AMENDMENT-02|01,02,03,05,07,09|Preflight,01,10|Freeze exclusivo y commiteado antes de TASK-01, hashes/commits cotejados, test_access histórico; test de byte alterado/enmienda ausente y protocol_compliance final|
|AMENDMENT-03|01,02|02,03,10|validate_adjudications y paquetes A/B; tests de review faltante, reviewer repetido, desacuerdo sin resolver, umbral9/10, cegamiento y cobertura de cluster|
|AMENDMENT-04|02,04,05,09|02,05,09,10|Fixture counts4/SHA3/clusters2; fixture ponderación principal1/2/secundarias2/3, macroF1 y deltas; bootstrap por group_id con draws pareados y reglas de indefinición; salidas sensitivity/confusions/draws/reporte|
|AMENDMENT-05|09,17|01,10|resolve_source + roots + source_locations; fixtures relocación/escape/hash/SRC/cobertura, pip check fallido y secrets; environment completo y portability_check|
|AMENDMENT-06|07,08,10,14|06,09,10|claim_language_issues con cuatro ubicaciones, rechazo de eficiencia sin criterio previo y auditoría CSV; benchmark descriptivo no se promociona a comparativo|
|AMENDMENT-07|01,02,04,14|02,03,09,10|Audit/report con parámetros y límites; fixtures de absolutos propios y citas históricas; editorial_claim_audit y comprobación final|

Interfaces reconciliadas: root mapping y source_locations nacen en TASK-01 y los consume TASK-03/verificación; model2_frozen_manifest contiene image_id, cluster_id y group_id; TASK-05 admite matrices float, aplica clases fijas y une predicciones por ID (no sólo SHA); TASK-09 extiende document_checks originado en TASK-08; TASK-10 reutiliza contratos sin implementar otro framework. Paths de outputs relativos al checkout, fuentes resueltas por root explícito.

Verificación de orden: revisión fresca del delta → registro de condición satisfecha → commits de SPEC/plan → freeze con esos commits/hashes → commit del freeze/ledger → B/C satisfechos → TASK-01. Implementador fresco por tarea, self-review/tests → commit candidato → revisión SPEC/calidad BASE..HEAD → fixes revisados → cierre. No consulta entre tareas ordinarias ni push/merge implícito. Pi/GT/M1 histórico exacto no bloquean partes independientes.

No placeholders nuevos ni cambios de interpretación primaria autorizados. Se conservaron las tareas científicas preexistentes y se añadieron contratos verificables a 01/02/05/09/10; 03 recibe raíces y campos de grupos para evitar ruptura de interfaz. Las siete enmiendas tienen salidas concretas y REVIEW existentes; no se inventaron REVIEW nuevos. La disponibilidad real del entorno/hardware/datos sigue sin comprobarse en esta fase documental.

Self-review no independiente. La revisión fresca puede abrir hallazgos; sólo el coordinador registra aprobación efectiva y freeze después de resolver HIGH/MEDIUM. No se ejecutaron tests científicos ni se crearon resultados experimentales.

## Revisión posterior de ADR-LOW-01 — 2026-09-19

Revisé el cambio documental contra `963b03ecaa6585628f79142ffdddc6992dc238a5`. El bloque de instalación fija la raíz y declara `$AuditPython` antes de `& $AuditPython -m venv .venv` en la misma invocación. Los 27 ejemplos de TASK-01 a TASK-10 usan `.\.venv\Scripts\python.exe` desde el `workdir` del checkout; fuera de instalación no queda `$Python` implícito. `configure_environment(root)` sigue siendo requisito de cada CLI científica antes de sus imports. No cambié métodos, parámetros ni gates.

Dos procesos PowerShell nuevos comprobaron, sin lanzar ejecutables científicos: la raíz y existencia de AuditPython junto con `-m venv .venv`, y las rutas y prefijo `-m` de los 27 comandos por tarea. La futura `.venv` aún no existe. El plan conserva CRLF sin LF sueltos ni caracteres de sustitución; `git -c core.whitespace=cr-at-eol diff --check` pasó. La revisión de diff muestra sólo estos preámbulos y referencias al ejecutable.

Esto cierra la corrección documental solicitada para ADR-LOW-01, sujeto a revisión independiente del commit candidato. No se ejecutó TASK-01, no se creó `.venv`, no hubo instalación ni import de runtime científico; no se reclama ejecutabilidad de CLIs futuras ni estado DONE global.
