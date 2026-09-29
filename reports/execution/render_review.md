# Revisión del render del manuscrito

**Fecha:** 2026-09-29 · **DOCX:** `manuscript/source/Articulo_Mango_ALBUS_revision.docx`, SHA-256 `f16115958d081467283089639b9f5f7a901acca2a835e20c364c55be016395ed` (pasada 2h) · **PDF:** `manuscript/output/Articulo_Mango_ALBUS_revision.pdf`, SHA-256 `86bd462910f09b41d4a9920f30bd1022d0a26c98e56fcb30653e233222120b28`, 16 páginas.

**Orden:** `powershell -File provenance/commands/task09/render_pdf.ps1 <docx> <pdf>` (Microsoft Word 16.0 por COM, documento abierto en sólo lectura, salida 0). Las páginas se inspeccionaron como PNG con `provenance/commands/task09/pdf_pages.ps1`. La pasada 2h sólo cambia la versión citada del repositorio en la página 16, que se inspeccionó en el render final. Las páginas 3, 7 a 10 y 15 se inspeccionaron en el render de la pasada 2g con la Figura 1 definitiva. Las páginas 1, 2, 4 a 6 y 11 a 14 se inspeccionaron en el primer render de la pasada 2g. Su DOCX sólo difiere del final en la imagen de la Figura 1, con el mismo tamaño en píxeles; el texto y los saltos de página son los mismos.

| Página | Contenido | Comprobación |
|---|---|---|
| 1 | Título, autores, resumen, palabras clave, inicio de la Sección 1 | El resumen ya no atribuye el costo al «productor rural colombiano». Las cifras de M1 y M2 no cambian |
| 2 | Secciones 1, 2 y 3.1 | «Kapoor y Narayanan (2023) documentan…». La Sección 2.4 remite a «los dos corpus públicos de mango» y la frase de Padilla et al. (2020) queda aparte |
| 3 | Figura 1, justificación de la cascada, 3.2.1 y Tabla 1 | La flecha del Modelo 2 dice «clase». La justificación dice «el corpus con cajas en escenas de campo abierto» |
| 4 | 3.2.1 a 3.3.2 | 3.3.1 describe primero la adjudicación asistida por agentes de IA, con su ciego por instrucción y su fiabilidad limitada, y después la revisión manual de una integrante del equipo. Los grupos proceden de las decisiones registradas. 3.3.2 queda en una sola frase, sin «anomalía significativa» |
| 5 | Fin de 3.3.2, 3.4, Tabla 2 y 3.5 | «Una nueva ejecución del detector de duplicados en esta revisión…»; «Se usa la modalidad de clasificación…» |
| 6 | Tabla 3, 3.6, Figura 2 y 3.7 | 3.6 dice «una clasificación con confianza inferior a 0,4». La Tabla 3 no se corta |
| 7 | Fin de 3.7, 4.1.1, Figura 3 y Tabla 4 | Sin cambios de contenido |
| 8 | 4.1.2, Tabla 5, 4.1.3 y Figura 4 | Cifras y matriz iguales a las de la pasada 2f |
| 9 | 4.1.4, Figura 5 e inicio de 4.1.5 | Sin cambios de contenido |
| 10 | Fin de 4.1.5 y 4.2.1 a 4.2.3 | Sin cambios de contenido |
| 11 | Tabla 7, confusiones, Figura 6 y 4.2.4 | 4.2.4: «no demuestra que las clases asignadas sean correctas» |
| 12 | Figura 7, fuente y 4.3 | «La clase de enfermedad la asigna el Modelo 2» |
| 13 | 5, 5.1 a 5.4, 6 e inicio de 6.1 | 5.2 habla de «las cinco clases» y de «caja y enfermedad adjudicadas». 5.4 ya no dice «métricas estables» |
| 14 | Fin de 6.1, Tabla 8 y 6.2 | 6.1 añade la limitación de la adjudicación y remite a 3.3.1. La Tabla 8 dice «Etiquetas de imagen completa en MangoDHDS» |
| 15 | 7, disponibilidad de datos, agradecimientos e inicio de las referencias | Sin cambios de contenido |
| 16 | Referencias (fin) | 22 entradas en orden alfabético; el repositorio del trabajo se cita en la versión 1.0.1 |

Numeración: Secciones 1 a 7 con sus subsecciones en orden; Tablas 1 a 8 y Figuras 1 a 7 consecutivas. Ningún título queda solo al pie de una página, ninguna tabla se corta entre páginas y ningún título de tabla se separa de su tabla.

Citas: `provenance/commands/task09/check_citations.py` encuentra 22 entradas y 22 claves citadas, sin huecos.

El pie de página «ALBUS 2025, 3, x. https://doi.org/» es la plantilla de la revista y lo completa la editorial.
