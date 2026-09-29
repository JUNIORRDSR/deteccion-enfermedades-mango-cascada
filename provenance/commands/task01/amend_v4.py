"""Apply version 4 of PROTOCOL-AMENDMENT-008 after the third independent review."""

import hashlib
from pathlib import Path

BS = chr(92)


def sha(relative: str) -> str:
    return hashlib.sha256(Path(relative).read_bytes()).hexdigest()


def main() -> int:
    path = Path('provenance/protocol_amendments/PROTOCOL-AMENDMENT-008-kaggle-compute.md')
    s = path.read_text(encoding='utf-8')
    replacements = []

    replacements.append(('**Versión 3.**', '**Versión 4.**'))
    replacements.append((
        'Esta versión responde a todos.',
        'La v3 fue rechazada una tercera vez (HIGH 2, MEDIUM 3), aunque cerró seis hallazgos. '
        'El patrón que el revisor identificó es exacto: la v3 **describía** mecanismos en vez de '
        'construirlos. Esta versión los construye y los deja ejecutables.'))
    replacements.append(('| `version` | 3 |', '| `version` | 4 |'))
    replacements.append((
        '| `review_v3` | **pendiente** |' + chr(10) + '| `state` | **PROPOSED_V3** |',
        '| `review_v3` | `reports/amendments/amendment-008-independent-review-round3.md`, SHA256 `'
        + sha('reports/amendments/amendment-008-independent-review-round3.md')[:16]
        + '...`, veredicto NO APROBAR, HIGH 2 / MEDIUM 3, más N-03 MEDIUM. Cerró H-01, H-04, H-05, '
          'H-06, N-01 y N-02 |' + chr(10)
        + '| `review_v4` | **pendiente** |' + chr(10) + '| `state` | **PROPOSED_V4** |'))

    validator_block = (
        'El esquema y el validador **ya existen y son ejecutables**. No son una promesa:' + chr(10) * 2
        + '| artefacto | ruta | SHA256 |' + chr(10) + '|---|---|---|' + chr(10)
        + '| esquema de entrada | `configs/kaggle_input_schema.json` | `'
        + sha('configs/kaggle_input_schema.json')[:32] + '...` |' + chr(10)
        + '| validador | `src/evaluation/kaggle_inputs.py` | `'
        + sha('src/evaluation/kaggle_inputs.py')[:32] + '...` |' + chr(10)
        + '| fixtures | `tests/test_kaggle_inputs.py` | `'
        + sha('tests/test_kaggle_inputs.py')[:32] + '...` |' + chr(10) * 2
        + '15 fixtures, positivos y negativos, uno por cada bypass que esta enmienda dice cerrar: '
          'archivo no declarado, split de test en fase de entrenamiento, **imagen de test renombrada '
          'detectada por hash de bytes**, grupo excluido, campo `download` en el YAML, entrada `test` '
          'en el YAML de entrenamiento, hash alterado, extensión desconocida **rechazada y no '
          'ignorada**, hardlink, versión efectiva nula de un recurso adjunto, y raíz FATAL sin '
          'definir. La revisión independiente puede **ejecutarlos**, que era el criterio de cierre '
          'exigido:' + chr(10) * 2
        + '```powershell' + chr(10)
        + '& .' + BS + '.venv' + BS + 'Scripts' + BS + 'python.exe -m unittest tests.test_kaggle_inputs -v'
        + chr(10) + '```' + chr(10) * 2
        + 'El contrato de raíces es **cerrado** y vive en el esquema: cada raíz declara su variable de '
          'entorno, su valor por defecto y su comportamiento si no está definida (`FATAL`, '
          '`USE_DEFAULT` o `TOLERATE_ABSENT`). Incluye `KAGGLEHUB_CACHE`, `XDG_CACHE_HOME`, '
          '`PIP_CACHE_DIR`, `TORCH_HOME`, `HF_HOME`, `TMPDIR`, `YOLO_CONFIG_DIR`, `/kaggle/input`, '
          '`/kaggle/working`, `/kaggle/temp` y el directorio de trabajo. Añadir o quitar una raíz '
          '**es una enmienda del esquema**, no una decisión del operador.' + chr(10) * 2
        + 'La gramática de indirecciones también es **cerrada**: sólo se parsean `.txt` (una ruta por '
          'línea) y `.yaml`/`.yml` (claves `path`, `train`, `val`, `test`). Cualquier otra extensión '
          'que no sea imagen, etiqueta o checkpoint se **rechaza**, de modo que una indirección en un '
          'formato no previsto no pueda pasar inadvertida.' + chr(10) * 2
        + 'Una **versión efectiva nula** de un recurso adjunto es fatal, igual que una discrepancia '
          'entre la versión declarada y la efectiva.')
    replacements.append((
        'Antes de cualquier subida se congela, con hash, un **esquema de inventario y un validador '
        'ejecutable** con fixtures positivos y negativos. «Fail closed» deja de depender de '
        'decisiones posteriores de implementación.', validator_block))

    custodian = (
        '- **Custodio distinto, o bloqueo explícito.** Un custodio identificado y distinto de quien '
        'elige el umbral verifica y hashea el paquete previo al test antes de que el recurso de test '
        'se adjunte. **A día de hoy no hay custodio designado ni clave de firma configurada en este '
        'repositorio.** Por tanto la fase de test de TASK-05 queda **`BLOCKED_BY_CUSTODIAN`** y así '
        'se declara, en lugar de fingir un procedimiento aprobado con un custodio que el proyecto no '
        'tiene. Designarlo, con su clave y huella, es un prerrequisito bloqueante y una decisión del '
        'usuario.' + chr(10)
        + '- **Primitiva inmutable con comandos exactos**: el paquete previo al test se sella como '
          '**etiqueta anotada y firmada de Git** y se verifica antes de adjuntar el test:' + chr(10) * 2
        + '```powershell' + chr(10)
        + 'git tag -a -s pretest/EXP-R02 -m "sealed pre-test bundle"' + chr(10)
        + 'git tag -v pretest/EXP-R02' + chr(10)
        + 'git rev-parse pretest/EXP-R02^{}' + chr(10)
        + '```' + chr(10) * 2
        + '  La ausencia del objeto al verificar es **fallo del Gate E**, no una omisión. Se conserva '
          'además una copia de sólo lectura fuera del alcance de escritura del operador; su ubicación '
          'y titular se registran al designar al custodio. Sin custodio no hay sellado, y sin sellado '
          'no hay fase de test.')
    replacements.append((
        '- **Un custodio identificado y distinto de quien elige el umbral** verifica y hashea el '
        'paquete previo al test **antes** de que el recurso de test se adjunte. Sin esa firma, la '
        'fase de test no se lanza.' + chr(10)
        + '- **Primitiva de almacenamiento inmutable declarada**: el paquete previo al test se sella '
          'como objeto Git anotado y firmado en este repositorio, con su hash registrado, más copia '
          'de sólo lectura. No es «un archivo que decimos que es de escritura única».', custodian))

    replacements.append((
        '- **Reconciliación con la plataforma**: al cerrar la fase se obtiene del historial de la '
        'cuenta la lista de versiones de kernel, intentos y salidas, y se **reconcilia con el '
        'registro local**. Un intento visible en la cuenta y ausente del registro local, o borrado, '
        'es **fallo del Gate E**, no una omisión menor.',
        '- **Reconciliación con la plataforma, con su límite declarado.** La interfaz pública de '
        'Kaggle documenta listar kernels, empujar y recuperar salidas y consultar el estado del '
        '**último** run; **no documenta una exportación de auditoría que garantice enumerar todo '
        'intento, cancelación y borrado**. La afirmación se **acota**: se reconcilia lo que la '
        'interfaz expone y, como esa fuente no es exhaustiva, se añade un **registro de lanzamiento '
        'y acceso retenido de forma independiente**, fuera del alcance de escritura del operador, '
        'contra el que se contrasta. Un intento visible en una fuente y ausente en la otra es '
        '**fallo del Gate E**.'))

    replacements.append((
        '- **Taxonomía cerrada de reintento técnico**, fijada antes de lanzar: (a) fallo de '
        'infraestructura de la plataforma, (b) cuota agotada, (c) fallo de integridad verificable en '
        'la carga de entradas. Nada más. Se elimina «error de carga» por ambiguo. Cualquier otra '
        'causa es una parada, no un reintento.',
        '- **Taxonomía cerrada de reintento técnico**, fijada antes de lanzar: (a) fallo de '
        'infraestructura de la plataforma **acreditado con evidencia de la propia plataforma**, no '
        'con la apreciación del operador; (b) fallo de integridad verificable en la carga de '
        'entradas, es decir el validador de §4.1 devolviendo `FAIL`. Nada más. **Se elimina «cuota '
        'agotada» como causa de reintento**: si el run no cabe, debe rechazarlo la regla de capacidad '
        'de §7.2 antes de lanzar. Todo reintento permitido reutiliza el **paquete sellado byte a '
        'byte** y sella cualquier salida parcial ya producida antes de relanzar.'))

    capacity = (
        'El plan de capacidad **está congelado y es concreto**: `configs/capacity_plan.json`, SHA256 `'
        + sha('configs/capacity_plan.json')[:32] + '...`. Fija la carga sin test, tres épocas medidas '
        'con una de calentamiento excluida, qué overhead se incluye, estimador por mediana con cota '
        'superior por máximo, **factor de seguridad 1,35 fijado antes de medir**, y tres '
        'desigualdades de aprobación o rechazo contra límite de sesión, cuota restante y memoria de '
        'GPU. Declara además que el modelo y las métricas de la sonda **se descartan y no se '
        'reportan nunca**, porque conservarlos la convertiría en un experimento no declarado.'
        + chr(10) * 2
        + 'Si falla, TASK-04 sigue `BLOCKED_BY_CAPACITY`: **no se reduce la configuración para que '
          'quepa**, lo que sería un cambio material con su propia enmienda. Una varianza entre épocas '
          'superior al 25 % hace la sonda inconclusa, y una sonda interrumpida **falla**, no se '
          'repite en silencio.' + chr(10) * 2
        + '**La cuota de GPU no es la única capacidad.** Se exige verificar también los **scopes de '
          'API**: leer metadatos de dataset, crear o actualizar dataset, crear sesión de notebook, '
          'guardar y ejecutar notebook, y leer su salida. Sobre esta cuenta ya se observó un scope de '
          'lectura **denegado** (`datasets.get`). Si falta un scope de escritura, TASK-04 queda '
          'bloqueada aunque sobre cuota de GPU, y así debe declararse.')
    replacements.append((
        '- **Estimación de recursos y rendimiento predeclarada**, derivada de la configuración '
        'aprobada (150 épocas, batch 16, 640 px) y medida **sin datos de test**, por ejemplo con un '
        'número reducido de épocas sobre la partición de entrenamiento.' + chr(10)
        + '- **Regla de aprobación o rechazo explícita** que ate esa estimación al límite de sesión y '
          'a la cuota medidos. Si la configuración aprobada no cabe con margen, TASK-04 **no se '
          'desbloquea**; no se reduce la configuración a posteriori ni se improvisa un reintento a '
          'mitad de run.' + chr(10)
        + '- Re-sondeo de cuota inmediatamente antes de lanzar, con la respuesta conservada.',
        capacity))

    replacements.append((
        'El esquema exacto y **un único evaluador autoritativo se eligen y se congelan antes de '
        'inferir**, no después de ver resultados. El esquema fija:',
        'El esquema **está serializado y congelado**: `configs/prediction_transfer_schema.json`, '
        'SHA256 `' + sha('configs/prediction_transfer_schema.json')[:32] + '...`. Designa **un único '
        'evaluador autoritativo** (`src.evaluation.evaluate`, pendiente de implementar en TASK-05) y '
        'declara explícitamente que el evaluador integrado del framework **no** es autoritativo, de '
        'modo que no se pueda elegir evaluador después de ver una discrepancia. El esquema fija:'))

    replacements.append((
        '`provenance/environment/cpu_topology_probe.json` preserva comando, exit code y salida cruda '
        'de:',
        '`provenance/environment/cpu_topology_probe.json` preserva comando, exit code, stderr y '
        'salida cruda, y cada sonda lleva estado `MEASURED` o `UNAVAILABLE`. El estado global es '
        '**`PARTIAL` con exit 1**, no `PASS`: la consulta del plan de energía devuelve vacío en este '
        'host y se declara **`UNAVAILABLE`** en lugar de contarse como éxito (hallazgo N-03). '
        'Sondas:'))

    missing = []
    for old, new in replacements:
        if s.count(old) != 1:
            missing.append(old[:70])
            continue
        s = s.replace(old, new)
    path.write_text(s, encoding='utf-8')
    print('applied', len(replacements) - len(missing), 'of', len(replacements))
    if missing:
        print('NOT APPLIED:')
        for item in missing:
            print('  -', item)
    return 0 if not missing else 1


if __name__ == '__main__':
    raise SystemExit(main())
