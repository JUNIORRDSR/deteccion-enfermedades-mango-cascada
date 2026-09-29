# Respuesta a la segunda revisión adversarial de TASK-01

Revisión: `reports/execution/task-01-independent-rereview.md`. Veredicto **REJECT**: 3 HIGH, 8 MEDIUM, 1 LOW, incluidos dos hallazgos nuevos.

El revisor ejecutó sondas reales contra la implementación y falsificó afirmaciones concretas del commit `3367672`. Todas se comprobaron antes de responder. **Ninguna se rechazó.**

## Lo que quedó falsificado, en sus propios términos

El commit afirmaba que los hallazgos estaban cerrados, que el exit 2 era total para entrada malformada, que toda escape falla y que la corrida de 11.137 filas probaba unicidad canónica. Las sondas de hardlink, root arbitrario, ADS, CSV malformado, codificación, `PYTHONPATH` externo y hash de registro falsifican esas cuatro afirmaciones. La afirmación defendible era más estrecha: **los bytes y filas actuales se verificaron; el validador y la puerta de evidencia estaban incompletos.**

## Hallazgo 1 HIGH — canonicalización de ruta no es identidad de archivo

**Aceptado.** El revisor lo demostró con dos hardlinks reales de `kernel32.dll`: `os.path.samefile` da verdadero y el par dispositivo/inodo coincide, pero `realpath` devuelve dos cadenas distintas. Mi comprobación los habría aceptado como dos SRC-ID.

Corregido con `file_identity(path)`, que devuelve `(st_dev, st_ino)` para archivos existentes y cae a la ruta canónica cuando no existen. `validate_locations` rechaza ahora dos SRC-ID que sean el mismo archivo físico. Test con `os.link` real, que se salta con motivo si el sistema de archivos no lo soporta.

El informe declara ahora **el método que realmente ejecuta** y sus límites: SUBST, unidades de red mapeadas, alias 8.3 y puntos de reanálisis no soportados **no se ejercitaron en este host y no se reclaman**.

## Hallazgo 2 HIGH — la autorización de escritura seguía siendo del llamante

**Aceptado, y era peor de lo que yo había entendido.** El revisor mostró que `check_output(Path('C:/Windows'), ...)` se aceptaba, que `authorized_root` sólo comprobaba que **existiera un archivo con ese nombre**, que `src/evaluation/provenance.py` se aceptaba como salida, y que `NUL:$DATA` y `provenance/protocol_freeze.json:evil` pasaban por ser flujos de datos alternativos de NTFS.

Corregido:

- `authenticate_root` comprueba el **digest** del freeze, no su nombre. Un archivo llamado igual con otros bytes ya no autentica nada, y hay test para eso.
- `check_output`, `create_run` y `configure_environment` autentican el root en cada llamada.
- Se rechaza cualquier parte con dos puntos, salvo el ancla de unidad, lo que cierra ADS y formas relativas a unidad.
- Política de salida real: `OUTPUT_SUBTREES` explícitos, `OUTPUT_FILES` para los dos registros, y `src/`, `tests/`, `.git/` y `.venv/` **nunca** son salida.
- Comparación de protegidos por identidad de archivo además de por ruta, así que un hardlink a un protegido tampoco pasa.
- `install_reconstructed.py` ya no confía en `Path.cwd()`: usa `authorized_root()` y `check_output`.

**Residual que sigue abierto y declarado:** la carrera check/use con puntos de reanálisis. `realpath` resuelve en el momento de comprobar; sustituir un directorio intermedio entre la comprobación y la escritura sigue siendo posible. Cerrarlo requiere un descriptor abierto revalidado o una estrategia no-follow.

## Hallazgo 3 HIGH — la prueba de contención seguía incompleta

**Aceptado parcialmente y corregido en lo verificable.**

- El revisor comprobó que los tres archivos externos siguen presentes con tamaños, mtimes y hashes coincidentes con `INCIDENT-001`, que las copias preservadas coinciden, y que no aparecieron cachés nuevas de matplotlib, torch o numba fuera del checkout. Registró el incidente como **materialmente honesto**.
- **`YOLO_OFFLINE=true` se fija ahora antes del import** en el modo con guarda. La sonda de red al importar pasa de `true` a **`false`** medido. Eso convierte la intención offline en algo comprobado, no descrito.
- Las diez integraciones remotas quedan en `false`, comprobado.

## Hallazgo N1 MEDIUM — el verificador informaba PASS con una escape registrada

**Aceptado. Es el mismo defecto que ya había tenido que corregir una vez, y volvió en otra forma.** El modo sin guarda registraba `datasets_dir` fuera del checkout y el informe global decía `PASS`, mientras el docstring y mi respuesta afirmaban «toda escape falla» y «sin escapes».

Corregido: las escapes esperadas del test negativo se nombran una por una en `EXPECTED_HAZARD_KEYS`; **una escape no nombrada hace fallar la puerta**. Al aplicarlo aparecieron dos que yo no había previsto, `weights_dir` y `runs_dir`, y el gate las atrapó. El informe publica ahora `containment_claim` con las escapes con guarda, las esperadas sin guarda, y una nota explícita de que `PASS` **no** significa que ninguna ruta escapara.

## Hallazgo N2 MEDIUM — registré un hash falso

**Aceptado sin atenuantes.** `ART-103` declaraba 902 bytes y un SHA256 que no corresponde: registré la fila y después recorté el salto de línea final del archivo sin volver a registrar. Un consumidor que siguiera el registro tendría que rechazar el artefacto. En un proyecto cuyo objeto es la procedencia, es un fallo de procedencia.

Corregido con `register_artifacts.py`, que regenera las filas desde los bytes exactos, rellena los campos que el resto del registro tiene no vacíos y enlaza cada artefacto con el comando que lo produce. Se añade un **test de integridad de todo el registro**, que ya atrapó una deriva real: tras regenerar `command.txt` y los informes, tres filas quedaron obsoletas y el test falló hasta re-registrar.

También se corrigió una colisión que yo mismo estaba a punto de crear: el script asignó `ART-106`, que la enmienda reservaba para el checkpoint base. Es la misma clase de error que `ART-005`. Ahora hay una **fila de reserva explícita** para `ART-106` y la sonda de CPU pasó a `ART-107`.

## Hallazgos 5 y 8 MEDIUM — CSV y esquema

**Aceptados.** El revisor mostró cuatro contraejemplos: bytes no UTF-8 con traceback y exit 1; un CSV sin las columnas requeridas con `KeyError` y exit 1; una cabecera duplicada colapsada en silencio; y una fila corta que produce `None`, que `str(None)` convertía en «no vacío».

Corregido con `read_rows`, que valida cabecera presente, sin duplicados, con las columnas requeridas y con **anchura exacta** por fila, y traduce errores de decodificación y de formato a `InvalidInput`. `require_schema` rechaza `None`, valores que no sean cadenas y celdas sobrantes. `validate_locations` exige el esquema por sí misma en lugar de confiar en que el llamante lo recuerde. Siete tests nuevos, uno por contraejemplo.

## Hallazgo 6 MEDIUM — formas de secreto no cubiertas

**Aceptado.** Seguían pasando `private_key`, `access_key_id`, `auth`, `Cookie: session=...` y el par estructurado `{'name': 'Authorization', 'value': 'Bearer abc'}`.

Corregido: la política de claves se amplía con límites por `_`, `-` o extremo, de modo que `access_key_id` y `session_token` coinciden y `author` no. `sanitize_obj` reconoce registros divididos nombre/valor. `sanitize_text` cubre `Cookie`, `Set-Cookie`, `Proxy-Authorization` y `Signature`.

## Hallazgo 7 MEDIUM — el proceso era certificable con imports externos

**Aceptado.** El revisor lanzó un hijo con `PYTHONPATH=C:\Windows` y `verify_environment` devolvió éxito.

Corregido: se valida que ninguna entrada de `sys.path` quede fuera del checkout, del intérprete o del árbol del propio módulo, y que **ningún módulo científico esté ya importado** antes de verificar. Más el `YOLO_OFFLINE` previo al import ya descrito.

Queda en pie su observación de que en este venv `site.ENABLE_USER_SITE` es falso aun sin `PYTHONNOUSERSITE`, así que esa comprobación **no demuestra** que la asignación tardía cause el aislamiento. No lo reclamo.

## Hallazgos 9, 10 y 11

- **9:** se añaden 19 tests nuevos, uno por bypass demostrado. Total 47, todos verdes. La historia RED de la ronda anterior sigue rebajada a no acreditada, y `red-round2.log` conserva la RED de esta.
- **10:** el registro usa ahora los campos no vacíos del resto de filas y enlaza cada artefacto a su comando; `command.txt` incluye la captura de entorno, la sonda de CPU y el registro, con la advertencia de que re-ejecutar la instalación reemplaza el entorno reconstruido.
- **11:** el revisor tenía razón en que «aceptado y diferido» no es cierre. Se crea `docs/research/evidence_publication_policy.md` como autoridad duradera: clasificación privada frente a publicable, reglas de sustitución determinista, enlace por hash y fallo cerrado. El generador y su test se implementan en TASK-10, y hasta entonces **no se publica nada** de `provenance/environment/`.

## Estado

47/47 tests verdes; 11.137 fuentes con 0 discrepancias bajo identidad de archivo y esquema completo; contención con guarda sin escapes, sonda de red desactivada y diez integraciones apagadas; registro íntegro comprobado por test.

**TASK-01 no se declara cerrada.** Vuelve a revisión independiente. Siguen explícitamente abiertos: el residual TOCTOU con puntos de reanálisis, los alias no ejercitables en este host (SUBST, unidades de red, 8.3), la disposición de los tres archivos externos, y la ejecución de la proyección publicable en TASK-10.
