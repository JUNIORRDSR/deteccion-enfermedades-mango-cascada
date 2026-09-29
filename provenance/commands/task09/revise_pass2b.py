"""TASK-09 pass 2b: methods and training from EXP-R01; nothing here depends on test results.

Table 2 and section 3.4 take their values from the retained EXP-R01 attempt (receipt, the
Ultralytics args and job log, the selection record); section 3.7 states the frozen evaluation
protocol as implemented in src/evaluation/evaluate.py and src/statistics/intervals.py;
Figure 3 is redrawn by figure3_training.py and section 4.1.1 reads results.csv.
"""

import csv
import json
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import docx  # noqa: E402
from docx_edit import cell_text, set_runs, sha  # noqa: E402

DOCX = ROOT / 'manuscript/source/Articulo_Mango_ALBUS_revision.docx'
RUN = ROOT / 'experiments/model1/EXP-R01'
FIG3 = ROOT / 'manuscript/figures/fig3_entrenamiento.png'


def facts() -> dict:
    receipt = json.loads((RUN / 'v1/receipt.json').read_text(encoding='utf-8'))
    selection = json.loads((RUN / 'selection_record.json').read_text(encoding='utf-8'))
    log = (RUN / 'v1/job_log.txt').read_text(encoding='utf-8', errors='replace')
    optimizer = re.search(r'optimizer:\S*\s+(\w+)\(lr=([0-9.]+), momentum=([0-9.]+)\)', log)
    rows = [{k.strip(): float(v) for k, v in r.items()} for r in
            csv.DictReader(open(RUN / 'v1/run/train/results.csv', encoding='utf-8'))]
    env = receipt['environment']
    return {'minutes': (receipt['finished_unix'] - receipt['started_unix']) / 60,
            'optimizer': optimizer.group(1), 'lr': optimizer.group(2),
            'momentum': optimizer.group(3), 'torch': env['torch'].split('+')[0],
            'cuda': env['cuda'], 'epochs': len(rows), 'selected': selection['selected_epoch'],
            'fitness': float(selection['selected_fitness_repr']),
            'val_cls_first': rows[0]['val/cls_loss'], 'val_cls_last': rows[-1]['val/cls_loss'],
            'map50_selected': next(r for r in rows if int(r['epoch']) == selection['selected_epoch'])
            ['metrics/mAP50(B)']}


def es(value: float, digits: int = 3) -> str:
    return f'{value:.{digits}f}'.replace('.', ',')


def replace_media(path: Path, name: str, source: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / 'out.docx'
        with zipfile.ZipFile(path) as src, zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as dst:
            for item in src.infolist():
                dst.writestr(item, source.read_bytes() if item.filename == name
                             else src.read(item.filename))
        shutil.copyfile(out, path)


def main() -> int:
    before = sha(DOCX)
    f = facts()
    d = docx.Document(DOCX)
    table = d.tables[1]
    labels = [row.cells[0].text for row in table.rows]
    values = {'Optimizador': f"auto → {f['optimizer']}",
              'Learning rate (lr0 / lrf)': f"{f['lr']} (auto) / 0.01",
              'Momentum': f"{f['momentum']} (auto)",
              'Dispositivos': '1 × T4 (Kaggle)',
              'Tiempo total': f"≈ {f['minutes']:.1f} min (sesión completa)",
              'Pre-entrenamiento': 'Pesos COCO YOLO26n (v8.4.0)'}
    for label, value in values.items():
        cell_text(d, 1, labels.index(label), 1, value)
    row = labels.index('IoU (NMS, train)')
    cell_text(d, 1, row, 0, 'Supresión de duplicados')
    cell_text(d, 1, row, 1, 'extremo a extremo (sin NMS)')

    set_runs(d, 'Se utilizó la variante nano de YOLO en su versión 26', [
        ('Se utilizó la variante ', ''), ('nano', 'i'),
        (' de YOLO en su versión 26 (YOLO26n), distribuida por Ultralytics (Jocher et al., 2026). '
         'El reentrenamiento parte del checkpoint oficial yolo26n.pt de la release v8.4.0 '
         '(SHA-256 9b09cc8b…4fef, verificado contra el digest publicado) y usa Ultralytics '
         '8.4.52; el run histórico registra la versión 8.4.39. La variante ', ''), ('nano', 'i'),
        (' fue seleccionada por su equilibrio entre velocidad de inferencia, precisión sobre '
         'objetos medianos y huella de memoria compatible con despliegue en hardware de borde. '
         f"El entrenamiento se ejecutó en Kaggle sobre una GPU Tesla T4 (torch {f['torch']}, "
         f"CUDA {f['cuda']}). Cada imagen de entrenamiento y validación se descargó del commit "
         'público del corpus y se verificó por hash contra el manifiesto congelado; las de '
         'prueba no se descargaron. Se conservó la configuración del run histórico (Tabla 2). '
         f"El checkpoint se eligió por el máximo mAP@0,5:0,95 de validación sin redondear entre "
         f"las {f['epochs']} épocas.", '')])
    set_runs(d, 'Para el Modelo 1 se reportan', [(
        'Para el Modelo 1, cada detección se empareja con a lo sumo una caja real, con IoU ≥ '
        '0,5 y por IoU decreciente; una detección emparejada con la clase equivocada cuenta como '
        'error de ambas clases. En un umbral de confianza operativo se reportan, por clase, la '
        'precisión P = TP/(TP+FP), la sensibilidad R = TP/(TP+FN) y F2 = 5PR/(4P+R). El '
        'mAP@0,5 y el mAP@0,5:0,95 (umbrales IoU de 0,5 a 0,95 con paso 0,05) se calculan con '
        'las funciones de Ultralytics sobre todas las detecciones guardadas, sin umbral. El '
        'umbral operativo es el que maximiza el F2 de Enfermo en validación, sobre la rejilla de '
        '0,05 a 0,95 con paso 0,05: el F2 pesa más la sensibilidad porque un fruto enfermo no '
        'detectado cuesta más que una falsa alarma. La validación sirvió sólo para elegir el '
        'checkpoint y el umbral; la prueba se evaluó una sola vez, con ambos fijados. Los '
        'intervalos de confianza del 95 % son percentiles de 2000 remuestras bootstrap con '
        'semilla 42, que remuestrean grupos de origen y no imágenes. Si una métrica tiene menos '
        'de dos grupos con la clase, o más de un 5 % de remuestras indefinidas, no se da '
        'intervalo. Para el Modelo 2 se reportan la exactitud top-1, la precisión, la '
        'sensibilidad y el F1 por clase, la matriz de confusión y el macro-F1, sobre las 219 '
        'imágenes de prueba de MangoDHDS_clean, con intervalos que remuestrean sus grupos. Como '
        'análisis de sensibilidad, las mismas métricas se recalculan con una imagen por SHA-256 '
        'y dando a cada cluster el mismo peso.', '')])
    set_runs(d, 'El entrenamiento del detector se realizó', [(
        f"El entrenamiento del detector duró {es(f['minutes'], 1)} minutos en una GPU T4 "
        f"(Kaggle). La Figura 3 muestra la evolución de las pérdidas y de las métricas de "
        f"validación a lo largo de las {f['epochs']} épocas. La pérdida de clasificación de "
        f"validación desciende de {es(f['val_cls_first'], 2)} en la época 1 a "
        f"{es(f['val_cls_last'], 2)} en la época {f['epochs']}. El checkpoint seleccionado "
        f"corresponde a la época {f['selected']}, con mAP@0,5:0,95 de validación "
        f"{es(f['fitness'])} y mAP@0,5 {es(f['map50_selected'])} según el registro de "
        'entrenamiento; las métricas de validación del evaluador del artículo, con el umbral '
        'operativo, se dan en la Tabla 4.', '')])
    set_runs(d, 'Figura 3. Evolución del entrenamiento del Modelo 1', [
        ('Figura 3. ', 'b'),
        ('Evolución del reentrenamiento del Modelo 1: (a) pérdidas de caja y de clasificación '
         'en entrenamiento y validación (la pérdida DFL de YOLO26, inferior a 0,016 en todas las '
         'épocas, se omite); (b) métricas de validación del registro de Ultralytics. La estrella '
         f"marca la época seleccionada ({f['selected']}) por el máximo mAP@0,5:0,95. Fuente: "
         'elaboración propia a partir del registro de entrenamiento de EXP-R01 (results.csv).',
         '')])
    d.save(DOCX)
    replace_media(DOCX, 'word/media/image3.png', FIG3)
    docx.Document(DOCX)
    log = ROOT / 'manuscript/source/edit_log.json'
    entries = json.loads(log.read_text(encoding='utf-8'))
    entries.append({'pass': '2b', 'script': 'provenance/commands/task09/revise_pass2b.py',
                    'before_sha256': before, 'after_sha256': sha(DOCX), 'facts': f,
                    'figure3_sha256': sha(FIG3)})
    log.write_text(json.dumps(entries, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(entries[-1], indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
