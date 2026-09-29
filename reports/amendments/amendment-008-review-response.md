# Respuesta a la revisión adversarial de PROTOCOL-AMENDMENT-008

Revisión: `reports/amendments/amendment-008-independent-review.md`, SHA256 `a840c3a9becab09346fd80fbf102b4228271edaba7ce6038912e3d02d188501d`. Veredicto: **no aprobar**, 6 HIGH y 3 MEDIUM abiertos.

Los dos hallazgos factuales comprobables se verificaron de forma independiente antes de responder. **Ambos eran correctos y ambos eran errores míos.** Ningún hallazgo se rechazó.

## Lo que la revisión concedió, y que no me atribuyo como mérito

El revisor determinó por su cuenta que la reinterpretación de la cláusula congelada es **textualmente legítima**, que el freeze **no fue modificado** (comprobó los dos blobs contra el commit `7d0f998`), y que el estado `PROPOSED` **se respetó**: no hay notebook, versión de dataset, identificador de kernel, salida de `EXP-R01`, checkpoint descargado ni resultado de GPU en el rango revisado. Señaló además que `has_ever_run=true` en la sonda de cuota es historial de cuenta y no evidencia de que este protocolo se ejecutara. Lo registro porque delimita qué estaba bien y qué no.

## H-06 — marqué como OBSERVED algo que el registro dice UNVERIFIED

**Verificado y aceptado.** `provenance/experiment_registry.csv`, EXP-001, campo `hardware`, dice literalmente: `device=0,1 verified metadata; 2 x NVIDIA T4 / Kaggle claimed by PDF, hardware log UNVERIFIED`. Mi tabla de evidencia lo daba por observado. **Era falso.** Sólo el número de dispositivos es metadato verificado; el modelo concreto es una afirmación del manuscrito sin log.

Corregido en v2: la fila se declara «afirmado por el PDF, log no verificado», se retira toda afirmación de coincidencia de familia de acelerador, y EXP-R01 se declara **run reconstruido de novo**, no reproducción. Se añade el compromiso de no usar coincidencia numérica como prueba de reproducibilidad histórica ni discrepancia como prueba de inestabilidad.

**Hallazgo colateral que refuerza la enmienda, no que la debilita.** Al verificar ese campo encontré que el campo `dataset` de EXP-001 es `mangoUnhealty v2 via Kaggle /kaggle/input/datasets/jairoall/mangodataset/data.yaml`. **El entrenamiento histórico ya se ejecutó en Kaggle**, y eso procede de la configuración guardada del propio run, no del PDF. Kaggle no es una sede nueva: es la sede original. Lo incorporo como evidencia `OBSERVED` separada, sin mezclarla con la afirmación no verificada del modelo de GPU.

## H-04 — `ART-005` ya estaba ocupado

**Verificado y aceptado.** `provenance/artifact_registry.csv` línea 6: `ART-005` es el `args.yaml` histórico de `Entrenamiento-1`, vinculado a EXP-001. Mi propuesta habría creado **dos identidades incompatibles para un mismo ID**. El siguiente libre, tras registrar ART-101 a ART-105 en TASK-01, es **`ART-106`**, que es el asignado ahora al checkpoint base.

El resto de H-04 también aceptado: el checkpoint base se adquiere en un paso registrado aparte con URL, editor, versión, licencia, metadatos de respuesta, tamaño y SHA256; los bytes verificados van a una entrada inmutable; y **la red queda desactivada durante entrenamiento e inferencia**, en lugar de dejarla abierta «para bajar el checkpoint».

Sobre la asimetría del entorno que señaló el revisor: tenía razón. Exigir enmienda sólo si fallaba Ultralytics 8.4.52, mientras se aceptaba en silencio el torch/CUDA que trajera la imagen de Kaggle, era incoherente. v2 congela y registra la imagen, Python, todos los paquetes con hashes de build, torch/torchvision/CUDA/cuDNN, driver y topología **antes** del run.

**Dato medido que añado por relevancia directa:** Ultralytics ejecuta una sonda de red **al importar** (`ONLINE = is_online()`), confirmado como `ultralytics_online_probe_at_import: true` en la contención de TASK-01. Con la red desactivada falla de forma benigna, pero debe constar para que nadie lo lea como una conexión intencionada.

## H-01 — el registro de enmienda estaba incompleto

**Aceptado.** Faltaban marca de tiempo con zona, ID y hash del protocolo base, declaración explícita de exposición previa al test y de accesos nuevos, ID de decisión, identidad del revisor y hash de su informe, y el acompañante legible por máquina.

v2 añade la sección 0 con todos esos campos y el sidecar `PROTOCOL-AMENDMENT-008-kaggle-compute.json`. Queda declarado: `test_observed_before_freeze = true`, `new_test_access_since_freeze = false` enlazado al log, `DECISION-028`, revisor y hash del informe, y los recuentos de hallazgos. Se añade la obligación de que **todo registro de run cite el commit del freeze y la enmienda con su versión**; el que no lo haga no vale como evidencia del Gate E.

## H-02 — «cargas separadas más anti-unión de IDs» no aísla el test

**Aceptado íntegro. Mi mecanismo era insuficiente y el revisor enumeró exactamente por qué.** Una anti-unión por `image_id` no detecta un test renombrado, un duplicado exacto bajo otro ID, una fuga de etiqueta, un equivalente de grupo o secuencia, ni archivos no declarados en el montaje.

v2 sustituye la declaración por mecanismo: handles de dataset **fijados por número de versión**; carga de entrenamiento con sólo train y validación de M1, el checkpoint preverificado y un `data.yaml` **generado sin entrada `test`**; la carga de test **no se adjunta** hasta que exista el artefacto congelado del punto de operación; e inventario **fail-closed** de `/kaggle/input`, directorio de trabajo y cachés, verificando cada archivo por ruta relativa, hash de bytes, hash de etiqueta, `image_id`, `group_id` y split, y rechazando montajes extra y entradas de caché o de salidas previas.

Sobre el fallback `../` de Ultralytics al resolver el YAML: verificado en el código instalado. v2 exige resolver el YAML con el propio código de Ultralytics y **afirmar que toda ruta resuelta queda dentro del montaje permitido** antes de instanciar el modelo.

## H-03 — el mismo operador podía usar información del test

**Aceptado.** Es el hallazgo más incómodo y el más importante después de H-02, porque no se arregla con código sino con procedimiento verificable. Mi regla de reintento cubría sólo la interrupción por cuota, no la cancelación manual, el run completo con resultado poco atractivo ni el cambio motivado por el test.

v2: congelación en registro de escritura única, **antes** de adjuntar el test, de hashes de notebook, checkpoint, versiones de dataset, predicciones de validación, umbral, configuración, entorno y comando; ejecución **no interactiva**; conservación de **todos** los intentos, cancelaciones y fallos; criterios de reintento **técnicos** fijados antes de lanzar, con prohibición explícita de reintentar por una métrica; registro de cada acceso a salidas del test; y cualquier cambio posterior de selección dispara la regla de detención global, no un re-run.

## H-05 — permiso, atribución, privacidad y minimización no estaban establecidos

**Aceptado.** Apoyarme en «CC BY 4.0, luego puedo subirlo» era insuficiente: la licencia de un dataset no certifica que el publicador tuviera derechos sobre cada imagen fuente, y los propios registros del proyecto marcan la cobertura de DATA-001 como `PARTIALLY_SUPPORTED` y la identidad de DATA-004/005 sin resolver entre repositorio y espejo.

**El punto que más me faltó:** mis manifiestos congelados contienen `local_absolute_path`, así que subirlos tal cual habría revelado rutas locales y el nombre de cuenta, justo lo que la autorización prohíbe. v2 sube un **manifiesto saneado** con ruta relativa y hash.

v2 añade además manifiesto de egreso a nivel de archivo con titular, autoría, URL de origen y de licencia, avisos y modificaciones; resolución **bloqueante** de las lagunas de DATA-001 y DATA-004/005 antes de subir nada; carga mínima por fase; inspección y retirada de EXIF; registro del ajuste de privacidad y versión; y verificación final de la lista subida contra la permitida.

## M-01 — la cuota no prueba capacidad ejecutable

**Aceptado.** Una respuesta de cuota es un saldo en una fecha, no una asignación con modelo y número de GPU, memoria y límite de sesión; y además se renueva el 2026-09-26. v2 mantiene la capacidad **condicional** hasta un preflight sin datos de test que registre el acelerador real, y re-sondea la cuota justo antes de lanzar. Se **retira** la comparación «30 h frente a 21 min históricos», que presuponía el hardware no verificado.

## M-02 — GPU e estadística local exigen contrato de transferencia

**Aceptado, con la precisión del revisor.** No hay inconsistencia inherente: el puente son las predicciones, no el procesador que hace la aritmética. Lo que faltaba era el contrato. v2 lo fija antes de inferir: esquema y precisión completa sin redondeo, estado pre/post NMS, suelo de score, mapa de clases, IDs y hashes de imagen/etiqueta/grupo, hashes de checkpoint/config/manifiesto/entorno, cobertura total y por imagen, orden y desempates deterministas, versión de serialización y commit del código de métricas. Hash en Kaggle, verificación de los mismos bytes localmente, y toda la estadística derivada de esos bytes sin volver a inferir.

## M-03 — la CPU era la correcta, pero mi cita no lo probaba

**Aceptado, y el revisor fue más riguroso que yo.** Confirmó por sondeo del registro que el host **es** un Ryzen 5 7520U, y aun así marcó el hallazgo, porque el artefacto que yo citaba (`hardware.json`) sólo registraba `AMD64 Family 23 Model 160`, que no nombra el procesador. Presentar una inferencia como si el artefacto la probara es exactamente el defecto que este proyecto combate.

Cerrado midiéndolo y guardándolo: `hardware.json:cpu_identity` contiene ahora `ProcessorNameString = AMD Ryzen 5 7520U with Radeon Graphics`, 4 núcleos físicos, 8 lógicos, con el comando de sondeo y su exit code. La decisión de mantener el benchmark local queda sostenida por medición. Se conserva que será una **medición fresca**, no la recuperación de los 145 ms históricos, y que la Raspberry Pi sigue `BLOCKED_BY_HARDWARE`.

## Estado

| hallazgo | severidad | estado en v2 |
|---|---|---|
| H-01 registro de enmienda | HIGH | cerrado, sección 0 y sidecar JSON |
| H-02 aislamiento del test | HIGH | cerrado, mecanismo en lugar de declaración |
| H-03 grados de libertad del operador | HIGH | cerrado, procedimiento de una sola dirección |
| H-04 checkpoint, entorno e ID de artefacto | HIGH | cerrado, ART-106 y red desactivada |
| H-05 licencia, privacidad y egreso | HIGH | cerrado como requisito bloqueante previo a subir |
| H-06 relación con el run histórico | HIGH | cerrado, y con evidencia nueva de sede |
| M-01 capacidad | MEDIUM | cerrado, capacidad condicional |
| M-02 transferencia de predicciones | MEDIUM | cerrado, contrato fijado |
| M-03 identidad de la CPU | MEDIUM | cerrado, medido |

**La enmienda no se declara aprobada por esta respuesta.** Pasa a `PROPOSED_V2` y vuelve a revisión independiente fresca. Hasta que esa revisión cierre sin HIGH ni MEDIUM: **cero ejecuciones en Kaggle y cero subidas de datos.**

---

## Corrección posterior: la re-revisión encontró que me extralimité

La re-revisión independiente de la versión 2 (`amendment-008-independent-rereview.md`) devolvió **HIGH 5, MEDIUM 4**, cerró sólo H-04, y abrió dos hallazgos nuevos. El principal, **N-01 HIGH**, apunta a esta misma respuesta: mi afirmación de que «el entrenamiento histórico ya se ejecutó en Kaggle», presentada arriba como evidencia que refuerza la enmienda, **es una extralimitación**.

El revisor verificó que las rutas con forma de Kaggle existen de verdad, incluso en los opcodes del pickle y en la cadena `/kaggle/working/runs/detect/train-2`. Y aun así concluyó, correctamente, que una ruta guardada en una configuración no prueba dónde se ejecutó el entrenamiento: una configuración puede copiarse, reutilizarse o editarse, y el repositorio registra como ausentes el notebook, el manifiesto, la invocación, el entorno y el log de hardware.

Es exactamente el mismo tipo de error que yo estaba corrigiendo en H-06, sólo que en la dirección contraria. Queda retirado. La clasificación vigente es **circunstancial**, con la sede de ejecución **no verificada**, y la enmienda ya no usa ese argumento como justificación.

El segundo hallazgo nuevo, **N-02 MEDIUM**, señala que el sidecar declaraba los hallazgos cerrados antes de que la revisión lo aceptara. También correcto: el cierre lo determina la revisión, no el autor. El campo pasa a `claimed_remediation_pending_independent_review` y los encabezados dicen «responde a», no «cierra».

El detalle de los siete hallazgos que siguieron abiertos y su tratamiento en la versión 3 está en el propio documento de la enmienda. Estado: `PROPOSED_V3`, sin autorización de ejecución ni de subida.
