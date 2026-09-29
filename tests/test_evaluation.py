"""TASK-05 evaluation contracts. Fictitious records only: no model is loaded."""

import csv
import hashlib
import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.evaluation.evaluate import (
    GRID, RunRejected, ap_from_stats, average_precision, classification_metrics,
    detection_confusion, freeze_operating_point, frozen_threshold, load_records, match,
    operating_metrics, per_image_stats, read_config, read_manifest, score, select_threshold,
    verified_provenance, yolo_labels_to_gt,
)

from tests import runtime_stub

ROOT = Path(__file__).resolve().parents[1]
NAMES = ['Enfermo', 'Saludable']
E, S = 0, 1


def setUpModule():
    runtime_stub.start()


def tearDownModule():
    runtime_stub.stop()


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def box(class_id, xyxy, score=None):
    item = {'class_id': class_id, 'xyxy': list(map(float, xyxy))}
    if score is not None:
        item['score'] = score
    return item


def manifest_row(image_id, split):
    return {'image_id': image_id, 'sha256': sha(image_id.encode()),
            'label_sha256': sha(f'{image_id}.txt'.encode()), 'group_id': f'G-{image_id}',
            'cluster_id': f'C-{image_id}', 'proposed_split': split}


def record(image_id, split, gt, detections):
    row = manifest_row(image_id, split)
    return {'image_id': image_id, 'sha256': row['sha256'], 'label_sha256': row['label_sha256'],
            'group_id': row['group_id'], 'split': split, 'width': 100, 'height': 100,
            'gt': gt, 'detections': detections}


MANIFEST = [manifest_row('SRC-1', 'valid'), manifest_row('SRC-2', 'valid'),
            manifest_row('SRC-3', 'test'), manifest_row('SRC-4', 'train')]
VALID = [
    # Enfermo found at 0.5; a background Enfermo at 0.3 on the healthy image.
    record('SRC-1', 'valid', [box(E, [10, 10, 50, 50])], [box(E, [10, 10, 50, 50], .5)]),
    record('SRC-2', 'valid', [box(S, [0, 0, 20, 20])],
           [box(S, [0, 0, 20, 20], .9), box(E, [60, 60, 90, 90], .3)]),
]
TEST = [record('SRC-3', 'test', [box(E, [5, 5, 25, 25])], [box(E, [5, 5, 25, 25], .4)])]
CONFIG = {'model_id': 'model1', 'class_names': NAMES, 'positive_class': 'Enfermo',
          'iou_match': 0.5, 'nms_iou': 0.6, 'max_det': 300, 'min_score': 0.001, 'imgsz': 640,
          'threshold_grid': '0.05..0.95 step 0.05, ties to lower', 'checkpoint_sha256': 'c' * 64}


def write_jsonl(path: Path, records: list[dict]) -> Path:
    path.write_text(''.join(json.dumps(r) + '\n' for r in records), encoding='utf-8')
    return path


def write_manifest(path: Path) -> Path:
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(MANIFEST[0]))
        writer.writeheader()
        writer.writerows(MANIFEST)
    return path


FROZEN_INFERENCE = {'min_score': 0.001, 'nms_iou': 0.6, 'max_det': 300, 'imgsz': 640}
TASK04 = ROOT / 'provenance' / 'commands' / 'task04'
sys.path.insert(0, str(TASK04))
import verify_kaggle_run as verifier  # noqa: E402


def label_text(gt: list[dict], width: int = 100, height: int = 100) -> bytes:
    lines = [f"{g['class_id']} {(g['xyxy'][0] + g['xyxy'][2]) / 2 / width} "
             f"{(g['xyxy'][1] + g['xyxy'][3]) / 2 / height} "
             f"{(g['xyxy'][2] - g['xyxy'][0]) / width} {(g['xyxy'][3] - g['xyxy'][1]) / height}"
             for g in gt]
    return ('\n'.join(lines) + '\n').encode() if lines else b''


def write_chain_manifest(path: Path, labels: Path) -> Path:
    """MANIFEST plus the path and label columns a rebuild reads; labels are absolute paths
    outside the repository and carry the GT of VALID and TEST."""
    gt = {r['image_id']: r['gt'] for r in VALID + TEST}
    rows = []
    for row in MANIFEST:
        label = labels / f"{row['image_id']}.txt"
        label.parent.mkdir(parents=True, exist_ok=True)
        label.write_bytes(label_text(gt.get(row['image_id'], [])))
        split = row['proposed_split']
        rows.append({**row, 'label_sha256': sha(label.read_bytes()), 'label': str(label),
                     'path': f"legacy/docs/MangosDataset/{split}/images/{row['image_id']}.jpg"})
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return path


def git(root: Path, *args):
    subprocess.run(['git', '-c', 'user.email=t@t', '-c', 'user.name=t', *args], cwd=root,
                   check=True, capture_output=True)


def commit(root: Path, message: str = 'step'):
    git(root, 'add', '-A')
    git(root, 'commit', '-qm', message, '--allow-empty')


def make_attempt(root: Path, phase: str, config: Path, manifest: Path, records: list[dict],
                 status: str = 'COMPLETE', stage: str = 'done', receipt_change=None,
                 executed_prefix: str = '') -> Path:
    """A downloaded, reconciled predict attempt exactly as the renderer, the job, the platform
    and verify_kaggle_run.py leave it; `executed_prefix` is what the platform ran before the
    rendered text (DECISION-039)."""
    from src.evaluation import kaggle_job as job
    experiment = job.EXPERIMENT_OF[phase]
    run = root / 'experiments' / 'model1' / experiment / 'v1'
    run.mkdir(parents=True)
    rows = [r for r in read_manifest(manifest) if r['proposed_split'] == phase]
    by_id = {r['image_id']: r for r in records}
    payload = {'mode': 'predict', 'phase': phase, 'experiment_id': experiment,
               'checkpoint_sha256': 'c' * 64, 'inference': FROZEN_INFERENCE,
               'config_sha256': sha(config.read_bytes()), 'manifest_sha256': sha(manifest.read_bytes())}
    kernel = job.render(payload)
    (run / 'kernel.py').write_text(kernel, encoding='utf-8', newline='\n')
    payload_sha = sha(json.dumps(payload, sort_keys=True).encode())
    (run / 'render_record.json').write_text(json.dumps({
        'kernel_sha256': sha((run / 'kernel.py').read_bytes()),
        'kernel_source_sha256': job.source_sha256(kernel), 'payload_sha256': payload_sha,
        'manifest_sha256': sha(manifest.read_bytes()), 'mode': 'predict',
        'experiment_id': experiment, 'attempt': 1}), encoding='utf-8')
    raw = ''.join(json.dumps({'file': Path(r['path']).name, 'width': 100, 'height': 100,
                              'detections': by_id[r['image_id']]['detections']},
                             sort_keys=True) + '\n' for r in rows)
    (run / 'predictions_raw.jsonl').write_text(raw, encoding='utf-8', newline='\n')
    (run / 'evidence').mkdir()
    (run / 'evidence' / 'pip_check.stdout.txt').write_text('', encoding='utf-8')
    (run / 'job_log.txt').write_text('ok\n', encoding='utf-8')
    receipt = {'payload_sha256': payload_sha,
               'kernel_source_sha256': job.source_sha256(executed_prefix + kernel),
               'status': status, 'stage': stage, 'mode': 'predict', 'phase': phase,
               'experiment_id': experiment, 'checkpoint_sha256': 'c' * 64,
               'predictions_raw_sha256': sha(raw.encode()), 'end2end': True,
               'agnostic_nms': False, 'single_cls': False,
               'effective_suppression': job.suppression(True, 0.6),
               'input_contract': job.INPUT_CONTRACT, 'model_names': {'0': 'Enfermo', '1': 'Saludable'},
               'predict_args': job.predict_args(FROZEN_INFERENCE),
               'inventory': {'evidence/pip_check.stdout.txt': sha(b''),
                             'predictions_raw.jsonl': sha(raw.encode())},
               'files': [{'path': r['path'].split('/', 1)[1], 'image_sha256': r['sha256'],
                          'label_lf_sha256': sha(job.lf(Path(r['label']).read_bytes())),
                          'split': 'predict'} for r in rows], **(receipt_change or {})}
    (run / 'receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    (run / 'platform_log.json').write_text('[]', encoding='utf-8')
    (run / 'platform.json').write_text(json.dumps({
        'version': 1, 'status': 'COMPLETE' if status == 'COMPLETE' else 'ERROR',
        'docker_image': 'd', 'outputs': ['evidence/pip_check.stdout.txt', 'job_log.txt',
                                         'predictions_raw.jsonl', 'receipt.json']}),
        encoding='utf-8')
    verifier.finalize(run, 1, verifier.reconcile(run, 1), None)
    commit(root, f'{experiment} v1')
    return run.parent


def run_cli(*args):
    return subprocess.run([sys.executable, '-m', 'src.evaluation.evaluate', *map(str, args)],
                          cwd=ROOT, capture_output=True, text=True)


def run_frozen(root: Path, *args):
    """A literal frozen command, with the evaluator's data root pointed at a synthetic repository."""
    driver = (runtime_stub.DRIVER + 'import sys; from pathlib import Path; '
              'import src.evaluation.evaluate as e; '
              f'e.REPO = Path({str(root)!r}); sys.argv[0] = "evaluate"; '
              'from src.evaluation.provenance import InvalidInput\n'
              'try:\n    sys.exit(e.main(sys.argv[1:]))\n'
              'except (e.RunRejected, InvalidInput) as error:\n'
              '    print(f"REJECTED: {error}", file=sys.stderr); sys.exit(2)')
    return subprocess.run([sys.executable, '-c', driver, *map(str, args)], cwd=ROOT,
                          capture_output=True, text=True)


class ClassificationMetrics(unittest.TestCase):
    def test_plan_red_fixture(self):
        """Verbatim from the plan."""
        m=classification_metrics([[8,2],[1,9]])
        assert abs(m['accuracy'] - 17/20) < 1e-12
        assert abs(m['macro_f1'] - (16/19+18/21)/2) < 1e-12

    def test_denominators_and_names_are_returned(self):
        m = classification_metrics([[8, 2], [1, 9]], NAMES)
        enfermo = m['per_class']['Enfermo']
        self.assertEqual((enfermo['precision_denominator'], enfermo['recall_denominator'],
                          enfermo['f1_denominator'], m['accuracy_denominator']), (9, 10, 19, 20))
        self.assertEqual(list(m['per_class']), NAMES)

    def test_absent_gt_class_makes_its_f1_and_macro_f1_undefined(self):
        m = classification_metrics([[5, 1], [0, 0]], NAMES)
        self.assertIsNone(m['per_class']['Saludable']['recall'])
        self.assertIsNone(m['per_class']['Saludable']['f1'])
        self.assertIsNone(m['macro_f1'])

    def test_undefined_precision_does_not_prevent_f1_zero(self):
        m = classification_metrics([[5, 0], [3, 0]], NAMES)
        saludable = m['per_class']['Saludable']
        self.assertIsNone(saludable['precision'])
        self.assertEqual(saludable['f1'], 0.0)
        self.assertAlmostEqual(m['macro_f1'], (10 / 13 + 0) / 2, places=12)

    def test_empty_matrix_has_undefined_accuracy(self):
        self.assertIsNone(classification_metrics([[0, 0], [0, 0]])['accuracy'])


class Labels(unittest.TestCase):
    def test_yolo_line_becomes_pixel_xyxy(self):
        [gt] = yolo_labels_to_gt('1 0.5 0.5 0.2 0.4\n', 100, 50)
        self.assertEqual(gt['class_id'], 1)
        for got, want in zip(gt['xyxy'], [40, 15, 60, 35]):
            self.assertAlmostEqual(got, want, places=9)

    def test_empty_label_file_is_background(self):
        self.assertEqual(yolo_labels_to_gt('', 100, 100), [])

    def test_malformed_lines_are_rejected(self):
        for line in ('0 0.5 0.5 0.2', 'x 0.5 0.5 0.2 0.2', '0.5 0.5 0.5 0.2 0.2',
                     '-1 0.5 0.5 0.2 0.2', '0 1.5 0.5 0.2 0.2', '0 0.5 0.5 0 0.2',
                     '0 nan 0.5 0.2 0.2', '0 0.5 0.5 0.2 0.2 7',
                     '0 0.5 0.5 0.2 0.2\n0 0.5 0.5 0.2 0.2'):
            with self.subTest(line=line), self.assertRaises(RunRejected):
                yolo_labels_to_gt(line, 100, 100)


class Records(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def load(self, records, split='valid'):
        return load_records(write_jsonl(self.dir / 'p.jsonl', records), split, MANIFEST, NAMES)

    def test_valid_records_load(self):
        self.assertEqual([r['image_id'] for r in self.load(VALID)], ['SRC-1', 'SRC-2'])

    def test_image_without_detections_is_allowed(self):
        self.load([VALID[0], {**VALID[1], 'detections': []}])

    def test_invalid_records_are_rejected(self):
        one, two = VALID
        bad_box = {**two, 'detections': [box(S, [20, 0, 10, 20], .9)]}
        cases = {
            'duplicate image_id': [one, two, one],
            'not in manifest': [one, two, record('SRC-9', 'valid', [], [])],
            'other split in manifest': [one, two, record('SRC-3', 'valid', [], [])],
            'record split differs': [one, {**two, 'split': 'test'}],
            'sha256': [one, {**two, 'sha256': '0' * 64}],
            'label_sha256': [one, {**two, 'label_sha256': '0' * 64}],
            'group_id': [one, {**two, 'group_id': 'G-other'}],
            'x2<=x1': [one, bad_box],
            'y2<=y1': [one, {**two, 'gt': [box(S, [0, 20, 20, 20])]}],
            'score above 1': [one, {**two, 'detections': [box(S, [0, 0, 20, 20], 1.5)]}],
            'negative score': [one, {**two, 'detections': [box(S, [0, 0, 20, 20], -.1)]}],
            'class outside list': [one, {**two, 'gt': [box(2, [0, 0, 20, 20])]}],
            'incomplete coverage': [one],
        }
        for name, records in cases.items():
            with self.subTest(case=name), self.assertRaises(RunRejected):
                self.load(records)

    def test_non_finite_numbers_are_rejected(self):
        path = write_jsonl(self.dir / 'p.jsonl', VALID)
        for token in ('NaN', 'Infinity', '1e999'):
            with self.subTest(token=token):
                path.write_text(path.read_text(encoding='utf-8').replace('0.9', token, 1),
                                encoding='utf-8')
                with self.assertRaises(RunRejected):
                    load_records(path, 'valid', MANIFEST, NAMES)
                write_jsonl(path, VALID)


class Matching(unittest.TestCase):
    def test_two_predictions_on_one_gt_give_one_match_and_one_fp(self):
        result = match([box(E, [0, 0, 10, 10])],
                       [box(E, [0, 0, 10, 10], .9), box(E, [0, 0, 10, 9], .8)])
        self.assertEqual([(m['gt'], m['pred']) for m in result['matches']], [(0, 0)])
        self.assertEqual(result['unmatched_pred'], [1])
        self.assertEqual(result['unmatched_gt'], [])

    def test_gt_without_prediction_is_fn(self):
        result = match([box(E, [0, 0, 10, 10])], [])
        self.assertEqual((result['matches'], result['unmatched_gt']), ([], [0]))

    def test_equal_iou_ties_follow_stable_indices(self):
        same = [0, 0, 10, 10]
        result = match([box(E, same), box(S, same)], [box(E, same, .5)])
        self.assertEqual([(m['gt'], m['pred']) for m in result['matches']], [(0, 0)])
        result = match([box(E, same)], [box(E, same, .5), box(S, same, .9)])
        self.assertEqual([(m['gt'], m['pred']) for m in result['matches']], [(0, 0)])

    def test_matching_is_class_agnostic(self):
        result = match([box(E, [0, 0, 10, 10])], [box(S, [0, 0, 10, 10], .9)])
        self.assertEqual(len(result['matches']), 1)

    def test_below_iou_threshold_is_fp_and_fn(self):
        result = match([box(E, [0, 0, 10, 10])], [box(E, [5, 0, 15, 10], .9)])  # IoU 1/3
        self.assertEqual((result['unmatched_gt'], result['unmatched_pred']), ([0], [0]))

    def test_unsorted_names_dict_is_ordered_by_id(self):
        names = {1: 'Alpha', 0: 'Zulu'}
        records = [record('SRC-1', 'valid', [box(0, [0, 0, 10, 10])], [box(0, [0, 0, 10, 10], .9)])]
        metrics = operating_metrics(records, .5, names)
        self.assertEqual(list(metrics), ['Zulu', 'Alpha'])
        self.assertEqual((metrics['Zulu']['tp'], metrics['Alpha']['tp']), (1, 0))
        self.assertEqual(detection_confusion(records, .5, names)[0][0], 1)


class DetectionOperatingPoint(unittest.TestCase):
    RECORDS = [
        record('A', 'valid', [box(E, [0, 0, 10, 10])],
               [box(E, [0, 0, 10, 10], .9), box(S, [50, 50, 60, 60], .8)]),
        record('B', 'valid', [box(S, [0, 0, 10, 10])], []),
        record('C', 'valid', [box(E, [0, 0, 10, 10])], [box(S, [0, 0, 10, 10], .7)]),
    ]

    def test_confusion_puts_background_last(self):
        self.assertEqual(detection_confusion(self.RECORDS, .5, NAMES),
                         [[1, 1, 0], [0, 0, 1], [0, 1, 0]])

    def test_threshold_filters_detections_first(self):
        self.assertEqual(detection_confusion(self.RECORDS, .75, NAMES),
                         [[1, 0, 1], [0, 0, 1], [0, 1, 0]])

    def test_operating_metrics_count_background_and_report_no_accuracy(self):
        m = operating_metrics(self.RECORDS, .5, NAMES)
        enfermo, saludable = m['Enfermo'], m['Saludable']
        self.assertEqual((enfermo['tp'], enfermo['fp'], enfermo['fn']), (1, 0, 1))
        self.assertEqual((enfermo['precision'], enfermo['recall']), (1.0, .5))
        self.assertAlmostEqual(enfermo['f1'], 2 / 3, places=12)
        self.assertAlmostEqual(enfermo['f2'], 5 / 9, places=12)
        self.assertEqual((saludable['tp'], saludable['fp'], saludable['fn']), (0, 2, 1))
        self.assertEqual(saludable['f1'], 0.0)
        self.assertIsNone(saludable['f2'])  # P = R = 0: 5PR/(4P+R) is 0/0
        self.assertNotIn('accuracy', json.dumps(m))


class ThresholdSelection(unittest.TestCase):
    def test_grid_is_exact(self):
        self.assertEqual(GRID, [round(0.05 * k, 2) for k in range(1, 20)])
        self.assertEqual((GRID[0], GRID[5], GRID[-1], len(GRID)), (0.05, 0.3, 0.95, 19))

    def test_maximum_f2_with_ties_to_the_lower_threshold(self):
        chosen = select_threshold(VALID, NAMES)
        self.assertEqual(chosen['threshold'], 0.35)  # F2=1 on 0.35..0.5; 0.3 keeps the FP
        grid = {row['threshold']: row['f2'] for row in chosen['grid']}
        self.assertAlmostEqual(grid[0.3], 2.5 / 3, places=12)
        self.assertIsNone(grid[0.55])
        self.assertIn('F2', chosen['rule'])

    def test_all_undefined_raises(self):
        records = [record('SRC-1', 'valid', [box(E, [0, 0, 10, 10])], [])]
        with self.assertRaisesRegex(RunRejected, 'undefined'):
            select_threshold(records, NAMES)

    def test_test_records_are_rejected(self):
        with self.assertRaisesRegex(RunRejected, 'test'):
            select_threshold(VALID + TEST, NAMES)


class AveragePrecision(unittest.TestCase):
    def test_perfect_predictions_reach_the_pinned_evaluator_maximum(self):
        """Ultralytics 8.4.52 integrates 101 points and drops to 0 after the last recall,
        so an all-correct ranking gives 0.995, not 1.0 (the same value `val` prints)."""
        records = [record('A', 'valid', [box(E, [0, 0, 10, 10]), box(S, [20, 20, 40, 40])],
                          [box(E, [0, 0, 10, 10], .9), box(S, [20, 20, 40, 40], .8)]),
                   record('B', 'valid', [box(E, [5, 5, 30, 30])], [box(E, [5, 5, 30, 30], .7)])]
        ap = average_precision(records, NAMES)
        for name in NAMES:
            self.assertAlmostEqual(ap['per_class'][name]['ap50'], 0.995, places=12)
            self.assertAlmostEqual(ap['per_class'][name]['ap50_95'], 0.995, places=12)
        self.assertAlmostEqual(ap['map50'], 0.995, places=12)
        self.assertAlmostEqual(ap['map50_95'], 0.995, places=12)

    def test_duplicating_one_image_in_stats_equals_duplicating_its_record(self):
        records = [record('A', 'valid', [box(E, [0, 0, 10, 10])],
                          [box(E, [50, 50, 60, 60], .9), box(E, [0, 0, 10, 10], .6)]),
                   record('B', 'valid', [box(E, [0, 0, 10, 10]), box(S, [20, 20, 40, 40])],
                          [box(E, [0, 0, 10, 10], .8), box(S, [20, 20, 40, 40], .7)])]
        stats = per_image_stats(records)
        doubled = ap_from_stats(stats + [stats[0]], NAMES)
        self.assertEqual(doubled, average_precision(records + [{**records[0], 'image_id': 'A#2'}],
                                                    NAMES))
        self.assertNotEqual(doubled['map50'], ap_from_stats(stats, NAMES)['map50'])

    def test_class_without_gt_has_undefined_ap_and_mean(self):
        records = [record('A', 'valid', [box(E, [0, 0, 10, 10])], [box(E, [0, 0, 10, 10], .9)])]
        ap = average_precision(records, NAMES)
        self.assertIsNone(ap['per_class']['Saludable']['ap50'])
        self.assertIsNone(ap['map50'])
        self.assertIsNone(ap['map50_95'])


class Chain(unittest.TestCase):
    """A synthetic committed repository with the real sealed code, the canonical authorities and
    an EXP-V01 attempt reconciled by the real verifier (TASK-05 rounds 3-4)."""

    def setUp(self):
        from src.evaluation import evaluate
        self.tmp = TemporaryDirectory()
        self.root = Path(self.tmp.name) / 'repo'
        for name in (*evaluate.SEALED_CODE, 'provenance/protocol_freeze.json',
                     'provenance/environment/inference_environment.txt',
                     'provenance/environment/inference_runtime.txt',
                     'provenance/environment/inference_interpreter.json'):
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        self.manifest = write_chain_manifest(self.root / evaluate.M1_MANIFEST,
                                             Path(self.tmp.name) / 'labels')
        Path(str(self.manifest) + '.sha256').write_text(
            f'{sha(self.manifest.read_bytes())}  model1_clean_manifest.csv\n', encoding='ascii')
        (self.root / evaluate.FREEZE_RECORD).write_text('{}', encoding='utf-8')
        self.selection = self.root / evaluate.SELECTION_RECORD
        self.selection.parent.mkdir(parents=True)
        self.selection.write_text(json.dumps({'selected_sha256': 'c' * 64, 'kernel_version': 1}),
                                  encoding='utf-8')
        self.config = self.root / evaluate.EVALUATION_CONFIG
        self.config.parent.mkdir(parents=True, exist_ok=True)
        self.config.write_text(json.dumps({
            **CONFIG, 'manifest_sha256': sha(self.manifest.read_bytes()),
            'selection_record_sha256': sha(self.selection.read_bytes()),
            'training_kernel_version': 1}), encoding='utf-8')
        git(self.root, 'init', '-q')
        self.approve()
        self.valid_exp = make_attempt(self.root, 'valid', self.config, self.manifest, VALID)
        evaluate.write_predictions(self.valid_exp, self.config, self.manifest, 'valid', self.root)
        self.valid = self.valid_exp / 'predictions.jsonl'
        self.frozen = self.root / evaluate.FROZEN_CONFIG

    def tearDown(self):
        self.tmp.cleanup()

    def approve(self, message='authorities'):
        """The inference review approving exactly the M1 authorities now in the tree."""
        from src.evaluation import authority
        amendment = self.root / authority.AMENDMENT
        amendment.parent.mkdir(parents=True, exist_ok=True)
        amendment.write_text(json.dumps({
            'state': 'APPROVED', 'inference_approved': True,
            'approved_code': {'job_sha256': sha((self.root / authority.JOB).read_bytes())},
            'inference_approval': {'state': 'APPROVED',
                                   'm1': authority.snapshot(self.root, 'm1')}}), encoding='utf-8')
        commit(self.root, message)

    def freeze(self):
        frozen = freeze_operating_point(self.valid, self.config, self.manifest, self.root)
        self.seal(frozen)
        return frozen

    def seal(self, config: dict):
        self.frozen.write_text(json.dumps(config, indent=2) + '\n', encoding='utf-8')
        Path(str(self.frozen) + '.sha256').write_text(
            f'{sha(self.frozen.read_bytes())}  evaluation_frozen.json\n', encoding='ascii')
        commit(self.root, 'frozen')

    def provenance(self, phase='valid', predictions=None):
        return verified_provenance(predictions or self.valid, self.config if phase == 'valid'
                                   else self.frozen, self.manifest, phase, self.root)


class FreezeAndScore(Chain):
    def test_committed_config_is_readable(self):
        config = read_config(ROOT / 'configs' / 'evaluation.json')
        self.assertEqual((config['class_names'], config['positive_class']), (NAMES, 'Enfermo'))

    def test_freeze_writes_threshold_and_every_sealed_hash(self):
        from src.evaluation.evaluate import code_hashes, test_selection_digest
        frozen = self.freeze()
        self.assertEqual(frozen['threshold'], 0.35)
        self.assertNotIn('frozen_threshold', frozen)  # one canonical field (review HIGH-02)
        self.assertEqual(frozen['validation_predictions_sha256'], sha(self.valid.read_bytes()))
        self.assertEqual(frozen['manifest_sha256'], sha(self.manifest.read_bytes()))
        self.assertEqual(frozen['source_config_sha256'], sha(self.config.read_bytes()))
        self.assertEqual((frozen['checkpoint_sha256'], frozen['training_kernel_version']),
                         ('c' * 64, 1))
        self.assertEqual(frozen['selection_record_sha256'], sha(self.selection.read_bytes()))
        self.assertEqual(frozen['code_sha256'], code_hashes(self.root))
        self.assertEqual(frozen['code_sha256'], code_hashes(ROOT))  # the real sealed code
        self.assertEqual(frozen['test_selection_digest'],
                         test_selection_digest(read_manifest(self.manifest)))
        self.assertEqual(frozen['validation_provenance']['attempt']['attempt'], 1)

    def test_freeze_rejects_a_config_without_checkpoint_hash(self):
        self.config.write_text(json.dumps({**json.loads(self.config.read_text(encoding='utf-8')),
                                           'checkpoint_sha256': None}), encoding='utf-8')
        self.approve('reviewed config without checkpoint')
        with self.assertRaisesRegex(RunRejected, 'checkpoint'):
            freeze_operating_point(self.valid, self.config, self.manifest, self.root)

    def test_freeze_needs_committed_authorities_and_approved_inference(self):
        self.selection.write_text(json.dumps({'selected_sha256': 'c' * 64, 'kernel_version': 1,
                                              'note': 'x'}), encoding='utf-8')
        with self.assertRaisesRegex(RunRejected, 'committed'):
            freeze_operating_point(self.valid, self.config, self.manifest, self.root)
        git(self.root, 'checkout', '--', '.')
        from src.evaluation import evaluate
        (self.root / evaluate.AMENDMENT).write_text(json.dumps({'state': 'PROPOSED_V8'}),
                                                    encoding='utf-8')
        commit(self.root)
        with self.assertRaisesRegex(RunRejected, 'APPROVED'):
            freeze_operating_point(self.valid, self.config, self.manifest, self.root)

    def test_test_split_needs_a_frozen_config(self):
        with self.assertRaisesRegex(RunRejected, 'frozen'):
            frozen_threshold(self.config, read_config(self.config), 'test', self.manifest, self.root)

    def test_frozen_config_needs_the_frozen_manifest(self):
        self.freeze()
        config = read_config(self.frozen)
        self.manifest.write_text(self.manifest.read_text(encoding='utf-8') + '\n', encoding='utf-8')
        with self.assertRaises(RunRejected):
            frozen_threshold(self.frozen, config, 'test', self.manifest, self.root)

    def test_frozen_test_scoring_rebuilds_the_test_attempt(self):
        from src.evaluation import evaluate
        self.freeze()
        test_exp = make_attempt(self.root, 'test', self.frozen, self.manifest, TEST)
        evaluate.write_predictions(test_exp, self.frozen, self.manifest, 'test', self.root)
        config = read_config(self.frozen)
        threshold = frozen_threshold(self.frozen, config, 'test', self.manifest, self.root)
        provenance = self.provenance('test', test_exp / 'predictions.jsonl')
        self.assertEqual(provenance['experiment_id'], 'EXP-R02')
        records = load_records(test_exp / 'predictions.jsonl', 'test', read_manifest(self.manifest),
                               NAMES)
        result = score(records, config, threshold)
        self.assertEqual(result['threshold'], 0.35)
        self.assertEqual(result['counts'], {'images': 1, 'instances': 1, 'groups': 1,
                                            'instances_per_class': {'Enfermo': 1, 'Saludable': 0}})
        self.assertEqual(result['operating_metrics']['Enfermo']['recall'], 1.0)
        self.assertIsNone(result['average_precision']['map50'])  # no Saludable GT in this test


class IntervalMetrics(unittest.TestCase):
    """The hook src.statistics.intervals uses for the M1 group bootstrap."""

    def test_specs_reproduce_the_point_estimates_and_share_draws(self):
        from src.evaluation.evaluate import interval_metrics
        from src.statistics.intervals import intervals_for
        records = [dict(r, gt_classes=sorted({NAMES[g['class_id']] for g in r['gt']}))
                   for r in VALID]
        specs = interval_metrics({**CONFIG, 'threshold': 0.25})
        out = intervals_for(records, specs, seed=42, n_resamples=20)
        expected = operating_metrics(records, 0.25, NAMES)['Enfermo']['recall']
        self.assertEqual(out['metrics']['Enfermo.recall']['estimate'], expected)
        self.assertEqual(out['metrics']['map50']['estimate'],
                         average_precision(records, NAMES)['map50'])
        self.assertTrue(out['metrics']['Enfermo.recall']['blocked'])  # 1 group carries Enfermo

    def test_threshold_is_required(self):
        from src.evaluation.evaluate import interval_metrics
        with self.assertRaises(RunRejected):
            interval_metrics(CONFIG)


class ReviewRound1(Chain):
    """TASK-05 independent review: contracts between files, not formulas."""

    def test_freezer_output_feeds_the_interval_hook_unchanged(self):
        from src.evaluation.evaluate import interval_metrics
        self.freeze()
        config = read_config(self.frozen)
        self.assertEqual(config['threshold'], 0.35)
        self.assertIn('Enfermo.recall', interval_metrics(config))

    def test_a_rehashed_alternative_manifest_is_rejected(self):
        other = self.root / 'data' / 'manifests' / 'other.csv'
        other.write_text(self.manifest.read_text(encoding='utf-8') + '\n', encoding='utf-8')
        commit(self.root)
        with self.assertRaisesRegex(RunRejected, 'manifest'):
            freeze_operating_point(self.valid, self.config, other, self.root)

    def test_an_altered_frozen_inference_setting_is_rejected(self):
        for key, value in (('min_score', 0.01), ('nms_iou', 0.7), ('max_det', 100), ('imgsz', 320)):
            bad = Path(self.tmp.name) / f'bad_{key}.json'
            bad.write_text(json.dumps({**CONFIG, key: value}), encoding='utf-8')
            with self.assertRaisesRegex(RunRejected, key):
                read_config(bad)

    def test_operating_iou_is_the_ultralytics_float32_iou_at_the_boundary(self):
        import torch
        from ultralytics.utils.metrics import box_iou
        from src.evaluation.evaluate import _iou
        a, b = [0.0, 0.0, 1.0, 1.0], [1 / 3, 0.0, 4 / 3, 1.0]
        self.assertEqual(_iou(a, b), float(box_iou(torch.tensor([a]), torch.tensor([b]))[0, 0]))
        self.assertEqual(match([box(E, a)], [box(E, b, .9)], 0.5)['matches'], [])


class ReviewRound4(Chain):
    """TASK-05 rounds 3-4: consumers rebuild from the one definitive committed attempt; a
    replacement, even fully rehashed, lacks that root; the seal names committed authorities."""

    def rejects(self, pattern=None):
        with self.assertRaisesRegex(RunRejected, pattern or '.'):
            self.provenance()
        with self.assertRaises(RunRejected):
            freeze_operating_point(self.valid, self.config, self.manifest, self.root)

    def attempt(self, name):
        return self.valid_exp / 'v1' / name

    def test_the_intact_chain_passes_with_its_attempt_identity(self):
        identities = self.provenance()
        self.assertEqual(identities['attempt']['attempt'], 1)
        self.assertEqual(identities['experiment_id'], 'EXP-V01')
        self.assertEqual(identities['model_names'], {'0': 'Enfermo', '1': 'Saludable'})

    def test_synthetic_final_predictions_with_their_own_sidecar_and_provenance_are_rejected(self):
        forged = [dict(r, detections=[box(E, [0, 0, 99, 99], .99)]) for r in VALID]
        text = ''.join(json.dumps(r, sort_keys=True) + '\n' for r in forged)
        self.valid.write_text(text, encoding='utf-8', newline='\n')
        Path(str(self.valid) + '.sha256').write_text(f'{sha(text.encode())}  predictions.jsonl\n',
                                                     encoding='ascii')
        record = self.valid.with_name('prediction_provenance.json')
        record.write_text(json.dumps({**json.loads(record.read_text(encoding='utf-8')),
                                      'predictions_sha256': sha(text.encode())}), encoding='utf-8')
        self.rejects('rebuilt')

    def test_a_fully_rehashed_raw_run_without_the_committed_root_is_rejected(self):
        """The round-4 counter-example: raw detections, receipt digest and inventory changed and
        every derived file regenerated; selecting 0.05 needs the committed reconciled root."""
        from src.evaluation import evaluate
        raw = self.attempt('predictions_raw.jsonl')
        lines = [json.loads(line) for line in raw.read_text(encoding='utf-8').splitlines()]
        for item in lines:
            item['detections'] = [dict(d, score=0.06) for d in item['detections']]
        text = ''.join(json.dumps(item, sort_keys=True) + '\n' for item in lines)
        raw.write_text(text, encoding='utf-8', newline='\n')
        receipt = json.loads(self.attempt('receipt.json').read_text(encoding='utf-8'))
        receipt['predictions_raw_sha256'] = sha(text.encode())
        receipt['inventory']['predictions_raw.jsonl'] = sha(text.encode())
        self.attempt('receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
        for name in ('predictions.jsonl', 'predictions.jsonl.sha256', 'prediction_provenance.json'):
            (self.valid_exp / name).unlink()
        with self.assertRaisesRegex(RunRejected, 'reconciliation'):
            evaluate.write_predictions(self.valid_exp, self.config, self.manifest, 'valid', self.root)
        run = self.valid_exp / 'v1'
        (run / 'reconciliation.json').write_bytes(verifier.dumps(verifier.reconcile(run, 1)))
        with self.assertRaisesRegex(RunRejected, 'ledger'):
            evaluate.write_predictions(self.valid_exp, self.config, self.manifest, 'valid', self.root)
        outcome = verifier.reconcile(run, 1)
        (self.valid_exp / 'attempts.jsonl').write_bytes(verifier.dumps_line(
            verifier.ledger_entry(outcome, (run / 'reconciliation.json').read_bytes())))
        with self.assertRaisesRegex(RunRejected, 'committed'):
            evaluate.write_predictions(self.valid_exp, self.config, self.manifest, 'valid', self.root)

    def test_a_provenance_record_missing_or_altered_in_any_field_is_rejected(self):
        record = self.valid.with_name('prediction_provenance.json')
        original = json.loads(record.read_text(encoding='utf-8'))
        for key in ('agnostic_nms', 'single_cls', 'kernel_source_sha256', 'payload_sha256',
                    'predictions_raw_sha256', 'effective_suppression', 'input_contract',
                    'model_names', 'predict_args', 'attempt'):
            with self.subTest(key=key):
                record.write_text(json.dumps({k: v for k, v in original.items() if k != key}),
                                  encoding='utf-8')
                self.rejects('provenance')
        record.unlink()
        self.rejects('provenance')

    def test_each_uncommitted_change_to_the_attempt_is_rejected(self):
        cases = {'raw predictions': ('predictions_raw.jsonl', lambda t: t.replace('0.5', '0.55', 1)),
                 'receipt flags': ('receipt.json', lambda t: t.replace('"agnostic_nms": false',
                                                                       '"agnostic_nms": true')),
                 'kernel body': ('kernel.py', lambda t: t.replace('PREFIX = ', 'PREFIX  = ')),
                 'job log': ('job_log.txt', lambda t: t + 'x\n')}
        for name, (file, change) in cases.items():
            with self.subTest(case=name):
                path = self.attempt(file)
                backup = path.read_bytes()
                path.write_text(change(path.read_text(encoding='utf-8')), encoding='utf-8',
                                newline='\n')
                self.rejects()
                path.write_bytes(backup)

    def test_predictions_come_only_from_their_experiment(self):
        from src.evaluation import evaluate
        with self.assertRaisesRegex(RunRejected, 'EXP-R02'):
            evaluate.attempt_root(self.valid_exp, 'test', self.root)

    def test_a_failure_after_the_predictions_were_hashed_is_used_and_declared(self):
        """NEW-HIGH-04: definitive from predictions_written; the later failure travels along."""
        from src.evaluation import evaluate
        shutil.rmtree(self.valid_exp)
        commit(self.root, 'drop EXP-V01')
        exp = make_attempt(self.root, 'valid', self.config, self.manifest, VALID, status='FAILED',
                           stage='predictions_written',
                           receipt_change={'error': 'OSError: copying settings failed'})
        identities = evaluate.write_predictions(exp, self.config, self.manifest, 'valid', self.root)
        self.assertEqual((identities['receipt_status'], identities['receipt_error']),
                         ('FAILED', 'OSError: copying settings failed'))

    def test_a_failure_before_the_predictions_supplies_nothing(self):
        from src.evaluation import evaluate
        shutil.rmtree(self.valid_exp)
        commit(self.root, 'drop EXP-V01')
        exp = make_attempt(self.root, 'valid', self.config, self.manifest, VALID, status='FAILED',
                           stage='predict', receipt_change={'predictions_raw_sha256': None})
        with self.assertRaisesRegex(RunRejected, 'definitive'):
            evaluate.write_predictions(exp, self.config, self.manifest, 'valid', self.root)

    def test_a_version_saved_from_the_kaggle_editor_supplies_its_predictions(self):
        """DECISION-039: the run executed the rendered kernel after the editor's cell marker."""
        from src.evaluation import evaluate
        shutil.rmtree(self.valid_exp)
        commit(self.root, 'drop EXP-V01')
        exp = make_attempt(self.root, 'valid', self.config, self.manifest, VALID,
                           executed_prefix='# %% [code]\n')
        identities = evaluate.write_predictions(exp, self.config, self.manifest, 'valid', self.root)
        self.assertEqual(identities['experiment_id'], 'EXP-V01')

    def test_executed_source_is_the_rendered_text_or_its_editor_form_only(self):
        from src.evaluation import evaluate
        from src.evaluation import kaggle_job as job
        kernel = 'print(1)\n'
        for executed in (kernel, '# %% [code]\n' + kernel):
            self.assertEqual(evaluate.executed_source(kernel, job.source_sha256(executed)), executed)
        for other in ('# %% [markdown]\n' + kernel, '# %% [code]\n# %% [code]\n' + kernel,
                      'print(2)\n'):
            with self.subTest(other=other), self.assertRaisesRegex(RunRejected, 'executed source'):
                evaluate.executed_source(kernel, job.source_sha256(other))
        with self.assertRaisesRegex(RunRejected, 'executed source'):
            evaluate.executed_source(kernel, None)

    def test_sealed_config_rejects_changed_code_selection_record_or_kernel_version(self):
        from src.evaluation import evaluate
        frozen = self.freeze()
        evaluate.sealed_config(self.frozen, self.manifest, self.root)
        cases = {
            'code': {**frozen, 'code_sha256': {**frozen['code_sha256'],
                                               'src/evaluation/evaluate.py': '0' * 64}},
            'test selection': {**frozen, 'test_selection_digest': '0' * 64},
            'kernel version': {**frozen, 'training_kernel_version': 2},
            'selection record hash': {**frozen, 'selection_record_sha256': '0' * 64},
            'off-grid threshold': {**frozen, 'threshold': 0.123},
        }
        for name, config in cases.items():
            with self.subTest(case=name):
                self.seal(config)
                with self.assertRaises(RunRejected):
                    evaluate.sealed_config(self.frozen, self.manifest, self.root)
        self.seal(frozen)
        (self.root / 'src/evaluation/evaluate.py').write_text('# changed\n', encoding='utf-8')
        commit(self.root, 'other evaluator')
        with self.assertRaisesRegex(RunRejected, 'snapshot'):  # committed, but not reviewed
            evaluate.sealed_config(self.frozen, self.manifest, self.root)
        self.approve('reviewed other evaluator')
        with self.assertRaisesRegex(RunRejected, 'evaluating code'):
            evaluate.sealed_config(self.frozen, self.manifest, self.root)
        Path(str(self.frozen) + '.sha256').unlink()
        with self.assertRaisesRegex(RunRejected, 'sidecar'):
            evaluate.sealed_config(self.frozen, self.manifest, self.root)

    def test_the_freezer_binds_the_config_to_the_selection_record(self):
        self.selection.write_text(json.dumps({'selected_sha256': 'c' * 64, 'kernel_version': 2}),
                                  encoding='utf-8')
        self.approve('reviewed other selection record')
        with self.assertRaisesRegex(RunRejected, 'selection record'):
            freeze_operating_point(self.valid, self.config, self.manifest, self.root)

    def test_an_altered_verifier_outside_the_approved_snapshot_is_refused(self):
        """Round-5 HIGH-04: the reconciler is an approved authority loaded from the tree."""
        from src.evaluation import authority, evaluate
        verifier = self.root / authority.VERIFIER
        verifier.write_text(verifier.read_text(encoding='utf-8') + '\n# altered\n',
                            encoding='utf-8')
        with self.assertRaisesRegex(RunRejected, 'committed'):
            evaluate.attempt_root(self.valid_exp, 'valid', self.root)
        commit(self.root, 'altered verifier')
        with self.assertRaisesRegex(RunRejected, 'snapshot'):
            evaluate.attempt_root(self.valid_exp, 'valid', self.root)

    def test_inference_runs_only_in_the_recorded_interpreter(self):
        """Round-7: a foreign interpreter or another package set is refused."""
        from unittest import mock

        from src.evaluation import authority, evaluate
        with mock.patch.object(authority.sys, 'prefix', str(Path(self.tmp.name) / 'stubenv')):
            with self.assertRaisesRegex(RunRejected, 'inference runs only'):
                evaluate.approved_inference(self.root)
        with mock.patch.object(authority, 'environment_lines', return_value='ultralytics==0\n'):
            with self.assertRaisesRegex(RunRejected, 'installed packages'):
                evaluate.approved_inference(self.root)

    def test_a_committed_replacement_chain_after_approval_is_refused(self):
        """Round-5 NEW-HIGH-03: selection record, checkpoint, kernel version and config replaced
        and committed after the reviewed snapshot; the freezer refuses before any selection."""
        self.selection.write_text(json.dumps({'selected_sha256': 'd' * 64, 'kernel_version': 9}),
                                  encoding='utf-8')
        self.config.write_text(json.dumps({
            **json.loads(self.config.read_text(encoding='utf-8')), 'checkpoint_sha256': 'd' * 64,
            'selection_record_sha256': sha(self.selection.read_bytes()),
            'training_kernel_version': 9}), encoding='utf-8')
        commit(self.root, 'replacement chain')
        with self.assertRaisesRegex(RunRejected, 'snapshot'):
            freeze_operating_point(self.valid, self.config, self.manifest, self.root)

    def test_fixed_config_values_are_enforced(self):
        for key, value in (('iou_match', 0.4), ('positive_class', 'Saludable'),
                           ('class_names', ['Saludable', 'Enfermo']), ('model_id', 'other')):
            bad = Path(self.tmp.name) / f'bad_{key}.json'
            bad.write_text(json.dumps({**CONFIG, key: value}), encoding='utf-8')
            with self.subTest(key=key), self.assertRaisesRegex(RunRejected, key):
                read_config(bad)


class FrozenCommands(Chain):
    """TASK-05 round-4 NEW-MEDIUM-02: the literal plan commands (lines 284-288) run end to end
    against the synthetic committed repository."""

    def test_the_m1_commands_run_in_order(self):
        from src.evaluation import evaluate
        exp_v01 = self.root / 'experiments' / 'model1' / 'EXP-V01'
        done = run_frozen(self.root, '--model-id', 'model1', '--config', self.config,
                          '--split', 'val', '--run-dir', exp_v01)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertTrue((exp_v01 / 'metrics.json').is_file())
        commit(self.root, 'EXP-V01 metrics')
        done = run_frozen(self.root, '--freeze-operating-point', '--predictions',
                          exp_v01 / 'predictions.jsonl', '--config', self.config, '--out', self.frozen)
        self.assertEqual(done.returncode, 0, done.stderr)
        commit(self.root, 'frozen')
        exp_r02 = make_attempt(self.root, 'test', self.frozen, self.manifest, TEST)
        done = run_frozen(self.root, '--model-id', 'model1', '--config', self.frozen,
                          '--split', 'test', '--run-dir', exp_r02)
        self.assertEqual(done.returncode, 0, done.stderr)
        metrics = json.loads((exp_r02 / 'metrics.json').read_text(encoding='utf-8'))
        self.assertEqual(metrics['threshold'], 0.35)
        self.assertEqual(metrics['prediction_provenance']['experiment_id'], 'EXP-R02')
        done = run_frozen(self.root, '--model-id', 'model1', '--config', self.frozen,
                          '--split', 'test', '--run-dir', exp_r02)
        self.assertEqual(done.returncode, 2)  # never overwrites
        self.assertIn('never overwritten', done.stderr)
        self.assertEqual(evaluate.FROZEN_CONFIG, 'configs/evaluation_frozen.json')
        commit(self.root, 'EXP-R02 metrics')
        driver = (runtime_stub.DRIVER + 'import sys; from pathlib import Path; '
                  'import src.evaluation.evaluate as e; from src.statistics import intervals; '
                  f'e.REPO = Path({str(self.root)!r}); '
                  f'sys.exit(intervals.main(sys.argv[1:], root=Path({str(self.root)!r})))')
        done = subprocess.run([sys.executable, '-c', driver, '--predictions',
                               str(exp_r02 / 'predictions.jsonl'), '--groups', str(self.manifest),
                               '--seed', '42', '--resamples', '20', '--out',
                               'artifacts/metrics/model1_intervals.json'],
                              cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        intervals = json.loads((self.root / 'artifacts/metrics/model1_intervals.json')
                               .read_text(encoding='utf-8'))
        self.assertIn('Enfermo.recall', intervals['metrics'])

    def test_the_m2_command_runs_exp_r03_with_the_canonical_inputs(self):
        from unittest import mock

        from src.evaluation import evaluate, predict_model2
        run_dir = self.root / 'experiments' / 'model2' / 'EXP-R03'
        with mock.patch.object(predict_model2, 'run', return_value={'images': 219}) as run:
            evaluate.main(['--model-id', 'model2', '--config', str(self.frozen), '--split', 'test',
                           '--run-dir', str(run_dir)])
        manifest, weights, target = run.call_args.args
        self.assertEqual(manifest, evaluate.REPO / predict_model2.M2_MANIFEST)
        self.assertEqual(weights.as_posix().rsplit('/', 3)[-3:],
                         predict_model2.ART002_PATH.split('/'))
        self.assertEqual((target, run.call_args.kwargs['config']), (run_dir, self.frozen))

    def test_an_m2_refusal_through_the_literal_wrapper_exits_2(self):
        """Round-7 NEW-LOW-01: the producer refuses (no approval yet, or a config outside the
        real checkout); the literal command stops with exit 2 and a message, no traceback,
        model call or run directory."""
        run_dir = self.root / 'experiments' / 'model2' / 'EXP-R03'
        done = run_frozen(self.root, '--model-id', 'model2', '--config', self.frozen,
                          '--split', 'test', '--run-dir', run_dir)
        self.assertEqual(done.returncode, 2, done.stderr)
        self.assertIn('REJECTED', done.stderr)
        self.assertNotIn('Traceback', done.stderr)
        self.assertFalse(run_dir.exists())


if __name__ == '__main__':
    unittest.main()
