# Política de publicación de la evidencia de entorno

Autoridad duradera. Cierra el hallazgo 11 (LOW) de la primera revisión adversarial y su reapertura en la segunda, que señaló con razón que **aceptar un hallazgo y diferir su ejecución no es cerrarlo**.

## El problema concreto

`provenance/environment/`, `provenance/incidents/` y los informes de contención contienen, hoy y a propósito:

- el nombre de cuenta de Windows `junio` en rutas absolutas;
- el identificador de paquete del sandbox, `Claude_pzs8sxrjxfjjc`;
- la disposición completa del perfil y del árbol de trabajo;
- un UUID de máquina generado por Ultralytics.

No son credenciales, y **parte de esa evidencia absoluta la exige el protocolo congelado**: sin rutas y ejecutables exactos no hay reproducibilidad. El conflicto es real, no aparente: lo que hace la evidencia útil es lo que la hace identificable.

## Clasificación

| clase | contenido | destino |
|---|---|---|
| **Privada, enlazada por hash** | rutas absolutas, nombre de cuenta, identificador de sandbox, UUID de máquina, inventario de perfil, rutas de los incidentes | se conserva íntegra en el repositorio de revisión; **no** se publica como material suplementario |
| **Publicable** | sistema operativo y build, versiones de Python y de cada paquete con sus hashes de build, índices efectivos con host pero sin credenciales, identidad y topología del procesador, presencia o ausencia de GPU y CUDA, comandos con ejecutable **relativo**, exit codes, y el SHA256 de cada artefacto privado correspondiente | proyección determinista generada en TASK-10 |

## Reglas de la proyección

1. **Determinista y comprobable.** Dos ejecuciones sobre la misma evidencia privada producen bytes idénticos. Se prueba con un test, no se afirma.
2. **Sustitución, no borrado.** El nombre de cuenta pasa a `<USER>`, el identificador de sandbox a `<SANDBOX>`, la raíz del checkout a `<CHECKOUT>`, y el UUID de máquina a `<MACHINE_UUID>`. Sustituir preserva la estructura, que es lo que un revisor necesita para juzgar el aislamiento.
3. **Nada científicamente necesario se pierde.** Versiones, hashes, host de los índices, topología, exit codes y comandos permanecen legibles. Si una sustitución impidiera reproducir algo, se revisa la regla, no se publica el dato crudo.
4. **Enlace por hash.** Cada archivo publicable declara el SHA256 del archivo privado del que deriva, de modo que un revisor con acceso al repositorio pueda verificar la correspondencia.
5. **Fallo cerrado.** Un patrón identificable conocido que aparezca en la proyección hace fallar la generación. La lista de patrones vive junto al generador y ampliarla es una edición ordinaria, no una enmienda.

## Los tres archivos externos de INCIDENT-001

`C:/Users/junio/AppData/Roaming/Ultralytics/settings.json`, su vista redirigida por el sandbox y `C:/tmp/Ultralytics/settings.json` contienen rutas del workspace y el UUID de máquina. **Su disposición corresponde al dueño del equipo y sigue pendiente.** Sea cual sea la decisión, las copias y hashes preservados en `provenance/incidents/` permanecen como evidencia, y su contenido cae en la clase privada: no se publica.

## Cuándo se ejecuta

El generador y su test se implementan en **TASK-10**, que es la tarea que prepara la entrega. Diferir la ejecución es razonable; lo que no era aceptable, y por eso existe este documento, es haber llamado «aceptado» a un hallazgo sin dejar una política duradera que fije qué se retiene, qué se publica y cómo se comprueba.

Hasta que esa proyección exista y pase su test, **no se publica ningún archivo de `provenance/environment/` como material suplementario**.
