# PROTOCOL-AMENDMENT-008 — Sede de cómputo Kaggle para M1

**Versión 8.** Responde a la ronda 7 (`reports/amendments/amendment-008-independent-review-round7.md`: NO APROBAR; HIGH 1, MEDIUM 2, LOW 1). Cuatro cambios: cada modo renderiza un solo experimento y cada línea del registro queda atada a él (H-03); un reintento exige la evidencia completa del intento anterior y la reconciliación recalculada idéntica a la comprometida (H-03); la reconciliación enumera todas las salidas de la plataforma y hashea también los artefactos parciales de un corte (N-07); y la reconciliación se escribe de forma atómica y se puede reanudar (NEW-M-01). Además, un `pip check` sano ya no bloquea (NEW-L-01). La ronda 7 cerró N-05 y N-06. **Versión 7.** Respondía a la parte A de la revisión de puerta de la ronda 6 (`reports/amendments/gate-review-exp-r01.md`: NO APROBAR; HIGH 1, MEDIUM 2, LOW 1). Tres cambios: una sola máquina de estados de intentos, idéntica en el código, el JSON y este texto (H-03, N-05); una regla para `pip check` y la evidencia de plataforma retenida byte a byte (N-06); y un recibo durable en cada etapa, con reconciliación de sesiones cortadas (N-07). La ronda 6 cerró H-02 y M-01. **Versión 6.** Respondía a la ronda 5 (NO APROBAR; HIGH 2, MEDIUM 3): raíz de confianza local para el manifiesto y el código (H-02), reglas exactas de intento y reintento (H-03), sonda de capacidad con modelo (M-01), evidencia de entorno (N-06) y registro ante fallos (N-07). La v5 era una reescritura: las v1 a v4 fueron rechazadas por revisión independiente (historial en §9). La v4 diseñaba controles para **datasets adjuntos y subidos a Kaggle**: validador de montajes, contrato de raíces, gramática de indirecciones, licencias de subida. La ronda 4 encontró que ese validador podía eludirse. La v5 elimina la superficie atacada en vez de parchearla: **no se sube ni se adjunta ningún dato**. Cada sesión descarga de una fuente pública fijada por commit sólo los archivos de su fase y verifica cada byte contra hashes derivados del manifiesto congelado antes de construir un modelo. Los encabezados dicen «responde a» porque el cierre lo decide la revisión (N-02).

## 0. Registro formal

| campo | valor |
|---|---|
| `amendment_id` | PROTOCOL-AMENDMENT-008 |
| `version` | 8 |
| `recorded_at` | 2026-09-23T12:00:00+00:00 |
| `base_protocol` | ALBUS26-116-PROTOCOL-001, commit `7d0f9985cce73740cfa2ae26154971b55282ad52`, JSON `6d5aa3ff47cba97f8ecd0dd15683bb96f0d53146f3af1ce1e95bf24cec7cbc8b`, MD `1a41b1aa684e26e5853aae31369c5200b29ae25a70bc383e3f0bd3ef136058be` |
| `modifica` | SPEC §7 «reconstruir la configuración … en entorno aislado dentro del workspace» y plan TASK-04 «proponer CPU si es el único dispositivo»: la sede de TASK-04 y de la inferencia de TASK-05 pasa a Kaggle |
| `no_modifica` | hiperparámetros, semillas, partición, selección de checkpoint, regla de umbral, evaluación única del test, estadística, reglas de detención (§7) |
| `test_observed_before_freeze` | true (heredado) |
| `user_decision` | DECISION-031 y DECISION-033: el usuario ordena el 2026-09-22 que todo entrenamiento y procesamiento se haga en Kaggle |
| `state` | **APPROVED** para el entrenamiento EXP-R01 (revisión de la ronda 8); la inferencia sigue bloqueada por §5 |
| `execution_permitted` | el entrenamiento EXP-R01 y las sondas no científicas de §6; EXP-V01 y EXP-R02 sólo con `inference_approved` tras la revisión de TASK-05 |

## 1. Motivo, sin sobredimensionarlo — responde a N-04

La CPU local es **viable** y el plan congelado la autoriza: 336 s por época medidos, unas 15 h para 150 épocas y unas 20 h con el factor 1,35 (DECISION-030). Kaggle **no es la única vía científicamente válida**. Es la sede que el usuario eligió por velocidad y que ahora exige (DECISION-033). El cambio sólo es admisible si Kaggle no debilita ningún control del protocolo congelado; §2 a §5 lo demuestran mecanismo por mecanismo.

## 2. Entradas: sin subidas, sin adjuntos — responde a H-02

**Fuente.** El corpus DATA-001 está versionado en el repositorio público `DANN-MAGE/SemilleroTI-Mangos`, commit `98614804dd967e19a77af9fc58c27364d2e43bc9`. Verificado localmente contra el manifiesto: las 669 imágenes son idénticas byte a byte. De las etiquetas, 465 son idénticas y 204 difieren sólo por LF→CRLF, que introdujo `core.autocrlf=true` en la copia local. Ninguna difiere en contenido (DECISION-033).

**Carga cerrada** (`src/evaluation/kaggle_job.py`, generada por `provenance/commands/task04/render_kaggle_job.py`). El kernel lleva un único `PAYLOAD` JSON con:

- `paths_digest`: SHA256 de la lista ordenada de las 669 rutas de imagen del commit. Otra lista aborta.
- `split`: un carácter por imagen en ese orden (`t` train, `v` valid, `x` fuera de fase). En una sesión de entrenamiento **las imágenes de test no se piden nunca**. El renderizador rechaza el payload si contiene la ruta, el nombre de archivo o el hash de un archivo de test.
- `files_digest`: SHA256 de las tuplas ordenadas (ruta, SHA256 de imagen, SHA256 de etiqueta en LF) de los archivos seleccionados. El renderizador exige antes que los bytes locales coincidan con el manifiesto.
- Digest oficial del checkpoint base, versión de Ultralytics, hiperparámetros congelados y el código del entrenador con su SHA256.

**Verificación en Kaggle antes de importar Ultralytics:**

1. `/kaggle/input` debe estar vacío: no hay datasets adjuntos que validar ni por los que eludir. Esto sustituye al validador de montajes de la v4 y a sus bypasses: prefijo de cadena, symlinks de directorio, campos de identidad opcionales y recursos declarados por el operador.
2. El árbol del commit se obtiene de la API de GitHub; un listado truncado aborta.
3. Cada archivo descargado se compara con el SHA-1 de blob git del árbol y, en conjunto, con `files_digest`. Si falla, se guarda un recibo con los hashes por archivo y el job aborta.
4. El `data.yaml` lo escribe el propio job, sin `test` ni `download`.

**Evidencia ejecutada:** la sonda `KAGGLE-PROBE-001` (§6) verificó las 669 imágenes y etiquetas y el checkpoint base. Tests: `tests/test_kaggle_job.py`, 13 casos, entre ellos que el script renderizado no nombra ninguna ruta de test y que un árbol truncado o un blob alterado abortan.

**Raíz de confianza — responde a H-02 de la ronda 5.** La ronda 5 demostró que la cadena de bytes no tenía raíz: el renderizador aceptaba cualquier manifiesto con su sidecar, y una fila de test cambiada a train (`SRC-009688`) pasaba todas las comprobaciones. Ahora la raíz es local, está comprometida en git y se comprueba dos veces:

1. **Antes de renderizar** (`check_bindings`): el manifiesto debe ser exactamente `data/manifests/model1_clean_manifest.csv` con el SHA256 del registro de congelación `data/manifests/model1_clean_manifest.freeze.json`. El manifiesto, su sidecar, el registro y esta enmienda tienen que estar comprometidos y sin cambios. Los SHA256 de `train_model1.py` y de `kaggle_job.py` deben coincidir con `approved_code` del JSON de esta enmienda: son constantes aprobadas, no autohashes del payload. Cambiar cualquiera de los dos exige nueva versión y nueva revisión.
2. **Después del run** (`verify_receipt`): el recibo debe nombrar exactamente los archivos de la fase del manifiesto congelado, con sus hashes, venir del payload renderizado y declarar el hash del código fuente realmente ejecutado. Kaggle ejecuta un kernel de script como una celda de notebook; el job lee el texto de esa celda y lo hashea normalizando sólo finales de línea. Además, `get_notebook_info` devuelve el código guardado por la plataforma, la versión y el digest de la imagen Docker; se registran junto al run.

Tests negativos (`tests/test_kaggle_job.py`): otro manifiesto con sidecar válido, el manifiesto correcto con otro hash, un entrenador cambiado con autohash coherente, un job cambiado, un recibo con un archivo de más o mal asignado y un recibo de otro código fuente.

**Límite declarado:** la red está activa durante la sesión, porque Kaggle no permite cortarla a mitad. Ultralytics se importa sólo después de todas las descargas, con `YOLO_OFFLINE=true` como en el runner local. La fuente de los gráficos se descarga antes y se registra su hash. El código ejecutado queda fijado por la versión del kernel en Kaggle y por su SHA256 local.

## 3. Checkpoint base y entorno

- **Base:** `yolo26n.pt` de la release oficial `ultralytics/assets` v8.4.0, digest publicado `sha256:9b09cc8bf347f0fc8a5f7657480587f25db09b34bf33b0652110fb03a8ad4fef`, 5.544.453 bytes. El mismo mecanismo de digest reproduce el hash ya registrado de ART-004 (`c62d41bf…bd7`), lo que lo valida. Se registra como **ART-106** al adquirirlo. El job rechaza además el hash del M1 entrenado.
- **Entorno medido por la sonda:** Python 3.12.13, torch 2.10.0+cu128, CUDA 12.8, 2× Tesla T4 de 15 GB, Ultralytics 8.4.52 instalado por versión exacta. El `pip freeze` completo y su hash quedan en el recibo.
- **Evidencia de entorno — responde a N-06.** Cada sesión guarda en `/kaggle/working/evidence/`, con salida estándar, errores y código de salida: `pip install --report` (orígenes y hashes de los paquetes instalados), `pip check`, `pip config list`, `pip debug --verbose` (etiquetas de plataforma), `pip freeze` y `nvidia-smi`; además, una lista blanca de variables de entorno sin secretos, cuDNN, el `data.yaml` usado y los ajustes de Ultralytics. `/tmp` guarda la vista de datos, el checkpoint base y la caché de Ultralytics: se reconstruyen por hash y el recibo conserva el hash de cada archivo, así que no hace falta conservarlos. 
**`pip check` y evidencia retenida — responde a N-06 de la ronda 6.** Un `pip check` con código 1 ya no se registra sin más. `pip_check_verdict` examina cada línea y bloquea en dos casos: si la línea no tiene la forma de un conflicto de pip, o si el paquete cuyo requisito falla está en el cierre de dependencias de `ultralytics`, `torch` y `torchvision`, calculado en la propia sesión con `importlib.metadata`. Si bloquea, el job aborta en la etapa `environment`, antes de descargar datos. Con código 0 sólo se aceptan una salida vacía o la línea de éxito de pip, `No broken requirements found.`; cualquier otra línea bloquea. En la sonda de capacidad, los seis conflictos eran de paquetes preinstalados que el pipeline no importa: bigframes, google-adk, google-colab, dopamine-rl y moviepy. La regla no existía entonces; rige desde EXP-R01. Cada intento retiene los bytes de `evidence/`, comprobados contra el recibo. Son las salidas y los códigos de salida de `pip install --report`, `pip check`, `pip config`, `pip debug`, `pip freeze` y `nvidia-smi`, más `data.yaml` y los ajustes de Ultralytics. `pip config` sólo muestra ajustes globales, sin credenciales. `platform.json` guarda lo que da la plataforma: estado, versión, lista de salidas y digest de la imagen Docker. La evidencia de la sonda de capacidad está retenida y comprobada byte a byte en `experiments/model1/KAGGLE-CAPACITY-001/evidence/`, y el renderizador rechaza EXP-R01 si falta o difiere (`capacity_retained`).
- **Diferencia declarada frente al entorno local reconstruido** (torch 2.12.0+cpu): torch, CUDA y precisión mixta automática de Ultralytics en GPU. Ultralytics 8.4.52 coincide. Se usa un solo dispositivo (`device='0'`); el run histórico usó `0,1`. EXP-R01 es un run nuevo, no una reproducción, y la coincidencia numérica con el histórico no se usará como evidencia (antes H-06).

## 4. Test de una sola vía — responde a H-03

El protocolo congelado exige que el test no intervenga en ninguna selección, que la evaluación sea única y que los accesos se registren (SPEC §6 y §7, `provenance/test_access_log.csv`). No exige custodio para la sede local. La v4 añadió un custodio que el proyecto no tiene y dejó la fase de test bloqueada. La v5 aplica a Kaggle **los mismos controles que a la sede local, más evidencia de plataforma que la sede local no ofrece**:

1. **Nada que seleccionar con el test.** El checkpoint lo fija el fitness de validación (máximo sin redondear, última época en empate). El umbral lo fija la rejilla F2 sobre predicciones de validación (`EXP-V01`). El evaluador es código versionado. La sesión de test no tiene ningún grado de libertad.
2. **Sello previo, verificable por bytes.** Antes de crear el kernel de test se hace un commit con `configs/evaluation_frozen.json` y su `.sha256`. El archivo contiene el SHA256 del checkpoint seleccionado y el umbral. También contiene los SHA256 del código que evalúa (`evaluate.py`, `intervals.py` y `kaggle_job.py`), el digest de la selección de test, el SHA256 del registro de selección de EXP-R01 y la versión de su kernel. El kernel de test lleva en su payload el SHA256 de ese archivo, verifica los bytes del checkpoint adjunto y aborta ante cualquier diferencia. El evaluador corre en local. Antes de puntuar o de calcular intervalos, `sealed_config` compara el archivo con tres cosas: los bytes del código, la selección de test recalculada desde el manifiesto y el registro de selección comprometido.
3. **Intentos y reintentos — responde a H-03.** Rige la máquina de estados de §6, la misma para EXP-V01 y EXP-R02. Hay un solo kernel de test, `albus26-m1-exp-r02`. Un intento de predicción es definitivo en cuanto escribe `predictions_raw.jsonl` y lo hashea en un recibo durable (`stage = predictions_written`). Se evalúan esas predicciones, y si después el intento falla o se corta, el fallo se declara junto al resultado. Antes de reintentar, el intento fallido se reconcilia y se añade a `test_access_log.csv` como `FAILED_BEFORE_PREDICTIONS`. Son **fallos del Gate E**, que se declaran sin sustituir el resultado, un segundo kernel de test y cualquier versión que la máquina no permita. La lista de kernels de la cuenta se guarda antes y después como evidencia de apoyo, **no exhaustiva**.
4. **Nunca por una métrica.** Un run completo con resultado desfavorable es el resultado.

**Límite declarado, idéntico al de la sede local:** no hay un custodio independiente. Un operador con control de la cuenta podría crear y borrar kernels. Ni el protocolo congelado ni esta enmienda afirman lo contrario. Kaggle registra la fecha de cada versión y la lista de kernels; la sede local no registra nada equivalente. El manuscrito lo declara como limitación.

## 5. Transferencia de predicciones — responde a M-02

El evaluador autoritativo será `src/evaluation/evaluate.py` (TASK-05). **La aprobación de esta versión habilita sólo el entrenamiento EXP-R01.** Las sesiones de inferencia (EXP-V01 y EXP-R02) quedan bloqueadas hasta que el evaluador esté implementado con tests y revisado de forma independiente. El mismo archivo, verificado por hash, correrá en Kaggle. Formato: una línea JSON por imagen con `image_id`, `sha256`, `label_sha256`, `group_id` y la lista de detecciones, que puede estar vacía. Cada detección lleva `class_id`, `score` y la caja `xyxy` en píxeles de la imagen original, post-NMS, con score ≥ 0,001. Esto resuelve la contradicción de la v4 entre detecciones múltiples y el `image_id` duplicado. El hash del archivo de predicciones va en un sidecar `.sha256`, nunca dentro del propio archivo. Las métricas se recalculan localmente con los mismos bytes y deben coincidir con tolerancia 1e-9. Hay una sola derivación de los registros, `evaluate.rebuild_predictions`. Exige que:

- `kernel.py` sea exactamente la renderización del job aprobado con su propio payload;
- el recibo pase `verify_prediction_run`, con los indicadores de ejecución comparados por valor exacto;
- el archivo crudo sea el que el kernel hasheó;
- la verdad de terreno salga de las etiquetas que fija el manifiesto.

La usa el constructor de predicciones, y la vuelven a ejecutar la congelación del umbral, la puntuación del test y los intervalos antes de usar los registros. Un registro de procedencia escrito aparte nunca se acepta por sí solo.

### 5.1 Alcance de inferencia — propuesta de la versión 9, responde a la ronda 4 de TASK-05

La aprobación de la v8 cubre sólo el entrenamiento y no cambia. Este apartado propone lo que la inferencia necesita; `inference_approved` sigue en `false` hasta que una revisión independiente lo acepte.

- **Raíz del intento — responde a HIGH-04 y NEW-HIGH-01.** Las predicciones de validación salen sólo de `experiments/model1/EXP-V01`, y las de prueba sólo de `experiments/model1/EXP-R02` (`attempt_root`). Se exige lo siguiente:
  - el registro `attempts.jsonl` termina en su único intento definitivo;
  - la reconciliación de ese intento, recalculada desde sus archivos, es idéntica byte a byte a la comprometida y a su línea del registro;
  - el registro y todos los archivos del intento están comprometidos en git sin cambios.

  El repositorio es la raíz de confianza, sin custodio independiente, como declara §4. Un conjunto de artefactos regenerado y rehasheado que no esté reconciliado y comprometido no pasa.
- **Autoridades del sello — responde a NEW-HIGH-03.** Antes de congelar el umbral deben estar comprometidos y sin cambios, en sus rutas canónicas: `configs/evaluation.json`, el manifiesto con su sidecar y su registro de congelación, el registro de selección de EXP-R01, esta enmienda y los tres archivos de código sellados. La enmienda debe estar `APPROVED` con `inference_approved` y el hash del job aprobado igual al del job del árbol. `sealed_config` repite esas comprobaciones antes de puntuar el test o calcular intervalos.
- **Evidencia exacta de ejecución — responde a MEDIUM-04 y NEW-MEDIUM-03.** Se comprueban por valor exacto `end2end = true`, los nombres `{0: Enfermo, 1: Saludable}` y los argumentos completos de la llamada a `predict`. El experimento del payload y del recibo debe ser el de la fase. Todos esos campos viajan en la procedencia.
- **Fallo después de las predicciones — responde a NEW-HIGH-04.** Un intento que hashea `predictions_raw.jsonl` en un recibo durable (`stage = predictions_written`) es definitivo. Sus predicciones se evalúan, y el fallo o corte posterior se declara junto al resultado (`receipt_status`, `receipt_error`).
- **Instantánea aprobada — responde a NEW-HIGH-03 de la ronda 5.** La aprobación de la inferencia queda ligada a bytes exactos. El JSON guarda en `inference_approval` el SHA256 de cada autoridad (`src/evaluation/authority.py`):
  - para M1: `configs/evaluation.json`, ya con las identidades de EXP-R01; el manifiesto, su sidecar y su registro de congelación; el registro de selección de EXP-R01; `evaluate.py`, `intervals.py`, `kaggle_job.py`, `authority.py` y `verify_kaggle_run.py`;
  - para M2: el manifiesto M2 y su sidecar, `predict_model2.py`, `intervals.py` y `authority.py`.

  Cada consumidor exige que esas autoridades estén comprometidas y sean idénticas a la instantánea. Un commit posterior que cambie cualquiera de ellas deja la inferencia sin aprobar hasta una revisión nueva.
- **Verificador — responde a HIGH-04 de la ronda 5.** `verify_kaggle_run.py` es una autoridad de la instantánea. `attempt_root` lo carga desde el árbol aprobado y sólo después de comprobar sus bytes; un verificador alterado, comprometido o no, se rechaza.
- **Productor de EXP-R03 — responde a NEW-HIGH-05 de la ronda 5.** `run_record.json` registra el SHA256 de `predict_model2.py`. Tras `evaluate --model-id model2 ...` se comprometen, como paso de promoción, `predictions.jsonl`, su sidecar y `run_record.json` de `experiments/model2/EXP-R03`, y sólo después se ejecutan los intervalos M2. Esos intervalos exigen la instantánea M2 aprobada, el paquete comprometido y sin cambios, y que el productor registrado sea el aprobado. Responde además a la ronda 6: el productor comprueba la aprobación de la instantánea M2 antes de leer ningún byte de prueba, exige `configs/evaluation_frozen.json` comprometido, y exige que Ultralytics 8.4.52 y torch vengan del intérprete y no de archivos del checkout. Tras la ronda 7, el entorno local forma parte de las dos instantáneas: `provenance/environment/inference_environment.txt` lista las 43 distribuciones instaladas. La aprobación exige el `.venv` de esta copia con exactamente esos paquetes (DECISION-036). `run_record.json` registra esos datos y los intervalos los comprueban.
- **Código importado y congelación de M1 — responde a la ronda 7 (NEW-HIGH-05 y NEW-LOW-01).** La aprobación verifica el código que se ejecuta, no sólo los nombres de los paquetes (`authority.check_environment`):
  - el intérprete base es el registrado en `provenance/environment/inference_interpreter.json`, autoridad de las dos instantáneas: `sys.base_prefix`, `sys.base_exec_prefix` y el `home` de `pyvenv.cfg` deben coincidir con él, y `sys.path` sólo puede contener el checkout (con su `.venv`) y la biblioteca de ese intérprete (ronda 12: un `python._pth` junto al lanzador añadía un directorio externo cuyo `csv.py` reescribía `sys.base_prefix`). Los archivos `._pth` cuentan como código;
  - no hay `PYTHONPATH`, `PYTHONHOME`, `PYTHONSTARTUP`, `PYTHONPLATLIBDIR` ni `PYTHONPYCACHEPREFIX`, ningún `sitecustomize` o `usercustomize` cargado o alcanzable en `sys.path`, en fuente o compilado, y sólo los buscadores de importación estándar; el site de usuario ya se rechaza aparte;
  - el checkout no tiene código importable sin versionar, ignorado o modificado (`.py`, `.pyw`, `.pyc`, `.pyo`, `.pyd`, `.dll`, `.so`), con la extensión comparada sin distinguir mayúsculas (ronda 9: Windows importa `csv.PYC` por `csv.pyc`). Los archivos se recorren en el disco, no se listan con git, que resume un repositorio incrustado sin versionar en una sola entrada (ronda 10); sólo se omiten el `.venv`, el bytecode nuevo y los directorios `.git`, y todo enlace simbólico o unión se rechaza sin seguirlo. Se admiten sólo las cachés de este intérprete que leería para una fuente versionada y que son esa fuente compilada (ronda 8: un `csv.pyc` sin fuente en la raíz se carga antes que la biblioteca estándar). Git se toma del `PATH`, nunca del checkout ni del `.venv`, porque Windows ejecuta antes un `git.exe` del directorio actual;
  - «comprometido y sin cambios» significa que los bytes del archivo son el blob de `HEAD`, calculado aquí, sin pasar por `git status` (ronda 9, NEW-HIGH-07): una entrada del índice marcada `assume-unchanged` o `skip-worktree` y el código añadido al índice sin commit se rechazan. Git se llama sin objetos de reemplazo, sin `fsmonitor` y sin variables `GIT_*`. Vale para la enmienda, las autoridades, los intentos, el paquete de promoción de EXP-R03 y el código del checkout;
  - cada archivo instalado de cada distribución coincide con el hash de su `RECORD`, y no hay código sin registrar en todo el `.venv`, cuya raíz también está en `sys.path` antes que site-packages. Toda caché del `.venv` que este intérprete leería es su fuente compilada, la liste `RECORD` o no, y también cuando la lista sin hash (`ruta,,`), como hace pip (ronda 11: un `.pyc` de `_distutils_hack` que carga al arrancar un `.pth` registrado); el resto del código debe figurar en un `RECORD` con hash. El SHA256 del `RECORD` de cada distribución queda en `provenance/environment/inference_runtime.txt`, autoridad de las dos instantáneas, y debe coincidir: un archivo sustituido junto con su `RECORD` cambia esa tabla (ronda 11). La identidad del entorno es el SHA256 de la tabla;
  - cada módulo cargado viene de la biblioteca del intérprete, de un archivo registrado de una distribución instalada o de una fuente de `HEAD` del checkout; el origen que declara coincide con el archivo que leyó su cargador y con su `__file__`; y el bytecode en caché del que pudo leerse es su fuente compilada. Un módulo sin ubicación sólo se admite si es interno, congelado, un paquete de espacio de nombres sobre directorios verificados, uno de los módulos de tiempo de ejecución de C o Cython, o lo creó un padre ya verificado: un módulo que borra su propio `__spec__` se rechaza;
  - las importaciones posteriores compilan desde las fuentes verificadas en un directorio de bytecode nuevo dentro de `provenance/runtime_state/pycache`, que se borra al salir, y tras importar se repite la comprobación anterior; Ultralytics y torch deben venir de archivos registrados de su propia distribución.

  El productor de EXP-R03 valida `configs/evaluation_frozen.json` con `sealed_config` de M1 antes de leer ningún byte de prueba: sidecar, umbral de la rejilla, manifiesto, código, selección de prueba y checkpoint de EXP-R01. `run_record.json` registra la identidad del entorno y el origen de Ultralytics y torch. Los intervalos M2 repiten la validación de la congelación y comparan esa identidad con la del intérprete. Las negativas del productor por el comando literal salen con código 2 y un mensaje, sin traza.
- **Comandos — responde a NEW-MEDIUM-02.** Los comandos literales del plan congelado siguen siendo la interfaz:
  - `evaluate --model-id model1 --config configs/evaluation.json --split val --run-dir experiments/model1/EXP-V01`;
  - `evaluate --freeze-operating-point --predictions experiments/model1/EXP-V01/predictions.jsonl --config configs/evaluation.json --out configs/evaluation_frozen.json`;
  - `evaluate --model-id model1 --config configs/evaluation_frozen.json --split test --run-dir experiments/model1/EXP-R02`;
  - `evaluate --model-id model2 --config configs/evaluation_frozen.json --split test --run-dir experiments/model2/EXP-R03`;
  - `intervals --predictions experiments/model1/EXP-R02/predictions.jsonl --groups data/manifests/model1_clean_manifest.csv --seed 42 --resamples 2000 --out artifacts/metrics/model1_intervals.json`.

  Con `--model-id model1`, el comando construye `<EXP>/predictions.jsonl` desde el intento definitivo y escribe `<EXP>/metrics.json`. Con `--model-id model2`, ejecuta la única inferencia local de EXP-R03. Antes de cada comando van los pasos de sede de §6: renderizado, ejecución en Kaggle, descarga, `verify_kaggle_run.py` y commit. `tests/test_evaluation.py` (`FrozenCommands`) ejecuta los comandos M1 e intervalos de extremo a extremo contra un repositorio sintético comprometido.

## 6. Capacidad — responde a M-01

La capacidad se demostró ejecutando, no declarando:

| capacidad | evidencia |
|---|---|
| cuota GPU | `get_accelerator_quota`: 108.000 s, 0 usados, renovación 2026-09-26 |
| crear y ejecutar kernel privado con GPU e internet | `KAGGLE-PROBE-001`, kernel 135462618, versión 1, `COMPLETE` |
| leer estado y salidas del kernel | `get_notebook_session_status`, `list_notebook_session_output`; recibo descargado |
| leer metadatos de dataset | `get_dataset_info` responde (el `datasets.get` denegado de la v4 ya no se reproduce) |
| crear datasets | **no disponible** en el MCP; innecesario con §2 |

`KAGGLE-PROBE-001` es una **sonda sin modelo**. Instaló el entorno, descargó y verificó las 669 imágenes y el checkpoint base, y no construyó ningún modelo ni hizo inferencia. Leyó bytes de test sólo para hashearlos, como la auditoría local, y consta en `test_access_log.csv` como `INTEGRITY_CHECK_NO_INFERENCE`. **Se ejecutó antes de aprobar esta versión, contra el texto de la v4 («cero ejecuciones»), a petición expresa del usuario de validar la viabilidad.** Se declara como desviación de procedimiento sin efecto científico.

**Tiempo de sesión — responde a M-01 de la ronda 5.** La documentación oficial de Kaggle (<https://www.kaggle.com/docs/notebooks>, consultada el 2026-09-23) fija 12 h por sesión de CPU/GPU. La v5 afirmaba que 150 épocas cabían «con holgura» sin medirlo; se retira. Antes de EXP-R01 se ejecuta la sonda de capacidad `KAGGLE-CAPACITY-001`, no científica: 3 épocas sobre el train/valid congelado, con la salida de validación silenciada y los pesos borrados al terminar. Nada de lo que mide puede informar ninguna selección. La regla está fijada en el código antes de medir (`capacity_verdict`): la primera época es calentamiento y se excluye, y la más lenta de las restantes se proyecta a 150 épocas con factor 1,35 más el tiempo de preparación. La sesión cabe si el total no pasa de 43.200 s. Registra además la memoria GPU pico asignada y reservada, el tamaño de las salidas y el disco libre. Si no cabe, TASK-04 queda `BLOCKED_BY_CAPACITY` y no se reduce la configuración.

**Resultado de `KAGGLE-CAPACITY-001`** (kernel `jorgesolanodev/albus26-m1-kaggle-capacity-001`, versión 2; `experiments/model1/KAGGLE-CAPACITY-001/`, verificado con `verify_kaggle_run.py`). El hash del código ejecutado, leído por el kernel en `/kaggle/src/script.py`, coincide con el renderizado (`8fe32e2a…c259`), y se verificaron 552 archivos de train/valid. Intervalos medidos: 46,56 s, 7,20 s, 6,98 s y 7,69 s. Ultralytics dispara `on_fit_epoch_end` también en `final_eval`, tras validar `best.pt` (`engine/trainer.py:859` de 8.4.52), así que el cuarto intervalo es esa evaluación final y no una época. La regla se aplicó tal como estaba escrita, sin cambiarla después de medir, y usó el máximo de los tres últimos intervalos: 7,69 s. Como la evaluación final dura más que cualquier época, la proyección resulta más conservadora de lo que la regla pretendía. Preparación 32,45 s. Proyección: 32,45 + 7,69 × 150 × 1,35 = **1.590,6 s**, el 3,7 % del límite de 43.200 s. **Cabe.** Memoria GPU pico: 2,58 GB asignados y 3,33 GB reservados, de 15 GB. Salidas del run: 17,0 MB; disco libre: 1,1 TB. La versión 1 falló en la etapa `download` sin construir modelo: el split se había transcrito a mano en el texto del kernel. `select()` lo detectó, y el hash del código ejecutado difería del renderizado (`attempt1/attempt.json`). La causa se corrigió en el renderizador (split por longitud de rachas), no en los datos. Por la etapa y la ausencia de salidas de modelo, el reintento cumple la regla de abajo. Pero la regla se escribió después, y el estado y el log de plataforma de la versión 1 no se retuvieron antes de reintentar; la plataforma ya no sirve las salidas de esa versión. Se declara como desviación de una sonda no científica. El `attempts.jsonl` de la sonda está reconstruido y lo indica en cada línea. La sonda también mostró un defecto: el job dejaba la fuente en `YOLO_CONFIG_DIR/` y Ultralytics la busca en `YOLO_CONFIG_DIR/Ultralytics/`, así que la descargó de nuevo durante el run. Está corregido antes de EXP-R01 y no afecta a la medida.

**Intentos y reintentos — responde a H-03 y N-05 de la ronda 6.** Una sola máquina de estados rige la sonda, EXP-R01, EXP-V01 y EXP-R02. Vive en el código (`RETRY_POLICY`, `retry_allowed` y `check_attempt` en `kaggle_job.py`), y el JSON de esta enmienda la copia literalmente; un test exige que sean iguales.

- **Un experimento por modo — responde a H-03 de la ronda 7.** El entrenamiento sólo renderiza `EXP-R01`; la predicción de validación, `EXP-V01`; la de prueba, `EXP-R02`; las sondas, `KAGGLE-CAPACITY-NNN` (`EXPERIMENT_OF` y `check_experiment` en `kaggle_job.py`). No hay un segundo espacio de nombres para el mismo entrenamiento. Cada línea del registro lleva modo y experimento, y una línea de otro modo o experimento bloquea.
- **Un intento, un directorio.** Cada versión del kernel es un intento y se renderiza en su propio directorio, `experiments/model1/<EXP>/v<N>/`, que nunca se sobrescribe.
- **Lo que se descarga — responde a N-07 de la ronda 7.** Tras cada intento se descargan **todas** las salidas que lista la plataforma. De la plataforma se guardan el estado, el log, la lista de salidas y el digest de la imagen Docker, en `platform.json` y `platform_log.json`.
- **Reconciliación.** `verify_kaggle_run.py` hashea cada archivo descargado. Marca como «atestiguado» el que coincide con el inventario del recibo, y como no atestiguado cualquier otro, por ejemplo un peso parcial escrito después del último recibo de una sesión cortada. Si falta una salida de la plataforma, sobra un archivo que la plataforma no lista, o hay recibo sin `job_log.txt`, se detiene. Escribe de forma atómica, en este orden, `reconciliation.json`, el sello de un run completo (`verification.json` o `selection_record.json`) y, al final, la línea de `attempts.jsonl`. Si se interrumpe, volver a ejecutarlo completa lo que falte, y exige que lo ya escrito sea idéntico al recálculo (NEW-M-01).
- **Cuándo hay una versión N > 1.** Sólo si se cumplen todas estas condiciones:
  - el registro y todos los archivos de la versión N−1 están comprometidos;
  - la versión N−1 conserva `kernel.py`, `render_record.json`, `platform.json`, `platform_log.json`, `receipt.json`, `job_log.txt` y `reconciliation.json`;
  - su reconciliación, recalculada desde esos archivos, es idéntica byte a byte a la comprometida, y su línea del registro coincide;
  - ninguna versión anterior es definitiva y N ≤ 3;
  - `retry_allowed`, recalculado, lo permite.
- **Cuándo lo permite `retry_allowed`.** Sólo si se cumple todo lo siguiente:
  - hay recibo con `status = FAILED` y la plataforma dice `ERROR`;
  - la etapa del fallo es anterior al modelo: `start`, `environment`, `download` o `base` al entrenar; `start`, `environment`, `download` o `predict` al predecir;
  - no hay ninguna salida de modelo (`.pt`, `epoch_records.jsonl`, `predictions_raw.jsonl`);
  - ninguna línea del log de la plataforma ni del job coincide con `mAP50|fitness|metrics/`.
- **Lo que nunca se reintenta.**
  - Una cancelación del operador, o cualquier estado de plataforma distinto de `ERROR`.
  - Una sesión cortada sin recibo `FAILED`, por corte duro o por límite de tiempo.
  - Un fallo ocurrido después de construir el modelo o de empezar a entrenar.
  - Cualquier cosa posterior a una versión `COMPLETE`.
- **El primer intento `COMPLETE` es el definitivo.** Nunca se elige entre dos entrenamientos terminados.
- **Si EXP-R01 falla sin poder reintentarse,** TASK-04 queda `BLOCKED` y se declara. No se relanza con otra configuración.

**Registro ante fallos — responde a N-07 de las rondas 6 y 7.** El recibo se escribe de forma atómica al empezar y en cada cambio de etapa. Lleva `status = RUNNING` y el inventario de hashes de todas las salidas que existen en ese momento. Al terminar se reescribe con `COMPLETE` o `FAILED`, el error y el inventario final. Un corte duro no ejecuta `finally`, así que deja el recibo de la última etapa alcanzada con `RUNNING`, y la máquina de estados lo trata como no reintentable. Todo lo que imprimen el job y Ultralytics va a `job_log.txt`, volcado línea a línea. Cada época se añade a `epoch_records.jsonl` y se vuelca a disco. `verify_kaggle_run.py` reconcilia cualquier intento, completo, fallido o cortado. Hashea todos los archivos que la plataforma devolvió, incluidos los parciales posteriores al último recibo, y distingue los atestiguados por el recibo de los que no. `evidence/` se retiene entero; un entrenamiento completo retiene además, atestiguados, `epoch_records.jsonl` y `selected.pt`. Tests:

- `tests/test_kaggle_job.py`: corte durante el entrenamiento, recibo atómico, experimento por modo y registro atado a modo y experimento.
- `tests/test_verify_kaggle_run.py`:
  - sesión sin recibo;
  - artefactos parciales tras el último recibo;
  - salidas no descargadas o no listadas;
  - recibo sin log;
  - evidencia ausente o alterada;
  - interrupción en cada escritura y reanudación;
  - reintento en un repositorio git temporal con otro espacio de nombres, otro modo, evidencia ausente, alterada o sin comprometer.

## 7. Invariantes que no cambian

Semillas (partición 42, entrenamiento 0, bootstrap 42). Hiperparámetros congelados (150/100/16/640/auto). Selección de checkpoint y verificación de sus bytes (`src/evaluation/train_model1.py`, el mismo archivo que corre en Kaggle, verificado por hash). Umbral F2 en validación. Una sola evaluación de test. Ningún test de software exige un mínimo de métricas. Las reglas de detención de la SPEC §11 siguen vigentes. El benchmark de TASK-06 **no** se traslada: REVIEW-07 pregunta por el Ryzen 5 7520U local, y medir otra CPU respondería otra pregunta.

## 8. Criterio de cierre

`APPROVED` sólo cuando una revisión independiente fresca no deje HIGH ni MEDIUM abiertos. La aprobación habilita EXP-R01; la inferencia requiere además el prerrequisito de §5. Hasta entonces sólo se permiten las sondas no científicas de §6. Todo registro de run cita el commit del freeze y esta enmienda con su versión.

## 9. Historial

| versión | revisión | resultado |
|---|---|---|
| 1 | `reports/amendments/amendment-008-independent-review.md` | NO APROBAR, HIGH 6 / MEDIUM 3 |
| 2 | `reports/amendments/amendment-008-independent-rereview.md` | NO APROBAR, HIGH 5 / MEDIUM 4, más N-01 y N-02 |
| 3 | `reports/amendments/amendment-008-independent-review-round3.md` | NO APROBAR, HIGH 2 / MEDIUM 3; cerró H-01, H-04, H-05, H-06, N-01, N-02 |
| 4 | `reports/amendments/amendment-008-independent-review-round4.md` | NO APROBAR, HIGH 2 / MEDIUM 2; cerró M-03/N-03 |
| 5 | `reports/amendments/amendment-008-independent-review-round5.md` | NO APROBAR, HIGH 2 / MEDIUM 3; cerró M-02 para el alcance de entrenamiento, N-04 y N-05 |
| 6 | `reports/amendments/gate-review-exp-r01.md`, parte A | NO APROBAR, HIGH 1 / MEDIUM 2 / LOW 1; cerró H-02 y M-01 |
| 7 | `reports/amendments/amendment-008-independent-review-round7.md` | NO APROBAR, HIGH 1 / MEDIUM 2 / LOW 1; cerró N-05 y N-06 |
| 8 | `reports/amendments/amendment-008-independent-review-round8.md` | **APROBAR para EXP-R01**, HIGH 0 / MEDIUM 0 / LOW 2 (NEW-L-02 y NEW-L-03, que no reabren ningún reintento ni cambian la selección) |

La v5 retira los artefactos de la v4 que sólo servían a la vía de subida y adjunto: `src/evaluation/kaggle_inputs.py`, `tests/test_kaggle_inputs.py`, `configs/kaggle_input_schema.json`, `configs/capacity_plan.json` y `configs/prediction_transfer_schema.json`. Siguen en el historial de git. H-05, sobre licencias y privacidad de las subidas, queda sin objeto porque no hay subidas.
