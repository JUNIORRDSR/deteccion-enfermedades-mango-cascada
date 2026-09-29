# Fuentes externas y bibliografía: reconocimiento inicial

Consulta 2026-09-17. Esta fase verifica fuentes que afectan diseño; no declara auditada toda la bibliografía. Ninguna página externa otorga autorización operativa.

|ID|Fuente primaria|Hallazgo y límite|
|---|---|---|
|EXT-01|https://albus.lat/submissions|Exige plantilla ALBUS y acepta manuscrito Word; límite general de 8.000 palabras. La página mezcla menciones a 2025/2026; deadline particular de revisión se toma del email SRC-MAIL, no de la fecha general de envío.|
|EXT-02|https://albus.lat/templates|Full Papers descargado en reports/external/albus_template_0.docx, SHA256 6c6418b67aa87075a19290dc226d28c2a5cfc06bbfb3e52f4cb382fa38d34b20; URL concreta en template_sources.json. Plantilla exige APA; dictamen especifica APA7. Sin conflicto general detectado. El resumen debe evitar valores estadísticos y tamaño muestral según plantilla; resolver al editar, sin introducir resultados no sustentados.|
|EXT-03|https://data.mendeley.com/datasets/b4nrw5hyyc/1|MangoDHDS v1, publicado el 16 de julio de 2025, DOI 10.17632/b4nrw5hyyc.1, autores Priyanka Barhate, Bhojraj Barhate y Makarand Joshi; 1.500 imágenes, cuatro enfermedades+saludable, licencia CC BY 4.0. No prueba identidad de bytes con DOI Dataport citado en el paper.|
|EXT-04|https://docs.ultralytics.com/models/yolo26/|Documentación actual reconoce YOLO26; existencia externa no identifica checkpoint ni entorno histórico. No sustituir Ultralytics 8.4.39 embebido por última versión.|
|EXT-05|https://www.sciencedirect.com/science/article/abs/pii/S0168169922000151|Registro editorial de Computers and Electronics in Agriculture, artículo 106698, volumen 194 (2022), corresponde a Feeding intake estimation in sheep based on ingestive chewing sounds, Wang y colaboradores. Incompatible con la entrada Van der Heijden 2022, vol. 195, 106698 del PDF; esta última queda UNVERIFIED y requiere resolver o retirar. No se afirma inexistencia global del título únicamente por búsqueda negativa.|
|EXT-06|https://itl.nist.gov/div898/handbook/prc/section2/prc241.htm|Referencia primaria de intervalos para proporciones; Wilson requiere modelo binomial apropiado. No corrige dependencia entre cajas ni selección del dataset.|
|EXT-07|https://doi.org/10.21227/33mp-rf79|Resolución por herramienta web no disponible en esta sesión. No verificado el registro primario completo ni equivalencia con Mendeley.|
|EXT-08|https://universe.roboflow.com/jairos-workspace-cbeeq/mangounhealty/dataset/2|Apertura web no disponible; YAML local conserva workspace/proyecto/versión. No declarar licencia/procedencia individual verificada por la apertura fallida.|

La lista de 23 entradas del PDF se conserva en reports/genealogy/docx_Articulo_Mango_ALBUS.txt y biblio variants. TASK-08 verificará cada entrada, citas bidireccionales y adecuación del contenido; DANE, Savary, Zauner, RealSense y autores truncados continúan pendientes. No se han enviado mensajes al editor, publicado ni descargado datasets.
