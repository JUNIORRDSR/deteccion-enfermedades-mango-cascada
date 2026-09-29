# Detección y clasificación automatizada de enfermedades en mango

Código, pesos y evidencia del artículo *Detección y clasificación automatizada de enfermedades fitopatológicas en mango: un enfoque de arquitectura en cascada* (Villa Bastidas, Solano Romero y Molina-Cárdenas), en su versión revisada. El manuscrito está en `manuscript/`: `source/` tiene el DOCX y `output/` el PDF.

El sistema es una cascada de dos modelos. Un detector YOLO26n localiza frutos y los clasifica como Enfermo o Saludable. Un clasificador YOLO11n-cls asigna a cada fruto detectado una de cuatro patologías (Antracnosis, Cancro bacteriano, Costras, Podredumbre del extremo del tallo) o Saludable.

## Resultados y su alcance

- **Detector** (partición de prueba por grupos de origen, 117 imágenes y 98 grupos): mAP@0,5 de 0,807 [0,677; 0,887] y sensibilidad para Enfermo de 0,577 [0,273; 0,735].
- **Clasificador** (prueba de MangoDHDS_clean, 219 imágenes): exactitud de 0,909 [0,869; 0,946] y macro-F1 de 0,909 [0,869; 0,945].

Los corchetes dan intervalos bootstrap del 95 % por grupo, condicionales al modelo y a la partición. Las dos pruebas son evaluaciones internas retrospectivas sobre imágenes ya publicadas, no pruebas prospectivas. No hay verdad de terreno conjunta para medir la cascada completa. El sistema no se validó en campo. Las etiquetas son las de los conjuntos de terceros, sin confirmación fitopatológica. La Sección 6 del manuscrito y `reports/final_adversarial_review.md` detallan las limitaciones.

## Contenido

| Ruta | Qué contiene |
|---|---|
| `src/` | Auditoría de fuga (`leakage_audit/`), evaluación, intervalos, benchmark y cascada |
| `provenance/` | Protocolo congelado (`protocol_freeze.*`), enmiendas, registro de accesos a la prueba, entornos y las órdenes que produjeron cada resultado |
| `data/manifests/`, `data/audits/` | Manifiestos congelados con el SHA-256 de cada imagen, pares candidatos, adjudicaciones y grupos |
| `experiments/` | Kernels de Kaggle renderizados, recibos, registros, predicciones guardadas y métricas de cada experimento |
| `artifacts/metrics/` | Intervalos, sensibilidad a duplicados y latencia |
| `reports/` | Auditorías, revisiones independientes, reproducción, portabilidad y cumplimiento del protocolo |
| `docs/` | Diseño, plan, registro de decisiones y matriz de afirmaciones |
| `tests/` | Pruebas unitarias |

## Pesos

| Modelo | Ruta | SHA-256 |
|---|---|---|
| Detector YOLO26n, época 91 (EXP-R01) | `experiments/model1/EXP-R01/v1/run/weights/selected.pt` | `0648da3f3641e3cdb5a1908a092ba892548942836a249bb3b39667f9ae8e8125` |
| Clasificador YOLO11n-cls (ART-002) | `models/clasificador_enfermedad.pt` | `e277717e6ca9d7f308d22697550a5a4e80613929acb68eeb790f3304ebfdb08e` |

`src/evaluation/predict_model2.py` busca el clasificador en `<legacy_corpus>/Mango-vision/models/clasificador_enfermedad.pt` y comprueba su hash.

## Datos

Las imágenes no están en el repositorio. Proceden de dos conjuntos públicos con licencia CC BY 4.0:

- mangoUnhealty v2 (Jairos Workspace, Roboflow Universe), para el detector. Los kernels lo descargan del commit público `DANN-MAGE/SemilleroTI-Mangos@98614804` y verifican cada archivo por hash contra `data/manifests/model1_clean_manifest.csv`.
- MangoDHDS v1 (Barhate et al., Mendeley Data, DOI 10.17632/b4nrw5hyyc.1), para el clasificador.

Las figuras y los lotes de entrenamiento incluidos reproducen imágenes de esos conjuntos, con su atribución.

## Reproducción

1. Python 3.12 con los paquetes de `provenance/environment/inference_environment.txt`. La evaluación local se niega a correr con otro conjunto de paquetes.
2. En `configs/root_mapping.json`, `legacy_corpus` apunta a la carpeta con las copias de los conjuntos. Las rutas absolutas de los informes son las de la máquina original y sólo documentan esa ejecución.
3. Las órdenes, desde la raíz y con `py = python` del entorno:

| Paso | Orden |
|---|---|
| Auditoría del detector | `py -m src.leakage_audit.audit --dataset-id DATA-001 --manifest data/manifests/legacy_dataset_inventory.csv --out data/audits/model1` |
| Partición | `py -m src.leakage_audit.split --audit data/audits/model1 --seed 42 --ratios 0.70 0.15 0.15 --extra-relations data/audits/model1/supplementary_relations.csv --out data/manifests/model1_clean_manifest.csv --proposal reports/model1_split_proposal.md` |
| Entrenamiento e inferencia del detector | `provenance/commands/task04/render_kaggle_job.py` genera el kernel de Kaggle; `verify_kaggle_run.py` verifica su salida |
| Métricas | `py -m src.evaluation.evaluate --model-id model1 --config configs/evaluation_frozen.json --split test --run-dir experiments/model1/EXP-R02` |
| Intervalos | `py -m src.statistics.intervals --predictions experiments/model1/EXP-R02/predictions.jsonl --groups data/manifests/model1_clean_manifest.csv --seed 42 --resamples 2000 --out artifacts/metrics/model1_intervals.json` |
| Latencia | `py -m src.benchmarks.run --config configs/benchmark.json --out artifacts/metrics/benchmark_raw.csv --report reports/benchmark_report.md` |
| Cifras del manuscrito | `py -m src.evaluation.document_checks --docx manuscript/source/Articulo_Mango_ALBUS_revision.docx --claims docs/research/claim_evidence_matrix.csv --metrics artifacts/metrics --out reports/manuscript_consistency.json` |
| Pruebas | `py -m unittest discover -s tests -p "test_*.py"` |

La puntuación, los intervalos y las cifras del manuscrito se regeneran byte a byte desde las predicciones guardadas (`reports/reproduction_check.md`). La inferencia puede repetirse con los pesos publicados.

## Uso de IA

La adjudicación visual de la auditoría de fuga del detector se hizo primero con apoyo de agentes de IA (Claude); sus respuestas están en `data/audits/model1/`. Después, una integrante del equipo revisó manualmente los candidatos (Sección 3.3.1 del manuscrito). Esa revisión manual no tiene un registro caso a caso en el repositorio (DECISION-040 en `docs/research/decision_log.md`). La ejecución de la revisión se hizo con asistentes de IA de programación, bajo la dirección de los autores. Lo mismo vale para el código, los análisis y las revisiones metodológicas de `reports/`.

## Qué no se incluye

No se incluyen la correspondencia de la revisión por pares, las versiones anteriores del manuscrito ni la plantilla de la revista.

## Licencia y cita

El código y los pesos se distribuyen bajo AGPL-3.0 (`LICENSE`), la licencia de Ultralytics. Los conjuntos de datos conservan su licencia CC BY 4.0. Para citar el repositorio, use `CITATION.cff`.
