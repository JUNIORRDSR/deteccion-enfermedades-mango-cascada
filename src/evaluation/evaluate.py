"""TASK-05: metrics from saved per-image records, frozen operating point and scoring.

All metrics come from unrounded float counts. An undefined metric (zero denominator,
or a class without ground truth) is None, never 0, and a mean over classes is None
when any class is undefined. Detection confusion keeps background as the LAST index;
background is never a real class and detection reports no accuracy.

AP reuses the installed Ultralytics 8.4.52: `box_iou`, `BaseValidator.match_predictions`
(class-aware, IoU 0.50:0.05:0.95, as `DetectionValidator._process_batch`) and
`ap_per_class`. Records hold boxes in original-image pixels; Ultralytics matches in
letterboxed space, which is a uniform scale plus shift, so IoU is the same up to float32.
"""

import argparse
import csv
import hashlib
import json
import math
import os
import sys
from pathlib import Path
from types import SimpleNamespace

GRID = [round(0.05 * k, 2) for k in range(1, 20)]
RULE = ('threshold maximising F2 = 5PR/(4P+R) of the positive class on validation records '
        'over 0.05..0.95 step 0.05; undefined F2 is skipped; ties go to the lower threshold')
VALIDATION_SPLIT = 'valid'  # the manifests' proposed_split value
REQUIRED = ('image_id', 'sha256', 'label_sha256', 'group_id', 'split', 'width', 'height',
            'gt', 'detections')
MANIFEST_FIELDS = ('image_id', 'sha256', 'label_sha256', 'group_id', 'proposed_split')
# SPEC section 7 inference settings; a config that changes any of them is rejected.
FROZEN_INFERENCE = {'min_score': 0.001, 'nms_iou': 0.6, 'max_det': 300, 'imgsz': 640}
GRID_DECLARATION = '0.05..0.95 step 0.05, ties to lower'
FIXED_CONFIG = {'model_id': 'model1', 'class_names': ['Enfermo', 'Saludable'],
                'positive_class': 'Enfermo', 'iou_match': 0.5}
FROZEN_CONFIG = 'configs/evaluation_frozen.json'
CODE = Path(__file__).resolve().parents[2]  # where this code lives
REPO = CODE  # the data root; tests of the literal commands point it at a synthetic repository
sys.path.insert(0, str(CODE))
# The canonical authorities, the code a frozen operating point seals and the approval snapshot
# live in one module (TASK-05 rounds 3-5).
from src.evaluation import authority  # noqa: E402
from src.evaluation.authority import (  # noqa: E402,F401
    AMENDMENT, EVALUATION_CONFIG, FREEZE_RECORD, M1_MANIFEST, SEALED_CODE, SELECTION_RECORD,
    VERIFIER, committed_clean,
)
SPLIT_NAMES = {'val': 'valid', 'valid': 'valid', 'test': 'test'}
# DECISION-039: Kaggle's web editor, the only venue that attaches the EXP-R01 output, saves a
# script version with this cell marker before the rendered text; nothing else may differ.
KAGGLE_EDITOR_CELL = '# %% [code]\n'


class RunRejected(Exception):
    """An input or record that must stop the run rather than be worked around."""


def executed_source(kernel: str, executed_sha256: str | None) -> str:
    """The text a Kaggle run executed: the rendered kernel itself, or the kernel after the one
    cell marker the web editor prepends (DECISION-039). Any other text is refused."""
    from src.evaluation import kaggle_job as job
    for text in (kernel, KAGGLE_EDITOR_CELL + kernel):
        if job.source_sha256(text) == executed_sha256:
            return text
    raise RunRejected('the executed source differs from the rendered kernel')


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _names(class_names) -> list[str]:
    """A model.names dict is ordered by id, never alphabetically."""
    if isinstance(class_names, dict):
        if sorted(class_names) != list(range(len(class_names))):
            raise RunRejected(f'class ids must be 0..n-1: {sorted(class_names)}')
        return [class_names[i] for i in range(len(class_names))]
    return list(class_names)


def _ratio(numerator: float, denominator: float) -> float | None:
    return numerator / denominator if denominator else None


def _number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _class_counts(cm: list[list[float]], i: int) -> dict:
    """TP diagonal, FP column minus TP, FN row minus TP; no GT support -> recall/F1 None."""
    tp = cm[i][i]
    support = sum(cm[i])
    fp = sum(row[i] for row in cm) - tp
    fn = support - tp
    return {'tp': tp, 'fp': fp, 'fn': fn, 'support': support,
            'precision': _ratio(tp, tp + fp), 'precision_denominator': tp + fp,
            'recall': _ratio(tp, support), 'recall_denominator': support,
            'f1': _ratio(2 * tp, 2 * tp + fp + fn) if support else None,
            'f1_denominator': 2 * tp + fp + fn}


def classification_metrics(cm: list[list[float]], class_names: list[str] | None = None) -> dict:
    """Rows are truth, columns prediction."""
    n = len(cm)
    names = [str(i) for i in range(n)] if class_names is None else _names(class_names)
    if len(names) != n or any(len(row) != n for row in cm):
        raise RunRejected('the confusion matrix must be square and match the class names')
    cm = [[float(v) for v in row] for row in cm]
    if not all(math.isfinite(v) and v >= 0 for row in cm for v in row):
        raise RunRejected('confusion counts must be finite and non-negative')
    total = sum(map(sum, cm))
    per_class = {name: _class_counts(cm, i) for i, name in enumerate(names)}
    f1 = [c['f1'] for c in per_class.values()]
    return {'class_names': names, 'accuracy': _ratio(sum(cm[i][i] for i in range(n)), total),
            'accuracy_denominator': total,
            'macro_f1': None if None in f1 else sum(f1) / n, 'per_class': per_class}


def yolo_labels_to_gt(text: str, width: int, height: int) -> list[dict]:
    """YOLO 'cls cx cy w h' normalised lines to xyxy pixels. Blank lines are skipped."""
    if not all(isinstance(v, int) and not isinstance(v, bool) and v > 0 for v in (width, height)):
        raise RunRejected(f'image size must be positive integers: {width}x{height}')
    gt, seen = [], set()
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            parts = line.split()
            if len(parts) != 5:
                raise ValueError
            cls, (cx, cy, w, h) = int(parts[0]), map(float, parts[1:])
        except ValueError:
            raise RunRejected(f'label line {number} is not "cls cx cy w h": {line!r}') from None
        if cls < 0 or not all(math.isfinite(v) and 0 <= v <= 1 for v in (cx, cy, w, h)) \
                or w <= 0 or h <= 0:
            raise RunRejected(f'label line {number} is out of range: {line!r}')
        # Ultralytics silently drops duplicate label rows; refuse them instead.
        if (cls, cx, cy, w, h) in seen:
            raise RunRejected(f'label line {number} duplicates an earlier line: {line!r}')
        seen.add((cls, cx, cy, w, h))
        gt.append({'class_id': cls, 'xyxy': [(cx - w / 2) * width, (cy - h / 2) * height,
                                             (cx + w / 2) * width, (cy + h / 2) * height]})
    return gt


def _check_box(item, n_classes: int, detection: bool, where: str) -> None:
    if not isinstance(item, dict):
        raise RunRejected(f'{where}: box is not an object')
    cls = item.get('class_id')
    if not isinstance(cls, int) or isinstance(cls, bool) or not 0 <= cls < n_classes:
        raise RunRejected(f'{where}: class_id {cls!r} is outside the class list')
    xyxy = item.get('xyxy')
    if not isinstance(xyxy, list) or len(xyxy) != 4 or not all(map(_number, xyxy)):
        raise RunRejected(f'{where}: xyxy must be four finite numbers: {xyxy!r}')
    if xyxy[2] <= xyxy[0] or xyxy[3] <= xyxy[1]:
        raise RunRejected(f'{where}: box needs x2>x1 and y2>y1: {xyxy}')
    if detection and not (_number(item.get('score')) and 0 <= item['score'] <= 1):
        raise RunRejected(f"{where}: score {item.get('score')!r} is outside [0, 1]")


def _non_finite(token: str):
    raise RunRejected(f'non-finite number {token} in predictions')


def load_records(path: Path, split: str, manifest_rows: list[dict], class_names) -> list[dict]:
    """JSON Lines, one record per image; coverage of the split must be total."""
    n_classes = len(_names(class_names))
    expected = {row['image_id']: row for row in manifest_rows if row['proposed_split'] == split}
    records, seen = [], set()
    for number, line in enumerate(Path(path).read_text(encoding='utf-8').splitlines(), 1):
        where = f'{Path(path).name} line {number}'
        try:
            record = json.loads(line, parse_constant=_non_finite)
        except json.JSONDecodeError as error:
            raise RunRejected(f'{where}: not JSON: {error}') from None
        if not isinstance(record, dict) or any(key not in record for key in REQUIRED):
            raise RunRejected(f'{where}: record needs the keys {REQUIRED}')
        image_id = record['image_id']
        if image_id in seen:
            raise RunRejected(f'{where}: duplicate image_id {image_id}')
        seen.add(image_id)
        if record['split'] != split:
            raise RunRejected(f"{where}: {image_id} has split {record['split']!r}, "
                              f'expected {split!r}')
        row = expected.get(image_id)
        if row is None:
            raise RunRejected(f'{where}: {image_id} is not in the {split!r} split of the manifest')
        for key in ('sha256', 'label_sha256', 'group_id'):
            if record[key] != row[key]:
                raise RunRejected(f'{where}: {key} of {image_id} disagrees with the manifest')
        for key in ('width', 'height'):
            value = record[key]
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise RunRejected(f'{where}: {key} must be a positive integer')
        for kind in ('gt', 'detections'):
            if not isinstance(record[kind], list):
                raise RunRejected(f'{where}: {kind} must be a list')
            for item in record[kind]:
                _check_box(item, n_classes, kind == 'detections', f'{where} {kind}')
        records.append(record)
    missing = sorted(expected.keys() - seen)
    if missing:
        raise RunRejected(f'{len(missing)} images of split {split!r} have no record, '
                          f'first {missing[0]}')
    return records


def _iou(a: list[float], b: list[float]) -> float:
    """The arithmetic of ultralytics.utils.metrics.box_iou (float32, eps 1e-7), so the
    operating-point match and AP@0.5 agree at the boundary (TASK-05 review MEDIUM-03)."""
    import numpy as np
    a, b = np.asarray(a, dtype=np.float32), np.asarray(b, dtype=np.float32)
    inter = np.clip(np.minimum(a[2:], b[2:]) - np.maximum(a[:2], b[:2]), 0, None).prod()
    return float(inter / ((a[2:] - a[:2]).prod() + (b[2:] - b[:2]).prod() - inter
                          + np.float32(1e-7)))


def match(gt: list[dict], pred: list[dict], iou_threshold: float = 0.5) -> dict:
    """One-to-one, class-agnostic: IoU descending, then gt index, then pred index."""
    pairs = sorted(((iou, g, p) for g, a in enumerate(gt) for p, b in enumerate(pred)
                    if (iou := _iou(a['xyxy'], b['xyxy'])) >= iou_threshold),
                   key=lambda t: (-t[0], t[1], t[2]))
    used_gt, used_pred, matches = set(), set(), []
    for iou, g, p in pairs:
        if g not in used_gt and p not in used_pred:
            used_gt.add(g)
            used_pred.add(p)
            matches.append({'gt': g, 'pred': p, 'iou': iou})
    return {'matches': matches,
            'unmatched_gt': [g for g in range(len(gt)) if g not in used_gt],
            'unmatched_pred': [p for p in range(len(pred)) if p not in used_pred]}


def detection_confusion(records: list[dict], threshold: float, class_names,
                        iou_threshold: float = 0.5) -> list[list[float]]:
    """(n+1)x(n+1), rows truth, columns prediction, background last; bg/bg stays 0."""
    n = len(_names(class_names))
    cm = [[0.0] * (n + 1) for _ in range(n + 1)]
    for record in records:
        gt = record['gt']
        kept = [d for d in record['detections'] if d['score'] >= threshold]
        result = match(gt, kept, iou_threshold)
        for pair in result['matches']:
            cm[gt[pair['gt']]['class_id']][kept[pair['pred']]['class_id']] += 1
        for g in result['unmatched_gt']:
            cm[gt[g]['class_id']][n] += 1
        for p in result['unmatched_pred']:
            cm[n][kept[p]['class_id']] += 1
    return cm


def _f2(p: float | None, r: float | None) -> float | None:
    if p is None or r is None or 4 * p + r == 0:
        return None
    return 5 * p * r / (4 * p + r)


def operating_metrics(records: list[dict], threshold: float, class_names,
                      iou_threshold: float = 0.5) -> dict:
    """Per real class P/R/F1/F2 with counts; FP and FN include background."""
    cm = detection_confusion(records, threshold, class_names, iou_threshold)
    out = {}
    for i, name in enumerate(_names(class_names)):
        counts = _class_counts(cm, i)
        out[name] = {**counts, 'f2': _f2(counts['precision'], counts['recall'])}
    return out


def select_threshold(val_records: list[dict], class_names, positive_class: str = 'Enfermo',
                     iou_threshold: float = 0.5) -> dict:
    if any(record['split'] == 'test' for record in val_records):
        raise RunRejected('test records can never choose the operating point')
    if positive_class not in _names(class_names):
        raise RunRejected(f'positive class {positive_class!r} is not a class name')
    grid, best = [], None
    for threshold in GRID:
        f2 = operating_metrics(val_records, threshold, class_names,
                               iou_threshold)[positive_class]['f2']
        grid.append({'threshold': threshold, 'f2': f2})
        if f2 is not None and (best is None or f2 > best['f2']):  # strict: ties keep the lower
            best = grid[-1]
    if best is None:
        raise RunRejected(f'F2 of {positive_class} is undefined at every threshold')
    return {'rule': RULE, 'positive_class': positive_class, 'grid': grid,
            'threshold': best['threshold'], 'f2': best['f2']}


def per_image_stats(records: list[dict]) -> list[dict]:
    """Per-image arrays as DetectionValidator.update_metrics builds them; any multiset of
    these (duplicates included) can be passed to ap_from_stats."""
    import numpy as np
    import torch
    from ultralytics.engine.validator import BaseValidator
    from ultralytics.utils.metrics import box_iou

    matcher = SimpleNamespace(iouv=torch.linspace(0.5, 0.95, 10))  # DetectionValidator.iouv
    stats = []
    for record in records:
        gt, det = record['gt'], record['detections']
        target_cls = torch.tensor([g['class_id'] for g in gt], dtype=torch.float32)
        pred_cls = torch.tensor([d['class_id'] for d in det], dtype=torch.float32)
        if gt and det:
            iou = box_iou(torch.tensor([g['xyxy'] for g in gt], dtype=torch.float64),
                          torch.tensor([d['xyxy'] for d in det], dtype=torch.float64))
            tp = BaseValidator.match_predictions(matcher, pred_cls, target_cls, iou).cpu().numpy()
        else:  # as _process_batch
            tp = np.zeros((len(det), matcher.iouv.numel()), dtype=bool)
        stats.append({'image_id': record['image_id'], 'tp': tp,
                      'conf': np.array([d['score'] for d in det], dtype=np.float64),
                      'pred_cls': pred_cls.numpy(), 'target_cls': target_cls.numpy()})
    return stats


def ap_from_stats(stats: list[dict], class_names) -> dict:
    """Ultralytics ap_per_class; a class without GT is undefined, and so are the means."""
    import numpy as np
    from ultralytics.utils.metrics import ap_per_class

    names = _names(class_names)
    if not stats:
        raise RunRejected('no images to compute AP on')
    joined = {k: np.concatenate([s[k] for s in stats], 0)
              for k in ('tp', 'conf', 'pred_cls', 'target_cls')}
    ap, classes = ap_per_class(joined['tp'], joined['conf'], joined['pred_cls'],
                               joined['target_cls'])[5:7]
    per_class = {name: {'ap50': None, 'ap50_95': None} for name in names}
    for row, c in zip(ap, classes):
        per_class[names[c]] = {'ap50': float(row[0]), 'ap50_95': float(row.mean())}
    defined = len(classes) == len(names)
    return {'per_class': per_class,
            'map50': float(ap[:, 0].mean()) if defined else None,  # DetMetrics.map50
            'map50_95': float(ap.mean()) if defined else None}  # DetMetrics.map


def average_precision(records: list[dict], class_names) -> dict:
    return ap_from_stats(per_image_stats(records), class_names)


def interval_metrics(config: dict) -> dict:
    """Metric specs for src.statistics.intervals at the FROZEN operating point.

    Each metric receives a group bootstrap resample; a class CI needs >=2 groups carrying
    GT of that class (records are annotated with 'gt_classes' by the caller). Per-image AP
    statistics are computed once per image_id and reused across draws.
    """
    names, threshold = _names(config['class_names']), config.get('threshold')
    if threshold is None:
        raise RunRejected('interval metrics need the frozen threshold')
    cache: dict[str, dict] = {}

    def ap(key):
        def metric(records):
            missing = [r for r in records if r['image_id'] not in cache]
            for r, s in zip(missing, per_image_stats(missing)):
                cache[r['image_id']] = s
            return ap_from_stats([cache[r['image_id']] for r in records], names)[key]
        return metric

    def operating(name, key):
        return lambda records: operating_metrics(records, threshold, names)[name][key]

    specs = {'map50': {'metric': ap('map50'), 'required_classes': names, 'class_key': 'gt_classes'},
             'map50_95': {'metric': ap('map50_95'), 'required_classes': names,
                          'class_key': 'gt_classes'}}
    for name in names:
        for key in ('precision', 'recall', 'f1', 'f2'):
            specs[f'{name}.{key}'] = {'metric': operating(name, key), 'required_classes': [name],
                                      'class_key': 'gt_classes'}
    return specs


def read_config(path: Path) -> dict:
    try:
        config = json.loads(Path(path).read_text(encoding='utf-8'))
    except json.JSONDecodeError as error:
        raise RunRejected(f'config is not JSON: {error}') from None
    names = config.get('class_names') if isinstance(config, dict) else None
    if not isinstance(names, list) or not names or len(set(names)) != len(names) \
            or not all(isinstance(n, str) and n for n in names):
        raise RunRejected('config class_names must be a list of distinct names ordered by id')
    if config.get('positive_class') not in names:
        raise RunRejected('config positive_class is not one of class_names')
    if not (_number(config.get('iou_match')) and 0 < config['iou_match'] <= 1):
        raise RunRejected('config iou_match must be in (0, 1]')
    for key, value in {**FROZEN_INFERENCE, **FIXED_CONFIG}.items():
        if config.get(key) != value:
            raise RunRejected(f'config {key} must be the frozen {value}')
    if config.get('threshold_grid') != GRID_DECLARATION:
        raise RunRejected('config threshold_grid must declare the frozen grid')
    return config


def _hex64(value) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef'
                                                               for c in value)


def _require_committed(root: Path, *paths: str) -> None:
    if not committed_clean(root, *paths):
        raise RunRejected(f'these authorities must be committed and unmodified: {list(paths)}')


def _canonical(path: Path, root: Path, relative: str, what: str) -> None:
    if Path(path).resolve() != (root / relative).resolve():
        raise RunRejected(f'the {what} is only {relative}')


def test_selection_digest(rows: list[dict]) -> str:
    """The test images the operating point is sealed for: image_id, image and label SHA256."""
    lines = sorted(f"{r['image_id']}\t{r['sha256']}\t{r['label_sha256']}\n"
                   for r in rows if r['proposed_split'] == 'test')
    return hashlib.sha256(''.join(lines).encode()).hexdigest()


def code_hashes(root: Path | None = None) -> dict[str, str]:
    root = Path(root) if root else REPO
    return {name: _sha(root / name) for name in SEALED_CODE}


def approved_inference(root: Path | None = None) -> dict:
    """Inference is approved for exactly the committed M1 authorities in the tree (TASK-05
    round-5 NEW-HIGH-03): the amendment's reviewed snapshot, not mere cleanliness."""
    root = Path(root) if root else REPO
    try:
        return authority.approved_inference(root, 'm1')
    except authority.NotApproved as error:
        raise RunRejected(str(error)) from None


def imported_runtime() -> dict[str, str]:
    """TASK-05 round 7: the AP code runs on Ultralytics and torch; import them and require that
    they came from recorded files of the verified interpreter."""
    import torch  # noqa: F401
    import ultralytics  # noqa: F401
    try:
        return authority.check_imported('ultralytics', 'torch')
    except authority.NotApproved as error:
        raise RunRejected(str(error)) from None


def bound_selection(config: dict, root: Path | None = None) -> dict:
    """TASK-05 round-3 NEW-HIGH-03: the checkpoint, the committed EXP-R01 selection record by
    hash and the training kernel version agree."""
    root = Path(root) if root else REPO
    path = root / SELECTION_RECORD
    if not path.is_file():
        raise RunRejected(f'the EXP-R01 selection record is missing: {path}')
    selection = json.loads(path.read_text(encoding='utf-8'))
    version = config.get('training_kernel_version')
    if (not _hex64(config.get('checkpoint_sha256')) or _sha(path) != config.get('selection_record_sha256')
            or selection.get('selected_sha256') != config['checkpoint_sha256']
            or not isinstance(version, int) or isinstance(version, bool)
            or selection.get('kernel_version') != version):
        raise RunRejected('the config does not name the checkpoint, selection record hash and '
                          'training kernel version of the EXP-R01 selection record')
    return selection


def sealed_config(config_path: Path, manifest: Path, root: Path | None = None) -> dict:
    """The ONE validator of a frozen operating point (TASK-05 rounds 2-4): the canonical,
    committed config and sidecar, a grid threshold, the manifest by hash, the evaluating code
    by committed bytes, the test selection, and the checkpoint bound to the committed EXP-R01
    selection record."""
    root = Path(root) if root else REPO
    _canonical(config_path, root, FROZEN_CONFIG, 'frozen operating point')
    _canonical(manifest, root, M1_MANIFEST, 'M1 manifest')
    config = read_config(config_path)
    sidecar = Path(str(config_path) + '.sha256')
    if not sidecar.is_file():
        raise RunRejected(f'frozen config sidecar missing: {sidecar}')
    if sidecar.read_bytes().split()[:1] != [_sha(config_path).encode()]:
        raise RunRejected(f'frozen config hash differs from its sidecar {sidecar}')
    _require_committed(root, FROZEN_CONFIG, FROZEN_CONFIG + '.sha256')
    approved_inference(root)
    if config.get('threshold') not in GRID:
        raise RunRejected(f"frozen threshold {config.get('threshold')!r} is not a grid value")
    _anchored(config, manifest)
    if config.get('code_sha256') != code_hashes(root):
        raise RunRejected('the evaluating code differs from the bytes the frozen config seals')
    if config.get('test_selection_digest') != test_selection_digest(read_manifest(manifest)):
        raise RunRejected('the test selection differs from the one the frozen config seals')
    bound_selection(config, root)
    return config


def _anchored(config: dict, manifest: Path) -> None:
    """The manifest must be the one the config names (TASK-05 review MEDIUM-01)."""
    if config.get('manifest_sha256') != _sha(manifest):
        raise RunRejected('the manifest is not the one the config names by hash')


def _legacy_root() -> Path:
    mapping = json.loads((CODE / 'configs/root_mapping.json').read_text(encoding='utf-8'))
    return Path(mapping['legacy_corpus'])


def _verifier(root: Path):
    """The approved verify_kaggle_run.py of the tree: approved_inference has checked its bytes
    against the reviewed snapshot before it is loaded (TASK-05 round-5 HIGH-04)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location('verify_kaggle_run', Path(root) / VERIFIER)
    module = importlib.util.module_from_spec(spec)
    path = list(sys.path)
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path[:] = path  # the verifier adds its checkout; imports resolve before this
    return module


def attempt_root(experiment_dir: Path, phase: str, root: Path | None = None) -> tuple[Path, dict]:
    """TASK-05 round-4 HIGH-04 / NEW-HIGH-01: the predictions of a phase come only from the one
    definitive attempt of its experiment, as recorded in the committed ledger, whose
    reconciliation re-derives byte for byte from its committed files."""
    root = Path(root) if root else REPO
    from src.evaluation import kaggle_job as job
    name = job.EXPERIMENT_OF[phase]
    experiment = Path(experiment_dir).resolve()
    if experiment != (root / 'experiments' / 'model1' / name).resolve():
        raise RunRejected(f'{phase} predictions come only from experiments/model1/{name}')
    approved_inference(root)
    verify = _verifier(root)
    ledger = verify.read_ledger(experiment / 'attempts.jsonl')
    definitive = [e for e in ledger if e.get('definitive')]
    if len(definitive) != 1 or ledger[-1] is not definitive[0] or any(
            e.get('mode') != 'predict' or e.get('experiment_id') != name
            or e.get('phase') not in (phase, None) for e in ledger) or ledger[-1]['phase'] != phase:
        raise RunRejected(f'the ledger of {name} does not end in its one definitive attempt')
    entry = ledger[-1]
    run = experiment / f"v{entry['version']}"
    try:
        outcome = verify.reconcile(run, entry['version'])
    except SystemExit as error:
        raise RunRejected(f'the attempt does not reconcile: {error}') from None
    stored = (run / 'reconciliation.json').read_bytes()
    if verify.dumps(outcome) != stored or verify.ledger_entry(outcome, stored) != entry:
        raise RunRejected('the reconciliation differs from its files or from its ledger line')
    files = [p.relative_to(root.resolve()).as_posix() for p in sorted(run.rglob('*'))
             if p.is_file() and not p.name.endswith('.tmp')]
    _require_committed(root, (experiment / 'attempts.jsonl').relative_to(root.resolve()).as_posix(),
                       *files)
    return run, {'experiment_id': name, 'attempt': entry['version'],
                 'reconciliation_sha256': entry['reconciliation_sha256'],
                 'receipt_sha256': entry['receipt_sha256']}


def rebuild_predictions(run_dir: Path, config_path: Path, manifest: Path,
                        phase: str) -> tuple[str, dict]:
    """The ONE derivation of evaluator records from a Kaggle predict attempt, used by the
    builder and re-run by every consumer (TASK-05 rounds 3-4).

    kernel.py must be exactly the current approved job rendering of its own payload; the render
    record must name its bytes and payload; the receipt must pass verify_prediction_run (the
    experiment, exact runtime evidence, checkpoint, config and manifest by hash, phase, frozen
    settings, executed source and the phase's files); the raw predictions must be the bytes the
    kernel hashed; and the ground truth comes from the labels whose hashes the manifest fixes."""
    from src.evaluation import kaggle_job as job
    run = Path(run_dir)
    config = read_config(config_path)
    rows = read_manifest(manifest)
    if any(key not in rows[0] for key in ('path', 'label')):
        raise RunRejected('the manifest needs path and label to rebuild predictions')
    try:
        kernel = (run / 'kernel.py').read_text(encoding='utf-8')
        render = json.loads((run / 'render_record.json').read_text(encoding='utf-8'))
        receipt = json.loads((run / 'receipt.json').read_text(encoding='utf-8'))
        raw = (run / 'predictions_raw.jsonl').read_bytes()
    except (OSError, json.JSONDecodeError) as error:
        raise RunRejected(f'the Kaggle run is incomplete: {error}') from None
    try:
        payload = job.payload_of(kernel)
        if job.source_sha256(job.render(payload)) != job.source_sha256(kernel):
            raise RunRejected('kernel.py is not the approved job rendering of its payload')
        payload_sha = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        if render.get('kernel_source_sha256') != job.source_sha256(kernel) \
                or render.get('payload_sha256') != payload_sha:
            raise RunRejected('kernel.py differs from its render record')
        legacy = _legacy_root()
        chosen = [r for r in rows if r['proposed_split'] == phase]
        labels, expected = {}, {}
        for r in chosen:
            data = (legacy / r['label']).read_bytes()
            if hashlib.sha256(data).hexdigest() != r['label_sha256']:
                raise RunRejected(f"local label differs from the manifest: {r['image_id']}")
            labels[r['image_id']] = data
            expected[r['path'].split('/', 1)[1]] = ('predict', r['sha256'],
                                                    hashlib.sha256(job.lf(data)).hexdigest())
        identities = job.verify_prediction_run(
            receipt, executed_source(kernel, receipt.get('kernel_source_sha256')), config, phase,
            expected, _sha(config_path), _sha(manifest))
    except job.JobRejected as error:
        raise RunRejected(str(error)) from None
    if hashlib.sha256(raw).hexdigest() != receipt.get('predictions_raw_sha256'):
        raise RunRejected('raw predictions differ from the bytes the kernel hashed')
    by_name = {Path(r['path']).name: r for r in chosen}
    out = []
    for line in raw.decode('utf-8').splitlines():
        item = json.loads(line)
        r = by_name.pop(item['file'], None)
        if r is None:
            raise RunRejected(f"raw prediction for an unknown or repeated file: {item['file']}")
        out.append({'image_id': r['image_id'], 'sha256': r['sha256'],
                    'label_sha256': r['label_sha256'], 'group_id': r['group_id'], 'split': phase,
                    'width': item['width'], 'height': item['height'],
                    'gt': yolo_labels_to_gt(labels[r['image_id']].decode('utf-8'),
                                            item['width'], item['height']),
                    'detections': item['detections']})
    if by_name:
        raise RunRejected(f'images without predictions: {sorted(by_name)[:3]}')
    text = ''.join(json.dumps(o, sort_keys=True) + '\n'
                   for o in sorted(out, key=lambda o: o['image_id']))
    return text, {**identities, 'predictions_sha256': hashlib.sha256(text.encode()).hexdigest(),
                  'images': len(out),
                  'selection_record_sha256': config.get('selection_record_sha256'),
                  'training_kernel_version': config.get('training_kernel_version')}


def rebuilt(experiment_dir: Path, config_path: Path, manifest: Path, phase: str,
            root: Path | None = None) -> tuple[str, dict]:
    """The records of the definitive committed attempt of a phase, with its attempt identity."""
    root = Path(root) if root else REPO
    run, attempt = attempt_root(experiment_dir, phase, root)
    text, identities = rebuild_predictions(run, config_path, manifest, phase)
    return text, {**identities, 'attempt': attempt}


def write_predictions(experiment_dir: Path, config_path: Path, manifest: Path, phase: str,
                      root: Path | None = None) -> dict:
    """<EXP>/predictions.jsonl, its sidecar and prediction_provenance.json; a rerun must find
    the same bytes."""
    root = Path(root) if root else REPO
    text, identities = rebuilt(experiment_dir, config_path, manifest, phase, root)
    experiment = Path(experiment_dir)
    outputs = {'predictions.jsonl': text.encode('utf-8'),
               'predictions.jsonl.sha256': f"{identities['predictions_sha256']}  predictions.jsonl\n".encode('ascii'),
               'prediction_provenance.json': (json.dumps(identities, indent=2) + '\n').encode('utf-8')}
    for name, data in outputs.items():
        target = experiment / name
        if target.exists():
            if target.read_bytes() != data:
                raise RunRejected(f'{target} exists with other bytes than the rebuild')
        else:
            target.write_bytes(data)
    return identities


def verified_provenance(predictions: Path, config_path: Path, manifest: Path, phase: str,
                        root: Path | None = None) -> dict:
    """Every consumer rebuilds the predictions from the definitive committed attempt and
    requires the same bytes, sidecar and provenance record; nothing self-authored is trusted
    (TASK-05 rounds 3-4)."""
    root = Path(root) if root else REPO
    predictions = Path(predictions)
    sidecar = Path(str(predictions) + '.sha256')
    record = predictions.with_name('prediction_provenance.json')
    if predictions.name != 'predictions.jsonl' or not sidecar.is_file() or not record.is_file():
        raise RunRejected('predictions need <EXP>/predictions.jsonl, its .sha256 sidecar and '
                          'prediction_provenance.json')
    text, identities = rebuilt(predictions.parent, config_path, manifest, phase, root)
    if predictions.read_bytes() != text.encode('utf-8'):
        raise RunRejected('predictions differ from the ones rebuilt from the Kaggle run')
    if sidecar.read_text(encoding='ascii').split()[:1] != [identities['predictions_sha256']]:
        raise RunRejected('predictions differ from their sidecar')
    if json.loads(record.read_text(encoding='utf-8')) != identities:
        raise RunRejected('prediction provenance differs from the identities rebuilt from the run')
    return identities


def read_manifest(path: Path) -> list[dict]:
    with Path(path).open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    if not rows or any(field not in rows[0] for field in MANIFEST_FIELDS):
        raise RunRejected(f'manifest needs the columns {MANIFEST_FIELDS}')
    ids = [row['image_id'] for row in rows]
    if len(set(ids)) != len(ids):
        raise RunRejected('manifest repeats an image_id')
    return rows


def freeze_operating_point(predictions: Path, config_path: Path, manifest: Path,
                           root: Path | None = None) -> dict:
    """Validation records only, from the definitive committed EXP-V01 attempt. Every authority
    the seal names is canonical and committed before it is hashed, and inference is approved
    for the job in the tree (TASK-05 round-4 NEW-HIGH-03)."""
    root = Path(root) if root else REPO
    _canonical(config_path, root, EVALUATION_CONFIG, 'validation config')
    _canonical(manifest, root, M1_MANIFEST, 'M1 manifest')
    approved_inference(root)
    config = read_config(config_path)
    if not _hex64(config.get('checkpoint_sha256')):
        raise RunRejected('config checkpoint_sha256 must name the evaluated weights')
    _anchored(config, manifest)
    bound_selection(config, root)
    provenance = verified_provenance(predictions, config_path, manifest, VALIDATION_SPLIT, root)
    rows = read_manifest(manifest)
    records = load_records(predictions, VALIDATION_SPLIT, rows, config['class_names'])
    chosen = select_threshold(records, config['class_names'], config['positive_class'],
                              config['iou_match'])
    return {**config, 'threshold': chosen['threshold'], 'threshold_rule': chosen['rule'],
            'threshold_f2': chosen['f2'], 'threshold_grid_values': chosen['grid'],
            'validation_predictions_sha256': _sha(predictions),
            'manifest_sha256': _sha(manifest), 'source_config_sha256': _sha(config_path),
            'code_sha256': code_hashes(root), 'test_selection_digest': test_selection_digest(rows),
            'validation_provenance': provenance}


def frozen_threshold(config_path: Path, config: dict, split: str, manifest: Path,
                     root: Path | None = None) -> float | None:
    """A frozen config must match its sidecar and manifest; test needs one."""
    root = Path(root) if root else REPO
    if 'threshold' not in config:
        if split == 'test':
            raise RunRejected('the test split needs a frozen config from --freeze-operating-point')
        _anchored(config, manifest)
        return None
    return sealed_config(config_path, manifest, root)['threshold']


def score(records: list[dict], config: dict, threshold: float | None) -> dict:
    """Operating metrics need a threshold; AP always uses every saved detection."""
    names, iou = config['class_names'], config['iou_match']
    operating = confusion = None
    if threshold is not None:
        operating = operating_metrics(records, threshold, names, iou)
        confusion = {'rows': 'truth', 'columns': 'prediction', 'labels': [*names, 'background'],
                     'matrix': detection_confusion(records, threshold, names, iou)}
    return {'threshold': threshold, 'operating_metrics': operating,
            'detection_confusion': confusion,
            'average_precision': average_precision(records, names),
            'counts': {'images': len(records),
                       'instances': sum(len(r['gt']) for r in records),
                       'instances_per_class': {name: sum(g['class_id'] == i for r in records
                                                         for g in r['gt'])
                                               for i, name in enumerate(names)},
                       'groups': len({r['group_id'] for r in records})}}


def _write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def _score_split(predictions: Path, config_path: Path, manifest: Path, split: str,
                 root: Path | None = None) -> dict:
    root = Path(root) if root else REPO
    config = read_config(config_path)
    threshold = frozen_threshold(config_path, config, split, manifest, root)
    provenance = verified_provenance(predictions, config_path, manifest, split, root)
    records = load_records(predictions, split, read_manifest(manifest), config['class_names'])
    from src.evaluation.provenance import (
        authorized_root, configure_environment, verify_environment,
    )
    checked = authorized_root()  # before the first scientific import (AP)
    configure_environment(checked)
    verify_environment(checked)
    os.environ['YOLO_OFFLINE'] = 'true'
    imported_runtime()
    return {'split': split, **score(records, config, threshold),
            'predictions_sha256': _sha(predictions), 'manifest_sha256': _sha(manifest),
            'config_sha256': _sha(config_path), 'prediction_provenance': provenance}


def _new(path: Path) -> Path:
    if path.exists() or Path(str(path) + '.sha256').exists():
        raise RunRejected(f'output already exists and is never overwritten: {path}')
    return path


def main(argv: list[str] | None = None) -> int:
    """The frozen TASK-05 commands (plan lines 284-287) and the explicit score form:

    --model-id model1 --config C --split val|test --run-dir experiments/model1/EXP-V01|EXP-R02
        predictions of the definitive committed attempt into <run-dir>, then metrics.json;
    --freeze-operating-point --predictions P --config C --out O [--manifest M]
        the operating point from EXP-V01;
    --model-id model2 --config C --split test --run-dir experiments/model2/EXP-R03
        the single local EXP-R03 inference of ART-002 (src/evaluation/predict_model2.py)."""
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--freeze-operating-point', action='store_true')
    mode.add_argument('--score', action='store_true')
    mode.add_argument('--model-id', choices=('model1', 'model2'))
    parser.add_argument('--predictions', type=Path)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--split')
    parser.add_argument('--run-dir', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args(argv)
    args.manifest = args.manifest or REPO / M1_MANIFEST

    if args.model_id == 'model2':
        if SPLIT_NAMES.get(args.split) != 'test' or not args.run_dir:
            parser.error('model2 runs only --split test with --run-dir')
        from src.evaluation import predict_model2
        mapping = json.loads((CODE / 'configs/root_mapping.json').read_text(encoding='utf-8'))
        weights = Path(mapping['legacy_corpus']) / predict_model2.ART002_PATH
        try:  # TASK-05 round 7 NEW-LOW-01: the wrapper's own refusal contract, exit 2
            result = predict_model2.run(REPO / predict_model2.M2_MANIFEST, weights, args.run_dir,
                                        config=args.config)
        except predict_model2.RunRejected as error:
            raise RunRejected(str(error)) from None
        print(json.dumps(result))
        return 0
    if args.model_id == 'model1':
        split = SPLIT_NAMES.get(args.split)
        if not split or not args.run_dir:
            parser.error('model1 needs --split val|test and --run-dir')
        target = _new(args.run_dir / 'metrics.json')
        write_predictions(args.run_dir, args.config, args.manifest, split)
        _write_json(target, _score_split(args.run_dir / 'predictions.jsonl', args.config,
                                         args.manifest, split))
        print(f'wrote {target}')
        return 0
    if not args.predictions or not args.out:
        parser.error('--predictions and --out are required')
    out = _new(args.out)
    if args.freeze_operating_point:
        sidecar = Path(str(out) + '.sha256')
        _write_json(out, freeze_operating_point(args.predictions, args.config, args.manifest))
        sidecar.write_text(f'{_sha(out)}  {out.name}\n', encoding='ascii')
        print(f'wrote {out} and {sidecar.name}')
        return 0
    split = SPLIT_NAMES.get(args.split)
    if not split:
        parser.error('--score needs --split val|test')
    _write_json(out, _score_split(args.predictions, args.config, args.manifest, split))
    print(f'wrote {out}')
    return 0


if __name__ == '__main__':
    from src.evaluation.provenance import InvalidInput
    try:
        sys.exit(main())
    except (RunRejected, InvalidInput) as error:
        print(f'REJECTED: {error}', file=sys.stderr)
        sys.exit(2)
