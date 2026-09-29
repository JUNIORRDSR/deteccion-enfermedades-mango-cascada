# Arqueología experimental y trazabilidad del código — ALBUS26-116

Fecha de auditoría: 2026-09-17. Alcance: lectura de artefactos locales, historial Git, código, notebooks, CSV, log y metadatos estáticos de checkpoints. **No se ejecutó entrenamiento, evaluación, inferencia, benchmark ni código legacy. Todos los experimentos tienen `reproduced=NO`.** Las cifras calculadas aquí son transcripción o aritmética de archivos preexistentes; no son una reproducción experimental.

Las rutas de este informe son relativas a `C:/Users/junio/Downloads/mango-vision`. El manuscrito sometido es `Articulo_Mango_ALBUS.pdf`, confirmado expresamente por el usuario el 17-09-2026 y vinculado a su SHA256; se leyó mediante `ALBUS26_major_revision/reports/submitted_candidate_text.txt`. No se recuperó un recibo binario de CMT. La diferencia de paginación del dictamen permanece documentada en genealogía. Los hashes y `SRC-*` se resuelven en `provenance/source_manifest.csv`, y los artefactos relevantes tienen además IDs `ART-*` en `provenance/artifact_registry.csv`.

## Resultado principal

Hay evidencia local de un entrenamiento **YOLO26n binario** y de un entrenamiento **YOLO11n-cls de cinco clases**, además de CSV y figuras de sus evaluaciones internas. Los dos modelos no deben confundirse con el detector genérico YOLO11n que permanece como código de una ruta distinta en `Mango-vision`. Las métricas principales de test tienen respaldo en CSV agregados, pero faltan predicciones por imagen, hashes asociados a cada ejecución de evaluación, fecha/comando exactos y manifiestos históricos de datos. Esto permite rastrear cifras; no permite certificar que una reevaluación de los pesos actuales las produciría.

La afirmación de integración de la cascada en FastAPI **contradice el flujo de llamadas del código disponible**. Las cifras de latencia de 145 ms, 0.18–0.6 s y <5/>5 s carecen de registros suficientes para considerarlas benchmarks verificables. Además, el temporizador de cascada existente excluye el dibujo de anotaciones.

## Registro de experimentos y estado

El registro completo, con todos los campos solicitados, está en `provenance/experiment_registry.csv`.

| ID | Evidencia existente | Relación con manuscrito | Estado |
|---|---|---|---|
| EXP-001 | `args.yaml`, 150 filas `results.csv`, `best.pt`, figuras | Modelo 1, Tabla 2, Tabla 4 y Figura 3 | Ejecución histórica respaldada; entorno incompleto; NO reproducida |
| EXP-002 | Código de `model.val` y CSV global/por clase | Modelo 1, Tabla 5, 33 imágenes/99 GT | Métricas agregadas existentes; vínculo exacto ejecución/pesos incompleto |
| EXP-003 | Matching explícito, matriz 3×3 y CSV P/R/F1 | Modelo 1, Figura 4 del PDF | Umbral distinto al de EXP-002; NO reproducida |
| EXP-004 | Log de entrenamiento, dos checkpoints idénticos, historial embebido de 27 épocas | Modelo 2, Tabla 3 y §4.2.2 | Ejecución histórica CPU respaldada; NO reproducida |
| EXP-005 | Código, matriz 5×5 y CSV por clase | Modelo 2, Tabla 7 y Figura 6 | Aritmética verificable; ejecución/pesos exactos incompletos |
| EXP-006 | Código y galería detector de nueve imágenes | Figura 5 del PDF | Evidencia cualitativa; no validación nueva |
| EXP-007 | Código de cascada, galería y 33 imágenes anotadas conservadas | Figura 7, §4.2.4 y afirmación de integración | Evidencia cualitativa; latencia sin benchmark; API contradictoria |
| EXP-008 | Texto del PDF: 145 ms CPU | Párrafo de latencia, página 9 | **Afirmación sin ejecución recuperada**, `UNVERIFIED` |
| EXP-009 | Texto del PDF: <5 s y >5 s Raspberry Pi 4 | Párrafo de latencia; §6.1/Tabla 8 | **Afirmaciones contradictorias sin ejecución recuperada**, `UNVERIFIED` |

EXP-008/009 se registran para impedir que las afirmaciones pierdan trazabilidad; no se presentan como experimentos cuya ejecución haya quedado demostrada. Los notebooks vacíos, las configuraciones propuestas y las variantes futuras no se cuentan como experimentos realizados.

## Cadena real de modelos, datos y código

### Modelo 1 publicado: YOLO26n binario

`SemilleroTI-Mangos/docs/Yolo26n-model-docs/Entrenamiento-1/args.yaml:1-26` documenta `task: detect`, `model: yolo26n.pt`, dataset Kaggle `/kaggle/input/datasets/jairoall/mangodataset/data.yaml`, 150 épocas, paciencia 100, batch 16, 640 px, `device: 0,1`, semilla 0 y optimizador automático. `save_dir` apunta a `/kaggle/working/runs/detect/train-2` (línea 110). No se encontró el notebook/script original de ese entrenamiento entre los archivos inventariados.

`models/best.pt` contiene literalmente las referencias `DetectionModel`, `yolo26n.yaml`, las clases `Enfermo` y `Saludable`, versión Ultralytics `8.4.39` y fecha embebida `2026-04-18T22:39:04.577835`. Esto respalda la identidad local YOLO26n sin cargar el modelo. La zona horaria y autenticidad externa de la fecha no están probadas por ese campo. No hay motivo documental para cambiar arbitrariamente el nombre a YOLO11.

El dataset local asociado es `SemilleroTI-Mangos/docs/MangosDataset`, con configuración de dos clases. La correspondencia binaria es `0=Enfermo`, `1=Saludable`, también escrita por `Articulo/scripts/evaluate_detector_test.py:36-44`. Un snapshot actual de datos no sustituye el manifiesto de las imágenes y etiquetas realmente usadas en Kaggle.

El historial CSV contiene 150 épocas y un tiempo acumulado final de 1281.61 s, consistente aritméticamente con ≈21.4 min. El checkpoint conserva un historial embebido completo; se transcribió de forma estática a `reports/experiments/SemilleroTI-Mangos_best_embedded_train_results.csv`. La presencia de dos índices de dispositivo no acredita por sí sola el modelo de GPU: **2×T4** queda como afirmación documental sin captura de hardware del entrenamiento recuperada. Python, PyTorch, CUDA/cuDNN y optimizador finalmente elegido quedan `UNVERIFIED` para EXP-001; los valores nominales de `optimizer=auto` no prueban qué algoritmo se ejecutó.

### Ruta distinta: detector genérico YOLO11n

`Mango-vision/src/utils/config.py` define `MODEL_DET="yolo11n.pt"`, semilla 42, 100 épocas y dataset `DatasetMango_Detector` de Luigui Cerna. `src/training/train_det_generic.py` reescribe el YAML a una sola clase `mango`, activa `cos_lr=True`, entrena y copiaría pesos a `models/detector_mango.pt`. `src/inference/infer_cascade.py:73-100` clasifica todos los recortes detectados, sin compuerta binaria `Enfermo`.

Esta ruta **no implementa la configuración del entrenamiento YOLO26n recuperado**: cambian arquitectura, dataset, clases, semilla, épocas y lógica de cascada. No se localizó su checkpoint final `models/detector_mango.pt`, su dataset de detector descargado ni un historial que acreditara su entrenamiento en el inventario. `notebooks/03_entrenamiento_det.ipynb` es una receta, con celdas sin contador ni outputs. No debe citarse como código exacto del experimento publicado.

### Modelo 2: clasificación YOLO11n-cls

`Mango-vision/src/training/train_cls.py` usa `src/training/make_cls_layout.py` y `src/utils/config.py`. La fuente del layout es `DatasetMango_YOLO_clean`; `valid` se convierte en `val`, la primera etiqueta asigna la carpeta de clase, y en Windows se copian archivos. `ensure_layout` reutiliza el layout existente; el log confirma esa reutilización. Por ello, la relación con la versión concreta de datos requiere los hashes del layout, no solo la existencia del script de preparación.

`Articulo/reports/train_cls_log.txt` registra Ultralytics 8.4.52, Python 3.13.13, torch 2.12.0+cpu, CPU AMD Ryzen 5 7520U, 1064/217/219 imágenes, batch 32, 224 px, semilla 42 y `train_cls_50e`. También registra AdamW con `lr=0.001111`, `momentum=0.9`, parada en época 27 tras 15 sin mejora y mejores resultados en época 12. El tiempo de 0.396 h y los 1424.05 s del historial son compatibles con los 24 min redondeados del manuscrito. Las líneas relevantes del archivo físico LF pueden localizarse con las cadenas `Ultralytics`, `optimizer:`, `EarlyStopping`, `27 epochs completed` y `Speed:`; contiene retornos de carro y ANSI de barras de progreso, por lo que diferentes lectores muestran distinta numeración visual.

La fecha embebida del checkpoint es `2026-05-24T17:00:24.164716`, versión 8.4.52 y arquitectura `yolo11n-cls.yaml`. Los dos archivos `Mango-vision/models/clasificador_enfermedad.pt` y `SemilleroTI-Mangos/models/clasificador_enfermedad.pt` son **idénticos por SHA-256**, no dos entrenamientos independientes. El checkpoint conserva las 27 filas de historial aunque el campo `epoch` está en −1 después de eliminación del estado de entrenamiento; la selección de época 12 se sostiene en el log, no en ese −1.

`Articulo/notebooks/train_cls_kaggle.ipynb` propone batch 64 y GPU `0,1`; no contiene ejecución ni salidas. Los cuatro notebooks de `Mango-vision/notebooks` tampoco conservan ejecución/salidas. No son prueba de entrenamiento en Kaggle del clasificador; el entrenamiento recuperado fue CPU. `Mango-vision/yolo11n-cls.pt` presenta metadatos de preentrenamiento ImageNet, fecha 2024 y versión 8.2.100; no es un tercer entrenamiento del proyecto.

## Hashes de los checkpoints y límites de procedencia

| Artefacto | Ruta | SHA-256 |
|---|---|---|
| ART-001 | `SemilleroTI-Mangos/models/best.pt` | `595fa3ea9b0670f63289529bde3333124ff1179588b52fbe16c9c454b6e488de` |
| ART-002 | `Mango-vision/models/clasificador_enfermedad.pt` | `e277717e6ca9d7f308d22697550a5a4e80613929acb68eeb790f3304ebfdb08e` |
| ART-003 | `SemilleroTI-Mangos/models/clasificador_enfermedad.pt` | `e277717e6ca9d7f308d22697550a5a4e80613929acb68eeb790f3304ebfdb08e` |
| ART-004 | `Mango-vision/yolo11n-cls.pt` | `c62d41bf9625777760018bf914d2e6cd472420ccd01706d97a61cb6c82502bd7` |

Los pesos se inspeccionaron mediante `zipfile` y `pickletools.genops`, sin `pickle.load`, `torch.load`, importación de Ultralytics/PyTorch ni construcción de objetos del checkpoint. Un decodificador limitado a primitivas transcribió `train_args`, `train_metrics` y `train_results`; rechaza instrucciones de construcción de objetos. Los opcodes íntegros y `checkpoint_static_metadata.json` preservan evidencia verificable de la lectura. La coincidencia de una ruta escrita en código no acredita que el mismo hash se usara en una ejecución histórica.

`SemilleroTI-Mangos` tiene HEAD `98614804dd967e19a77af9fc58c27364d2e43bc9`. El detector, argumentos e historial aparecen en el commit `e1477b53d7db3eede52f32904c07242153a65e8d` (2026-04-20); es el commit que incorpora artefactos, **no un commit probado de entrenamiento**. `core/cascade.py`, `run_cascade.py` y `models/clasificador_enfermedad.pt` estaban sin seguimiento. No se les atribuye HEAD ni otro commit. Había modificaciones previas de `.pyc` y de `mango_detecciones.db`, además de archivos sin seguimiento; se mantuvieron.

`Mango-vision` tiene HEAD `e7e59d1bce74a7ae12674f5b6068068681e691ce`; `train_cls.py` fue incorporado por `e9ac0f45057fc131c00737b6c90fd3b3fa05dc06`. El checkpoint del clasificador no está versionado. La receta de preparación fue cambiada por `136930b8e092b666aed208d56edcb42853dcbeef`. Ninguno de esos hechos identifica automáticamente el checkout usado en mayo. `Articulo` queda fuera de esos dos repositorios; sus scripts/figuras no tienen commit asignable por este inventario.

## Métricas: qué coincide y qué debe corregirse

### EXF-01 — Máximos de validación de épocas distintas

La Tabla 4 combina máximos de distintas épocas. Esto es verificable como resumen de una trayectoria, pero no como vector de resultados de un único checkpoint:

| Magnitud | CSV existente | Implicación |
|---|---:|---|
| Máximo mAP50 | 0.93174, época 95 | Redondea a 0.9317; no es el mAP50 de `best.pt` actual |
| Máximo mAP50–95 | 0.80478, época 137 | Coincide con `train_metrics` del checkpoint |
| Máxima precisión | 0.94734, época 101 | Otra época |
| Máximo recall incluyendo época 1 | 0.90552, época 1 | Mayor que el «mejor R» presentado en Tabla 4 |
| Recall excluyendo época 1 | ≈0.8731, época 88 | El script de figura excluye explícitamente época 1, pero la Tabla 4 no lo explica |
| Última época | mAP50=0.90977; P=0.92006; R=0.84827 | Coincide con los redondeos publicados |

`Articulo/figs/fig3_curvas.py:37-45` marca el máximo mAP50; las líneas 60–65 calculan resúmenes y excluyen época 1 para recall. El checkpoint tiene `train_metrics` P=0.92061, R=0.83326, mAP50=0.91607 y mAP50–95=0.80478, valores que corresponden a la fila de época 137. Identificarlo con esa época es una inferencia documental fuerte, no una reevaluación.

La discusión de una caída de ≈9 puntos, de 0.932 a 0.845, compara el máximo mAP50 de época 95 con test de los «mejores pesos». Si test usó el checkpoint actual asociado a época 137, la comparación homogénea sería 0.91607 frente al CSV test 0.8448387: ≈7.12 puntos. Debe aclararse el criterio de selección y la identidad de pesos antes de cambiar ese análisis; este informe no sustituye automáticamente la cifra por una nueva métrica.

### EXF-02 — Evaluación AP y matriz de confusión usan protocolos distintos

`Articulo/scripts/evaluate_detector_test.py:48-49` llama a `model.val` con `split=test`, `imgsz=640`, `conf=.001`, `iou=.6`. Los CSV conservados reproducen por **transcripción**, no por ejecución, los valores de Tabla 5:

| Métrica | Global/macro | Enfermo | Saludable |
|---|---:|---:|---:|
| mAP50 | 0.8448387283 | 0.8680678018 | 0.8216096549 |
| mAP50–95 | 0.7836653068 | 0.8342291814 | 0.7331014321 |
| P | 0.8836085982 | 0.8041404003 | 0.9630767961 |
| R | 0.7370304114 | 0.8461538462 | 0.6279069767 |
| F1 | No guardado globalmente | 0.8246123308 | 0.7601870613 |

El segundo bloque del mismo script, líneas 117–169, predice con **conf=.25**, IoU de supresión .6 y matching geométrico greedy por IoU≥.5. Su matriz tiene filas GT, columnas predicción y tercera categoría fondo:

```text
                 Enfermo  Saludable  Fondo
GT Enfermo          11       1         1
GT Saludable         3      61        22
GT Fondo             4      13         0
```

De ella resultan P/R/F1 de Enfermo = **0.6111/0.8462/0.7097**, y de Saludable = **0.8133/0.7093/0.7578**. El CSV `confusion_matrix_metrics.csv` concuerda. No se deben mezclar con P/R/F1 del primer bloque o con los umbrales de despliegue .5/.7. Los 99 GT son 13 Enfermo y 86 Saludable; los 17 FP de la fila fondo no son 17 imágenes ni verdaderos negativos. La suma de celdas extendida no define una accuracy estándar de detección.

No se guardan aquí predicciones por imagen para rehacer AP, curvas o matching sin inferencia. No hay evidencia de evaluación externa independiente en estos CSV: se usa el `test` interno del conjunto del detector. Su independencia biológica/geográfica no se deriva del nombre de carpeta.

### EXF-03 — Clasificador: consistencia de conteos y doble redondeo

`Articulo/scripts/evaluate_classifier.py:20-30` intenta primero un `best.pt` de `runs/classify/train_cls_50e`, y si falta elige una de las dos copias de `clasificador_enfermedad.pt`. No guarda qué hash resolvió. Las líneas 49–69 ordenan nombres de clase/carpeta y predicen imágenes completas a 224 px en CPU, sin rechazo por confianza. Las salidas guardadas son métricas agregadas y matriz; `y_conf` no se exporta.

La matriz existente suma 219 muestras, con diagonal 199: **199/219=0.9086757991**, compatible con top1=.909. Los soportes son 46/45/44/42/42 en orden Antracnosis/Cancro/Costras/Podredumbre/Saludable. Hay 6+6 confusiones Cancro↔Costras, verificables en el CSV.

El macro-F1 recalculado **solo desde la matriz guardada** es **0.9094733437**, que redondeado directamente a tres decimales es **0.909**. El CSV lo guarda primero a cuatro decimales (0.9095); volver a redondear ese valor produce 0.910. La cifra publicada 0.910 es explicable por doble redondeo. En revisión, las tablas deberían derivarse de valores no redondeados y declarar una precisión consistente. No altera el orden de desempeño entre clases, pero evita presentar redondeo como mejora.

El F1 de Cancro es 74/89=0.8314606742: redondea directamente a .831, mientras el CSV de cuatro decimales .8315 produce .832 al redondearse otra vez.

Los F1 exactos de Podredumbre y Saludable son 0.9761904762; redondean a .976. El detalle de la aritmética está en `reports/experiments/csv_arithmetic_check.json`. Esto no prueba ausencia de fuga de datos, exactitud diagnóstica de las etiquetas, independencia del test ni transferencia a recortes de campo: tales asuntos requieren la auditoría de datos y, eventualmente, un protocolo nuevo autorizado.

## EXF-04 — Cascada existente y API realmente conectada

En `SemilleroTI-Mangos/core/cascade.py:104-148` el detector produce clases binarias. Solo `cls_name == 'Enfermo'` entra al clasificador (línea 122). Los recortes tienen límites de imagen; `conf_cls` controla diagnóstico o `Enfermo_no_clasificado`. `Saludable` evita el clasificador. Si el clasificador no existe, el componente funciona con salida binaria (líneas 74–82). `final_conf` se asigna a la confianza del clasificador en líneas 139/142, no a un producto calibrado de probabilidades; la docstring que la llama «conf compuesta» no describe ese cálculo.

Callers comprobados de la cascada: `SemilleroTI-Mangos/run_cascade.py:15,103` y `Articulo/figs/fig7_cascade_demo.py:15,21`. La galería usa `conf_det=.5` y **`conf_cls=.35`**, no el default .4 (`fig7_cascade_demo.py:21-22`), semilla 7 y primeras nueve imágenes JPG tras shuffle. Su comentario dice «pool mixto», pero el código toma únicamente test del detector (líneas 24–28). No hay etiquetas por enfermedad fina en ese test binario que permitan computar desempeño de la cascada completa.

El flujo FastAPI disponible es:

```text
static/script.js:131
  -> POST /api/inference/process_image
  -> api/routers/inference.py:103-129
  -> core/vision.py:MangoVisionGenerator.process_image (39-68)
  -> self.model.predict (solo YOLO(models/best.pt))
  -> conteos sano/enfermo + results[0].plot + JPEG/base64 + SQLite
```

Para video, `core/vision.py:91-98` usa el mismo único modelo con `track`, BoT-SORT y `persist=True`; no aplica el Modelo 2. El objeto global de visión se instancia en `core/vision.py:137`, y el router lo importa en `api/routers/inference.py:7`. `core/config.py:25-27` fija conf=.70 y CPU. El historial real se expone en `/api/history/` (`api/routers/history.py:4-8`). `api/main.py:15-16` registra esos routers; no define `/predict`.

Por tanto, el texto §4.3 que afirma POST `/predict`, GET `/history` y API con cascada no corresponde al código actual. La docstring de `core/cascade.py:4-5` afirma uso vía `core.vision`, pero no existe tal import/call en `vision.py`. Recomendación editorial: describir por separado la API binaria y la cascada CLI/galería, o implementar y comprobar la integración en una fase posterior explícitamente autorizada. No se modificó el servicio para hacer coincidir retrospectivamente el manuscrito.

## EXF-05 — Hardware y latencia

| Afirmación | Evidencia local | Clasificación |
|---|---|---|
| M1 entrenamiento, 2×T4, ≈21.4 min | `device=0,1`, rutas Kaggle, CSV 1281.61 s; T4 solo en documentos | Tiempo respaldado por registro; GPU específica `UNVERIFIED` |
| M2 entrenamiento CPU Ryzen, ≈24 min | Log con CPU/entorno, 0.396h; historial 1424.05 s | Respaldada documentalmente, NO reproducida |
| M1 CPU, 145 ms promedio a 640×640 | Párrafo PDF, sin serie temporal/benchmark/log correspondiente recuperado | `UNVERIFIED` |
| Cascada, 0.18–0.6 s «end-to-end» con dibujo | Código temporiza `predict`, figuras muestran FPS; no tabla de tiempos ni repeticiones | Cifra `UNVERIFIED`; alcance descrito incompatible con timer disponible |
| Pi4, <5 s sin cuantización | Párrafo PDF y documentación antigua | `UNVERIFIED` |
| Pi4, >5 s sin cuantización; Tabla 8 menciona 832×832 | Limitaciones PDF | Contradicción interna no resuelta por datos |
| 8.4 ms inferencia por imagen en log M2 | Última validación de entrenamiento en CPU, con lotes | Dato de otra operación; no acredita latencia por imagen interactiva ni cascada |

`core/cascade.py:99` inicia `time.time()` y líneas 146–148 cierran el tiempo **antes** de `annotate` (línea 152). El timer incluye llamadas al detector y clasificadores secuenciales por fruto, recortes y preparación de la respuesta de detecciones. Excluye carga de pesos, lectura de archivo/captura de frame, `annotate`, codificación JPEG, escritura, red, frontend y SQLite. `run_cascade.py:35-37` dibuja después y aun así imprime el tiempo devuelto por `predict`. `fig7_cascade_demo.py:34-35` hace lo mismo. Ninguno implementa calentamiento, repeticiones, percentiles o un registro estructurado de latencia.

Las diferencias entre 145 ms, 0.18–0.6 s y varios segundos **podrían** reflejar componentes, número de frutos, hardware y resoluciones distintos. Eso no se puede convertir en explicación comprobada sin protocolos y registros. La referencia a 832 px aparece en la tabla de limitaciones, pero no rescata retrospectivamente el <5/>5 s ni demuestra una ejecución a 832. La base SQLite tampoco es una fuente de latencia por imagen: `api/routers/inference.py:115-122` guarda explícitamente `duracion_segundos=0.0` para imágenes.

Para una fase posterior se requerirían identidad de hardware/OS, versiones, hashes, resolución, número de frutos, batch, hilos, calentamiento, repeticiones, definición exacta del intervalo y tiempos por muestra. Este informe no ejecuta ni propone resultados de ese futuro benchmark.

## EXF-06 — Entorno y procedencia que aún bloquean reproducción

Los `requirements.txt` usan límites mínimos (`ultralytics>=8.3.0` en Mango-vision y `>=8.0.0` en Semillero), no versiones exactas. El requirements del directorio principal solo contiene matplotlib. Ninguno es una captura del entorno histórico de evaluación. La versión 8.4.39 embebida en M1 es la del guardado; no demuestra la versión usada al calcular sus CSV test. El log del entrenamiento M2 sí determina versiones de esa ejecución, pero no de toda evaluación/figura posterior. Tampoco se debe trasladar automáticamente la configuración del equipo actual a los experimentos antiguos.

Pendientes concretos para reconstrucción posterior:

1. Notebook/log original del entrenamiento M1, captura de GPU y versiones Python/PyTorch/CUDA; checkpoint base YOLO26n con hash.
2. Comandos y fechas de las evaluaciones M1/M2, hash de pesos resuelto en cada caso y manifiestos históricos de imágenes/etiquetas.
3. Predicciones por muestra con clase/score/caja e identificación de split que permitan auditar métricas sin reevaluar modelos.
4. Criterio explícito de selección del checkpoint M1 y comparación val/test de los mismos pesos; separar máximos por época de métrica final.
5. Distinguir `conf=.001` de evaluación AP, `.25` de matriz, `.5/.35` de galería y `.70` de API; ningún único punto operativo cubre los resultados actuales.
6. Evidencia real de benchmark y hardware para 145 ms, cascada y Raspberry Pi; mientras falta, marcar como preliminar no verificado o retirar la cuantificación.
7. Aclarar alcance de la API, galerías cualitativas y evaluación externa; la disponibilidad de código o datasets adicionales no prueba que se hayan evaluado.

Las posibles discrepancias de fuga, particiones, anotación y procedencia de imágenes se resuelven en el informe de datos; aquí no se certifica que `clean` esté libre de fuga solo por su nombre.

## Verificación de esta auditoría

Se ejecutó únicamente el lector propio `reports/experiments/inspect_existing_evidence.py` con biblioteca estándar, para hashes, opcodes y aritmética CSV, y `build_registries.py` para escribir registros en el directorio de revisión. Los checks verificaron 150 filas del detector, 219 celdas/muestras del clasificador, 199 aciertos en su matriz y hashes idénticos entre las copias del clasificador. `build_registries.py` comprobó IDs únicos, campos no vacíos y `reproduced=NO` en las nueve entradas. No se ejecutaron los scripts de entrenamiento/evaluación/figuras existentes ni se regeneraron figuras.

La inspección estática no transforma un CSV guardado en resultado reproducido ni elimina incertidumbre sobre el origen de ese CSV. Los registros conservan explícitamente `UNVERIFIED` para esos huecos.
