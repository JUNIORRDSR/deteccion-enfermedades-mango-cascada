# Registro de riesgos

Estado inicial; no resultados experimentales nuevos.

|risk_id|description|likelihood|impact|detection|mitigation|residual_risk|status|
|---|---|---|---|---|---|---|---|
|RISK-01|Frames del mismo video repartidos entre splits M1|HIGH|CRITICAL|432 sakit_mp4 en train/valid/test; DATA-001|Reconstruir secuencias; agrupación conservadora; reentrenar si contaminación|Nombre no demuestra escena exacta; pHash omite relaciones|OPEN|
|RISK-02|pHash no detecta todos recortes/iluminación/frutos repetidos|HIGH|HIGH|Contact sheets y metadatos externos|Separar similitud de procedencia y documentar límites|No puede certificar ausencia absoluta de fuga|OPEN|
|RISK-03|Test pequeño y unidades correlacionadas|HIGH|HIGH|33 imágenes / 99 instancias / 13 Enfermo|CI agrupados, n efectivo y lenguaje moderado|CI no resuelve sesgo de selección|OPEN|
|RISK-04|Falta GT específico para cascada y OOD colombiano|HIGH|CRITICAL|DATA-001 binario; DATA-006 mango; DATA-005 imagen|Bloquear métrica; protocolo anotación independiente|Puede impedir resolver cuantificación pedida|BLOCKED_BY_GROUND_TRUTH|
|RISK-05|Entorno original M1 y comando exacto incompletos|HIGH|HIGH|Metadata pesos identifica 8.4.39, no todas dependencias|Recuperar logs; etiquetar entorno nuevo reconstruido|No confundir reproducción parcial con exacta|OPEN|
|RISK-06|Hardware Raspberry Pi/logs latencia ausentes|HIGH|HIGH|Sin raw times; afirmaciones contradictorias|Benchmark real o retirar claim|No se demuestra cumplimiento edge|BLOCKED_BY_HARDWARE|
|RISK-07|Métricas Tabla 5 y Fig. 4 con puntos operativos diferentes|HIGH|HIGH|conf=.001 evaluación vs .25 matriz y matching|Unificar umbral primario validation, separar AP|Resultados históricos no directamente comparables|OPEN|
|RISK-08|Máximos por época confundidos con checkpoint elegido|HIGH|HIGH|best coincide con época 137; máximo mAP50 en época 95; máximo R en época 1 omitido|Reportar todas métricas de un checkpoint congelado|Cambiar números afecta conclusiones|OPEN|
|RISK-09|Redondeo doble de F1 y sumarios|HIGH|MEDIUM|Macro F1 de matriz=.9094733;CSV=.9095;paper=.910|Full precision hasta formato final|Pequeña diferencia no justifica ignorarla|OPEN|
|RISK-10|API descrita como cascada pero ruta real usa M1|HIGH|HIGH|Lectura callers api→vision|Describir implementación disponible; no desarrollar para validar historia|Versión externa no aportada podría existir|OPEN|
|RISK-11|Bibliografía no identificable o metadata contradictoria|HIGH|HIGH|Registro editorial 106698 ajeno a Van der Heijden; citas software genéricas|Auditoría primaria completa y alcance claim→citation|Acceso a fuente/licencia puede faltar|OPEN|
|RISK-12|Claim temprano/prevalencia/diagnóstico supera diseño|HIGH|HIGH|Sin temporalidad, epidemiología o GT clínico|Moderar o retirar|El prototipo sólo respalda signos visuales en datasets|OPEN|
|RISK-13|Etiquetas propias mezclan polígonos y bbox|HIGH|HIGH|965 líneas multipunto, 568 bbox|No descartar; elegir protocolo de conversión explícito si se usa|Caja derivada no equivale a diagnóstico|OPEN|
|RISK-14|Pipeline clasificador reutiliza layout y puede ignorar origen|MEDIUM|HIGH|make_cls_layout/log y correspondencia local por hash comprobada; vínculo histórico incompleto|Manifest de membresía/hash y aserción clean↔cls|Igual count no prueba misma membresía|OPEN|
|RISK-15|Duplicados dentro del test M2 alteran n efectivo|HIGH|HIGH|100 pares binarios corpus; agrupados entre splits pero conservados|Reportar estimando por imagen y CI por cluster; no borrar raw|Dependencia biológica más amplia que cluster pHash|OPEN|
|RISK-16|Fuente editable y figuras arrastran textos antiguos|HIGH|MEDIUM|Fig. 1 dice Roboflow propio / 5 enfermedades; prosa difiere|Editar texto embebido de figuras y revisar render|Nueva figura debe enlazar al mismo método final|OPEN|
|RISK-17|Acceso histórico al test permite decisiones retrospectivas|MEDIUM|HIGH|Resultados ya examinados/publicados; faltan logs de acceso|Preregistrar decisiones ahora; test futuro congelado; declarar historia previa|El test actual no es nuevo holdout prospectivo|OPEN|
|RISK-18|Legacy científico cambia inadvertidamente|LOW|CRITICAL|Manifest SHA256 y status inicial|Comparación fresca al final; salidas exclusivamente workspace|.git/.venv/__pycache__ excluidos del hash; no certificación universal|CONTROLLED_WITH_LIMITS|
|RISK-19|33 imágenes de test carecen grupos suficientes bajo partición conservadora|MEDIUM|HIGH|Auditoría aún pendiente|No fragmentar grupos para fabricar tamaño; bloquear inferencia por clase insuficiente|Puede requerir datos adicionales antes de reentrenar|OPEN|
|RISK-20|Datos/código/figuras no ligados al run de forma inmutable|HIGH|HIGH|Manifests históricos ausentes; notebooks sin outputs|RunID único, hashes, comando, logs, predicciones y registro de artefactos|Parte del pasado seguirá UNVERIFIED|OPEN|

HIGH indica evidencia o probabilidad cualitativa, no probabilidad numérica estimada. No se han probado los riesgos experimentales con ejecuciones nuevas.
