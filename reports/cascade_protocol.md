# Protocolo para evaluar la cascada M1→M2 con ground truth independiente

Este documento describe el protocolo que un estudio futuro debe seguir para
producir el recall conjunto y la precisión por enfermedad de la cascada
(SPEC §9). No se ejecuta en esta revisión porque no existe ground truth de
enfermedad específica sobre las mismas escenas/frutos que evaluó el detector
(ver `reports/cascade_ground_truth_assessment.md`). El esquema
(`data/manifests/cascade_annotation_schema.json`), el validador
(`validate_ground_truth`) y el evaluador (`score_cascade`), ambos en
`src/evaluation/cascade.py`, ya están implementados y probados; lo que falta
es la anotación real.

## 1. Ground truth independiente

- **Anotador:** un agrónomo o fitopatólogo que no participó en el desarrollo
  del detector ni del clasificador, sin acceso a las predicciones de M1/M2 al
  momento de diagnosticar. El diagnóstico se basa en inspección directa del
  fruto (visual, y de laboratorio cuando el caso lo exija), nunca en la salida
  de un modelo. `diagnostic_method='model_prediction'` queda rechazado por
  `validate_ground_truth`: es una regla de código, no solo una recomendación.
- **Unidad de anotación:** un fruto (`fruit_id`) dentro de una imagen
  (`image_id`, el SHA256 del archivo). Cada fruto recibe una caja
  (`bbox_xyxy`), una etiqueta específica (`disease_label`, una de las cuatro
  enfermedades o Saludable) y un juicio binario independiente
  (`healthy_or_diseased`) que debe ser consistente con la etiqueta específica.
- **Ambiguo o no diagnosticable:** si el agrónomo no puede asignar una
  enfermedad específica con confianza, la fila se conserva con
  `disease_label` igual a `AMBIGUOUS` o `UNDIAGNOSED`; no se fuerza una
  etiqueta ni se descarta la fila. `score_cascade` excluye estas filas de
  todo denominador diagnóstico y reporta su conteo en
  `excluded.ambiguous_or_undiagnosed_count`. Esto evita dos errores opuestos:
  inflar el recall descartando casos difíciles, o inventarles una etiqueta.

## 2. Grupos y anotadores

- **`group_id`** es la unidad de máxima dependencia disponible (mismo fruto
  fotografiado varias veces, misma rama, mismo árbol o misma sesión de
  adquisición, según lo que se pueda documentar). El remuestreo para el
  intervalo de confianza usa `group_id`, con el mismo criterio conservador de
  TASK-05: nunca se trata una imagen como independiente si comparte grupo con
  otra.
- Se registran al menos dos anotadores independientes por fruto cuando el
  presupuesto lo permita, siguiendo el mismo principio de cegamiento de la
  auditoría de fuga (SPEC §5): el segundo anotador no ve la etiqueta del
  primero ni las predicciones del modelo. El desacuerdo entre anotadores se
  resuelve por un tercer adjudicador, nunca por promedio o mayoría simple si
  solo hay dos jueces. Solo las filas con `adjudication_status =
  INDEPENDENT_ADJUDICATED` (el desacuerdo ya resuelto) producen métricas;
  `PENDING_ADJUDICATION` y `MODEL_ASSISTED` se cuentan y excluyen
  (`excluded.non_independent_count`), nunca se tratan como si no existieran.
- **`source`** documenta el origen de la campaña de anotación (sitio, fecha,
  organización), para que un tercero pueda auditar procedencia igual que con
  el resto del proyecto.

## 3. Qué se registra antes de tocar el modelo

Antes de correr una sola inferencia de M1 o M2 sobre el nuevo conjunto, se
congela y se publica:

1. El conjunto de imágenes anotadas y su partición train/validation/test (si
   el volumen alcanza para partición; si no, se declara que todo el conjunto
   es test y no hay ajuste posible sobre él).
2. El método diagnóstico exacto y los anotadores, con sus IDs opacos.
3. El umbral de abstención de M2. El candidato predefinido es **0.4** sobre
   la confianza del top-1 de M2 (`M2_DEFAULT_THRESHOLD` en
   `src/evaluation/cascade.py`), declarado a priori en este documento. Si en
   cambio se decide ajustar el umbral, eso se hace **solo** sobre un
   conjunto de validación independiente del test de cascada, nunca sobre el
   mismo test que reporta el resultado final. Cualquiera de las dos rutas
   (0.4 fijo, o ajuste en validación) se registra por escrito antes de ver
   una sola predicción de M2 sobre el test.
4. El umbral operativo de M1 (F2 de Enfermo, TASK-05 §7) ya congelado, sin
   volver a tocarlo para este experimento.

Este orden importa: registrar el umbral después de ver resultados de test es
indistinguible de optimizarlo sobre test, aunque el número final coincida con
uno "razonable".

## 4. Una sola evaluación de test

El test de cascada se corre **una vez** con las decisiones anteriores ya
congeladas. Si el resultado obliga a cambiar el umbral de M2, el modelo o el
criterio de éxito, eso es una enmienda de protocolo (igual que en el resto de
esta revisión, SPEC §4.2): se documenta como amendment, no se repite el test
con otra configuración hasta obtener el número que se prefiera. No hay
selección de checkpoint, arquitectura ni umbral con acceso a este test.

## 5. Por qué el desempeño de la cascada no es el producto de las métricas marginales

Un error común es estimar el recall conjunto como
`recall(M1) × accuracy(M2 | detectado)`, tratando la detección y el
diagnóstico como dos eventos independientes. `score_cascade` no hace esto, y
no es solo una elección de implementación: es incorrecto por al menos tres
razones concretas.

1. **No son eventos independientes.** Los frutos que M1 detecta mal (fondo
   confuso, oclusión, lesión pequeña) tienden a ser los mismos frutos donde
   la lesión es difícil de diagnosticar para M2. Multiplicar dos tasas
   marginales asume independencia estadística que no hay evidencia de que
   se cumpla; hacerlo puede sobrestimar o subestimar el resultado conjunto
   sin que el signo del sesgo sea predecible de antemano.
2. **El éxito es un evento conjunto sobre el mismo fruto, no dos sorteos
   separados.** `score_cascade` exige que la MISMA caja predicha (emparejada
   uno a uno por IoU≥0.5 con el matching de `src.evaluation.evaluate.match`)
   lleve la etiqueta específica correcta. Multiplicar marginales no verifica
   que el fruto detectado y el fruto clasificado correctamente sean el mismo
   fruto; con varios frutos por imagen esto puede acoplar el éxito de M2 en
   un fruto con la detección de otro.
3. **Los fallos de ruteo desaparecen en el producto.** Cuando M1 predice
   "sano" sobre un fruto enfermo, M2 nunca se ejecuta: ese fruto no es ni un
   verdadero positivo de M1 ni un dato de entrada para M2, así que no entra
   en ninguna de las dos tasas marginales que se multiplicarían. El mismo
   problema ocurre con la abstención de M2. `score_cascade` cuenta ambos
   casos como fallo dentro del denominador de recall conjunto
   (`joint_recall.denominator` incluye todo fruto enfermo adjudicado,
   detectado o no, clasificado o abstenido); un producto de marginales los
   perdería o los contaría de forma inconsistente según cómo se definan esas
   marginales.

Por esto la SPEC (§9) prohíbe explícitamente "multiplicar recalls
independientes de dos datasets para estimar recall conjunto", y por lo que
`score_cascade` calcula el recall conjunto contando éxitos sobre el mismo
fruto, fruto a fruto, en vez de combinar dos números ya agregados. El precio
de este rigor es que el número solo es válido si el ground truth adjudicado
cubre frutos reales de la cascada completa (misma escena, mismo fruto, mismo
recorte que M1 le pasaría a M2); de ahí que, sin ese ground truth, la salida
correcta hoy sea `BLOCKED_BY_GROUND_TRUTH` y no una estimación derivada de
DATA-001 y DATA-005 por separado.
