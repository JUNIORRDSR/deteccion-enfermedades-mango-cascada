"""REVIEW-15: configs/class_names.json, one row per class index with every name it carries.

Each name is read from its source, never typed, except the editorial name the manuscript uses
(Spanish sentence case). M1: the corpus data.yaml, the EXP-R01 view data.yaml, the selected
checkpoint's model.names and kaggle_job.M1_MODEL_NAMES must agree. M2: the ART-002 checkpoint's
model.names, predict_model2.CLASS_NAMES and the frozen manifest; the original MangoDHDS label
of each local folder is joined through the file-name prefix (An, Bc, Sc, Se, He) of Labels.csv,
so the mapping is checked, not assumed. Nothing is renamed or remapped.
"""

import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.evaluation import kaggle_job, predict_model2  # noqa: E402

M1_EDITORIAL = {'Enfermo': 'Enfermo', 'Saludable': 'Saludable'}
M2_EDITORIAL = {'Antracnosis': 'Antracnosis', 'Cancro_bacteriano': 'Cancro bacteriano',
                'Costras': 'Costras', 'Podredumbre_Extremo_tallo': 'Podredumbre del extremo del tallo',
                'Saludable': 'Saludable'}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def yaml_names(path: Path) -> list[str]:
    line = next(l for l in path.read_text(encoding='utf-8').splitlines() if l.startswith('names:'))
    return json.loads(line.split(':', 1)[1].strip().replace("'", '"'))


def model_names(path: Path) -> list[str]:
    from ultralytics import YOLO
    names = YOLO(str(path)).names
    return [names[i] for i in range(len(names))]


def main() -> int:
    legacy = Path(json.loads((ROOT / 'configs/root_mapping.json').read_text(encoding='utf-8'))
                  ['legacy_corpus'])
    m1_sources = {
        'SemilleroTI-Mangos/docs/MangosDataset/data.yaml': yaml_names(
            legacy / 'SemilleroTI-Mangos/docs/MangosDataset/data.yaml'),
        'experiments/model1/EXP-R01/v1/evidence/data.yaml': yaml_names(
            ROOT / 'experiments/model1/EXP-R01/v1/evidence/data.yaml'),
        'experiments/model1/EXP-R01/v1/run/weights/selected.pt': model_names(
            ROOT / 'experiments/model1/EXP-R01/v1/run/weights/selected.pt'),
        'src/evaluation/kaggle_job.py:M1_MODEL_NAMES': [
            kaggle_job.M1_MODEL_NAMES[str(i)] for i in range(len(kaggle_job.M1_MODEL_NAMES))],
    }
    m1 = next(iter(m1_sources.values()))
    assert all(v == m1 for v in m1_sources.values()), m1_sources

    rows = list(csv.DictReader(open(ROOT / predict_model2.M2_MANIFEST, encoding='utf-8')))
    m2_sources = {
        predict_model2.ART002_PATH: model_names(legacy / predict_model2.ART002_PATH),
        'src/evaluation/predict_model2.py:CLASS_NAMES': list(predict_model2.CLASS_NAMES),
    }
    m2 = m2_sources[predict_model2.ART002_PATH]
    assert sorted(m2_sources['src/evaluation/predict_model2.py:CLASS_NAMES']) == sorted(m2), m2_sources
    assert {r['class_name'] for r in rows} == set(m2)
    dhds = next(p for p in (legacy / 'Mango-vision').iterdir() if p.name.startswith('MangoDHDS'))
    labels = list(csv.DictReader(open(dhds / 'Labels.csv', encoding='utf-8')))
    prefix_label = {}
    for r in labels:
        prefix_label.setdefault(Path(r['filename']).name[:2], set()).add(r['label'])
    folder_prefix = {}
    for r in rows:
        folder_prefix.setdefault(r['class_name'], set()).add(Path(r['path']).name[:2])
    original = {}
    for folder, prefixes in folder_prefix.items():
        found = set().union(*(prefix_label[p] for p in prefixes))
        assert len(prefixes) == 1 and len(found) == 1, (folder, prefixes, found)
        original[folder] = found.pop()

    out = {
        'model1': {'sources': m1_sources, 'source_sha256': {
            'experiments/model1/EXP-R01/v1/run/weights/selected.pt': sha(
                ROOT / 'experiments/model1/EXP-R01/v1/run/weights/selected.pt')},
            'classes': [{'id': i, 'model_name': n, 'editorial': M1_EDITORIAL[n]}
                        for i, n in enumerate(m1)]},
        'model2': {'sources': m2_sources, 'source_sha256': {
            predict_model2.ART002_PATH: sha(legacy / predict_model2.ART002_PATH),
            'MangoDHDS/Labels.csv': sha(dhds / 'Labels.csv')},
            'classes': [{'id': i, 'model_name': n, 'mangodhds_label': original[n],
                         'editorial': M2_EDITORIAL[n]} for i, n in enumerate(m2)]},
        'rule': 'model_name is the index label of the weights; editorial is the only name the '
                'manuscript uses; mangodhds_label appears once, in section 3.1, as the source name.',
    }
    target = ROOT / 'configs/class_names.json'
    target.write_text(json.dumps(out, indent=2, ensure_ascii=False) + '\n', encoding='utf-8',
                      newline='\n')
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
