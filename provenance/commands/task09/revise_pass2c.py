"""TASK-09 pass 2c: results from the frozen artifacts (EXP-V01, EXP-R02, EXP-R03, TASK-06).

Every number is read from its artifact, never typed. Interpretive sentences live in
INTERPRETATION and are written only after the results are read; the pass refuses to run while
any is empty. Figures 4-7 come from figures_results.py and Tables 4, 5 and 7 from
results_tables.py; media paths and pixel sizes stay those of the figures they replace.
"""

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import docx  # noqa: E402
import results_tables  # noqa: E402
from docx_edit import replace, set_runs, sha  # noqa: E402
from results_tables import es, with_ci  # noqa: E402

DOCX = ROOT / 'manuscript/source/Articulo_Mango_ALBUS_revision.docx'
FIGURES = {'word/media/image4.png': 'manuscript/figures/fig4_confusion_m1.png',
           'word/media/image5.png': 'manuscript/figures/fig5_detecciones.png',
           'word/media/image6.png': 'manuscript/figures/fig6_confusion_m2.png',
           'word/media/image7.png': 'manuscript/figures/fig7_cascada_validacion.png'}
INTERPRETATION = {  # str.format templates over values(): no number is typed here
    'm1_test': (            # 4.1.2, the paragraph after Table 5
        'Frente a validación, el mAP@0,5 baja de {map50_val} a {map50_test}, y la caída se '
        'concentra en la clase Enfermo. Su sensibilidad pasa de {recall_Enfermo_val} en validación '
        'a {recall_Enfermo_test} en prueba, mientras que la de Saludable apenas cambia '
        '({recall_Saludable_val} frente a {recall_Saludable_test}). Es el resultado contrario al que '
        'se busca en este dominio, donde un fruto enfermo sin detectar cuesta más que una falsa '
        'alarma. La prueba tiene solo {n_E_test} instancias Enfermo en {groups_E_test} grupos de '
        'origen, así que el intervalo de esa sensibilidad es ancho; aun así, su extremo superior '
        'queda por debajo del valor de validación. El umbral se eligió en validación, lo que vuelve '
        'optimistas las cifras de esa partición, y la partición por grupos de origen hace que la '
        'prueba contenga montajes que el modelo no vio al entrenar.'),
    'm1_confusion': (       # 4.1.3, after the counts
        'En las dos clases, el error dominante es la falta de detección y no el cambio de '
        'etiqueta. El detector casi nunca etiqueta un fruto enfermo como Saludable, pero deja sin '
        'caja una parte importante de los frutos enfermos. Un ajuste del umbral para recuperarlos '
        'tendría que decidirse con datos nuevos, porque esta prueba ya se usó una vez.'),
    'm2_confusion': (       # 4.2.3, after the most frequent confusions
        'El intercambio entre Cancro bacteriano y Costras reúne la mayor parte de los errores, en '
        'las dos direcciones, y coincide con los F1 más bajos de la Tabla 7 ({f1_Cancro_bacteriano} '
        'y {f1_Costras}). Ambas patologías presentan lesiones oscuras e irregulares, y '
        'distinguirlas suele requerir detalles finos, como la textura local o el exudado '
        'bacteriano, que un clasificador a 224 px apenas captura. Saludable y Podredumbre del '
        'extremo del tallo alcanzan F1 de {f1_Saludable} y {f1_Podredumbre_Extremo_tallo}.'),
    'discussion': (         # 5.1
        'El Modelo 1 alcanza un mAP@0,5 de {map50_val} en validación y de {map50_test} en prueba, '
        'entrenado con una partición por grupos de origen que impide que un mismo montaje aparezca '
        'en entrenamiento y en prueba. Estas cifras no son comparables con las de la versión '
        'anterior del manuscrito, obtenidas sobre la partición publicada, que mezclaba montajes '
        'entre entrenamiento y prueba. Para el uso previsto, el resultado que más pesa es la '
        'sensibilidad para Enfermo en prueba, {recall_Enfermo_test}, muy por debajo de la de '
        'validación y con un intervalo ancho por las pocas instancias de esa clase. Como la '
        'precisión para Enfermo ({precision_Enfermo_test}) supera a su sensibilidad, el detector '
        'actual deja pasar más frutos enfermos de los que marca en falso. Las rutas de mejora son '
        '(i) reunir más imágenes '
        'de frutos enfermos de orígenes distintos, (ii) reponderar la función de pérdida para '
        'penalizar más los falsos negativos de Enfermo y (iii) fijar el umbral con datos de campo; '
        'cualquiera de ellas exige una partición de prueba nueva.'),
    'abstract': (           # the whole abstract after «Resumen:»; descriptive, no direction
        'Las enfermedades del mango causan pérdidas de producción, y su diagnóstico convencional '
        'depende de la inspección visual o del laboratorio, costosos o poco accesibles para el '
        'productor rural colombiano. Este trabajo presenta un sistema de detección visual '
        'automatizada de signos de enfermedad en frutos de mango, organizado como una cascada de '
        'dos modelos YOLO: un detector YOLO26n que localiza frutos y los clasifica como Enfermo o '
        'Saludable, y un clasificador YOLO11n-cls que asigna a cada fruto detectado una de cuatro '
        'patologías o Saludable. Una auditoría de fuga de datos mostró que la partición publicada '
        'del corpus del detector (669 imágenes de terceros) no era independiente: un mismo montaje '
        'de fotografías aparecía en entrenamiento y en prueba. El detector se reentrenó con una '
        'partición por grupos de origen; el checkpoint y el umbral de decisión se fijaron en '
        'validación antes de evaluar una sola vez la prueba ({n_test} imágenes, {groups_test} '
        'grupos). En prueba, el detector alcanza un mAP@0,5 de {map50_test} y una sensibilidad '
        'para Enfermo de {recall_Enfermo_test}, con el intervalo de confianza del 95 % por grupo '
        'entre corchetes. El clasificador, evaluado sobre la partición limpia de MangoDHDS '
        '({m2_n} imágenes), alcanza una exactitud de {m2_acc} y un macro-F1 de {m2_macro_f1}. No '
        'hay verdad de terreno conjunta para medir la cascada completa, y el sistema no se validó '
        'en cultivos de la región. Se publican el protocolo de auditoría y su código.'),
    'limitations': (        # 6.1, second paragraph up to «Finalmente»
        'La tercera limitación, y la de mayor peso para el uso previsto, es la baja sensibilidad '
        'del detector para Enfermo en prueba ({recall_Enfermo_test}), estimada con solo {n_E_test} '
        'instancias en {groups_E_test} grupos de origen. La cuarta es la confusión entre Cancro '
        'bacteriano y Costras en el clasificador, con F1 de {f1_Cancro_bacteriano} y {f1_Costras}: '
        'estas patologías comparten manifestaciones visuales y separarlas requeriría más datos, '
        'mayor resolución de entrada o módulos de atención local. La quinta es la decisión '
        'deliberada de operar solo sobre el canal RGB de la cámara disponible, sin explotar la '
        'morfología accesible por profundidad estéreo. La sexta es el desbalance entre las clases '
        'del detector: hay muchas más instancias Saludable que Enfermo, lo que puede sesgar el '
        'entrenamiento hacia Saludable y deja la estimación de Enfermo en prueba con poca '
        'precisión. Quedan dos limitaciones operativas: la saturación bajo iluminación ambiental '
        'intensa y la ausencia de mediciones en hardware de borde, pues la latencia en Raspberry '
        'Pi 4 no se midió.'),
    'conclusion': (         # 7, the results paragraph; descriptive, no direction
        'Este trabajo presentó el diseño y la implementación de un sistema de visión por '
        'computador para la detección visual automatizada de signos de enfermedad en frutos de '
        'mango, estructurado como una cascada de dos modelos YOLO especializados. El detector '
        'binario YOLO26n, reentrenado con una partición por grupos de origen y evaluado una sola vez '
        'sobre {n_test} imágenes de prueba de {groups_test} grupos, alcanza un mAP@0,5 de '
        '{map50_test} y una sensibilidad para Enfermo de {recall_Enfermo_test}. El clasificador '
        'YOLO11n-cls, evaluado sobre la partición limpia de MangoDHDS, alcanza una exactitud de '
        '{m2_acc} y un macro-F1 de {m2_macro_f1}. Entre corchetes se dan los intervalos de '
        'confianza del 95 % por grupo.'),
}
TABLE8 = {  # Tabla 8 rows whose impact depends on the results: label -> (label, impact, mitigation)
    'Confusión Cancro ↔ Costras': ('Confusión Cancro ↔ Costras',
                                   'F1 de {f1_Cancro_bacteriano} y {f1_Costras}',
                                   'Más datos, resolución 320 px, atención local'),
    'Asimetría de clases': ('Asimetría de clases',
                            'Sensibilidad para Enfermo de {recall_Enfermo_test} en prueba',
                            'Más imágenes de frutos enfermos, reponderar la pérdida, fijar el '
                            'umbral con datos nuevos'),
}


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def benchmark(path: str = 'artifacts/metrics/benchmark_raw.csv') -> dict:
    """Pooled median and p95 per wall stage over the measured repetitions that succeeded
    (the raw CSV has one row per repetition x stage; warm-ups are not in it)."""
    sys.path.insert(0, str(ROOT))
    from src.benchmarks.run import summarize
    rows = [r for r in csv.DictReader(open(ROOT / path, encoding='utf-8'))
            if r['kind'] == 'wall' and r['status'] == 'ok']
    out = {}
    for stage in ('m1', 'cascade', 'end_to_end'):
        s = summarize([int(r['wall_ns']) for r in rows if r['stage'] == stage])
        out[stage] = {k: s[k] / 1e6 for k in ('median', 'p95')}
    out['n'] = sum(r['stage'] == 'end_to_end' for r in rows)
    return out


def m2_confusions(path: str = 'experiments/model2/EXP-R03/predictions.jsonl') -> list[tuple]:
    """(truth, pred, count) off the diagonal, most frequent first."""
    pairs = {}
    for line in (ROOT / path).read_text(encoding='utf-8').splitlines():
        r = json.loads(line)
        if r['truth'] != r['pred']:
            pairs[(r['truth'], r['pred'])] = pairs.get((r['truth'], r['pred']), 0) + 1
    return sorted(((t, p, n) for (t, p), n in pairs.items()), key=lambda x: (-x[2], x[0], x[1]))


def facts() -> dict:
    frozen = load('configs/evaluation_frozen.json')
    names = frozen['class_names']
    classes = load('configs/class_names.json')
    m2 = load('artifacts/metrics/model2_intervals.json')
    m2_rows = list(csv.DictReader(open(ROOT / 'data/manifests/model2_frozen_manifest.csv',
                                       encoding='utf-8')))
    support = {n: sum(r['split'] == 'test' and r['class_name'] == n for r in m2_rows)
               for n in m2['class_names']}
    return {'m1_names': names, 'threshold': frozen['threshold'], 'threshold_f2': frozen['threshold_f2'],
            'val': load('experiments/model1/EXP-V01/metrics_frozen.json'),
            'test': load('experiments/model1/EXP-R02/metrics.json'),
            'm1_intervals': load('artifacts/metrics/model1_intervals.json'),
            'm2_intervals': m2, 'm2_support': support,
            'm2_editorial': {c['model_name']: c['editorial'] for c in classes['model2']['classes']},
            'm2_groups': m2['bootstrap']['n_groups'],
            'selection': load('experiments/model1/EXP-R01/selection_record.json'),
            'benchmark': benchmark(), 'm2_confusions': m2_confusions()}


def values(f: dict) -> dict:
    """Every number an interpretive template may cite, formatted once from the artifacts."""
    test, val, ci = f['test'], f['val'], f['m1_intervals']['metrics']
    m2, m2ci = f['m2_intervals'], f['m2_intervals'].get('intervals') or {}
    v = {'t': es(f['threshold'], 2), 'epoch': f['selection']['selected_epoch'],
         'map50_val': es(val['average_precision']['map50']),
         'map5095_val': es(val['average_precision']['map50_95']),
         'map50_test': with_ci(test['average_precision']['map50'], ci.get('map50')),
         'map5095_test': with_ci(test['average_precision']['map50_95'], ci.get('map50_95')),
         'n_test': test['counts']['images'], 'groups_test': test['counts']['groups'],
         'n_E_test': test['counts']['instances_per_class']['Enfermo'],
         'groups_E_test': (ci.get('Enfermo.recall') or {}).get('class_group_counts', {}).get('Enfermo'),
         'm2_acc': with_ci(m2['point']['accuracy'], m2ci.get('accuracy')),
         'm2_macro_f1': with_ci(m2['point']['macro_f1'], m2ci.get('macro_f1')),
         'm2_n': sum(f['m2_support'].values()), 'm2_groups': f['m2_groups'],
         'lat_e2e': es(f['benchmark']['end_to_end']['median'], 1),
         'lat_e2e_p95': es(f['benchmark']['end_to_end']['p95'], 1),
         'lat_m1': es(f['benchmark']['m1']['median'], 1),
         'lat_cascade': es(f['benchmark']['cascade']['median'], 1)}
    for name in f['m1_names']:
        for key in ('precision', 'recall', 'f1', 'f2'):
            v[f'{key}_{name}_test'] = with_ci(test['operating_metrics'][name][key],
                                              ci.get(f'{name}.{key}'))
            v[f'{key}_{name}_val'] = es(val['operating_metrics'][name][key])
    for name in m2['class_names']:
        for key in ('precision', 'recall', 'f1'):
            v[f'{key}_{name}'] = with_ci(m2['point'][f'{key}[{name}]'], m2ci.get(f'{key}[{name}]'))
    return v


def counts(metrics: dict) -> str:
    c = metrics['counts']
    per = c['instances_per_class']
    return (f"{c['images']} imágenes, {c['groups']} grupos de origen y {c['instances']} instancias: "
            f"{per['Enfermo']} Enfermo y {per['Saludable']} Saludable")


def confusion_text(metrics: dict) -> str:
    (ee, es_, eb), (se, ss, sb), (be, bs, _) = metrics['detection_confusion']['matrix']
    n_e, n_s = ee + es_ + eb, se + ss + sb
    return (f"De las {n_e:.0f} instancias Enfermo, {ee:.0f} reciben una detección Enfermo, {es_:.0f} "
            f"una Saludable y {eb:.0f} ninguna. De las {n_s:.0f} Saludable, {ss:.0f} se detectan como "
            f"Saludable, {se:.0f} como Enfermo y {sb:.0f} quedan sin detección. Además hay {be:.0f} "
            f"detecciones Enfermo y {bs:.0f} Saludable sin caja real a IoU ≥ 0,5.")


def m2_confusion_text(f: dict, top: int = 3) -> str:
    name = f['m2_editorial']
    pairs = [f"{n} {'imagen' if n == 1 else 'imágenes'} de {name[t]} "
             f"{'clasificada' if n == 1 else 'clasificadas'} como {name[p]}"
             for t, p, n in f['m2_confusions'][:top]]
    if not pairs:
        return 'La prueba no tiene errores de clasificación.'
    total = sum(n for _, _, n in f['m2_confusions'])
    return (f"De los {total} errores, los más frecuentes son: {'; '.join(pairs)} (Figura 6).")


def texts(f: dict) -> dict:
    t, test, val = es(f['threshold'], 2), f['test'], f['val']
    m2, b, v = f['m2_intervals'], f['benchmark'], values(f)
    ms = lambda x: es(x, 1)  # noqa: E731
    return {
        'table4': (f'Métricas del Modelo 1 sobre validación ({counts(val)}) con el umbral operativo '
                   f'{t}, elegido en esta misma partición; P, R, F1 y F2 son por ello optimistas.'),
        'm1_test': (f"El checkpoint de la época {f['selection']['selected_epoch']} y el umbral {t} "
                    f"(F2 de Enfermo en validación = {es(f['threshold_f2'])}) se fijaron antes de "
                    f"tocar la prueba, que se evaluó una sola vez (EXP-R02). La prueba tiene "
                    f"{counts(test)}. La Tabla 5 da cada métrica con su intervalo de confianza del "
                    '95 %, obtenido con 2000 remuestras bootstrap de los grupos de origen (semilla 42).'),
        'm1_reading': INTERPRETATION['m1_test'].format(**v),
        'table5': (f'Métricas del Modelo 1 sobre la partición de prueba ({counts(test)}) con el '
                   f'umbral {t}. Entre corchetes, IC del 95 % por grupo.'),
        'm1_confusion': f"{confusion_text(test)} {INTERPRETATION['m1_confusion'].format(**v)}",
        'fig4': (f'Matriz de confusión por instancia del Modelo 1 sobre la partición de prueba, con '
                 f'emparejamiento uno a uno independiente de la clase a IoU ≥ 0,5 y umbral {t}: '
                 '(a) conteos; (b) proporción por fila verdadera. La columna Fondo reúne las '
                 'instancias reales sin detección; la fila Fondo, las detecciones sin caja real, y no '
                 'tiene proporción. Fuente: elaboración propia.'),
        'qualitative': (f'La Figura 5 muestra nueve imágenes de prueba tomadas al azar (semilla 42) '
                        f'entre las que tienen alguna caja real, con las detecciones guardadas de '
                        f'EXP-R02 por encima del umbral {t}; no se eligieron por su resultado. El '
                        'título de cada panel cuenta, por clase, las instancias reales y las '
                        'detectadas.'),
        'fig5': ('Detecciones del Modelo 1 sobre nueve imágenes de prueba (muestra aleatoria, semilla '
                 '42). Rojo = Enfermo, verde = Saludable, con su confianza; «Real» y «Detectado» '
                 'cuentan instancias Enfermo (E) y Saludable (S). Las cajas, etiquetas y valores de '
                 'confianza superpuestos son salida del Modelo 1 generada por los autores; las '
                 'fotografías subyacentes proceden de las fuentes listadas debajo.'),
        'fig5_source': (f"Fuente de las imágenes. Partición de prueba (n = {test['counts']['images']}) "
                        'del conjunto mangoUnhealty v2, Roboflow Universe, licencia CC BY 4.0, '
                        'publicado por terceros (Jairos Workspace, 2026); muestreo aleatorio con '
                        'semilla 42. Referencias completas en la bibliografía al final del documento.'),
        'latency': ('La latencia se midió en CPU (AMD Ryzen 5 7520U, Windows 11) con un protocolo '
                    'fijado antes de medir: lote 1, FP32, Modelo 1 a 640 px y Modelo 2 a 224 px, un '
                    'proceso y un hilo, 10 calentamientos y 100 repeticiones por imagen sobre 32 '
                    f"imágenes de validación ({b['n']} repeticiones medidas). La mediana de extremo a "
                    f"extremo, de la lectura del archivo a la imagen anotada, es {ms(b['end_to_end']['median'])} "
                    f"ms (p95 {ms(b['end_to_end']['p95'])} ms); la llamada al Modelo 1 toma "
                    f"{ms(b['m1']['median'])} ms y la cascada completa {ms(b['cascade']['median'])} ms. "
                    'Es una medición descriptiva de un equipo, sin comparador. No se midió en '
                    'Raspberry Pi 4: no hubo acceso al equipo (Sección 6).'),
        'm2_test': (f"La evaluación se realizó sobre las {sum(f['m2_support'].values())} imágenes de "
                    'la partición de prueba, en la que no se detecta contaminación entre particiones '
                    'bajo el protocolo especificado (SHA-256 y pHash con Hamming < 5); esas imágenes '
                    f"forman {f['m2_groups']} grupos de similitud, que son la unidad de los "
                    'intervalos. El modelo alcanza una exactitud top-1 de '
                    f"{with_ci(m2['point']['accuracy'], (m2.get('intervals') or {}).get('accuracy'))} "
                    'y un macro-F1 de '
                    f"{with_ci(m2['point']['macro_f1'], (m2.get('intervals') or {}).get('macro_f1'))}, "
                    'distribuidos según la Tabla 7.'),
        'table7': (f"Métricas del Modelo 2 por clase sobre la partición de prueba de MangoDHDS_clean "
                   f"({sum(f['m2_support'].values())} imágenes, {f['m2_groups']} grupos). Entre "
                   'corchetes, IC del 95 % por grupo.'),
        'm2_confusion': f"{m2_confusion_text(f)} {INTERPRETATION['m2_confusion'].format(**v)}",
        'fig6': (f"Matriz de confusión del Modelo 2 sobre la partición de prueba de MangoDHDS_clean "
                 f"(n = {sum(f['m2_support'].values())}): (a) conteos; (b) proporción por fila "
                 'verdadera. Fuente: elaboración propia sobre MangoDHDS (Barhate et al., 2025).'),
        'cascade': (f'La Figura 7 ilustra la cascada completa sobre nueve imágenes de validación '
                    f'(muestra aleatoria, semilla 42): las cajas de EXP-V01 por encima del umbral {t} '
                    'se recortan y el Modelo 2 asigna a cada una su clase, o «Desconocido» si su '
                    'confianza es menor que 0,4, como hace el script de línea de comandos. Se usan '
                    'imágenes de validación para no mostrar la prueba más allá de sus métricas. El '
                    'Modelo 2 se ejecuta sobre cada caja detectada, así que el costo crece con el '
                    'número de frutos de la escena (Sección 4.1.5). La figura es ilustrativa: no hay '
                    'verdad de terreno de enfermedad específica para esas escenas y no evidencia '
                    'diagnósticos correctos.'),
        'fig7': ('Cascada completa Modelo 1 + Modelo 2 sobre nueve imágenes de validación. Cada caja '
                 'del Modelo 1 recibe la clase del Modelo 2 con su nombre interno (Antracnosis, '
                 'Cancro_bacteriano, Costras, Podredumbre_Extremo_tallo o Saludable) y su confianza, '
                 'o «Desconocido» por debajo de 0,4. Las etiquetas no están verificadas con verdad de '
                 'terreno de enfermedad. Las anotaciones superpuestas son salida del sistema '
                 'propuesto, generada por los autores; las fotografías subyacentes proceden de las '
                 'fuentes listadas debajo.'),
        'fig7_source': ('Fuente de las imágenes. Partición de validación del conjunto mangoUnhealty '
                        'v2, Roboflow Universe, licencia CC BY 4.0, publicado por terceros (Jairos '
                        'Workspace, 2026); muestreo aleatorio con semilla 42. El diagnóstico fino '
                        'proviene del Modelo 2, entrenado sobre MangoDHDS_clean (Barhate et al., '
                        '2025). Referencias completas en la bibliografía al final del documento.'),
        'discussion': INTERPRETATION['discussion'].format(**v),
        'abstract': INTERPRETATION['abstract'].format(**v),
        'limitations': INTERPRETATION['limitations'].format(**v),
        'conclusion': INTERPRETATION['conclusion'].format(**v),
        'table8': {k: tuple(s.format(**v) for s in row) for k, row in TABLE8.items()},
    }


def caption(d, start: str, number: str, text: str) -> None:
    set_runs(d, start, [(f'{number} ', 'b'), (text, '')])


def apply(d, f: dict) -> None:
    x = texts(f)
    set_runs(d, 'Resumen:', [('Resumen: ', 'b'), (x['abstract'], '')])
    results_tables.apply(d, f)
    caption(d, 'Tabla 4. Métricas del Modelo 1 sobre validación', 'Tabla 4.', x['table4'])
    replace(d, 'Evaluación sobre TEST independiente', 'Evaluación sobre la partición de prueba')
    set_runs(d, 'Como evaluación honesta de generalización', [(x['m1_test'], '')])
    caption(d, 'Tabla 5. Métricas del Modelo 1 sobre el conjunto de TEST', 'Tabla 5.', x['table5'])
    set_runs(d, 'La caída con respecto a validación es esperable', [(x['m1_reading'], '')])
    replace(d, 'Matriz de confusión sobre TEST', 'Matriz de confusión sobre la prueba')
    set_runs(d, 'La matriz de confusion (Figura 4) confirma', [(x['m1_confusion'], '')])
    caption(d, 'Figura 4. Matriz de confusión por instancia', 'Figura 4.', x['fig4'])
    set_runs(d, 'La Figura 5 ilustra detecciones representativas', [(x['qualitative'], '')])
    caption(d, 'Figura 5. Detección cualitativa', 'Figura 5.', x['fig5'])
    set_runs(d, 'Fuente de las imágenes. Partición de test (n=33)', [(x['fig5_source'], '')])
    set_runs(d, 'Sobre CPU multi-núcleo (AMD Ryzen 5 7520U', [(x['latency'], '')])
    replace(d, 'Métricas sobre TEST de MangoDHDS_clean', 'Métricas sobre la partición de prueba de '
                                                         'MangoDHDS_clean')
    set_runs(d, 'La evaluación se realizó sobre las 219 imágenes', [(x['m2_test'], '')])
    caption(d, 'Tabla 7. Métricas del Modelo 2 por clase', 'Tabla 7.', x['table7'])
    set_runs(d, 'La matriz de confusión (Figura 6) revela', [(x['m2_confusion'], '')])
    caption(d, 'Figura 6. Matriz de confusión del Modelo 2', 'Figura 6.', x['fig6'])
    set_runs(d, 'La Figura 7 ilustra la cascada completa', [(x['cascade'], '')])
    caption(d, 'Figura 7.  Cascada completa', 'Figura 7.', x['fig7'])
    set_runs(d, 'Fuente de las imágenes. Partición de test del conjunto', [(x['fig7_source'], '')])
    set_runs(d, 'El Modelo 1 alcanza un mAP@0.5 de 0.932', [(x['discussion'], '')])
    replace(d, 'bastan para alcanzar las métricas reportadas sobre el conjunto de test reservado, '
               'pero no permiten', 'no permiten')
    set_runs(d, 'La tercera limitación', [
        (x['limitations'] + ' Finalmente, el sistema aún carece de un conjunto de prueba ', ''),
        ('out-of-distribution', 'i'),
        (' externo, anotado de forma independiente, condición necesaria para sostener las '
         'afirmaciones de generalización en producción.', '')])
    labels = [row.cells[0].text for row in d.tables[7].rows]
    for old, row in x['table8'].items():
        for col, text in enumerate(row):
            results_tables.cell_text(d, 7, labels.index(old), col, text)
    set_runs(d, 'Este trabajo presentó el diseño y la implementación', [(x['conclusion'], '')])


def main() -> int:
    empty = [k for k, v in INTERPRETATION.items() if not v.strip()]
    empty += [k for k, row in TABLE8.items() if not all(s.strip() for s in row)]
    if empty:
        raise SystemExit(f'write the interpretation first: {empty}')
    before = sha(DOCX)
    f = facts()
    d = docx.Document(DOCX)
    apply(d, f)
    d.save(DOCX)
    from revise_pass2b import replace_media
    for name, source in FIGURES.items():
        replace_media(DOCX, name, ROOT / source)
    docx.Document(DOCX)
    log = ROOT / 'manuscript/source/edit_log.json'
    entries = json.loads(log.read_text(encoding='utf-8'))
    entries.append({'pass': '2c', 'script': 'provenance/commands/task09/revise_pass2c.py',
                    'before_sha256': before, 'after_sha256': sha(DOCX),
                    'figures': {k: sha(ROOT / v) for k, v in FIGURES.items()},
                    'benchmark': f['benchmark'], 'threshold': f['threshold']})
    log.write_text(json.dumps(entries, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(entries[-1], indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
