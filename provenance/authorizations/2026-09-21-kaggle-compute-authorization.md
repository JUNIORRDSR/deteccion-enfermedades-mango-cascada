# Autorización de usuario — 2026-09-21

## Cita literal de la instrucción recibida

> quiero Continuar con el desarrollo y que entiendas el contenido en el que estaba trabajando codex en "C:\Users\junio\Downloads\mango-vision", quiero que en base a eso sigas trabajando con todos los lineamientos correctos para el desarrollo y validacion cientifica para la publicacion de la revista; Quiero que primero revises todas las skills que tengas que te puedan ayudar en esto, tambien quiero que uses la skills de codex para generar adversarial reviews con sus mejores modelos para tener una calidad alta en el proyecto y poder calcular bien cualquier cosa y desicion que parezca saltada o poca validada/reproducible, si USA el MCP de Kaggle para montar todo el procesamiento del entrenamiento y toda la parte pesada de analisis en kaggle con sus GPU y procesamiento que tiene para tener buenos resultados en menores tiempos

## Qué autoriza explícitamente

1. Continuar la ejecución secuencial del plan congelado `ALBUS26-116-PROTOCOL-001`.
2. Usar el MCP de Kaggle como entorno de cómputo para el entrenamiento y el análisis pesado. Esto es una acción externa y, por tanto, requería la consulta prevista en la regla de detención global (1) de la SPEC §11; esta instrucción la satisface.
3. Emitir revisiones adversariales con los subagentes de Codex.

## Qué NO autoriza y sigue prohibido

- Publicación de datos o de cualquier artefacto: los datasets de Kaggle se crean **privados**. No se publica notebook, dataset, modelo ni manuscrito.
- `git push`, merge a repositorios externos o cambios en `Mango-vision` / `SemilleroTI-Mangos`.
- Subir el manuscrito, el dictamen del revisor, el correo editorial ni datos personales.
- Sustituir la medición de latencia en CPU local ni inventar mediciones de Raspberry Pi.

## Efecto sobre el freeze

El plan congelado contiene la restricción literal «Si no hay capacidad para entrenar, TASK-04 produce bloqueo con evidencia de capacidad y mantiene pendiente el resultado; no inventar hardware Kaggle». Esa cláusula prohibía **asumir** capacidad de Kaggle sin evidencia, no prohibía usarla con autorización y medición. El cambio de sede de cómputo es material, así que se tramita como `PROTOCOL-AMENDMENT-008` con evidencia de capacidad medida y revisión independiente fresca antes de ejecutar cualquier run.

## Interpretación registrada del alcance «todo el análisis pesado»

Se asigna a Kaggle el cómputo que el hardware local no puede realizar con validez científica (entrenamiento con GPU e inferencia con GPU). Se mantiene local el cómputo cuya validez depende precisamente del hardware local o cuya reproducibilidad se degradaría en GPU: benchmark de CPU (REVIEW-07/08), auditoría pHash y estadística determinista. El detalle y el motivo por tarea constan en `PROTOCOL-AMENDMENT-008`. Si el usuario quiere además esas partes en Kaggle, es una decisión suya que se tramitaría como enmienda adicional.
