# Registro de ejecución

Primera ejecución, 2026-09-17: **cero nuevos experimentos científicos**.

Se realizaron lectura de archivos, hashes SHA256, conteos de inventario, extracción de texto PDF/DOCX, índices ZIP, diffs, transcripción segura de metadata de checkpoints y contraste aritmético de CSV existentes. No se cargaron pesos en torch/Ultralytics, no se ejecutaron scripts legacy, no se calculó pHash nuevo ni se entrenó/evaluó/benchmarkeó un modelo. Ningún valor del manuscrito fue sustituido.

Los EXP históricos se registran en provenance/experiment_registry.csv; todos llevan reproduced=NO. Los comandos de investigación están en provenance/commands/ y los scripts de lectura especializados en reports/{datasets,experiments,genealogy}/. Las interrupciones por límite de uso no son runs experimentales fallidos: se conservaron artefactos y se reanudó la documentación tras «Continua».

Después de aprobación cada run deberá tener ID, timestamp, comando, exit code, entorno, entradas hasheadas, outputs, motivo de fallo y relación a claims. No sobrescribir ni eliminar resultados desfavorables.
