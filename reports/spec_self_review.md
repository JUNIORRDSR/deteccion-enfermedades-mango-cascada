# Self-review de la SPEC

Alcance: diseño documental de primera fase, no validación de datos ni modelos. Se realizó una segunda lectura como investigador externo siguiendo fuente→dato→run→claim, sin asumir que el nombre de un archivo prueba procedencia.

|Pregunta de revisión|Resultado y corrección|
|---|---|
|¿Responde a la solicitud real y al dictamen?|18 REVIEW-ID cubiertos. Se conserva el gate conjunto y la prohibición de nuevos experimentos en esta fase.|
|¿Distingue hechos e inferencias?|PDF confirmado por usuario; texto DOCX normalizado idéntico; época 137 inferida de métricas; origen exacto de entradas históricas no certificado.|
|¿Una auditoría sin pares puede llamarse limpia?|No. SHA/pHash, nombres, secuencias y dependencia biológica se distinguen; limitaciones explícitas.|
|¿La política de split es ejecutable?|Se precisó coste global normalizado, desempates, seed y condiciones de bloqueo. No se fragmentan grupos para fabricar test.|
|¿El checkpoint seleccionado existe?|RIR-01 corrigió el desempate: último máximo nativo, fitness sin redondear, registro de época y hash, conservación antes del stripping.|
|¿Hay contradicción de versiones?|RIR-03: un entorno reconstruido 8.4.52 propuesto; 8.4.39 permanece como evidencia histórica. Compatibilidad queda por comprobar antes de ejecutar.|
|¿Puede el runtime escribir en legacy/perfil global?|RIR-02 añadió redirección antes de instalar/importar y comprobación de rutas efectivas en proceso hijo. El aislamiento de diseño no equivale a una prueba de ejecución ya superada.|
|¿Los intervalos respetan dependencia y pequeños n?|Unidad grupo cuando existe; indefinición explícita; Wilson restringido; no se afirma que el CI elimine sesgo.|
|¿El benchmark promete lo que no mide?|Define archivo→JPEG con pesos residentes y etapas internas separadas; excluye red/API/SQLite, cold-start aparte. Pi exige hardware real.|
|¿La cascada puede evaluarse ahora?|No: falta GT específico por fruto. Se rechaza convertir predicciones en etiquetas; entregable futuro condicionado.|
|¿El plan puede cerrar con limitaciones?|Sí, retirando/moderando claims y respondiendo con causa, sin declarar resuelto experimentalmente lo bloqueado ni anticipar aceptación del congreso.|
|¿La fuente editable y bibliografía se eligen por comodidad?|No: genealogía y plantilla oficial respaldan DOCX; las 23 referencias necesitan auditoría completa posterior.|

RIR-04/05 corrigieron además la matriz de evidencia: conteos enlazados al manifiesto derivado y afirmación sobre cajas originales moderada. RIR-06 motivó lectura y corrección editorial completa. La revisión externa se conserva en `research_independent_review.md`; su relectura posterior debe comprobar la resolución sin reemplazar esta self-review.

Conclusión documental: diseño concreto para aprobación, con dependencias bloqueadas explícitas. La aprobación humana y todos los gates experimentales siguen pendientes.
