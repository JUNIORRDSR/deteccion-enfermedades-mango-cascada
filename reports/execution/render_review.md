# Revisión del render del manuscrito

**Fecha:** 2026-09-28 · **DOCX:** `manuscript/source/Articulo_Mango_ALBUS_revision.docx`, SHA-256 `d177dd9d2d944b021f3977ecf37271e235f7fcdfd2af8a48d2ce0f0af0397b1b` (pasada 2f) · **PDF:** `manuscript/output/Articulo_Mango_ALBUS_revision.pdf`, SHA-256 `43e79115f05061a5d1b3f0ca37d703ded310df21b0401df7cf29c3f723230418`, 16 páginas.

**Orden:** `powershell -File provenance/commands/task09/render_pdf.ps1 <docx> <pdf>` (Microsoft Word 16.0 por COM, documento abierto en sólo lectura, salida 0). Las 16 páginas se inspeccionaron como PNG con `provenance/commands/task09/pdf_pages.ps1`. Word no dejó archivos de bloqueo en el repositorio. Metadatos del PDF: `/Author` y `dc:creator` son «Daniela Villa Bastidas, Jorge Solano Romero y Marvin Molina-Cárdenas».

| Página | Contenido | Comprobación |
|---|---|---|
| 1 | Título, autores, resumen, palabras clave, inicio de la Sección 1 | Título sin cambios, por decisión de los autores; ambas pruebas declaradas retrospectivas; el resumen cita el repositorio público (Villa Bastidas et al., 2026) |
| 2 | Secciones 1, 2 y 3.1 | Sección 1 sin la cadena causal hacia los agroquímicos; 2.2 declara que no hubo búsqueda sistemática; 3.1 declara que el umbral de 0,4 no se calibró ni se validó |
| 3 | Figura 1, justificación de la cascada, 3.2.1 y Tabla 1 | Figura 1 a 300 ppp; Tabla 1 coherente con 4.1.2 |
| 4 | 3.2.1 a 3.3.2 | 3.3.1 nombra a los agentes de IA de la adjudicación, el ciego por instrucción, la ausencia de revisión humana, los controles positivos fallidos y los desacuerdos; la regla de partición se fijó antes de construir los grupos, no antes de ver los datos |
| 5 | Fin de 3.3.2, 3.4, Tabla 2 y 3.5 | 3.4 sin eficiencia de la variante nano; blanco al pie porque la Tabla 3 pasa entera a la página siguiente |
| 6 | Tabla 3, 3.6, Figura 2 y 3.7 | 3.6 distingue el proyecto original del repositorio del trabajo; 3.7 declara los intervalos condicionales |
| 7 | Fin de 3.7, 4.1.1, Figura 3 y Tabla 4 | 4.1.1 explica la diferencia entre el validador de entrenamiento y el evaluador del artículo |
| 8 | 4.1.2, Tabla 5, 4.1.3 y Figura 4 | Conteos iguales a la matriz |
| 9 | 4.1.4, Figura 5, fuente y 4.1.5 | Ninguna etiqueta de la Figura 5 sale del panel; en el panel con 10 cajas algunas se solapan entre sí (bajo, aceptado) |
| 10 | Fin de 4.1.5, 4.2.1 a 4.2.3 | Latencia con media, desviación típica, mínimo, máximo y composición del conjunto medido; 4.2.1 declara el cluster con etiquetas distintas y los duplicados de entrenamiento y validación |
| 11 | Tabla 7, confusiones, Figura 6 y 4.2.4 | Confusión Cancro–Costras como hipótesis |
| 12 | Figura 7, fuente y 4.3 | Panel del mosaico con 16 cajas y etiquetas pequeñas, dibujadas por el propio script de línea de comandos (bajo, aceptado) |
| 13 | 5, 5.1 a 5.4, 6 y 6.1 | 5.2 declara el cambio de dominio del clasificador; 5.3 cita el repositorio |
| 14 | Fin de 6.1, Tabla 8, 6.2 y 7 | 6.1 declara que las etiquetas miden concordancia con etiquetas visuales de terceros, no validez fitopatológica |
| 15 | Conclusión, disponibilidad de datos, agradecimientos y referencias | La disponibilidad de datos cita el repositorio, sus contenidos y la licencia AGPL-3.0 |
| 16 | Referencias (fin) | 22 entradas en orden alfabético; Ultralytics citado por la etiqueta v8.4.52; entrada del repositorio entre Venbrux y Zauner |

Numeración: Secciones 1 a 7 con sus subsecciones en orden; Tablas 1 a 8 y Figuras 1 a 7 consecutivas, cada una citada en el texto antes de aparecer. Ningún título queda solo al pie de una página, ninguna tabla se corta entre páginas y ningún título de tabla se separa de su tabla: la pasada 2f mantiene el título y cada fila de una tabla con la fila siguiente. El precio es blanco al pie de las páginas 5, 7 y 10.

Citas: `provenance/commands/task09/check_citations.py` encuentra 22 entradas y 22 claves citadas, sin huecos en ninguna dirección.

El pie de página «ALBUS 2025, 3, x. https://doi.org/» es la plantilla de la revista y lo completa la editorial.
