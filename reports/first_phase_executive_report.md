# Informe ejecutivo de primera fase — ALBUS26-116

Fecha: 2026-09-17. Se ha completado investigación documental, inventarios y propuestas. No hay entrenamiento, inferencia, pHash nuevo, splits nuevos ni cambios científicos del manuscrito. Las comprobaciones aritméticas sólo contrastan artefactos existentes. Confianza HIGH/MEDIUM/LOW califica cada conclusión documental; no equivale a validez científica del resultado.

## 1. ¿Cuál fue exactamente el manuscrito sometido?

[Articulo_Mango_ALBUS.pdf](<C:/Users/junio/Downloads/mango-vision/Articulo_Mango_ALBUS.pdf>) — **SRC-000002**, SHA256 `68d9f231ca9f6de3f994d93cd112717de0072a117822792cdba7ababfb1a499d`. Es el PDF de 16 páginas confirmado expresamente por el usuario. **HIGH**, por confirmación y archivo identificado. El dictamen SRC-MAIL usa algunas páginas que no coinciden; se conserva esa discrepancia, sin sustituir el archivo por otra versión. La identidad no se dedujo del nombre v9. Relacionado: REVIEW-14/18, GENE-001, DECISION-002.

## 2. ¿Cuál es la fuente editable más probable?

[Articulo_Mango_ALBUS.docx](<C:/Users/junio/Downloads/mango-vision/Articulo_Mango_ALBUS.docx>) — **SRC-000001**, SHA256 `7a5918854107ce22eec0539bbb6f7c0962685897187e57e1dba2dbb2e570bc86`. **HIGH**: texto normalizado del DOCX y PDF idéntico en 33.468 caracteres; SHA256 del texto normalizado `9f80a981be79aeab9f9e068c1adc6e1639681aaaaf09e06cdd7c7a7a4920773e`. Siete imágenes del DOCX coinciden binariamente con v9. Esto demuestra contenido normalizado, no igualdad de maquetación ni que otro archivo no se usara al exportar. Se propone copiar este DOCX como fuente canónica sólo tras aprobación. GENE-001/002; REVIEW-14/16/18.

## 3. ¿Cuál es la genealogía?

[docs/research/manuscript_genealogy.md](<C:/Users/junio/Downloads/mango-vision/ALBUS26_major_revision/docs/research/manuscript_genealogy.md>) documenta GENE-001–009 con hashes, fechas, títulos, secciones, tablas, figuras y referencias. Los paquetes ZIP v4–v6 conservan texto/bibliografía y cambian imágenes. El ZIP v8 coincide 16/16 y v9 17/17 con sus carpetas; v7 sólo 12/16 y el ZIP base 3/16, por lo que no son copias intercambiables. v9 es respaldo LaTeX próximo al DOCX, pero tiene título/formato distinto. No existe una secuencia lineal fiable inferible sólo por los números de versión. **HIGH** para comparaciones de bytes/texto; **MEDIUM** para orden causal de ediciones sin historial completo. REVIEW-14/18.

## 4. ¿Dónde está el código del Modelo 1?

- Evaluación: [Articulo/scripts/evaluate_detector_test.py](<C:/Users/junio/Downloads/mango-vision/Articulo/scripts/evaluate_detector_test.py>) — **SRC-000108**, SHA256 `9f14470005afecf586a4d672c77226c61697fce1c7ebd78f04f3505cb1a24973` — EXP-002/003.
- Servicio binario: [SemilleroTI-Mangos/core/vision.py](<C:/Users/junio/Downloads/mango-vision/SemilleroTI-Mangos/core/vision.py>) — **SRC-009681**, SHA256 `f6bfdd42aad7b9972bfd444f47bc0280983b1a4e7ff8fe90154597e766b60c7c`, llamado desde [SemilleroTI-Mangos/api/routers/inference.py](<C:/Users/junio/Downloads/mango-vision/SemilleroTI-Mangos/api/routers/inference.py>).
- Entrenamiento publicado: [SemilleroTI-Mangos/docs/Yolo26n-model-docs/Entrenamiento-1/args.yaml](<C:/Users/junio/Downloads/mango-vision/SemilleroTI-Mangos/docs/Yolo26n-model-docs/Entrenamiento-1/args.yaml>) — **SRC-011024**, SHA256 `3f115cc74d574593832a6362d9749699e5669ae7344e4de15157cef7ab43b0da` y [SemilleroTI-Mangos/docs/Yolo26n-model-docs/Entrenamiento-1/resultados/results.csv](<C:/Users/junio/Downloads/mango-vision/SemilleroTI-Mangos/docs/Yolo26n-model-docs/Entrenamiento-1/resultados/results.csv>) — EXP-001. **No se localizó el script/notebook ejecutado de ese entrenamiento**; el trainer genérico del otro repo no prueba ese run.

**HIGH** para rutas y comportamiento actual; **MEDIUM** para vínculo histórico parcial. REVIEW-03/09.

## 5. ¿Dónde está el código del Modelo 2?

[Mango-vision/src/training/train_cls.py](<C:/Users/junio/Downloads/mango-vision/Mango-vision/src/training/train_cls.py>) — **SRC-009666**, SHA256 `f37b00e2e234156fcdc5536b24c897b75f838b9a733ad6b24d6d62d3c5e9a060`. La preparación de layout está en [Mango-vision/src/training/make_cls_layout.py](<C:/Users/junio/Downloads/mango-vision/Mango-vision/src/training/make_cls_layout.py>); evaluación en [Articulo/scripts/evaluate_classifier.py](<C:/Users/junio/Downloads/mango-vision/Articulo/scripts/evaluate_classifier.py>) — **SRC-000107**, SHA256 `6f83d85a00e996397f074114f24ffbaa8a4ed9ac13087c714bf57736cd90c067`. EXP-004/005: log [Articulo/reports/train_cls_log.txt](<C:/Users/junio/Downloads/mango-vision/Articulo/reports/train_cls_log.txt>), checkpoint ART-002 y matriz de 219 imágenes. **HIGH** en identificación y evidencia local; la membresía histórica exacta no quedó congelada. REVIEW-09/15.

## 6. ¿Dónde está la cascada?

[SemilleroTI-Mangos/core/cascade.py](<C:/Users/junio/Downloads/mango-vision/SemilleroTI-Mangos/core/cascade.py>) — **SRC-009678**, SHA256 `397fe0bbf8172c63a475f0f6c779e8e63c56aa4dd473c0ba971033dd21e7091b`, invocada por [SemilleroTI-Mangos/run_cascade.py](<C:/Users/junio/Downloads/mango-vision/SemilleroTI-Mangos/run_cascade.py>) y [Articulo/figs/fig7_cascade_demo.py](<C:/Users/junio/Downloads/mango-vision/Articulo/figs/fig7_cascade_demo.py>) — EXP-007. La API de `api/routers/inference.py` utiliza `core/vision.py`, que ejecuta sólo M1. **HIGH**: el flujo actual no demuestra integración de cascada en la API ni diagnóstico end-to-end validado. REVIEW-07/12/13; CLAIM-039; DECISION-012.

## 7. ¿Dónde están los datasets?

|ID|Ruta absoluta|Snapshot observado|Confianza|
|---|---|---|---|
|DATA-001|[SemilleroTI-Mangos/docs/MangosDataset](<C:/Users/junio/Downloads/mango-vision/SemilleroTI-Mangos/docs/MangosDataset>)|669 imágenes: 502/134/33; 1.854 cajas, dos clases. Test: 99 cajas, 13 Enfermo|HIGH|
|DATA-002|[Mango-vision/MangoDHDS A Dataset of Diseased and Healthy Mangoe](<C:/Users/junio/Downloads/mango-vision/Mango-vision/MangoDHDS A Dataset of Diseased and Healthy Mangoe>)|1.500 imágenes sin split; 300 por cada una de cinco clases|HIGH|
|DATA-003|[Mango-vision/DatasetMango_YOLO](<C:/Users/junio/Downloads/mango-vision/Mango-vision/DatasetMango_YOLO>)|1.500: 1.125/300/75; cajas de imagen completa en layout derivado|HIGH|
|DATA-004|[Mango-vision/DatasetMango_YOLO_clean](<C:/Users/junio/Downloads/mango-vision/Mango-vision/DatasetMango_YOLO_clean>)|1.500: 1.064/217/219; copias exactas conservadas dentro de splits|HIGH|
|DATA-005|[Mango-vision/DatasetMango_YOLO_cls](<C:/Users/junio/Downloads/mango-vision/Mango-vision/DatasetMango_YOLO_cls>)|Misma membresía, hash y clase que DATA-004, con valid→val|HIGH|
|DATA-006|[Mango-vision/DatasetMango_Propias](<C:/Users/junio/Downloads/mango-vision/Mango-vision/DatasetMango_Propias>)|173: 121/35/17; una clase mango; 568 bbox + 965 polígonos. Sin diagnóstico específico|HIGH|
|DATA-007|[Mango-vision/Datasets Sucios personal/Camara VIVO Y21](<C:/Users/junio/Downloads/mango-vision/Mango-vision/Datasets Sucios personal/Camara VIVO Y21>)|174 fotografías sin GT diagnóstico; 173 nombres normalizados relacionados con exportación|HIGH para inventario; MEDIUM para relación de transformación|
|DATA-008|Ruta configurada DatasetMango_Detector|No localizada; configuración no equivale a datos presentes|HIGH para ausencia en corpus inventariado|

DER-001/002/003: [provenance/derived_evidence_registry.csv](<C:/Users/junio/Downloads/mango-vision/ALBUS26_major_revision/provenance/derived_evidence_registry.csv>); [reports/datasets/dataset_archaeology.md](<C:/Users/junio/Downloads/mango-vision/ALBUS26_major_revision/reports/datasets/dataset_archaeology.md>). Los 7.016 archivos son representaciones y copias, no 7.016 observaciones independientes. Los campos `box_rows/polygon_rows` por clase cuentan filas de imágenes que contienen esa clase; para número de objetos por clase usar `instances`. REVIEW-01/02/04/11/13.

## 8. ¿Dónde están los checkpoints?

|ART-ID|Ruta|SHA256|
|---|---|---|
|ART-001|[SemilleroTI-Mangos/models/best.pt](<C:/Users/junio/Downloads/mango-vision/SemilleroTI-Mangos/models/best.pt>)|`595fa3ea9b0670f63289529bde3333124ff1179588b52fbe16c9c454b6e488de`|
|ART-002|[Mango-vision/models/clasificador_enfermedad.pt](<C:/Users/junio/Downloads/mango-vision/Mango-vision/models/clasificador_enfermedad.pt>)|`e277717e6ca9d7f308d22697550a5a4e80613929acb68eeb790f3304ebfdb08e`|
|ART-003|[SemilleroTI-Mangos/models/clasificador_enfermedad.pt](<C:/Users/junio/Downloads/mango-vision/SemilleroTI-Mangos/models/clasificador_enfermedad.pt>)|Igual a ART-002|
|ART-004|[Mango-vision/yolo11n-cls.pt](<C:/Users/junio/Downloads/mango-vision/Mango-vision/yolo11n-cls.pt>)|`c62d41bf9625777760018bf914d2e6cd472420ccd01706d97a61cb6c82502bd7`|

**HIGH** para identidad actual. ART-004 presente no prueba que sus bytes fueran la base exacta del entrenamiento histórico. La base M1 `yolo26n.pt` no está identificada por hash histórico. Metadata inspeccionada estáticamente, sin cargar pickle ni modelos. REVIEW-09; [provenance/artifact_registry.csv](<C:/Users/junio/Downloads/mango-vision/ALBUS26_major_revision/provenance/artifact_registry.csv>).

## 9. ¿Qué experimentos pueden trazarse?

|EXP|Evidencia recuperada|Límite|Confianza|
|---|---|---|---|
|001 M1 train|args, 150 filas, checkpoint y métricas embebidas|Faltan comando, entorno completo, base y manifest históricos|HIGH documental, MEDIUM procedencia|
|002 M1 test AP|script, CSV global y por clase|Sin predicciones ni hash de ejecución|MEDIUM|
|003 M1 confusión|mismo script con conf .25 y matriz|Protocolo distinto de EXP-002|MEDIUM|
|004 M2 train|script, log CPU, 27 épocas y mejor 12, pesos|Sin manifest inmutable del run|HIGH documental, MEDIUM procedencia|
|005 M2 test|script, matriz y CSV, 219 casos|Sin ejecución nueva ni predicciones individuales|MEDIUM|
|006/007 galerías|scripts, figuras, seeds y umbrales|Cualitativas; no GT diagnóstico conjunto|HIGH identificación; LOW para eficacia clínica|
|008/009 latencias|Claims del PDF|Sin run recuperado ni tiempos crudos|LOW|

[provenance/experiment_registry.csv](<C:/Users/junio/Downloads/mango-vision/ALBUS26_major_revision/provenance/experiment_registry.csv>): nueve registros, todos `reproduced=NO`. [reports/experiments/experiment_archaeology.md](<C:/Users/junio/Downloads/mango-vision/ALBUS26_major_revision/reports/experiments/experiment_archaeology.md>). REVIEW-03/05/07/08/09/13.

## 10. ¿Qué métricas pueden reproducirse?

**Ninguna se ha reproducido experimentalmente en esta fase.** Hay entradas suficientes para proponer reevaluaciones M1/M2, condicionadas a auditoría de datos y compatibilidad. Sí puede comprobarse aritméticamente lo que dicen las matrices existentes: M2 tiene 199/219 aciertos (0,9086758), macro F1 0,9094733 y F1 Cancro 0,8314607. A tres decimales corresponden 0,909 y 0,831, mientras el paper usa doble redondeo para F1. Esto no prueba la validez del test ni modifica el manuscrito.

EXP-003 permite reconstruir P/R/F1 del umbral .25 desde su matriz; EXP-001 permite recuperar máximos y valores de época del CSV. AP necesita detecciones/puntuaciones individuales o una nueva inferencia; no se reconstruye desde una matriz de confusión. **HIGH** aritmética, **UNVERIFIED** reproducción experimental. REVIEW-04/05/09; [reports/experiments/csv_arithmetic_check.json](<C:/Users/junio/Downloads/mango-vision/ALBUS26_major_revision/reports/experiments/csv_arithmetic_check.json>) y verificación fresca de primera fase.

## 11. ¿Qué métricas carecen de procedencia suficiente?

145 ms CPU, rendimiento Raspberry Pi, eficacia diagnóstica conjunta, detección temprana y generalización rural no tienen la evidencia experimental necesaria. P/R/F1 de Tabla 5 y Fig. 4 responden a umbrales/matching distintos. La validación del best.pt coincide con época 137, pero el pico mAP50 usado en la comparación histórica es de época 95; no son el mismo punto del entrenamiento. El supuesto máximo de recall omite época 1. Las inferencias de época son fuertes, pero no reemplazan el log original. **HIGH** para identificar el hueco; **LOW** para sostener los claims cuantitativos ausentes. EXP-001/002/003/007/008/009; REVIEW-03/07/08/09/10/11/13.

## 12. ¿Existe evidencia preliminar de leakage?

Sí. DATA-003 tiene 41 pares de archivos binariamente iguales entre splits (29 train-valid, 10 train-test, 2 valid-test). DATA-004/005 no tienen esos cruces exactos; los 76 pares del reporte pHash histórico están coasignados. No se recalculó pHash ni se certifica independencia biológica. En M1, 432 nombres sakit_mp4 están repartidos 329/85/18 entre splits y siete bases freshMango aparecen en más de uno: **indicios temporales**, aunque los 669 hashes sean únicos. En DATA-006 nueve ráfagas nominales cruzan train/valid y cinco también test. **HIGH** para duplicación binaria y nombres; **MEDIUM** para inferencia de secuencia compartida hasta recuperar origen. DER-001/003; REVIEW-01/02/03.

## 13. ¿Qué comentarios requieren nuevos experimentos?

REVIEW-01/02: auditoría de similitud/procedencia y partición; REVIEW-03: reentrenamiento M1 sólo si cambia el split o la auditoría lo exige, seguido de evaluación; REVIEW-05: incertidumbre desde predicciones conservadas; REVIEW-07: benchmark real. REVIEW-08 requiere Pi real para producir cifras. REVIEW-13 exige GT específico conjunto; REVIEW-11 exige datos externos independientes si se quiere reclamar validación rural. REVIEW-09 requiere una reevaluación reconstruida además de investigación de procedencia. **HIGH** sobre necesidad; resultados todavía desconocidos. TASK-01–07.

## 14. ¿Qué comentarios sólo requieren cambios editoriales?

REVIEW-06 (desbalance no implica prevalencia), REVIEW-10 (retirar temporalidad no demostrada), REVIEW-14 (redacción), REVIEW-15 (nombres y taxonomía) y REVIEW-16–18 (normas y auditoría bibliográfica) no exigen entrenamiento. REVIEW-04 admite hacer explícitos n y limitación; sus intervalos pertenecen a REVIEW-05. La limitación rural de REVIEW-11 y la explicación de propagación de REVIEW-12 pueden corregirse editorialmente, pero no convierten en validada la cascada. Fig. 1 debe corregir origen del dataset y cuatro enfermedades + Saludable; descripción API/cascada debe reflejar rutas reales. **HIGH**; TASK-08/09, con investigación primaria para referencias.

## 15. ¿Qué está bloqueado?

- REVIEW-13: **BLOCKED_BY_GROUND_TRUTH**, sin enfermedad específica por fruto en escenas de detección.
- REVIEW-08: medición **BLOCKED_BY_HARDWARE**, no hay acceso documentado a Pi en esta fase. Se puede retirar el claim y responder con limitación.
- REVIEW-09: reproducción histórica exacta M1 bloqueada por entorno/base/comando incompletos; una reevaluación reconstruida es distinta y está planificada.
- REVIEW-02: confirmación de secuencias pendiente de originales; agrupamiento conservador permite avanzar sólo si deja unidades suficientes.
- REVIEW-18: referencia Van der Heijden / artículo 106698 discrepante; requiere identificar fuente, sustituirla justificadamente o retirar el claim.

Todas las implementaciones están además pendientes de aprobación SPEC+plan. **HIGH** para los huecos observados, sin suponer que archivos externos no aportados no existan. [docs/research/risk_register.md](<C:/Users/junio/Downloads/mango-vision/ALBUS26_major_revision/docs/research/risk_register.md>).

## 16. ¿Qué riesgos nuevos se descubrieron?

La API actual sólo usa M1; los puntos operativos del paper difieren; el best checkpoint no coincide con el pico mAP50; el máximo de recall excluye una época; hay doble redondeo en F1; el YAML clean aún apunta al dataset original; galerías usan transformaciones BGR/RGB que deben reconciliarse; los datos propios mezclan cajas y polígonos legítimos sin diagnóstico; el test ya examinado no es prospectivo; las figuras conservan taxonomía/procedencia incorrectas y hay una referencia editorial discrepante. **HIGH** documental; impacto cuantitativo sin evaluar. RISK-01–20, CLAIM-001–050, REVIEW-01/03/05/09/11/13/14/15/18.

La revisión independiente del diseño añadió dos riesgos de implementación: elegir una época sin conservar sus pesos y dejar cachés globales fuera del workspace. Ambos se incorporaron a la SPEC/plan mediante contratos y pruebas propuestas. RIR-01/02; DECISION-015/016. No se afirma que esas pruebas futuras ya pasen.

## 17. ¿Qué hará exactamente el plan tras aprobarse?

1. Congelar entradas y preparar entorno aislado reconstruido, con prueba de rutas y hashes.
2. Auditar M1 por igualdad, similitud y origen; comprobar M2 y sus layouts.
3. Conservar o proponer un único split por grupos, con manifest/hash y bloqueo si faltan unidades.
4. Reentrenar M1 desde base sólo si corresponde; conservar el checkpoint realmente seleccionado y toda su procedencia.
5. Evaluar pesos congelados con AP y punto operativo definidos, predicciones individuales e intervalos apropiados.
6. Medir tiempos crudos sobre hardware real; Pi sólo si se dispone de ella.
7. Preparar contrato/evaluador de cascada; métricas únicamente con GT conjunto independiente.
8. Auditar las 23 referencias contra fuentes primarias y normas ALBUS/APA7.
9. Editar una copia del DOCX canónico y regenerar tablas/figuras/respuesta desde artefactos; renderizar e inspeccionar todas las páginas.
10. Verificar desde entorno limpio y someter el resultado a revisión adversarial fresca; cerrar cada requisito con evidencia o bloqueo justificado.

Cada tarea fija archivos, entradas, salidas, precondiciones, tests, comandos y criterios de revisión. **HIGH** para la definición del trabajo; no es una promesa de métricas favorables ni de aceptación editorial.

## Entrega para aprobación

[SPEC](<C:/Users/junio/Downloads/mango-vision/ALBUS26_major_revision/docs/superpowers/specs/2026-09-17-albus26-major-revision-design.md>) · [Plan](<C:/Users/junio/Downloads/mango-vision/ALBUS26_major_revision/docs/superpowers/plans/2026-09-17-albus26-major-revision.md>) · [Self-review SPEC](<C:/Users/junio/Downloads/mango-vision/ALBUS26_major_revision/reports/spec_self_review.md>) · [Self-review plan](<C:/Users/junio/Downloads/mango-vision/ALBUS26_major_revision/reports/plan_self_review.md>) · [Revisión independiente inicial](<C:/Users/junio/Downloads/mango-vision/ALBUS26_major_revision/reports/research_independent_review.md>) · [Validación de primera fase](<C:/Users/junio/Downloads/mango-vision/ALBUS26_major_revision/docs/final_validation_report.md>).

El estado READY_FOR_REVIEW se refiere exclusivamente a los documentos para aprobación. GATE A es documental; B/C esperan aprobación humana y D–I no están superados. La revisión científica completa no está DONE. Se solicita aprobación conjunta antes de ejecutar TASK-01.
