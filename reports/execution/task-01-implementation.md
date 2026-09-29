# TASK-01 — Informe de implementación

- **BASE:** `bead3604aa2f969c827e240d87e8a60b298c85c0`
- **Autoridad:** plan congelado TASK-01; SPEC §4; brief verbatim en `.superpowers/sdd/2026-09-17-albus26-major-revision/task-1-brief.md`
- **Sede de ejecución:** workspace local, worktree `revision/execute-approved-plan`
- **Estado:** RECHAZADA por la revisión independiente (3 HIGH, 7 MEDIUM, 1 LOW); corregida y devuelta a revisión. Ver `reports/execution/task-01-review-response.md`.

## Historial de ejecución, sin ocultar la interrupción

La implementación la inició un implementador fresco (`/root/task01_implementer`) que quedó interrumpido por límite de uso antes de emitir su informe. Al reanudar, la suite dejada en disco **no estaba verde**: `tests/test_provenance.py::test_two_ids_cannot_map_one_logical_file` fallaba con `ValueError not raised`. Es un RED legítimo de TDD, no un fallo espurio: el test existía y la comprobación correspondiente no estaba implementada. El estado real de TASK-01 al reanudar era *en progreso*, no *completo*, y así se registra.

## Cambio aplicado al reanudar

`validate_locations` en `src/evaluation/provenance.py` ahora rechaza mapeos ambiguos: dos `source_id` distintos que resuelvan al mismo par `(logical_root, logical_path)`. El plan lo exige literalmente («requiere cobertura total y única de SRC originales y falla por mapeos ambiguos»). La iteración va ordenada por `source_id` para que el mensaje de error sea determinista. Las filas sin `logical_path` se omiten de la comprobación, porque `validate_locations` también se usa con el manifiesto original, que no tiene ese campo.

Nótese la consecuencia científica: la ejecución previa del CLI había informado «0 discrepancias» **sin** esta comprobación activa. Ese resultado anterior no acreditaba unicidad. La ejecución nueva sí.

## Verificación fresca

```
.\.venv\Scripts\python.exe -m unittest tests.test_provenance -v      → Ran 7 tests, OK, exit 0
.\.venv\Scripts\python.exe -m src.evaluation.provenance \
  --source-manifest provenance/source_manifest.csv \
  --source-locations provenance/source_locations.csv \
  --root-mapping configs/root_mapping.json \
  --out reports/source_verification.json                              → checked=11137 discrepancies=0, exit 0
```

Logs: `provenance/commands/task01/green.log`, `provenance/commands/task01/source_verification.log`. El RED original se conserva en `provenance/commands/task01/red.log` y `red-environment.log`.

CORRECCIÓN tras la revisión: esa afirmación era falsa cuando se escribió. La comprobación comparaba la grafía del CSV, no el archivo resuelto, así que no acreditaba unicidad. Tras cerrar el hallazgo 1 HIGH, la corrida nueva sí comprueba las tres cosas, y el propio reporte declara el método canónico que ejecutó.

## Qué cubre el contrato

`sha256` en streaming; `check_output` con `resolve().is_relative_to` y rechazo del propio root; `create_run` con `exist_ok=False`; `resolve_source` con validación de ruta relativa, rechazo de absolutas y de `..`, root explícito obligatorio y comparación de hash; `verify_sources` que acumula discrepancias en vez de abortar; `configure_environment` / `verify_environment` que fijan y luego comprueban las diez variables de aislamiento antes de cualquier import científico; `redact_url` / `sanitize_text` que preservan host y eliminan credenciales, tokens y query.

## Entorno reconstruido

Python 3.12.14 en `.venv` del workspace. `provenance/environment/` conserva versiones, ejecutable, configuración pip redactada, install report, `pip check`, freeze, paquetes y hardware. Es un entorno **reconstruido**: distinto del Python 3.13.13 del entrenamiento M2 y del Python desconocido del M1. La reproducción histórica exacta de M1 sigue bloqueada.

`hardware.json` documenta la ausencia comprobada de GPU NVIDIA y de runtime CUDA (`nvidia-smi` exit 127). Esa observación es la que motiva `PROTOCOL-AMENDMENT-008`.

## Límites y bloqueos que este informe NO resuelve

- Los cuatro pesos de `configs/inputs.json` siguen en `PRESENT_HASH_PENDING_VERIFICATION`: su hash local está registrado, pero no se ha comprobado carga ni correspondencia arquitectura/época.
- El checkpoint base de M1 permanece ausente: `BLOCKED_MISSING_BASE_CHECKPOINT`. Se propone resolverlo en TASK-04 vía `PROTOCOL-AMENDMENT-008` registrando el SHA256 del checkpoint oficial descargado, no reutilizando el `best.pt` entrenado.
- `pip check` y los artefactos de paquetes están registrados, pero ninguna métrica científica se ha producido en TASK-01.

## REVIEW-IDs

REVIEW-09 queda sostenido sólo en su parte de procedencia recuperable y de límites declarados. La procedencia histórica faltante del M1 sigue declarada como tal, no inventada.

## Contención del runtime después de importar Ultralytics

`provenance/commands/task01/verify_runtime_paths.py` ejecuta cuatro procesos hijo **sin heredar** las variables de aislamiento y guarda `provenance/environment/runtime_path_report.json` (estado `PASS`, log `runtime_paths.log`, exit 0):

1. `missing` — omitir `YOLO_CONFIG_DIR` es rechazado por `verify_environment` **antes** de importar.
2. `external` — apuntar `YOLO_CONFIG_DIR` a `C:/Windows/Temp` es rechazado con su causa concreta.
3. `import_configured` — con `configure_environment` + `verify_environment` antes del import: `datasets_dir`, `weights_dir`, `runs_dir` y el propio `settings.json` quedan dentro del checkout, y la telemetría (`sync`) queda desactivada.
4. `import_unguarded` — **peligro documentado, no defecto corregido.** Si un proceso importa Ultralytics sin llamar antes al helper, `get_user_config_dir` (`ultralytics/utils/__init__.py:901`) recurre a `%APPDATA%/Ultralytics` y escribe `settings.json` **fuera** del workspace, en silencio y sin error. El caso está asertado a la inversa: si algún día dejara de escapar, el test falla para forzar que se vuelva a derivar el contrato.

Consecuencia operativa de (4): **toda** CLI científica de TASK-02 a TASK-10 debe llamar `configure_environment(root)` y `verify_environment(root)` como primeras sentencias, antes de cualquier import de Ultralytics o torch. No basta con exportar variables en la shell.

## CUDA comprobado con torch, no sólo con nvidia-smi

Dentro del proceso guardado: `torch 2.12.0+cpu`, `torch.cuda.is_available() == False`, `torch.version.cuda == null`. `provenance/environment/hardware.json` sustituye `NOT_PROBED_WITH_TORCH` por esta medición. El entorno local no puede entrenar en GPU: es una rueda instalada explícitamente para CPU sobre una máquina sin dispositivo CUDA. Esta es la evidencia que sostiene `PROTOCOL-AMENDMENT-008`, no una conveniencia.


## Corrección posterior a la revisión independiente

Este informe fue escrito antes de la revisión y contenía afirmaciones que la revisión falsificó. Las dos principales: que la corrida de fuentes acreditaba unicidad, y que asertar el peligro de importación sin guarda era contención suficiente. Ninguna era cierta. La segunda es peor que un error de redacción: el propio verificador escribió fuera del workspace y lo informó como PASS. Queda registrado en `provenance/incidents/INCIDENT-001.json` y respondido en `reports/execution/task-01-review-response.md`.
