"""TASK-05 part 2: Wilson, M2 duplicate sensitivity and the paired group bootstrap.

Fixtures are the verbatim ones of the frozen plan. No model is loaded.
"""

import csv
import hashlib
import io
import json
import shutil
import subprocess
import sys
import unittest
from contextlib import nullcontext, redirect_stderr
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from src.statistics.intervals import (
    ResamplingBlocked, bootstrap_groups, delta, draw_groups, draws_sha256, intervals_for,
    m2_bootstrap, m2_sensitivity, main, paired_delta, resample, scheme_weights, wilson,
)

from tests import runtime_stub

A, B = 'A', 'B'
CLASSES = [A, B]
REPO = Path(__file__).resolve().parents[1]


def setUpModule():
    runtime_stub.start()


def tearDownModule():
    runtime_stub.stop()


def row(image_id, sha, cluster, truth, pred, group=None):
    return {'image_id': image_id, 'sha256': sha, 'cluster_id': cluster,
            'group_id': group or cluster, 'truth': truth, 'pred': pred}


def fixture():
    """Plan RED M2: a1,a2 share a SHA; cluster(a1,a2,a3)=c1, cluster(b1)=c2."""
    return [row('a1', 'sha-a', 'c1', A, B), row('a2', 'sha-a', 'c1', A, B),
            row('a3', 'sha-a3', 'c1', A, A), row('b1', 'sha-b', 'c2', B, B)]


def grouped():
    """g1 holds two clusters (c1, c2); A has support in 2 groups, B in 3."""
    return [row('a1', 'sha-a', 'c1', A, B, 'g1'), row('a2', 'sha-a', 'c1', A, B, 'g1'),
            row('a3', 'sha-a3', 'c1', A, A, 'g1'), row('b1', 'sha-b', 'c2', B, B, 'g1'),
            row('x1', 'sha-x', 'c3', B, A, 'g2'), row('y1', 'sha-y', 'c4', A, A, 'g3'),
            row('z1', 'sha-z', 'c5', B, B, 'g4')]


def estimand(result, scheme):
    return result['estimands'][scheme]['metrics']


def accuracy_of(scheme):
    return lambda rows: m2_sensitivity(rows, CLASSES)['estimands'][scheme]['metrics']['accuracy']


class Wilson(unittest.TestCase):
    def test_plan_fixture(self):
        lo, hi = wilson(0, 10)
        self.assertLess(abs(lo), 1e-12)
        self.assertTrue(.277 < hi < .278, hi)

    def test_undefined_or_impossible_proportions_raise(self):
        for k, n in ((0, 0), (0, -1), (-1, 10), (11, 10)):
            with self.subTest(k=k, n=n), self.assertRaises(ValueError):
                wilson(k, n)


class Sensitivity(unittest.TestCase):
    """Plan RED M2, two classes in a function fixture (production uses the five fixed)."""

    def test_plan_accuracies_weights_and_deltas(self):
        result = m2_sensitivity(fixture(), CLASSES)
        self.assertAlmostEqual(estimand(result, 'image_weighted')['accuracy'], 1 / 2, places=12)
        self.assertAlmostEqual(estimand(result, 'exact_sha_dedup')['accuracy'], 2 / 3, places=12)
        self.assertAlmostEqual(estimand(result, 'cluster_weighted')['accuracy'], 2 / 3, places=12)
        weights = scheme_weights(fixture(), 'cluster_weighted')
        for got, want in zip(weights, (1 / 3, 1 / 3, 1 / 3, 1)):
            self.assertAlmostEqual(got, want, places=12)
        self.assertEqual(scheme_weights(fixture(), 'exact_sha_dedup'), [1.0, 0.0, 1.0, 1.0])
        for scheme in ('exact_sha_dedup', 'cluster_weighted'):
            change = result['deltas'][scheme]['accuracy']
            self.assertAlmostEqual(change['units'], 1 / 6, places=12)
            self.assertAlmostEqual(change['percentage_points'], 100 / 6, places=10)

    def test_plan_macro_f1(self):
        result = m2_sensitivity(fixture(), CLASSES)
        self.assertAlmostEqual(estimand(result, 'image_weighted')['macro_f1'], 1 / 2, places=12)
        self.assertAlmostEqual(estimand(result, 'exact_sha_dedup')['macro_f1'], 2 / 3, places=12)
        self.assertAlmostEqual(estimand(result, 'cluster_weighted')['macro_f1'], 5 / 8, places=12)
        cluster = estimand(result, 'cluster_weighted')['per_class']
        self.assertAlmostEqual(cluster[A]['f1'], 1 / 2, places=12)
        self.assertAlmostEqual(cluster[B]['f1'], 3 / 4, places=12)
        self.assertAlmostEqual(result['deltas']['cluster_weighted']['macro_f1']['units'], 1 / 8,
                               places=12)
        confusion = result['estimands']['cluster_weighted']['confusion']
        self.assertAlmostEqual(confusion[0][0], 1 / 3, places=12)
        self.assertAlmostEqual(confusion[0][1], 2 / 3, places=12)
        self.assertEqual(confusion[1], [0.0, 1.0])

    def test_order_invariance(self):
        records = fixture()
        expected = m2_sensitivity(records, CLASSES)
        for order in (records[::-1], [records[2], records[0], records[3], records[1]]):
            self.assertEqual(m2_sensitivity(order, CLASSES), expected)

    def test_exact_dedup_keeps_the_lexicographic_minimum_image_id(self):
        """'img10' < 'img9' as strings; the copies disagree only in prediction."""
        records = [row('img9', 'sha-s', 'c1', A, A), row('img10', 'sha-s', 'c1', A, B),
                   row('b1', 'sha-b', 'c2', B, B)]
        for order in (records, records[::-1]):
            weights = dict(zip((r['image_id'] for r in order),
                               scheme_weights(order, 'exact_sha_dedup')))
            self.assertEqual(weights, {'img9': 0.0, 'img10': 1.0, 'b1': 1.0})
            result = m2_sensitivity(order, CLASSES)
            self.assertAlmostEqual(estimand(result, 'exact_sha_dedup')['accuracy'], 1 / 2)
            self.assertEqual([c['sha256'] for c in result['sha_prediction_conflicts']], ['sha-s'])

    def test_sha_with_inconsistent_gt_blocks_only_that_sensitivity(self):
        records = fixture()
        records[1]['truth'] = B  # a2 shares a1's bytes but not its label
        result = m2_sensitivity(records, CLASSES)
        blocked = result['estimands']['exact_sha_dedup']
        self.assertTrue(blocked['blocked'])
        self.assertIn('sha-a', blocked['reason'])
        self.assertIsNone(blocked['metrics'])
        self.assertIsNone(result['deltas']['exact_sha_dedup']['accuracy']['units'])
        self.assertIn('sha-a', result['deltas']['exact_sha_dedup']['accuracy']['reason'])
        self.assertFalse(result['estimands']['cluster_weighted']['blocked'])
        self.assertIsNotNone(estimand(result, 'image_weighted')['accuracy'])

    def test_id_coverage_is_enforced(self):
        cases = {'missing cluster': [{**fixture()[0], 'cluster_id': ''}] + fixture()[1:],
                 'missing key': [{k: v for k, v in fixture()[0].items() if k != 'sha256'}],
                 'repeated id': fixture() + [fixture()[0]],
                 'foreign class': fixture() + [row('c9', 'sha-c', 'c9', 'C', A)]}
        for name, records in cases.items():
            with self.subTest(name), self.assertRaises(ValueError):
                m2_sensitivity(records, CLASSES)

    def test_absent_gt_class_leaves_its_f1_and_macro_f1_undefined(self):
        result = m2_sensitivity(fixture(), [A, B, 'C'])
        metrics = estimand(result, 'image_weighted')
        self.assertIsNone(metrics['per_class']['C']['f1'])
        self.assertIsNone(metrics['per_class']['C']['recall'])
        self.assertIsNone(metrics['macro_f1'])
        self.assertIn('C', metrics['undefined']['macro_f1'])
        self.assertIn('f1[C]', metrics['undefined'])

    def test_precision_without_predictions_is_undefined_but_f1_is_zero(self):
        records = [row('a1', 'sha-a', 'c1', A, A), row('b1', 'sha-b', 'c2', B, A)]
        metrics = estimand(m2_sensitivity(records, CLASSES), 'image_weighted')
        self.assertIsNone(metrics['per_class'][B]['precision'])
        self.assertIn('precision[B]', metrics['undefined'])
        self.assertEqual(metrics['per_class'][B]['recall'], 0.0)
        self.assertEqual(metrics['per_class'][B]['f1'], 0.0)
        self.assertAlmostEqual(metrics['macro_f1'], (2 / 3 + 0) / 2, places=12)

    def test_structure_counts_match_the_task02_fixture(self):
        structure = m2_sensitivity(fixture(), CLASSES)['structure']
        self.assertEqual((structure['n_images'], structure['n_unique_sha'],
                          structure['n_clusters']), (4, 3, 2))
        self.assertEqual(structure['cluster_size_distribution'], {1: 1, 3: 1})


class Bootstrap(unittest.TestCase):
    """Plan RED bootstrap pareado."""

    @classmethod
    def setUpClass(cls):
        cls.shared = m2_bootstrap(grouped(), CLASSES, seed=42, n_resamples=2000)

    def test_a_group_with_two_clusters_is_resampled_together(self):
        drawn = resample(grouped(), ['g1'])
        self.assertEqual(sorted(r['image_id'] for r in drawn), ['a1', 'a2', 'a3', 'b1'])
        self.assertEqual({r['occurrence_id'] for r in drawn}, {0})
        sizes = {'g1': 4, 'g2': 1, 'g3': 1, 'g4': 1}
        for draw in self.shared['draws'][:50]:
            self.assertEqual(len(resample(grouped(), draw)), sum(sizes[g] for g in draw))

    def test_two_occurrences_keep_two_cluster_masses_and_two_sha_representatives(self):
        drawn = resample(grouped(), ['g1', 'g1'])
        self.assertEqual(len(drawn), 8)
        self.assertEqual({r['occurrence_id'] for r in drawn}, {0, 1})
        kept = sorted(r['image_id'] for r, w in
                      zip(drawn, scheme_weights(drawn, 'exact_sha_dedup')) if w)
        self.assertEqual(kept, ['a1', 'a1', 'a3', 'a3', 'b1', 'b1'])
        cluster = scheme_weights(drawn, 'cluster_weighted')
        self.assertAlmostEqual(sum(cluster), 4.0, places=12)  # c1 and c2, twice each
        self.assertAlmostEqual(cluster[0], 1 / 3, places=12)

    def test_draws_are_reproducible_and_hashed(self):
        draws = draw_groups(['g2', 'g1', 'g3', 'g4', 'g1'], 42, 2000)
        self.assertEqual(draws, draw_groups(['g1', 'g2', 'g3', 'g4'], 42, 2000))
        self.assertEqual((len(draws), {len(d) for d in draws}), (2000, {4}))
        result = bootstrap_groups(grouped(), accuracy_of('image_weighted'), 42, 2000)
        self.assertEqual(result['draws'], draws)
        canonical = json.dumps(draws, separators=(',', ':')).encode('utf-8')
        self.assertEqual(result['draws_sha256'], hashlib.sha256(canonical).hexdigest())
        self.assertNotEqual(draws_sha256(draws[:-1] + [['g1'] * 4]), result['draws_sha256'])

    def test_all_three_schemes_and_deltas_share_the_same_draws(self):
        shared = self.shared
        expected = draws_sha256(draw_groups(['g1', 'g2', 'g3', 'g4'], 42, 2000))
        self.assertEqual((shared['seed'], shared['n_resamples']), (42, 2000))
        self.assertEqual(shared['draws_sha256'], expected)
        summaries = [s for table in ('intervals', 'delta_intervals')
                     for per_scheme in shared[table].values() for s in per_scheme.values()]
        self.assertEqual({s['draws_sha256'] for s in summaries}, {expected})
        self.assertEqual(set(shared['intervals']), {'image_weighted', 'exact_sha_dedup',
                                                    'cluster_weighted'})
        self.assertEqual(set(shared['delta_intervals']), {'exact_sha_dedup', 'cluster_weighted'})
        keys = ('estimate', 'ci95', 'n_defined', 'undefined_count', 'blocked')
        alone = bootstrap_groups(grouped(), accuracy_of('cluster_weighted'),
                                 required_classes=CLASSES, class_key='truth',
                                 draws=shared['draws'])
        self.assertEqual({k: alone[k] for k in keys},
                         {k: shared['intervals']['cluster_weighted']['accuracy'][k] for k in keys})
        paired = bootstrap_groups(grouped(), paired_delta(accuracy_of('cluster_weighted'),
                                                          accuracy_of('image_weighted')),
                                  required_classes=CLASSES, class_key='truth',
                                  draws=shared['draws'])
        self.assertEqual({k: paired[k] for k in keys},
                         {k: shared['delta_intervals']['cluster_weighted']['accuracy'][k]
                          for k in keys})

    def test_draws_with_an_absent_class_are_counted_undefined_not_zero(self):
        support = {'g1': {A, B}, 'g2': {B}, 'g3': {A}, 'g4': {B}}
        expected = sum(1 for d in self.shared['draws']
                       if not {A, B} <= set().union(*(support[g] for g in d)))
        summary = self.shared['intervals']['image_weighted']['macro_f1']
        self.assertGreater(expected, 0)
        self.assertEqual(summary['undefined_count'], expected)
        self.assertEqual(summary['n_defined'] + expected, 2000)

    def test_a_sha_or_cluster_in_two_groups_fails(self):
        for field, value in (('sha256', 'sha-a'), ('cluster_id', 'c1')):
            records = grouped()
            records[4][field] = value  # x1 lives in g2
            with self.subTest(field), self.assertRaisesRegex(ResamplingBlocked, value):
                bootstrap_groups(records, lambda rows: 1.0, n_resamples=5)
            with self.subTest(field), self.assertRaises(ResamplingBlocked):
                m2_bootstrap(records, CLASSES, n_resamples=5)

    def simple(self, truths):
        return [{'image_id': f'i{n}', 'group_id': f'g{n}', 'truth': t}
                for n, t in enumerate(truths, 1)]

    @staticmethod
    def share_of_a(rows):
        truths = [r['truth'] for r in rows]
        return truths.count(A) / len(truths) if B in truths else None

    def test_more_than_five_percent_undefined_blocks_and_exactly_five_allows(self):
        records = self.simple([A, A, B, B])
        full, no_b = ['g1', 'g2', 'g3', 'g4'], ['g1', 'g1', 'g1', 'g1']
        allowed = bootstrap_groups(records, self.share_of_a, required_classes=CLASSES,
                                   class_key='truth', draws=[full] * 1900 + [no_b] * 100)
        self.assertFalse(allowed['blocked'], allowed['reason'])
        self.assertEqual((allowed['n_defined'], allowed['undefined_count']), (1900, 100))
        self.assertEqual(allowed['undefined_fraction'], .05)
        self.assertEqual(allowed['ci95'], [.5, .5])
        blocked = bootstrap_groups(records, self.share_of_a, required_classes=CLASSES,
                                   class_key='truth', draws=[full] * 1899 + [no_b] * 101)
        self.assertTrue(blocked['blocked'])
        self.assertIn('5%', blocked['reason'])
        self.assertIsNone(blocked['ci95'])
        self.assertEqual(blocked['estimate'], .5)  # the point estimate is still published

    def test_fewer_than_two_groups_blocks(self):
        one_b = bootstrap_groups(self.simple([A, A, A, B]), lambda rows: 1.0, n_resamples=50,
                                 required_classes=CLASSES, class_key='truth')
        self.assertTrue(one_b['blocked'])
        self.assertEqual(one_b['class_group_counts'], {A: 3, B: 1})
        self.assertIn('B', one_b['reason'])
        single = bootstrap_groups(self.simple([A]), lambda rows: 1.0, n_resamples=50)
        self.assertTrue(single['blocked'])
        self.assertIsNone(single['ci95'])

    def test_a_delta_is_undefined_when_either_metric_is(self):
        self.assertIsNone(delta(None, .5))
        self.assertIsNone(delta(.5, None))
        self.assertAlmostEqual(delta(.7, .5), .2)
        records = self.simple([A, A, B, B])
        draws = ([['g2', 'g2', 'g3', 'g4']] * 3 + [['g1', 'g2', 'g3', 'g3']] * 2
                 + [['g2', 'g2', 'g3', 'g3']] + [['g1', 'g2', 'g3', 'g4']] * 4)

        def needs(group):
            return lambda rows: 1.0 if any(r['group_id'] == group for r in rows) else None

        result = bootstrap_groups(records, paired_delta(needs('g1'), needs('g4')), draws=draws)
        self.assertEqual(result['undefined_count'], 6)  # 4 without g1, 3 without g4, 1 both

    def test_intervals_for_shares_one_set_of_draws(self):
        result = intervals_for(grouped(), {
            'accuracy': accuracy_of('image_weighted'),
            'cluster_accuracy': {'metric': accuracy_of('cluster_weighted'),
                                 'required_classes': CLASSES, 'class_key': 'truth'}},
            seed=42, n_resamples=100)
        self.assertEqual(result['draws_sha256'],
                         draws_sha256(draw_groups(['g1', 'g2', 'g3', 'g4'], 42, 100)))
        self.assertEqual(set(result['metrics']), {'accuracy', 'cluster_accuracy'})
        self.assertNotIn('draws', result['metrics']['accuracy'])


class Cli(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / 'provenance').mkdir()
        shutil.copyfile(REPO / 'provenance' / 'protocol_freeze.json',
                        self.root / 'provenance' / 'protocol_freeze.json')
        self.manifest = self.root / 'data' / 'manifests' / 'model2.csv'
        self.manifest.parent.mkdir(parents=True)
        self.write_manifest(grouped() + [row('t1', 'sha-t', 'c9', A, A, 'g9')],
                            splits=['test'] * 7 + ['train'])
        self.predictions = self.root / 'experiments' / 'model2' / 'predictions.jsonl'
        self.predictions.parent.mkdir(parents=True)
        for name in ('src/evaluation/predict_model2.py', 'src/statistics/intervals.py',
                     'src/evaluation/authority.py',
                     'provenance/environment/inference_environment.txt',
                     'provenance/environment/inference_runtime.txt',
                     'provenance/environment/inference_interpreter.json'):
            (self.root / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / name, self.root / name)
        self.config = self.root / 'configs' / 'evaluation_frozen.json'
        self.config.parent.mkdir(parents=True)
        self.config.write_text('{"threshold": 0.35}\n', encoding='utf-8')
        self.git('init', '-q')

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args):
        subprocess.run(['git', '-c', 'user.email=t@t', '-c', 'user.name=t', *args],
                       cwd=self.root, check=True, capture_output=True)

    def approve(self, contract):
        """The amendment approving the current M2 snapshot, committed with everything else."""
        from src.evaluation import authority, predict_model2
        self.git('add', '-A')
        self.git('commit', '-qm', 'bundle', '--allow-empty')
        with mock.patch.dict(predict_model2.M2_CONTRACT, contract):
            snapshot = authority.snapshot(self.root, 'm2')
        amendment = self.root / authority.AMENDMENT
        amendment.parent.mkdir(parents=True, exist_ok=True)
        amendment.write_text(json.dumps({'state': 'APPROVED', 'inference_approved': True,
                                         'inference_approval': {'state': 'APPROVED',
                                                                'm2': snapshot}}),
                             encoding='utf-8')
        self.git('add', '-A')
        self.git('commit', '-qm', 'approve', '--allow-empty')

    def write_manifest(self, records, splits):
        with self.manifest.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(['image_id', 'sha256', 'cluster_id', 'group_id', 'split',
                             'class_name'])
            for record, split in zip(records, splits):
                writer.writerow([record['image_id'], record['sha256'], record['cluster_id'],
                                 record['group_id'], split, record['truth']])
        digest = hashlib.sha256(self.manifest.read_bytes()).hexdigest()
        self.manifest.with_name('model2.csv.sha256').write_text(f'{digest}  model2.csv\n',
                                                                encoding='ascii')

    def contract(self):
        from src.evaluation.predict_model2 import ART002_SHA256
        return {'experiment_id': 'EXP-R03', 'manifest': 'data/manifests/model2.csv',
                'manifest_sha256': hashlib.sha256(self.manifest.read_bytes()).hexdigest(),
                'weights_sha256': ART002_SHA256, 'predictions': 'experiments/model2/predictions.jsonl',
                'imgsz': 224, 'rule': 'top-1 without rejection',
                'input_contract': 'Ultralytics file-path loader', 'class_names': ['A', 'B'],
                'ultralytics': '8.4.52', 'config': 'configs/evaluation_frozen.json',
                'dependencies_outside_checkout': True,
                'environment': 'provenance/environment/inference_environment.txt'}

    def run_cli(self, records, *extra, names=('A', 'B'), run_record=True, flag=True,
                out='artifacts/metrics/model2_sensitivity.json', record_change=None,
                manifest=None, override=None, approve=True, after_approval=None,
                real_freeze=False):
        """real_freeze=False stands in for a sealed M1 freeze, which this synthetic root lacks;
        test_the_config_must_be_the_m1_freeze runs the real validator."""
        self.predictions.write_text(''.join(
            json.dumps({'image_id': r['image_id'], 'split': 'test', 'sha256': r['sha256'],
                        'truth': r['truth'], 'pred': r['pred'],
                        'probs': {n: (0.9 if n == r['pred'] else 0.1) for n in ('A', 'B')},
                        **({'class_names': list(names)} if names else {}),
                        **(override or {}).get(r['image_id'], {})}) + '\n'
            for r in records), encoding='utf-8')
        digest = hashlib.sha256(self.predictions.read_bytes()).hexdigest()
        self.predictions.with_name('predictions.jsonl.sha256').write_text(
            f'{digest}  predictions.jsonl\n', encoding='ascii')
        contract = self.contract()
        record = self.predictions.with_name('run_record.json')
        record.unlink(missing_ok=True)
        if run_record:
            record.write_text(json.dumps({
                **{k: contract[k] for k in ('experiment_id', 'weights_sha256', 'manifest_sha256',
                                            'imgsz', 'rule', 'input_contract')},
                'model_names': {'0': 'A', '1': 'B'}, 'images': len(records),
                'predictions_sha256': digest,
                'producer_sha256': hashlib.sha256(
                    (self.root / 'src/evaluation/predict_model2.py').read_bytes()).hexdigest(),
                'ultralytics': '8.4.52', 'config': 'configs/evaluation_frozen.json',
                'config_sha256': hashlib.sha256(self.config.read_bytes()).hexdigest(),
                'dependencies_outside_checkout': True,
                'environment': 'provenance/environment/inference_environment.txt',
                'environment_sha256': hashlib.sha256((
                    self.root / 'provenance/environment/inference_environment.txt').read_bytes()
                ).hexdigest(),
                'runtime_sha256': runtime_stub.STUB,
                'runtime_modules': {'torch': 'Lib/site-packages/torch/__init__.py',
                                    'ultralytics': 'Lib/site-packages/ultralytics/__init__.py'},
                **(record_change or {})}), encoding='utf-8')
        from src.evaluation import evaluate, predict_model2
        if approve:
            self.approve(contract)
        if after_approval:
            after_approval()
        stderr = io.StringIO()
        freeze = nullcontext() if real_freeze else \
            mock.patch.object(evaluate, 'sealed_config', return_value={})
        with redirect_stderr(stderr), mock.patch.dict(predict_model2.M2_CONTRACT, contract), \
                freeze:
            code = main([*(['--m2-sensitivity'] if flag else []),
                         '--predictions', str(self.predictions),
                         '--groups', str(manifest or self.manifest), '--seed', '42',
                         '--resamples', '40', '--out', out, *extra], root=self.root)
        return code, stderr.getvalue()

    def test_m2_mode_writes_every_sibling_output(self):
        code, err = self.run_cli(grouped())
        self.assertEqual(code, 0, err)
        metrics = self.root / 'artifacts' / 'metrics'
        for name in ('model2_sensitivity.json', 'model2_sensitivity.csv',
                     'model2_sensitivity_confusions.json', 'model2_bootstrap_draws.json'):
            self.assertTrue((metrics / name).is_file(), name)
        self.assertTrue((self.root / 'reports' / 'model2_duplicate_sensitivity.md').is_file())
        draws = json.loads((metrics / 'model2_bootstrap_draws.json').read_text(encoding='utf-8'))
        self.assertEqual(draws_sha256(draws['draws']), draws['draws_sha256'])
        self.assertEqual(len(draws['draws']), 40)
        result = json.loads((metrics / 'model2_sensitivity.json').read_text(encoding='utf-8'))
        self.assertEqual(result['bootstrap']['draws_sha256'], draws['draws_sha256'])
        expected = m2_sensitivity(grouped(), CLASSES)
        self.assertEqual(result['estimands']['cluster_weighted']['metrics']['accuracy'],
                         estimand(expected, 'cluster_weighted')['accuracy'])
        code, err = self.run_cli(grouped())
        self.assertEqual(code, 2)  # never overwrites a published result
        self.assertIn('exists', err)

    def test_equal_hash_copies_with_different_ids_are_not_interchangeable(self):
        """SRC-1 and SRC-2 are byte copies; neither may stand in for the other."""
        copies = [row('SRC-1', 'sha-x', 'c1', A, A, 'g1'), row('SRC-2', 'sha-x', 'c1', A, A, 'g1'),
                  row('SRC-3', 'sha-y', 'c2', B, B, 'g2')]
        self.write_manifest(copies, ['test'] * 3)
        foreign = row('SRC-4', 'sha-x', 'c1', A, A, 'g1')
        cases = {'repeated': [copies[0], copies[0], copies[2]],
                 'missing': [copies[0], copies[2]],
                 'foreign': copies + [foreign]}
        for label, records in cases.items():
            with self.subTest(label):
                code, err = self.run_cli(records)
                self.assertEqual(code, 2)
                self.assertIn(label, err)

    def test_invalid_input_exits_2_with_a_message(self):
        code, err = self.run_cli(grouped(), names=None)  # no class names anywhere
        self.assertEqual((code, 'class names' in err), (2, True), err)
        self.manifest.write_text('image_id,sha256\nSRC-1,x\n', encoding='utf-8')
        code, err = self.run_cli(grouped())
        self.assertEqual((code, 'cluster_id' in err), (2, True))

    def test_m2_needs_the_exp_r03_run_record_and_the_manifest_truth(self):
        code, err = self.run_cli(grouped(), run_record=False)
        self.assertEqual((code, 'run_record' in err or 'run record' in err), (2, True), err)
        flipped = [dict(r, truth=B if r['truth'] == A else A) if i == 0 else r
                   for i, r in enumerate(grouped())]
        code, err = self.run_cli(flipped)
        self.assertEqual((code, 'class_name' in err), (2, True), err)

    def test_the_frozen_primary_m2_command_runs_the_m2_path(self):
        """Round-3 NEW-MEDIUM-01: the plan's command has no flag; the manifest selects M2."""
        code, err = self.run_cli(grouped(), flag=False, out='artifacts/metrics/model2_intervals.json')
        self.assertEqual(code, 0, err)
        result = json.loads((self.root / 'artifacts' / 'metrics' / 'model2_intervals.json')
                            .read_text(encoding='utf-8'))
        expected = m2_sensitivity(grouped(), CLASSES)
        self.assertEqual(result['estimand'], 'image_weighted')
        self.assertEqual(result['point']['accuracy'],
                         estimand(expected, 'image_weighted')['accuracy'])
        self.assertIn('accuracy', result['intervals'])

    def test_a_noncanonical_m2_manifest_or_run_record_is_rejected(self):
        """Round-3 MEDIUM-01: the ALT-G counter-example and weakened run-record fields."""
        alternative = self.root / 'data' / 'manifests' / 'alt.csv'
        alternative.write_bytes(self.manifest.read_bytes().replace(b'g1', b'ALT-G'))
        digest = hashlib.sha256(alternative.read_bytes()).hexdigest()
        alternative.with_name('alt.csv.sha256').write_text(f'{digest}  alt.csv\n', encoding='ascii')
        code, err = self.run_cli(grouped(), manifest=alternative)
        self.assertEqual(code, 2, err)
        for change in ({'experiment_id': 'OTHER'}, {'imgsz': 320}, {'rule': 'top-2'},
                       {'input_contract': 'cv2'}, {'model_names': {'0': 'A', '1': 'C'}},
                       {'images': 1}):
            with self.subTest(change=change):
                code, err = self.run_cli(grouped(), record_change=change)
                self.assertEqual(code, 2, err)

    def test_a_prediction_that_does_not_follow_its_probabilities_is_rejected(self):
        first = grouped()[0]
        wrong = B if first['pred'] == A else A
        code, err = self.run_cli(grouped(), override={first['image_id']: {'pred': wrong}})
        self.assertEqual(code, 2, err)
        self.assertIn('rule', err)
        from src.statistics.intervals import m2_pred
        self.assertEqual(m2_pred({'A': 0.5, 'B': 0.5}, ['A', 'B']), 'A')  # tie: first index
        self.assertEqual(m2_pred({'A': 0.4, 'B': 0.6}, ['A', 'B']), 'B')

    def test_exp_r03_needs_its_committed_bundle_approved_producer_and_snapshot(self):
        """Round-5 NEW-HIGH-05: a self-authored bundle outside the committed root fails."""
        def dirty():
            self.predictions.write_text(self.predictions.read_text(encoding='utf-8') + '\n',
                                        encoding='utf-8')
        code, err = self.run_cli(grouped(), after_approval=dirty)
        self.assertEqual((code, 'committed' in err), (2, True), err)
        code, err = self.run_cli(grouped(), record_change={'producer_sha256': '0' * 64})
        self.assertEqual((code, 'producer_sha256' in err), (2, True), err)

        def other_producer():
            (self.root / 'src/evaluation/predict_model2.py').write_text('# other\n',
                                                                         encoding='utf-8')
            self.git('commit', '-qam', 'other producer')
        code, err = self.run_cli(grouped(), after_approval=other_producer)
        self.assertEqual((code, 'snapshot' in err), (2, True), err)
        code, err = self.run_cli(grouped(), approve=False)
        self.assertEqual(code, 2, err)
        for change in ({'ultralytics': '8.4.52-shadow'}, {'config_sha256': '0' * 64},
                       {'dependencies_outside_checkout': False},
                       {'environment_sha256': '0' * 64}, {'runtime_sha256': '0' * 64},
                       {'runtime_modules': {'ultralytics': 'x'}}):
            with self.subTest(change=change):
                code, err = self.run_cli(grouped(), record_change=change)
                self.assertEqual(code, 2, err)

    def test_the_config_must_be_the_m1_freeze(self):
        """Round-7 NEW-HIGH-05: a committed file at the canonical path is not enough."""
        code, err = self.run_cli(grouped(), real_freeze=True)
        self.assertEqual((code, 'frozen M1 operating point' in err), (2, True), err)

    def test_every_record_must_carry_the_same_class_names(self):
        from src.statistics.intervals import _class_names
        with self.assertRaises(ValueError):
            _class_names(None, [{'class_names': ['A', 'B']}, {}])
        with self.assertRaises(ValueError):
            _class_names(None, [{'class_names': ['A', 'B']}, {'class_names': ['B', 'A']}])

class WilsonContract(unittest.TestCase):
    def test_non_integer_counts_and_bad_z_are_rejected(self):
        from src.statistics.intervals import wilson
        for args in ((1.5, 10), (True, 10), (1, 10.0), (1, 10, 0.0), (1, 10, float('inf'))):
            with self.assertRaises(ValueError):
                wilson(*args)


if __name__ == '__main__':
    unittest.main()
