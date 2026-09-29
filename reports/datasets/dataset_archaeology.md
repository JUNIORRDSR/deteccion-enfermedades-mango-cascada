# Arqueología de datasets y splits — ALBUS26-116

Fecha del inventario: 2026-09-17. Raíz de las rutas relativas citadas: `C:/Users/junio/Downloads/mango-vision/`.

**Resultado:** hay tres familias de datos distintas: detección binaria mangoUnhealty v2, clasificación de cinco clases MangoDHDS y capturas propias anotadas únicamente como `mango`. No son intercambiables para demostrar diagnóstico de enfermedades específicas, detección temprana ni validación clínica en campo. La evidencia de archivos permite reconstruir los splits presentes y algunos antecedentes de fuga; no permite certificar independencia biológica ni declarar un split limpio.

## Alcance y trazabilidad

Lectura de archivos, etiquetas, configuraciones, código, notebooks y resultados históricos. Los SHA256 se reutilizaron de `ALBUS26_major_revision/provenance/source_manifest.csv`; no se recalcularon hashes de imágenes. No se decodificaron imágenes ni modelos, no se ejecutaron scripts legacy, no se hizo un nuevo análisis pHash, ni se generaron splits, entrenamientos, evaluaciones o benchmarks.

`data/manifests/legacy_dataset_inventory.csv` contiene una fila por archivo de imagen: DATA-ID, split, clases, geometría de anotación, ruta, SRC-ID y SHA256 del archivo y su etiqueta cuando existe. Son **7.016 archivos de imagen**, incluyendo copias entre representaciones; no son 7.016 observaciones independientes. `reports/datasets/inventory_legacy.py` deja reproducible la lectura estructural con stdlib y comprobaciones de consistencia. Solo escribe productos de arqueología autorizados.

Grados: **HIGH** = observado directamente en bytes/metadatos capturados o código; **MEDIUM** = enlace de procedencia o interpretación apoyado parcialmente; **LOW** = afirmación no demostrada con este material. HIGH para un nombre o etiqueta no implica alta certeza de un diagnóstico biológico.

## Registro de datasets

| ID | Ruta exacta relativa a la raíz | Archivos de imagen | Etiquetas `.txt` de imágenes | Papel observado |
|---|---|---:|---:|---|
| DATA-001 | `SemilleroTI-Mangos/docs/MangosDataset` | 669 | 669 | Roboflow `mangounhealty`, versión 2; detector binario |
| DATA-002 | `Mango-vision/MangoDHDS A Dataset of Diseased and Healthy Mangoe` | 1.500 | 0 | Fuente por carpetas y `Labels.csv`, cinco clases |
| DATA-003 | `Mango-vision/DatasetMango_YOLO` | 1.500 | 1.500 | Representación YOLO histórica de DATA-002; cajas de imagen completa |
| DATA-004 | `Mango-vision/DatasetMango_YOLO_clean` | 1.500 | 1.500 | Representación redividida presente, denominada `_clean` por el proyecto |
| DATA-005 | `Mango-vision/DatasetMango_YOLO_cls` | 1.500 | 0 | Layout de clasificación por carpetas; refleja DATA-004 |
| DATA-006 | `Mango-vision/DatasetMango_Propias` | 173 | 173 | Roboflow `mango-desease`, versión 1, clase única `mango` |
| DATA-007 | `Mango-vision/Datasets Sucios personal/Camara VIVO Y21` | 174 | 0 | Fotos sin etiquetas de enfermedad ni splits |
| DATA-008 | `Mango-vision/DatasetMango_Detector` | 0 | 0 | Directorio ausente; dataset Luigui Cerna solo documentado/configurado |

Conteos y presencia: HIGH. Licencias, origen Roboflow/Mendeley y propósito: evidencia documental local; no se verificaron servicios externos ni se descargaron datos. El README fuente de MangoDHDS remite a un DOI de Mendeley sin proporcionar un DOI concreto. Su título es “Mango Diseased Healthy Dataset”; el README de la aplicación usa también “Mango Disease Hybrid Dataset”, de modo que esa expansión del acrónimo no constituye identificación bibliográfica validada.

## Conteos por split y clase

### DATA-001: mangoUnhealty v2

Cada imagen tiene una etiqueta asociada. Las clases pueden coexistir en una imagen; por eso las columnas de imágenes por clase no son aditivas.

| Split | Imágenes/archivos label | Imágenes con Enfermo | Cajas Enfermo | Imágenes con Saludable | Cajas Saludable | Total cajas |
|---|---:|---:|---:|---:|---:|---:|
| train | 502 | 270 | 445 | 274 | 961 | 1.406 |
| valid | 134 | 79 | 124 | 64 | 225 | 349 |
| test | 33 | 13 | 13 | 21 | 86 | 99 |
| Total | 669 | 362 | 582 | 359 | 1.272 | 1.854 |

`data.yaml:5-13` fija `0=Enfermo`, `1=Saludable`, proyecto `mangounhealty`, versión 2. Las 1.854 líneas son de cinco tokens, compatibles estructuralmente con cajas YOLO; ninguna es caja de imagen completa. HIGH. Los porcentajes de archivos son aproximadamente 75/20/5; no deben sustituirse por 70/15/15, que corresponde al código de otra familia de datos.

### DATA-002/003/004/005: MangoDHDS

DATA-002 tiene 300 imágenes y 300 filas de `Labels.csv` por clase: Anthracnose, Bacterial Canker, Healthy, Scab y Stem End Rot. Son 1.500 filas en total. Las carpetas y la columna `label` coinciden. DATA-003 y DATA-004 tienen exactamente una anotación por imagen, siempre `class 0.5 0.5 1.0 1.0`: 1.500/1.500 cajas de imagen completa en cada representación. Esto acredita clasificación nominal por imagen, no localización de lesiones.

| Representación/split | Saludable | Antracnosis | Cancro_bacteriano | Costras | Podredumbre_Extremo_tallo | Total |
|---|---:|---:|---:|---:|---:|---:|
| DATA-003 train | 219 | 222 | 240 | 226 | 218 | 1.125 |
| DATA-003 valid | 62 | 63 | 48 | 65 | 62 | 300 |
| DATA-003 test | 19 | 15 | 12 | 9 | 20 | 75 |
| DATA-004 train / DATA-005 train | 214 | 212 | 211 | 212 | 215 | 1.064 |
| DATA-004 valid / DATA-005 val | 44 | 42 | 44 | 44 | 43 | 217 |
| DATA-004 test / DATA-005 test | 42 | 46 | 45 | 44 | 42 | 219 |

Por cada uno de los 1.500 nombres se comprobó igualdad de SHA256 y clase entre DATA-003, DATA-004 y DATA-005, y coincidencia de split DATA-004→DATA-005 después de renombrar `valid` a `val`. Las cuatro representaciones DATA-002 a DATA-005 contienen los mismos 1.400 hashes únicos, aunque tienen 1.500 archivos cada una. Son copias de un corpus, no cuatro validaciones independientes. HIGH.

### DATA-006/007: propias

| Split DATA-006 | Imágenes/labels | Líneas clase mango | Cajas de 5 tokens | Polígonos de 7 o más tokens impares |
|---|---:|---:|---:|---:|
| train | 121 | 1.074 | 419 | 655 |
| valid | 35 | 325 | 101 | 224 |
| test | 17 | 134 | 48 | 86 |
| Total | 173 | 1.533 | 568 | 965 |

Todas las líneas tienen clase `0=mango`. Hay 67 imágenes con solo cajas, 60 con solo polígonos y 46 con ambas geometrías. Las 965 líneas largas son polígonos compatibles estructuralmente con coordenadas normalizadas; **no son 965 etiquetas corruptas**. Un lector que exija siempre cinco tokens omitiría anotaciones válidas para segmentación. La combinación de geometrías debe resolverse explícitamente antes de cualquier evaluación de detección; aquí no se convirtió ni evaluó nada.

No se encontraron imágenes sin su label, labels huérfanos, clases fuera de rango ni coordenadas fuera de [0,1] en la lectura estructural final. Este control no prueba exactitud de las anotaciones, validez clínica, topología de polígonos ni compatibilidad efectiva con un cargador concreto.

`README.roboflow.txt:5,20-27` declara exportación el 19-04-2026 a las 05:22 GMT, 173 imágenes, autoorientación con eliminación de EXIF, resize 640×640 estirado y ninguna aumentación. Los 173 nombres normalizados corresponden a 173 de las 174 fotos DATA-007; el nombre sin correspondencia es `IMG_20260418_144416.jpg`. No hay hashes de bytes compartidos entre ambas versiones, compatible con una exportación transformada; la derivación por nombres y README es MEDIUM, no comparación de píxeles ni prueba de autenticidad de captura. DATA-007 no contiene vídeos en el manifiesto: 174 JPG.

El nombre `v1-test-externo` no vuelve externas las 173 imágenes por sí solo: el export conserva 121/35/17 train/valid/test. `external_test.yaml` no está presente. `integrate_external_test.py:34-70` usaría exclusivamente `test/images` en sus tres claves y validaría el primer token de clase; no certifica independencia, identidad de frutos ni diagnóstico.

## Duplicados y dependencia: evidencia preliminar

### Igualdad exacta de archivo

| Dataset | Hashes únicos | Grupos de archivos idénticos | Archivos en esos grupos | Pares entre splits |
|---|---:|---:|---:|---:|
| DATA-001 | 669 | 0 | 0 | 0 |
| DATA-002 | 1.400 | 100 | 200 | No aplica: sin split |
| DATA-003 | 1.400 | 100 | 200 | 41 |
| DATA-004 | 1.400 | 100 | 200 | 0 |
| DATA-005 | 1.400 | 100 | 200 | 0 |
| DATA-006 | 173 | 0 | 0 | 0 |
| DATA-007 | 174 | 0 | 0 | No aplica: sin split |

En DATA-003 los 41 pares exactos se reparten en 29 train–valid, 10 train–test y 2 valid–test. `exact_duplicate_pairs_preliminary.csv` contiene ambos SRC-ID, rutas y SHA256 para cada par, incluidos los pares dentro del mismo split. HIGH para igualdad de bytes. No se hallaron hashes compartidos entre DATA-001, MangoDHDS y propias; esto no excluye recodificaciones, recortes, escenas o frutos comunes.

DATA-004/005 mantienen los 100 pares exactos dentro de los splits: el script agrupa para asignar splits, pero **no elimina copias**. La ausencia de pares exactos entre splits no equivale a independencia de muestras. Un SHA256 diferente tampoco acredita independencia biológica.

### pHash histórico, no auditoría nueva

`Articulo/reports/leakage_pairs.csv` (SRC-000100, líneas 2-77) contiene 76 pares históricos de DATA-003: 55 train–valid, 18 train–test y 3 valid–test. Distribución de distancia: 60 pares con 0, siete con 2 y nueve con 4; involucran 139 nombres de imagen. Solo 41 de los 76 pares tienen además igualdad de SHA256; **pHash=0 no implica bytes idénticos**.

La tabla histórica permite localizar sus dos nombres y hashes presentes en DATA-004/005. Los 76 pares ahora quedan en el mismo split en esas representaciones. `historical_phash_pairs_current_locations.csv` conserva línea de la tabla legacy, distancia reportada y ubicaciones actuales. HIGH para esa reubicación de los pares ya reportados; MEDIUM para la fidelidad/ejecución original del cálculo histórico, que no tiene un manifiesto de entrada firmado junto a cada par. No se calcularon nuevos hashes perceptuales. Este resultado se limita a los 76 pares conocidos, no a todas las relaciones posibles.

### Nombres de vídeo, ráfagas y escenas

DATA-001 contiene **432** archivos con prefijo `sakit_mp4-####`: 329 train, 85 valid y 18 test. HIGH para los nombres; MEDIUM para que representen fotogramas del mismo vídeo, porque falta una tabla fuente→fotograma/escena/fruto. Estos nombres sostienen un riesgo concreto de dependencia temporal entre splits, aunque no haya bytes iguales. No se puede contar cada fotograma como un fruto independiente.

En DATA-001 también hay siete bases `freshMango` compartidas entre splits tras quitar el sufijo Roboflow y la extensión original codificada: `freshMango-29-`, `-182-`, `-211-`, `-214-`, `-215-`, `-22-`, `-25-`. La tabla de evidencia conserva los 14 archivos. Esta normalización une nombres `_jpg`/`_png`; es una pista de origen común, no una demostración de duplicidad visual.

DATA-006 contiene **90** imágenes con nombres de nueve ráfagas `IMG_20260418_..._Burst##`, correspondientes a nueve grupos de diez fotos en DATA-007. Las nueve ráfagas están repartidas entre train y valid; cinco también aparecen en test. Ejemplo `IMG_20260418_144501_Burst`: seis train, dos valid y dos test. `sequence_name_hints.csv` conserva el desglose completo. HIGH para el reparto nominal; MEDIUM para origen en una misma ráfaga real. Ni timestamps nominales ni ráfagas identifican por sí solos árbol, parcela, fruto o sesión de captura independiente. La fecha 2026-04-18 es inferida del nombre, no fecha EXIF verificada.

## Código de preparación existente y límites

- `dedup_and_resplit.py:76-99,108-176` lee etiquetas, toma la primera clase, calcula pHash y forma componentes union-find con Hamming <5. Usa la clase mayoritaria del componente para estratificar, `seed=42` y proporciones 70/15/15 **sobre componentes**, no sobre imágenes. Copia todos sus miembros conservando etiquetas. No usa ID de vídeo, fruto, escena, árbol, finca o fecha; no valida clínicamente clases ni resuelve conflictos de clase. Su existencia no demuestra la cronología de una ejecución.
- El código no exporta manifiesto de componentes ni asignaciones; sus nombres `_clean` y comentarios “sin fuga” son aspiraciones/afirmaciones legacy. La agrupación perceptual no sustituye un split por unidad biológica ni demuestra ausencia de duplicados fuera del umbral. El nombre de destino podría colisionar si hubiera nombres repetidos; los 1.500 nombres distintos presentes no muestran esa pérdida en esta copia.
- `dedup_and_resplit.py:187-189` copia `data.yaml` sin reescribirlo. El YAML en DATA-004 es byte a byte igual al de DATA-003 y conserva rutas `DatasetMango_YOLO/...`. HIGH. Consumirlo directamente podría apuntar al layout original dependiendo de resolución de rutas. `make_cls_layout.py:29-37,54-89` evita ese YAML y usa directamente DATA-004; no debe generalizarse que todo consumidor usa el dataset redividido.
- `make_cls_layout.py:44-51` omite destinos existentes; `train_cls.py:47-53` reutiliza el layout si `train/` existe y no está vacío. Por tanto, la configuración actual sola no demuestra cuál era el contenido usado en un entrenamiento anterior. En la copia presente se verificó correspondencia completa DATA-004/005; faltan snapshots inmutables de la ejecución histórica.
- `check_leakage.py:31-40,62-75` compara pHash entre splits sin metadatos de adquisición. `video_to_frames.py:38-59` filtra frames similares dentro de una invocación y escribe `frame_######.jpg`; no conserva en el archivo de salida un ID de vídeo ni índice original y no implementa partición por sesión/fruto. No se encontró aquí evidencia de que ese script haya generado las fotos propias.
- `download_roboflow.py:50-62` elige `versions[0]`, sin fijar una versión en config. DATA-008 está ausente, por lo que las cifras ~1.334 del README para Luigui Cerna no son un conteo local ni describen DATA-001. No mezclar “detector genérico mango de Luigui Cerna” con el detector binario mangoUnhealty v2.

## Cronología reconstruible

| Evidencia | Qué permite afirmar | Confianza y límite |
|---|---|---|
| Git Mango-vision `d0529f6`, 2026-04-17 23:09:01 −05 | Commit inicial en historial local | HIGH sobre metadato Git; no fecha de toma o entrenamiento |
| Git Mango-vision `e9ac0f4`, 2026-04-19 00:54:16Z | Commit describe scaffolding de cascada | HIGH sobre historia registrada |
| Export propio README, 2026-04-19 05:22 GMT | Fecha declarada del export de 173 imágenes | HIGH sobre texto; no fecha verificada de captura |
| Git Mango-vision `136930b`, 2026-04-19 02:19:08 −05 | Commit describe deduplicación y documentación del pipeline | HIGH sobre registro; no log de generación del split |
| Git SemilleroTI-Mangos `e1477b5`, 2026-04-20 17:43:05 −05 | Primer commit localizado para YAML binario y args de entrenamiento | HIGH sobre registro; no orden causal certificado entre entrenamiento/datos |
| `Articulo/reports/train_cls_log.txt:1,8-11` | Log histórico dice “layout existente ... se reutiliza” y enumera 1.064/217/219 imágenes, cinco clases; config registra `train_cls_50e`, seed 42 | HIGH sobre contenido; MEDIUM para enlace con datasets presentes por coincidencia de ruta/conteos, sin manifiesto de entrada del run |
| `SemilleroTI-Mangos/docs/Yolo26n-model-docs/Entrenamiento-1/args.yaml:1-5,38` | Config histórica `detect`, yolo26n, ruta Kaggle `/kaggle/input/datasets/jairoall/mangodataset/data.yaml`, 150 épocas y split val | HIGH sobre config; MEDIUM para equivalencia del dataset Kaggle con DATA-001, sin hash del upload |
| Cuatro notebooks `Mango-vision/notebooks/*.ipynb` | 19 celdas en total; cero outputs y cero execution_count no nulos | HIGH: son instrucciones sin resultados guardados |

Los `modified_utc` del manifiesto son timestamps de archivos locales y no se usaron como fecha de experimento. El log coincidente y los archivos presentes no demuestran por sí solos que la deduplicación precedió al entrenamiento concreto cuyos pesos se conservan. No se cargaron pesos para investigarlo.

## Ground truth y alcance científico permitido

| Dataset | Ground truth disponible | Qué falta |
|---|---|---|
| DATA-001 | Cajas con `Enfermo`/`Saludable` | Etiqueta de enfermedad concreta, severidad/estadio, confirmación fitopatológica y unidad independiente de adquisición |
| DATA-002 a DATA-005 | Cinco etiquetas nominales de enfermedad/salud por imagen | Verificación clínica/laboratorio, protocolo de anotadores, identificación de fruto/árbol/sesión; cajas de lesión reales |
| DATA-006 | Clase única `mango` con mezcla de cajas y polígonos | Salud/enfermedad, diagnóstico específico, estadio temprano, seguimiento y confirmación experta/laboratorio |
| DATA-007 | Fotos nominalmente propias, sin labels | Todas las etiquetas diagnósticas y metadatos de independencia |
| DATA-008 | Solo documentación/configuración | Corpus local, versión congelada, anotaciones y resultados |

Ninguno de los esquemas presentes incluye `Cenicilla` ni una variable de “temprano”. El README fuente de MangoDHDS alterna “Bacterial Black Spot” en su lista (`README.txt:9`) y “Bacterial Canker” en ejemplo/CSV (`README.txt:28`, `Labels.csv`); se conserva esta ambigüedad terminológica, sin resolverla por inferencia médica. “Enfermo” no permite contar antracnosis, bacteriosis y cenicilla por separado. Una anotación visual `mango` no es un diagnóstico.

La procedencia en Sabanalarga, identidad de frutos y existencia de confirmación experta son afirmaciones que requieren registros de adquisición/anotación. No están acreditadas mediante un manifiesto por observación en los datasets revisados. Confianza LOW para independencia biológica, enfermedad específica en DATA-001/006 y detección temprana; no significa que sean falsas, sino que faltan pruebas. La documentación técnica del proyecto menciona enfermedades específicas y pruebas de campo, pero el esquema y los archivos aquí inventariados no proporcionan ese ground truth.

## Evidencia fuente principal y productos

Los SHA256 completos y rutas de **cada imagen/etiqueta** están en el inventario; los del resto de fuentes están en `provenance/source_manifest.csv`. Anclas principales:

| SRC-ID | Ruta y localizador | SHA256 |
|---|---|---|
| SRC-009684 | `SemilleroTI-Mangos/docs/MangosDataset/data.yaml:5-13` | `1dfe8956ac17d8c6c0ca1bf44079a81309db9f69127e4132da76372567e57889` |
| SRC-000463 | `Mango-vision/DatasetMango_YOLO/data.yaml:1-6` | `55937229a90654f785b4110751a627f1587f728ae9ae7370abfa848fb3371a7c` |
| SRC-003464 | `Mango-vision/DatasetMango_YOLO_clean/data.yaml:1-6` | `55937229a90654f785b4110751a627f1587f728ae9ae7370abfa848fb3371a7c` |
| SRC-008141 | `Mango-vision/MangoDHDS A Dataset of Diseased and Healthy Mangoe/Labels.csv:1-1501` | `1cc1dd03a5796c77836cf8b31ab6dc1ad132d8405ccf10cf1d5d4070564d21eb` |
| SRC-008142 | `Mango-vision/MangoDHDS A Dataset of Diseased and Healthy Mangoe/README.txt` | `f1a62632a75ec06408db621a180afd048c0e568b4c3a410b12177ac22466015f` |
| SRC-000116 | `Mango-vision/DatasetMango_Propias/data.yaml:5-13` | `f3f3f033764bb5a37aa601810f995e0e4df33deb071d7aad52b67c2af58d6366` |
| SRC-000115 | `Mango-vision/DatasetMango_Propias/README.roboflow.txt:5,20-27` | `b77c23b0b022b9a6aa7af174efbcb60f9af7216b8065ba5d3c0977c40fa83cea` |
| SRC-000100 | `Articulo/reports/leakage_pairs.csv:1-77` | `2907313148e9286c553aa60d055627eb1c6fbae8670eb56eb7eda012da279f2b` |
| SRC-000101 | `Articulo/reports/leakage_summary.csv:1-5` | `8ffe7cfa1feef44975b7fd832ff31af5868cf68cdbc5e02f745f6309fa7fbce1` |
| SRC-000105 | `Articulo/reports/train_cls_log.txt:1,8-11` | `89d35310642c1a101106b48777dcbba8f3db1ae527350b6695d88a6c6c344ce3` |
| SRC-009653 | `Mango-vision/src/data_prep/dedup_and_resplit.py` | `88ddfa9fd1add9cfa5d9a85a5159bdf511d1a42d0a03394d538b90dc3d7b2a03` |
| SRC-009665 | `Mango-vision/src/training/make_cls_layout.py` | `56b78d05decd8c8b546913f336b525739142cdc922cd77f884754b47ee760639` |
| SRC-009666 | `Mango-vision/src/training/train_cls.py` | `f37b00e2e234156fcdc5536b24c897b75f838b9a733ad6b24d6d62d3c5e9a060` |

Productos derivados en `ALBUS26_major_revision/reports/datasets/`:

- `counts_by_split_class.csv`: conteos de archivos, anotaciones, cajas y polígonos por split/clase. En clasificación, “instances” significa etiquetas por imagen, no número de frutos.
- `exact_duplicate_pairs_preliminary.csv`: igualdad exacta de bytes con SRC-ID y rutas de ambos archivos.
- `historical_phash_pairs_current_locations.csv`: transcripción y localización de los 76 pares legacy, sin pHash nuevo.
- `shared_filename_bases_preliminary.csv`, `sequence_name_hints.csv`: pistas nominales, no agrupaciones biológicas validadas.
- `cross_dataset_matches_preliminary.csv`: intersecciones de SHA256 y nombres entre representaciones.
- `structural_issues.csv`: solo cabecera en la ejecución final, cero incidencias en el control limitado descrito.
- `inventory_summary.json`: resumen de conteos, duplicados exactos, pares históricos y notebooks.

Este informe no autoriza usar `_clean` como sinónimo de “libre de fuga”. Cualquier evaluación futura requiere fijar procedencia y unidad de partición, asegurar ground truth para la pregunta clínica y vincular el manifiesto concreto a cada ejecución. No se realizaron esos experimentos en esta fase.
