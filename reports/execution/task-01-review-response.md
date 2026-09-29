# Respuesta a la revisión adversarial independiente de TASK-01

Revisión: `reports/execution/task-01-independent-review.md`, veredicto **FAIL / REJECT IN CURRENT FORM**, 3 HIGH + 7 MEDIUM + 1 LOW abiertos.

Se aplicó READ / UNDERSTAND / VERIFY / EVALUATE / RESPOND. **Ningún hallazgo se rechazó por conveniencia.** Los dos hallazgos factuales verificables se comprobaron de forma independiente antes de actuar, y ambos resultaron correctos.

## Hallazgo 3 HIGH — el verificador cometió la escritura externa que decía vigilar

**Aceptado sin reservas. Era el hallazgo más grave y el revisor tenía razón completa.**

Comprobado: existían `C:/Users/junio/AppData/Roaming/Ultralytics/settings.json` y su vista redirigida por el sandbox, creados a las 21:56 por mi propia ejecución, con rutas del workspace y un UUID de máquina de Ultralytics. La primera versión del script demostraba el peligro **provocándolo**, y aun así informaba `PASS`.

Preservado como `provenance/incidents/INCIDENT-001.json`, con copias y hashes de cada archivo.

Durante la reparación se produjo **una segunda fuga**, más pequeña: fijé las variables del perfil de prueba pero no creé `AppData/Roaming`, así que `is_dir_writeable` falló y Ultralytics cayó a su rama `/tmp`, creando `C:/tmp/Ultralytics/settings.json`. También queda registrada en el incidente. La registro porque ocultarla sería exactamente el defecto que el revisor señaló.

Reparación en `provenance/commands/task01/verify_runtime_paths.py`:

- El caso sin guarda ya **no** importa en un perfil no controlado: redirige `USERPROFILE`, `HOME`, `APPDATA`, `LOCALAPPDATA`, `XDG_CONFIG_HOME` y crea sus subdirectorios dentro de `provenance/runtime_state/profile_fixture/`. El fallback documentado de `get_user_config_dir` cae ahí y se observa sin tocar el perfil real.
- Una escape es **fallo** en el modo con guarda, nunca una expectativa.
- Se comprueba explícitamente que ninguna ruta llegue a `%APPDATA%`, `%LOCALAPPDATA%` ni `C:/tmp`.

Estado tras la reparación: `PASS`, exit 0, sin escapes y con las diez integraciones remotas desactivadas. Los tres archivos externos **siguen existiendo**: borrarlos es una acción externa y su disposición corresponde al dueño del equipo (`disposition: PENDING_OWNER_DECISION`).

**Observación nueva derivada de esta reparación:** Ultralytics ejecuta una sonda de red al importar (`ONLINE = is_online()`, `ultralytics/utils/__init__.py`). Queda registrada como `ultralytics_online_probe_at_import: true`. Afecta directamente a cualquier exigencia de ejecutar sin red, incluida la de `PROTOCOL-AMENDMENT-008`.

## Hallazgo 1 HIGH — la unicidad se comprobaba sobre la grafía del CSV

**Aceptado.** Mi corrección anterior comparaba `(logical_root, logical_path)` como cadenas, así que `sub/a.bin` y `sub/./a.bin` pasaban, igual que variantes de mayúsculas, barra invertida o dos roots apuntando al mismo directorio.

Ahora `validate_locations` resuelve cada fila por el mapping y canonicaliza con `os.path.normcase(os.path.realpath(...))`, rechazando dos SRC-ID que identifiquen el mismo archivo físico. Cubierto por RED/GREEN en `tests/test_provenance_hardening.py`: segmento `.`, barra invertida, mayúsculas, dos roots al mismo directorio, y el caso positivo de archivos distintos.

**Consecuencia sobre la afirmación anterior:** mi informe decía que «0 discrepancias» acreditaba correspondencia única SRC→archivo. **No lo acreditaba.** Ahora sí: la corrida nueva sobre las 11.137 filas pasa con el método canónico activo, y el reporte declara el método que realmente ejecutó (`uniqueness_method`).

## Hallazgo 2 HIGH — la autorización de escritura la elegía quien llamaba

**Aceptado.** Comprobado que `--out provenance/protocol_freeze.json` habría sobrescrito el freeze y que `--out NUL` descartaba el informe informando éxito.

- `authorized_root()` localiza el checkout que contiene el freeze en lugar de confiar en el cwd.
- `check_output` rechaza los ocho archivos protegidos, los nombres de dispositivo reservados (`NUL`, `CON`, `COM1`…) y los alias con punto o espacio final.
- `create_run(root, path)` exige el root y aplica containment.

Comprobado contra la CLI real: los cuatro casos hostiles devuelven **exit 2** y los hashes del freeze permanecen idénticos.

**Desviación declarada:** el brief congelado esboza `create_run(path)`. La restricción global congelada exige que toda función consumidora de rutas rechace escrituras fuera del checkout, y una sola posición no lo permite. Se refina la firma en favor de la restricción vinculante y se documenta en el módulo. No es un cambio silencioso.

**Residual que NO queda cerrado:** la carrera check/use con junctions. `realpath` resuelve en el momento de la comprobación; sustituir un directorio intermedio por un junction entre la comprobación y la escritura sigue siendo posible. Cerrarlo requiere un descriptor abierto revalidado o una estrategia no-follow. Queda declarado como residual, no como resuelto.

## Hallazgos 4 y 5 MEDIUM — clasificación de errores y totalidad del contrato de salida

**Aceptados.** Se introduce `InvalidInput(ValueError)`. `verify_sources` sólo captura `InvalidInput`, `FileNotFoundError` y `KeyError`; un `PermissionError` **propaga** con su traceback, comprobado con un test. `validate_root_mapping` rechaza JSON que no sea un objeto de cadenas y el JSON malformado se traduce a `InvalidInput`. La CLI mapea entrada inválida a **2** y cualquier fallo inesperado a traceback y **1**.

## Hallazgo 6 MEDIUM — redacción dependiente de la entrada

**Aceptado.** `sanitize_text` cubre ahora cabeceras `Authorization`, credenciales `Bearer`/`Basic` y userinfo sin esquema, preservando el host. Se añade `sanitize_obj`, que redacta **por clave** (`password`, `token`, `api_key`, `authorization`, `credential`) en estructuras anidadas. `install_reconstructed.py` pasa a usarlo.

Comprobado que el `install_report.json` ya versionado está limpio: 41 descargas, todas de `files.pythonhosted.org`, sin userinfo ni query. El revisor tenía razón en que ese resultado limpio era accidental respecto de las entradas que probó.

## Hallazgo 7 MEDIUM — aislamiento declarado pero no verificado

**Aceptado.** `verify_environment` comprueba ahora las cinco variables de aislamiento además de las diez de rutas, y verifica `site.ENABLE_USER_SITE` en el propio intérprete, porque `PYTHONNOUSERSITE` sólo actúa en el arranque y no retira retroactivamente el user-site.

`lock_ultralytics` desactiva las **diez** integraciones, no sólo `sync`. Antes quedaban activas `clearml`, `comet`, `dvc`, `hub`, `mlflow`, `neptune` y `raytune`, tal como el revisor observó. El verificador falla si alguna sigue activa.

## Hallazgo 8 MEDIUM — cobertura declarada sobre un esquema incompleto

**Aceptado.** `require_schema` exige los cinco campos, no vacíos, con SHA de 64 hex, y `validate_locations` comprueba que `local_absolute_path` coincida con el objetivo resuelto. La CLI lo aplica antes de declarar cobertura, y el reporte publica `schema_enforced`.

## Hallazgo 9 MEDIUM — la suite verde no probaba los métodos, y falta la RED narrada

**Aceptado en ambas partes.**

Se añaden 21 tests de método en `tests/test_provenance_hardening.py`. La suite completa son 28 tests, todos verdes.

Sobre la evidencia RED: `provenance/commands/task01/red-hardening.log` conserva la RED de esta ronda, con su causa (`ImportError: cannot import name 'InvalidInput'`). **La RED concreta de `test_two_ids_cannot_map_one_logical_file` (`ValueError not raised`) se observó al reanudar pero no se guardó como log.** El revisor tiene razón: esa parte de la historia TDD **no está acreditada por un artefacto** y se rebaja a historia no verificada. No la reclamo como probada.

## Hallazgo 10 MEDIUM — entregables y enlace de registros

**Aceptado.** Creados `provenance/environment/pip_config_redacted.txt` con la ruta estable que exige el brief y `provenance/commands/task01/command.txt` con root y ejecutable absolutos, reproducible en proceso nuevo. Registrados `ART-101` a `ART-105` en `provenance/artifact_registry.csv`, sin reescribir los manifiestos originales.

## Hallazgo 11 LOW — identificadores de máquina sin política de publicación

**Aceptado, con acción diferida y declarada.** La evidencia contiene el nombre de cuenta `junio` y el identificador de paquete del sandbox. No son credenciales y parte de la evidencia absoluta la exige el protocolo congelado. Política registrada: la evidencia cruda se conserva **privada** y enlazada por hash; la proyección publicable, que sustituye los componentes específicos de cuenta y aplicación preservando OS/build, versiones e índices, se genera en TASK-10, que es la tarea que prepara la entrega. No se difiere en silencio: queda escrito aquí y en el registro de decisiones.

## Estado

| hallazgo | severidad | estado |
|---|---|---|
| 1 unicidad canónica | HIGH | CERRADO |
| 2 autorización de escritura | HIGH | CERRADO con residual TOCTOU declarado |
| 3 escritura externa del verificador | HIGH | CERRADO en código; disposición de los archivos pendiente del dueño |
| 4 clasificación de errores | MEDIUM | CERRADO |
| 5 totalidad de exit codes | MEDIUM | CERRADO |
| 6 redacción | MEDIUM | CERRADO |
| 7 aislamiento e integraciones | MEDIUM | CERRADO |
| 8 esquema del sidecar | MEDIUM | CERRADO |
| 9 tests y evidencia RED | MEDIUM | CERRADO en tests; historia TDD de una comprobación rebajada a no acreditada |
| 10 entregables y registros | MEDIUM | CERRADO |
| 11 política de publicación | LOW | ACEPTADO, ejecución en TASK-10 |

Evidencia fresca: 28/28 tests en verde; 11.137 fuentes verificadas con 0 discrepancias bajo unicidad canónica y esquema completo; contención de runtime `PASS` sin escapes y con las diez integraciones desactivadas. Logs en `provenance/commands/task01/`.

**TASK-01 no se declara cerrada por esta respuesta.** Vuelve a revisión independiente. Dos puntos quedan explícitamente abiertos y no deben darse por resueltos: el residual TOCTOU y la disposición de los tres archivos externos.
