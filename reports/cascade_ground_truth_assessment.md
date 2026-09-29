# Evaluación de disponibilidad de ground truth de cascada — BLOCKED_BY_GROUND_TRUTH

Fuente: `data\manifests\legacy_dataset_inventory.csv` (inventario congelado en TASK-02).

## Hallazgo

No existe, para el corpus actual, ninguna escena/fruto con ground truth de
enfermedad específica adjudicado independientemente que coincida con las
imágenes usadas para evaluar el detector M1. Por lo tanto **no se calcula
ninguna métrica de la cascada** (recall conjunto, precisión por enfermedad,
clasificación condicional ni tasa de abstención) en esta edición: el estado
declarado por la SPEC §9 se mantiene, `BLOCKED_BY_GROUND_TRUTH`.

## Evidencia

- **DATA-001** (corpus del detector, `SemilleroTI-Mangos/docs/MangosDataset`):
  669 filas, clases ['Enfermo', 'Enfermo;Saludable', 'Saludable'], con cajas
  (`has_boxes=True`). Ejemplo de ruta: `SemilleroTI-Mangos/docs/MangosDataset/test/images/freshMango-174-_jpg.rf.42d216c523e3dc87799f16ad3b862eb9.jpg`.
  Etiqueta binaria Enfermo/Saludable por caja, nunca la enfermedad específica.
- **DATA-005** (corpus del clasificador, `Mango-vision/DatasetMango_YOLO_cls`):
  1500 filas, clases ['Antracnosis', 'Cancro_bacteriano', 'Costras', 'Podredumbre_Extremo_tallo', 'Saludable'], sin cajas de detección
  (`has_boxes=False`). Ejemplo de ruta: `Mango-vision/DatasetMango_YOLO_cls/test/Antracnosis/An111.jpg`.
  Imágenes centradas en el fruto de origen distinto (Mango-vision, no
  SemilleroTI-Mangos): no son las mismas escenas ni los mismos frutos que
  DATA-001, y no traen caja para emparejar con una detección M1.

Ningún archivo de `data\manifests\legacy_dataset_inventory.csv` vincula un `image_id` de DATA-001 con un
`image_id` de DATA-005 sobre el mismo fruto físico. Sin esa correspondencia no
hay unidad de análisis fruto-a-fruto que sostenga un recall conjunto: la salida
del clasificador tampoco puede sustituir esa anotación (`diagnostic_method`
`model_prediction` queda rechazado por `validate_ground_truth`).

## Qué se entrega en su lugar

El esquema (`data/manifests/cascade_annotation_schema.json`), el validador
(`validate_ground_truth`) y el evaluador (`score_cascade`) quedan implementados
y probados con fixtures sintéticos (`tests/test_cascade.py`); no se produce
ningún CSV de accuracy porque no hay entrada real que anotar. Ver
`reports/cascade_protocol.md` para el protocolo que un estudio futuro con GT
independiente debería seguir antes de ejecutar esta rama.
