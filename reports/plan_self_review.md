# Self-review y coherencia del plan

Primera fase: no se han ejecutado los comandos científicos que contiene el plan. Las CLIs y tests son entregables futuros identificados como tales.

- Las diez tareas incluyen FILES, CONSUMES, PRODUCES, PRECONDITIONS, STEPS, TESTS / VERIFICATION COMMANDS, EXPECTED RESULTS, ARTIFACTS y REVIEW-IDs SATISFIED. La matriz final cubre los 18 requisitos.
- El orden fija procedencia→auditoría→split→entrenamiento condicional→evaluación antes de editar métricas. Un bloqueo no se transforma en ejecución ficticia. No hay código de modelo nuevo en `src/` ni tests científicos implementados ahora.
- Se corrigió la selección de pesos: el test verifica ruta/hash y precisión, incluidos empates y valores distintos que colapsan a seis cifras; un entero epoch no basta.
- TASK-01 redirige configuración/cachés/temporales antes de venv/pip/imports, y exige una prueba del aislamiento en proceso hijo. La versión común coincide con la SPEC; la instalación no se presenta como realizada.
- El fixture de split usa `validate_group_atomicity` y exige el error `GROUP_CROSSES_SPLIT:g`; así no pasa por una ruta/label ausente. La validación completa prueba por separado las restantes entradas.
- El algoritmo del pool del benchmark es determinista por estrato y hash. El reloj falso distingue suma de etapas y temporizador exterior, evitando exigir una igualdad falsa.
- Los números sintéticos de clasificación, matching, abstención y bootstrap verifican el método; ninguna prueba impone rendimiento mínimo al modelo.
- Se conserva el esquema de GT y una salida de bloqueo útil aunque no haya anotaciones. La revisión bibliográfica es primaria y semántica, no sólo regex.
- El plan exige render y lectura visual de todas las páginas antes de afirmar build/manuscrito final correctos. Ni DOCX ni PDF fueron editados en esta fase.
- La última tarea requiere un revisor científico fresco y reproducción desde entorno limpio. La revisión del diseño actual no sustituye esa revisión adversarial final.

Relectura editorial: se restauraron espacios, frases y nombres; se conservaron comandos y valores. La verificación administrativa revisa además campos, IDs, cobertura y hashes. Ninguna casilla de implementación queda marcada como realizada. Resultado: plan listo para revisión humana una vez comprobados sus artefactos actuales.

Relectura adicional: se hizo explícita la correspondencia DATA-004→DATA-005 por nombre/hash/clase/split, con multiplicidad y SRC de ambos. Los intervalos consumen el manifiesto congelado M2 con IDs de predicción. Se añadieron comandos de validación y congelación del umbral previos al test y pruebas de rechazo por hash o split incorrectos.
