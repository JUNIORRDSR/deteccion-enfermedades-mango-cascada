"""Tables 4, 5 and 7 written straight from the metrics JSON, no intermediate rounding.

Table 4: M1 on validation at the frozen threshold (EXP-V01 scored with the frozen config).
         It replaces the old table of per-metric maxima over epochs, and takes the layout of
         Table 5 so both read the same way.
Table 5: M1 on test (EXP-R02) with the group-bootstrap CI of model1_intervals.json.
Table 7: M2 on test (EXP-R03) per class with the CI of model2_intervals.json; the weighted
         average row goes, since no frozen artifact computes it.
A blocked interval prints «IC no calculable» and its reason stays in the JSON.
"""

import copy
import json
from pathlib import Path

from docx_edit import cell_text

ROOT = Path(__file__).resolve().parents[3]
T4, T5, T7 = 3, 4, 6  # python-docx table indices of Tablas 4, 5 y 7


def es(value, digits: int = 3) -> str:
    return '—' if value is None else f'{value:.{digits}f}'.replace('.', ',')


def with_ci(estimate, interval: dict | None) -> str:
    if interval is None:
        return es(estimate)
    if interval.get('blocked') or interval.get('ci95') is None:
        return f'{es(estimate)} (IC no calculable)'
    low, high = interval['ci95']
    return f'{es(estimate)} [{es(low)}; {es(high)}]'


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def _fit_rows(table, n: int) -> None:
    rows = table._tbl.tr_lst
    while len(rows) < n:
        rows[-1].addnext(copy.deepcopy(rows[-1]))
        rows = table._tbl.tr_lst
    for tr in rows[n:]:
        table._tbl.remove(tr)


def _fill(d, index: int, rows: list[list[str]]) -> None:
    _fit_rows(d.tables[index], len(rows))
    for r, row in enumerate(rows):
        for c, text in enumerate(row):
            cell_text(d, index, r, c, text)


def m1_rows(metrics: dict, intervals: dict | None, names: list[str]) -> list[list[str]]:
    ci = (intervals or {}).get('metrics', {})
    ap = metrics['average_precision']
    op = metrics['operating_metrics']

    def interval(key):
        return ci.get(key) if intervals else None

    rows = [['Métrica', 'Media de clases', *names],
            ['AP@0,5', with_ci(ap['map50'], interval('map50')),
             *[es(ap['per_class'][n]['ap50']) for n in names]],
            ['AP@0,5:0,95', with_ci(ap['map50_95'], interval('map50_95')),
             *[es(ap['per_class'][n]['ap50_95']) for n in names]]]
    for key, label in (('precision', 'Precisión'), ('recall', 'Sensibilidad'), ('f1', 'F1'),
                       ('f2', 'F2')):
        rows.append([label, '—', *[with_ci(op[n][key], interval(f'{n}.{key}')) for n in names]])
    return rows


def m2_rows(intervals: dict, editorial: dict, support: dict) -> list[list[str]]:
    point, ci = intervals['point'], intervals.get('intervals') or {}
    rows = [['Clase', 'P', 'R', 'F1', 'n']]
    for name in intervals['class_names']:
        rows.append([editorial[name], *[with_ci(point[f'{k}[{name}]'], ci.get(f'{k}[{name}]'))
                                        for k in ('precision', 'recall', 'f1')],
                     str(support[name])])
    rows.append(['Media macro', '—', '—', with_ci(point['macro_f1'], ci.get('macro_f1')),
                 str(sum(support.values()))])
    return rows


def apply(d, facts: dict) -> None:
    names = facts['m1_names']
    t5 = d.tables[T5]
    old4 = d.tables[T4]._tbl
    old4.addnext(copy.deepcopy(t5._tbl))  # Table 4 takes Table 5's layout
    old4.getparent().remove(old4)
    _fill(d, T4, m1_rows(facts['val'], None, names))
    _fill(d, T5, m1_rows(facts['test'], facts['m1_intervals'], names))
    _fill(d, T7, m2_rows(facts['m2_intervals'], facts['m2_editorial'], facts['m2_support']))
