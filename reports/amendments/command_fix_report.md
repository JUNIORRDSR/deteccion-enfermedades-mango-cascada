# Corrección de comandos — ADR-LOW-01

Fecha: 2026-09-19. Base: `963b03ecaa6585628f79142ffdddc6992dc238a5`. Alcance: sólo autosuficiencia documental de los ejemplos PowerShell del plan; SPEC y reglas científicas intactas.

## Cambio

- Unifiqué el preámbulo de raíz y `$AuditPython` con el bloque de instalación que lo usa. `$Python` sigue definido antes de sus usos dentro de ese mismo bloque.
- En TASK-01 a TASK-10 sustituí 27 usos de `& $Python` por `& .\.venv\Scripts\python.exe`. El texto exige `workdir` del checkout activo o `Set-Location` en la misma invocación; las CLIs futuras siguen obligadas a llamar `configure_environment(root)` antes de imports científicos.

## Verificación inocua

- En un proceso PowerShell nuevo, extraje y ejecuté sólo las líneas `Set-Location` y asignación de `$AuditPython` del bloque; comprobé raíz, existencia del ejecutable de auditoría, orden declaración→uso y argumentos documentados `-m venv .venv`. No ejecuté `venv`.
- En otro proceso PowerShell nuevo, comprobé que los 27 ejemplos por tarea usan la ruta explícita bajo la raíz del checkout, empiezan con `-m` y no dependen de `$Python`. No ejecuté esos ejemplos.
- El plan mantiene CRLF, sin LF sueltos ni caracteres de sustitución. `git -c core.whitespace=cr-at-eol diff --check` pasó y el diff fue revisado para cambios de método o parámetros.

## Límites

La `.venv` aún no existe; por ello no se comprobó resolución real de ese ejecutable ni ejecución de las CLIs futuras. No hubo TASK-01, creación de entorno, instalación, import científico, ejecución experimental ni cambios legacy. Este reporte y el self-review no sustituyen la revisión independiente ni satisfacen gates o freeze.
