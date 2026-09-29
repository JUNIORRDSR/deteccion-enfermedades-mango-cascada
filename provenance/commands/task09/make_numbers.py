"""Write manuscript/numbers.json: every result number of the prose and captions, re-derived by
document_checks from its artifact (audit B, B-08). Tables 4, 5 and 7 and Figures 4 to 7 are
generated cell by cell from the same artifacts by results_tables.py and figures_results.py, so
they are not listed here; editorial_audit.md states that scope."""
import json
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
R02, V01 = 'experiments/model1/EXP-R02/metrics.json', 'experiments/model1/EXP-V01/metrics_frozen.json'
I1, I2 = 'artifacts/metrics/model1_intervals.json', 'artifacts/metrics/model2_intervals.json'
SEN, BEN = 'artifacts/metrics/model2_sensitivity.json', 'artifacts/metrics/benchmark_summary.json'
FRZ, SEL = 'configs/evaluation_frozen.json', 'experiments/model1/EXP-R01/selection_record.json'

A = {'abstract': 'Resumen:', 't4': 'Tabla 4. Métricas del Modelo 1 sobre validación',
     'm1test': 'se fijaron antes de evaluar la prueba una sola vez',
     't5': 'Tabla 5. Métricas del Modelo 1 sobre la partición de prueba',
     'reading': 'Frente a validación, el mAP@0,5 baja de', 'confusion': 'reciben una detección Enfermo',
     'fig4': 'Figura 4. Matriz de confusión por instancia',
     'fig5src': 'Fuente de las imágenes. Partición de prueba', 'latency': 'La latencia se midió en CPU',
     'm2test': 'La evaluación se realizó sobre las', 't7': 'Tabla 7. Métricas del Modelo 2 por clase',
     'sens': 'Los dos análisis de sensibilidad fijados en el protocolo',
     'm2conf': 'El intercambio entre Cancro bacteriano y Costras', 'disc': 'Estas cifras no son comparables',
     'lim': 'La tercera limitación, y la de mayor peso',
     'concl': 'Este trabajo presentó el diseño y la implementación',
     'audit1': 'Se auditaron las 669 imágenes con tres criterios',
     'm1val': 'El checkpoint seleccionado corresponde a la época 91'}
BLIND = 'data/audits/model1/blinding_log.json'

rows = []


def add(anchor, name, source, path, digits=3, **extra):
    rows.append({'id': f'{anchor}.{name}', 'source': source, 'path': path, 'digits': digits,
                 'anchor': A[anchor], **extra})


# Abstract
add('abstract', 'n_test', R02, ['counts', 'images'], 0)
add('abstract', 'groups_test', R02, ['counts', 'groups'], 0)
add('abstract', 'map50_test', R02, ['average_precision', 'map50'])
for i, end in enumerate(('low', 'high')):
    add('abstract', f'map50_ci_{end}', I1, ['metrics', 'map50', 'ci95', i])
    add('abstract', f'recall_E_ci_{end}', I1, ['metrics', 'Enfermo.recall', 'ci95', i])
    add('abstract', f'm2_acc_ci_{end}', I2, ['intervals', 'accuracy', 'ci95', i])
    add('abstract', f'm2_f1_ci_{end}', I2, ['intervals', 'macro_f1', 'ci95', i])
add('abstract', 'recall_E_test', R02, ['operating_metrics', 'Enfermo', 'recall'])
add('abstract', 'm2_n', SEN, ['structure', 'n_images'], 0)
add('abstract', 'm2_accuracy', I2, ['point', 'accuracy'])
add('abstract', 'm2_macro_f1', I2, ['point', 'macro_f1'])
# Table 4 and 5 captions
for key, path in (('images', ['counts', 'images']), ('groups', ['counts', 'groups']),
                  ('instances', ['counts', 'instances']),
                  ('enfermo', ['counts', 'instances_per_class', 'Enfermo']),
                  ('saludable', ['counts', 'instances_per_class', 'Saludable'])):
    add('t4', key, V01, path, 0)
    add('t5', key, R02, path, 0)
add('t4', 'threshold', FRZ, ['threshold'], 2)
add('t5', 'threshold', FRZ, ['threshold'], 2)
# 4.1.2
add('m1test', 'epoch', SEL, ['selected_epoch'], 0)
add('m1test', 'threshold', FRZ, ['threshold'], 2)
add('m1test', 'threshold_f2', FRZ, ['threshold_f2'])
for key, path in (('images', ['counts', 'images']), ('groups', ['counts', 'groups']),
                  ('instances', ['counts', 'instances']),
                  ('enfermo', ['counts', 'instances_per_class', 'Enfermo']),
                  ('saludable', ['counts', 'instances_per_class', 'Saludable'])):
    add('m1test', key, R02, path, 0)
add('m1test', 'resamples', I1, ['inputs', 'resamples'], 0)
add('m1test', 'seed', I1, ['inputs', 'seed'], 0)
add('reading', 'map50_val', V01, ['average_precision', 'map50'])
add('reading', 'map50_test', R02, ['average_precision', 'map50'])
add('reading', 'recall_E_val', V01, ['operating_metrics', 'Enfermo', 'recall'])
add('reading', 'recall_E_test', R02, ['operating_metrics', 'Enfermo', 'recall'])
add('reading', 'recall_S_val', V01, ['operating_metrics', 'Saludable', 'recall'])
add('reading', 'recall_S_test', R02, ['operating_metrics', 'Saludable', 'recall'])
for i, end in enumerate(('low', 'high')):
    add('reading', f'map50_ci_{end}', I1, ['metrics', 'map50', 'ci95', i])
    add('reading', f'recall_E_ci_{end}', I1, ['metrics', 'Enfermo.recall', 'ci95', i])
    add('reading', f'recall_S_ci_{end}', I1, ['metrics', 'Saludable.recall', 'ci95', i])
add('reading', 'n_E', R02, ['counts', 'instances_per_class', 'Enfermo'], 0)
add('reading', 'groups_E', I1, ['metrics', 'Enfermo.recall', 'class_group_counts', 'Enfermo'], 0)
# 4.1.3 and Figure 4
for (r, c), name in {(0, 0): 'EE', (0, 1): 'ES', (0, 2): 'EB', (1, 0): 'SE', (1, 1): 'SS',
                     (1, 2): 'SB', (2, 0): 'BE', (2, 1): 'BS'}.items():
    add('confusion', name, R02, ['detection_confusion', 'matrix', r, c], 0)
add('confusion', 'n_E', R02, ['counts', 'instances_per_class', 'Enfermo'], 0)
add('confusion', 'n_S', R02, ['counts', 'instances_per_class', 'Saludable'], 0)
add('fig4', 'threshold', FRZ, ['threshold'], 2)
add('fig5src', 'n_test', R02, ['counts', 'images'], 0)
# 4.1.5
for stage in ('end_to_end', 'm1', 'cascade'):
    add('latency', f'{stage}_median', BEN, ['stages', stage, 'median'], 1)
add('latency', 'end_to_end_p95', BEN, ['stages', 'end_to_end', 'p95'], 1)
for stat in ('mean', 'std', 'min', 'max'):  # final adversarial review, M-07
    add('latency', f'end_to_end_{stat}', BEN, ['stages', 'end_to_end', stat], 1)
# 3.3.1 and 4.1.1 (final adversarial review, H-01 and M-04)
add('audit1', 'units', BLIND, ['counts', 'candidates'], 0)
add('audit1', 'disagree', BLIND, ['counts', 'disagree'], 0)
add('audit1', 'positive_controls', BLIND, ['controls', 'positive'], 0)
add('m1val', 'map50', V01, ['average_precision', 'map50'])
add('m1val', 'map50_95', V01, ['average_precision', 'map50_95'])
add('latency', 'n', BEN, ['stages', 'end_to_end', 'n'], 0)
# 4.2.3
add('m2test', 'n', SEN, ['structure', 'n_images'], 0)
add('m2test', 'groups', I2, ['bootstrap', 'n_groups'], 0)
add('m2test', 'accuracy', I2, ['point', 'accuracy'])
add('m2test', 'macro_f1', I2, ['point', 'macro_f1'])
for i, end in enumerate(('low', 'high')):
    add('m2test', f'acc_ci_{end}', I2, ['intervals', 'accuracy', 'ci95', i])
    add('m2test', f'f1_ci_{end}', I2, ['intervals', 'macro_f1', 'ci95', i])
add('t7', 'n', SEN, ['structure', 'n_images'], 0)
add('t7', 'groups', I2, ['bootstrap', 'n_groups'], 0)
add('sens', 'n_images', SEN, ['structure', 'n_images'], 0)
add('sens', 'n_unique_sha', SEN, ['structure', 'n_unique_sha'], 0)
add('sens', 'resamples', SEN, ['inputs', 'resamples'], 0)
add('sens', 'seed', SEN, ['inputs', 'seed'], 0)
for scheme, short in (('exact_sha_dedup', 'sha'), ('cluster_weighted', 'cl')):
    for metric in ('accuracy', 'macro_f1'):
        add('sens', f'{short}_{metric}', SEN, ['estimands', scheme, 'metrics', metric])
        for i, end in enumerate(('low', 'high')):
            add('sens', f'{short}_{metric}_ci_{end}', SEN,
                ['bootstrap', 'intervals', scheme, metric, 'ci95', i])
            add('sens', f'{short}_{metric}_delta_ci_{end}', SEN,
                ['bootstrap', 'delta_intervals', scheme, metric, 'ci95', i], 2, scale=100)
        add('sens', f'{short}_{metric}_delta', SEN, ['deltas', scheme, metric, 'percentage_points'], 2)
# M2 confusions and F1
for (r, c), name in {(1, 2): 'cancro_as_costras', (2, 1): 'costras_as_cancro',
                     (2, 0): 'costras_as_antracnosis'}.items():
    add('m2conf', name, SEN, ['estimands', 'image_weighted', 'confusion', r, c], 0)
def ci(anchor, name, source, path):
    """Both printed endpoints of a 95 % interval (audit B round 2, R2-04)."""
    for i, end in enumerate(('low', 'high')):
        add(anchor, f'{name}_ci_{end}', source, [*path, 'ci95', i])


for cls in ('Cancro_bacteriano', 'Costras', 'Saludable', 'Podredumbre_Extremo_tallo'):
    add('m2conf', f'f1_{cls}', I2, ['point', f'f1[{cls}]'])
    ci('m2conf', f'f1_{cls}', I2, ['intervals', f'f1[{cls}]'])
# 5.1, 6.1, 7
add('disc', 'map50_val', V01, ['average_precision', 'map50'])
add('disc', 'map50_test', R02, ['average_precision', 'map50'])
ci('disc', 'map50', I1, ['metrics', 'map50'])
add('disc', 'recall_E_test', R02, ['operating_metrics', 'Enfermo', 'recall'])
ci('disc', 'recall_E', I1, ['metrics', 'Enfermo.recall'])
add('disc', 'precision_E_test', R02, ['operating_metrics', 'Enfermo', 'precision'])
ci('disc', 'precision_E', I1, ['metrics', 'Enfermo.precision'])
add('lim', 'recall_E_test', R02, ['operating_metrics', 'Enfermo', 'recall'])
ci('lim', 'recall_E', I1, ['metrics', 'Enfermo.recall'])
add('lim', 'n_E', R02, ['counts', 'instances_per_class', 'Enfermo'], 0)
add('lim', 'groups_E', I1, ['metrics', 'Enfermo.recall', 'class_group_counts', 'Enfermo'], 0)
add('lim', 'f1_cancro', I2, ['point', 'f1[Cancro_bacteriano]'])
ci('lim', 'f1_cancro', I2, ['intervals', 'f1[Cancro_bacteriano]'])
add('lim', 'f1_costras', I2, ['point', 'f1[Costras]'])
ci('lim', 'f1_costras', I2, ['intervals', 'f1[Costras]'])
add('concl', 'n_test', R02, ['counts', 'images'], 0)
add('concl', 'groups_test', R02, ['counts', 'groups'], 0)
add('concl', 'map50_test', R02, ['average_precision', 'map50'])
ci('concl', 'map50', I1, ['metrics', 'map50'])
add('concl', 'recall_E_test', R02, ['operating_metrics', 'Enfermo', 'recall'])
ci('concl', 'recall_E', I1, ['metrics', 'Enfermo.recall'])
add('concl', 'm2_accuracy', I2, ['point', 'accuracy'])
ci('concl', 'm2_accuracy', I2, ['intervals', 'accuracy'])
add('concl', 'm2_macro_f1', I2, ['point', 'macro_f1'])
ci('concl', 'm2_macro_f1', I2, ['intervals', 'macro_f1'])

ids = [r['id'] for r in rows]
assert len(ids) == len(set(ids)), 'duplicate ids'
OUT.write_text('[\n' + ',\n'.join('  ' + json.dumps(r, ensure_ascii=False) for r in rows) + '\n]\n',
               encoding='utf-8', newline='\n')
print(len(rows), 'numbers')
