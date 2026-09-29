# Genealogía documental del manuscrito ALBUS26-116

Fecha de revisión: 2026-09-17. Investigación documental de solo lectura sobre fuentes legacy; no se entrenó, evaluó, compiló ni ejecutó código del proyecto. Las métricas citadas en este informe son afirmaciones observadas en los manuscritos, salvo la comprobación aritmética explícita de la matriz impresa. No equivalen a resultados reproducidos.

## Conclusión y fuente editable

**GENE-001 — SUPPORTED / HIGH.** El usuario confirmó explícitamente el 2026-09-17 que `C:/Users/junio/Downloads/mango-vision/Articulo_Mango_ALBUS.pdf` es exactamente el PDF enviado a CMT. Se adopta ese binario como manuscrito sometido, identificado por SHA-256 `68d9f231ca9f6de3f994d93cd112717de0072a117822792cdba7ababfb1a499d`. Tiene 16 páginas. La confirmación del usuario supera la condición inicial de «candidato»; no se ha inspeccionado un recibo CMT que contenga hash o el adjunto original. Su ausencia no invalida la confirmación, pero limita la corroboración independiente del envío.

**GENE-002 — SUPPORTED / HIGH.** La mejor fuente editable es `C:/Users/junio/Downloads/mango-vision/Articulo_Mango_ALBUS.docx`, SHA-256 `7a5918854107ce22eec0539bbb6f7c0962685897187e57e1dba2dbb2e570bc86`. La extracción de texto del PDF, sin cabeceras repetidas ni marcadores de página, coincide **exactamente** con la extracción del cuerpo OOXML después de normalizar Unicode NFKD, minúsculas y caracteres alfanuméricos: 33 468 caracteres, SHA-256 normalizado `9f80a981be79aeab9f9e068c1adc6e1639681aaaaf09e06cdd7c7a7a4920773e`. Las diferencias de tokenización son exclusivamente separación/unión de palabras y números de secciones. La normalización no comprueba puntuación, tipografía ni maquetación.

Los siete archivos `word/media/image1.png` a `image7.png` del DOCX son idénticos byte a byte a los siete recursos de `C:/Users/junio/Downloads/mango-vision/articulo_overleaf_v9_merge/images/`. El PDF mantiene los píxeles originales de Figuras 1 y 2; reescala y, en las fotografías, recomprime las otras cinco figuras. La octava imagen del DOCX es un recurso de plantilla, no una octava figura científica. Se inspeccionaron visualmente las siete figuras en las páginas 3, 6, 7, 8, 9, 11 y 12 del PDF.

**GENE-003 — INFERRED / HIGH.** `C:/Users/junio/Downloads/mango-vision/articulo_overleaf_v9_merge/` es la fuente LaTeX más próxima al contenido sometido y un respaldo de sus recursos gráficos, pero no reproduce su título ni su plantilla. Su `main.tex:3` declara IEEEtran, y `main.tex:7` conserva «Desarrollo de un Sistema de Detección Temprana…», mientras el PDF y DOCX usan «DETECCIÓN Y CLASIFICACIÓN EFICIENTE…». La conversión LaTeX→Word no está registrada; no se afirma un historial de edición demostrado. No copiar a `source/` ni reconstruir el manuscrito todavía.

Los metadatos corroboran compatibilidad temporal, sin demostrar autoría ni envío: el PDF declara Microsoft Word y creación 2026-08-30 19:22:16 −05; el DOCX declara modificación 2026-08-31 00:22:00Z, equivalente al mismo minuto. El creador heredado «Luis Camacho» no sustituye los autores impresos; `lastModifiedBy` dice «Jorge Junior Solano Romero». El PDF conserva encabezados de plantilla «Author | short title» y pie «ALBUS 2025, 3, x».

## Alcance, evidencias y límites de comparación

Raíz de fuentes `R = C:/Users/junio/Downloads/mango-vision/`. Raíz de evidencias `E = C:/Users/junio/Downloads/mango-vision/ALBUS26_major_revision/reports/genealogy/`. En las tablas siguientes, `R + ruta` y `E + archivo` son expansiones literales a estas rutas absolutas. `archivo.zip!miembro` identifica contenido leído en memoria, no un archivo extraído a legacy.

Se inspeccionaron los índices de 10 ZIP de artículo antes de leer sus miembros: 163 entradas y ninguna ruta insegura detectada por la comprobación usada. No se ejecutó `extractall`. `img.zip` no se abrió: no es un paquete de manuscrito y los recursos necesarios estaban en las versiones de artículo. Se compararon cuatro DOCX de artículo, dos PDF y cinco árboles de fuentes LaTeX, además del Markdown `R + Articulo/Articulo_Mango_IEEE.md`. No se leyeron ni ejecutaron scripts legacy para esta genealogía. RTK.md no estaba disponible en las rutas revisadas por el coordinador; no se inventó su contenido.

Evidencias guardadas:

- `E + zip_indices.csv`: índices, tamaño, CRC y fecha interna declarada de cada miembro; las fechas ZIP no demuestran fecha de creación científica.
- `E + file_hashes.csv`: 272 registros de hashes de documentos, recursos y miembros inspeccionados; complementar con el manifiesto central `R + ALBUS26_major_revision/provenance/source_manifest.csv` para el inventario global.
- `E + archive_directory_file_hash_comparison.csv` y `verified_relationships.json`: igualdad exacta de miembros ZIP/carpeta, texto normalizado y figuras DOCX/v9.
- `E + version_deltas.json`, `archive_directory_deltas.json` y archivos `*.diff`: diferencias textuales unificadas entre versiones consecutivas nominales y entre ZIP/carpeta. Los `@@` preservan localizadores de línea de cada fuente.
- `E + figure_references.csv`, `caption_references.csv`, `image_hashes.csv`, `bibliography_keys.json`: mapas de recursos, captions, dimensiones, hashes y claves bibliográficas.
- `E + pdf_Articulo_Mango_ALBUS.txt`: texto con marcadores de página. `E + docx_Articulo_Mango_ALBUS.txt`: párrafos/celdas OOXML consecutivos numerados; sus números no son páginas Word.
- `E + pdf_docx_normalized_differences.json` y `text_similarity.json`: diferencias de tokenización y ranking exploratorio. La similitud LaTeX/PDF está afectada por comandos, orden y bibliografía; no es una probabilidad de procedencia.
- `E + verify_relationships.py`: comprobación documental ejecutada con éxito; afirma igualdad del texto normalizado y correspondencia única de las siete figuras. No ejecuta código legacy.

No hubo nueva auditoría de datos, comprobación de licencias en la web, revisión de checkpoints ni validación de las referencias contra sus publicaciones originales. La genealogía permite localizar afirmaciones y cambios, no certifica su verdad experimental. No se renderizó de nuevo el DOCX ni se compiló LaTeX; la concordancia Word/PDF se apoya en texto, imágenes, metadatos y el PDF existente.

## Relación entre paquetes y carpetas

**GENE-004 — OBSERVED / HIGH.** El nombre de una carpeta no garantiza que siga siendo la extracción del ZIP homónimo.

| ZIP bajo R | Carpeta bajo R | Miembros idénticos byte a byte | Diferencias observadas |
|---|---|---:|---|
| `articulo_deteccion_temprana_de_enfermedades_mango.zip` | `articulo_deteccion_temprana_de_enfermedades_mango/` | 3/16 | Cambian las siete imágenes, cinco secciones y biblio; no es una copia fiel del ZIP inicial. |
| `articulo_overleaf_v7.zip` | `articulo_overleaf_v7/` | 12/16 | Cambian métodos, resultados, conclusión y bibliografía. |
| `articulo_overleaf_v8.zip` | `articulo_overleaf_v8/` | 16/16 | Copia fiel de todos los miembros del ZIP. |
| `articulo_merge_docente_v9.zip` | `articulo_overleaf_v9_merge/` | 17/17 | Copia fiel, incluido IEEEtran.cls. |
| `Articulo/articulo_mango_overleaf.zip` | `Articulo/latex/` | 18/18 | Copia fiel de todos los miembros del ZIP. |

Las fuentes textuales de las carpetas `articulo_deteccion_temprana_de_enfermedades_mango/` y `articulo_overleaf_v7/` son iguales entre sí, aunque ambas difieren de sus ZIP. La comparación se limita a los miembros inventariados; igualdad de texto no implica fecha ni dirección de copia. El ZIP v9 tiene SHA-256 `4804d26107e62f52f8c8b5c528be35974f19d8711041f1417fd5a326fab16615`.

## Evolución del contenido, métodos y métricas

El orden siguiente expresa similitud y progresión nominal observada, no un historial Git ni una secuencia de edición probada. Los manuscritos anteriores al PDF confirmado son antecedentes/candidatos, no envíos CMT confirmados.

| Fuente bajo R | Diferencia relevante frente a las posteriores | Confianza |
|---|---|---|
| `Articulo/Articulo_Mango_IEEE.md:12` y `:36` | Describe el Modelo 2 como implementación parcial y métricas finales aún en evaluación; identifica MangoDHDS con Mendeley; resumen del detector con mAP .932/.800, P .916 y R .858. Contiene seis autores en línea 3. | HIGH, texto observado. |
| `Articulo/Articulo_Mango_IEEE.docx` | Mantiene detector «propio» y referencia de MangoDHDS en Mendeley; tiempo CPU aproximado 1.2 s en Intel i7. No es la versión sometida. | HIGH. |
| `Articulo/Articulo_Mango_IEEE_v2.docx` | Incluye test detector mAP .845, reparto limpio 1064/217/219 y 1337 clusters; Modelo 2 se describe como entrenado 50 épocas, pero remite resultados detallados a reportes. CPU pasa a Ryzen 5 7520U y 145 ms. | HIGH. |
| `Articulo/Articulo_Mango_IEEE_v3.docx` y `.pdf` | Ya explicita Modelo 2 top-1 .909, macro-F1 .910, test 219; parada época 27, mejor época 12. El PDF tiene 8 páginas, fecha Word 2026-05-24 y hash `b1e2da637aea3e25a26837c4f7a90780cdc65129782798bace71320f42ba369c`. | HIGH para contenido, MEDIUM para relación cronológica. |
| `articulo_deteccion_temprana_de_enfermedades_mango.zip` | Hereda cifras .932/.845 y clasificador .909/.910; resumen aún P .916 y F1 detector .79. 15 entradas bibliográficas. | HIGH. |
| `articulo_overleaf_actualizado.zip` | Reestructura resumen y amplía discusión/limitaciones. Conserva principales métricas y P .916 en resumen. | HIGH. |
| `articulo_overleaf_v3.zip` | Cambia P del resumen a «precisión máxima .947», explicita formato/captions y revisa bibliografía. No equivale a cambio demostrado de experimento. | HIGH. |
| `articulo_overleaf_v4.zip` | Incorpora justificación del umbral pHash y la afirmación de inspección visual de 76 pares. Reemplaza la referencia sobre pérdidas agrícolas por Savary. | HIGH. |
| `articulo_overleaf_v5.zip`, `v6.zip` | Texto .tex/.bib idéntico a v4; los cambios corresponden a recursos gráficos. Diffs textuales vacíos conservados. | HIGH. |
| `articulo_overleaf_v7.zip` | Normaliza YOLOv26n→YOLO26n y redacción de pérdidas agrícolas. Todavía describe el detector como conjunto propio. | HIGH. |
| Carpetas base y v7 | Añaden procedencia de terceros, fuentes de imágenes y tres entradas bibliográficas adicionales; no son el contenido del ZIP v7. | HIGH. |
| `articulo_overleaf_v8.zip` y carpeta v8 | Detector pasa explícitamente a mangoUnhealty v2 de terceros, 432+200+27+10 imágenes; añade disponibilidad y fuentes de figuras; distingue Mango Disease, 1019 imágenes, como conjunto no usado. 17 referencias. | HIGH. |
| `articulo_merge_docente_v9.zip` y carpeta v9 | Resumen comentado elimina las cifras de rendimiento visibles en v8; añade seis referencias y reorganiza citas. Conserva cifras en resultados/conclusión. 23 entradas. | HIGH. |
| `Articulo_Mango_ALBUS.docx` y `.pdf` | Nuevo título, tres autores, plantilla ALBUS y referencias autor-año; resultados/métodos y recursos gráficos corresponden estrechamente a v9. Texto normalizado DOCX/PDF idéntico. | HIGH. |

**GENE-005 — OBSERVED / HIGH.** Las cifras centrales del artículo sometido ya aparecen en versiones previas; no se observa en esta genealogía un nuevo experimento que las respalde. En PDF p.7, Tabla 4 reúne máximos de épocas diferentes: mAP@.5 .9317 en 95, mAP@.5:.95 .8048 en 137, P .9473 en 101 y R .8731 en 88. Por ello, el cambio del resumen .916→«máxima .947» debe interpretarse como selección/redacción de estadísticos, no como prueba de que un mismo checkpoint tenga todos esos máximos.

El PDF p.4 afirma pHash de 64 bits, distancia <5, union-find, división 70/15/15, semilla 42, inspección visual de 76 pares y cero pares entre splits después de regenerar. PDF p.10 añade 1064/217/219 y 1337 clusters. Son afirmaciones de método a contrastar con la auditoría experimental separada, no comprobaciones realizadas aquí. Fuentes próximas: `R + articulo_overleaf_v9_merge/secciones/02metodos.tex:45`, `:49`, `:51`; `secciones/04Resultados.tex:116` y `:117`.

**GENE-006 — OBSERVED / HIGH.** La prosa del PDF p.11 y la matriz impresa son coherentes para la exactitud top-1 del clasificador: matriz absoluta `[[44,1,0,1,0],[1,37,6,0,1],[2,6,36,0,0],[1,0,0,41,0],[1,0,0,0,41]]`, total 219, diagonal 199, 199/219 = 0.9086758, redondeado .909. Los seis errores Cancro→Costras y seis inversos también coinciden con la descripción. Esto acredita coherencia aritmética del objeto publicado, sin demostrar procedencia de predicciones ni ausencia de fuga. La alusión del dictamen a una matriz en página 9 debe conciliarse expresamente: en el PDF confirmado, p.9 contiene Fig.5 y Fig.6 está en p.11. No se usa esa diferencia para negar la confirmación de envío del usuario.

## Mapa de figuras del PDF sometido

Los recursos de la tabla están bajo `R + articulo_overleaf_v9_merge/images/`; sus hashes completos están en `E + image_hashes.csv`. `imageN.png` corresponde al miembro `word/media/imageN.png` del DOCX ALBUS. La igualdad DOCX↔recurso es de bytes, no sólo perceptual.

| Figura / página | Contenido | Recurso v9 / DOCX | Localizador LaTeX bajo `articulo_overleaf_v9_merge/secciones/` |
|---|---|---|---|
| 1 / 3 | Arquitectura en cascada | `arquitectura.png` / image1 | `02metodos.tex:9` |
| 2 / 6 | Servicio FastAPI y SQLite | `servicio_web.png` / image2 | `02metodos.tex:128` |
| 3 / 7 | Curvas de detector | `evolucion.png` / image3 | `04Resultados.tex:11` |
| 4 / 8 | Matriz de detector | `matriz_confusion.png` / image4 | `04Resultados.tex:69` |
| 5 / 9 | Mosaico cualitativo detector, nueve imágenes | `deteccion.png` / image5 | `04Resultados.tex:81` |
| 6 / 11 | Matriz clasificador, n=219 | `matriz_conf2.png` / image6 | `04Resultados.tex:150` |
| 7 / 12 | Mosaico cualitativo cascada, nueve imágenes | `cascada_completa.png` / image7 | `04Resultados.tex:164` |

Figuras 3–7 tienen además correspondencia de píxeles con `R + Articulo/latex/figs/fig3_curvas.png`, `fig5_confusion_matrix.png`, `fig4_test_inference.png`, `fig6_confusion_cls.png` y `fig7_cascade_demo.png`, respectivamente. No confundir la numeración de archivos antiguos con el número impreso: archivo fig5 corresponde a Figura 4 y archivo fig4 a Figura 5.

**GENE-007 — OBSERVED / HIGH.** La Figura 1 conserva textos incrustados obsoletos: «Roboflow propio (669 imgs)», «YOLOv26n» y «multiclase (5 enfermedades)». La prosa de p.3 declara dataset de terceros y p.4 enumera cinco clases incluyendo Saludable. En la discusión p.13 (`R + articulo_overleaf_v9_merge/secciones/04Resultados.tex:187`) se dice «seis posibles diagnósticos (5 enfermedades + sano)». El conjunto enumerado realmente contiene cuatro enfermedades y Saludable. Hay que corregir conjuntamente prosa y recursos gráficos en la futura revisión autorizada, no únicamente captions.

Fig.5 declara test n=33 y muestreo aleatorio semilla 42; Fig.7 declara test del detector y semilla 7. La existencia de estos textos no comprueba el muestreo. El mosaico Fig.7 contiene un panel «sin detecciones», carece de ground truth por enfermedad y no constituye por sí solo evaluación end-to-end. La atribución «Fuente: elaboración propia» distingue las anotaciones de las fotografías públicas en los captions recientes; no demuestra que las licencias cubran cada fotografía original.

## Mapa de tablas y cifras sometidas

| Tabla / página | Contenido | Localizador v9 | Cifras o cautela de interpretación |
|---|---|---|---|
| 1 / 3–4 | Distribución detector | `02metodos.tex:32` | 502/134/33 imágenes; 669 total, 582 instancias Enfermo y 1272 Saludable. |
| 2 / 4–5 | Configuración detector | `02metodos.tex:89` | YOLO26n, 640 px, 150 épocas, batch16, semilla0; no identifica por sí sola el checkpoint de cada máximo. |
| 3 / 5 | Configuración clasificador | `02metodos.tex:117` | YOLO11n-cls, 224 px, máximo50 épocas, paciencia15, batch32, semilla42; p.10 explica parada27/mejor12. |
| 4 / 7 | Máximos validación detector | `04Resultados.tex:34` | .9317/.8048/.9473/.8731 pertenecen a distintas épocas. |
| 5 / 7 | Test detector | `04Resultados.tex:57` | n33, 99 GT; macro mAP .845/.784, P .884, R .737; Enfermo R .846. |
| 6 / 10 | Pares casi duplicados | `04Resultados.tex:111` | train-valid55, train-test18, valid-test3, total76. |
| 7 / 10 | Test clasificador | `04Resultados.tex:141` | clases n46/45/44/42/42, top1 .909, macro-F1 .910. |
| 8 / 14 | Limitaciones y mitigación | `04Resultados.tex:222` | Detector669, sin test OOD, RGB, confusión Cancro/Costras, latencia y calibración. |

**GENE-008 — OBSERVED / HIGH.** Persisten afirmaciones de latencia no verificadas aquí: PDF p.9 declara detector 145 ms en Ryzen y Raspberry Pi <5 s; p.11 declara cascada 0.18–0.6 s; p.13 habla de latencia >5 s sin cuantización, y Tabla 8 p.14 menciona Raspberry Pi a 832×832. Pueden referirse a configuraciones distintas, pero la prosa no permite resolverlo. Fuentes v9 `04Resultados.tex:92`, `:160`, `:202`, `:219`. No seleccionar una cifra como benchmark confirmado sin sus registros y condiciones.

## Bibliografía y citas

**GENE-009 — OBSERVED / HIGH.** Se distinguen entradas existentes de referencias realmente citadas. ZIP inicial a ZIP v7 contienen 15 entradas; las carpetas base/v7 contienen 18; v8 contiene 17; v9 contiene 23. DOCX ALBUS tiene 23 párrafos de referencias (`E + docx_Articulo_Mango_ALBUS.txt`, líneas 337–359), correspondientes al listado de PDF pp.15–16. Las cifras de entradas no certifican calidad o existencia de publicaciones.

Cambios rastreables por clave y diffs:

- La familia inicial usa `12buolamwini2018perceptual`; luego se reemplaza por `12zauner2010perceptual`. También aparecen reemplazos `14tammina2019transfer`→`14kapoor2023leakage`, `15girshick2015fast`→`15padilla2020survey`, `04heliyon2024avances`→`04liu2021plant` y `02canton2021food`→`02savary2019global`.
- Las carpetas base/v7 añaden `16jairos2026mangounhealty`, `17luis2022mango` y `18villa2026mangodisease`; v8 elimina la entrada17 y conserva16/18.
- v9 añade `dofuor2023mango`, `iqbal2024powdery`, `khakimov2022traditional`, `buja2021advances`, `venbrux2023current` y `ciofini2022management`.
- v9 retira varias citas repetidas en métodos, resultados y agradecimientos dejando comentarios que explican la retirada. Ejemplo `R + articulo_overleaf_v9_merge/secciones/02metodos.tex:139`; las entradas permanecen en `biblio.bib`. No es desaparición de la fuente bibliográfica.
- El título/identidad de MangoDHDS pasa de la atribución inicial a Mendeley a IEEE Dataport, DOI 10.21227/33mp-rf79, visible en el PDF p.15. Esa transición textual no verifica el contenido real del dataset; corresponde a la auditoría de procedencia externa.

## Decisiones para la revisión y asuntos pendientes

1. Fijar el PDF confirmado y su SHA-256 como referencia de respuesta al dictamen. Etiquetar los demás PDF como antecedentes, no como sometidos.
2. Cuando se autorice editar, partir del DOCX ALBUS por su correspondencia demostrada; conservar v9 como fuente de imágenes y comparación, con un diff explícito si se migra de formato.
3. No restaurar silenciosamente citas, cifras, autores ni texto desde una carpeta cuyo nombre sugiere antigüedad. Comparar contenidos y usar los hashes.
4. Vincular a la auditoría experimental las afirmaciones de regeneración/split, máximos de validación, tiempos y cascada; esta genealogía no las convierte en resultados reproducidos.
5. Corregir en una fase futura las inconsistencias de figura/clases, localizadores del dictamen, número de Tabla III y referencias duplicadas «Sección Sección», conservando historial de cambios.

No se identificó una fuente LaTeX que, sin modificaciones, corresponda a la plantilla y título ALBUS; esa relación queda INFERRED/MEDIUM respecto del proceso exacto de conversión, aun cuando la correspondencia de contenido Word/PDF y recursos gráficos sea HIGH.

