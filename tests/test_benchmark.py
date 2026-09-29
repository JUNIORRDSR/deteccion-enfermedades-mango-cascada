"""TASK-06 contracts with a simulated clock and fake stages: no model is loaded."""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from src.benchmarks.run import (
    WALL, RunRejected, iteration, measure, read_config, rows_for, run_image, select_pool,
    summarize, synced_clock,
)

MS = 1_000_000
CONFIG = Path(__file__).resolve().parents[1] / 'configs' / 'benchmark.json'


class FakeClock:
    """Advances 1 ms per read; advance() simulates work that reads nothing."""

    def __init__(self):
        self.now = 0

    def __call__(self):
        value = self.now
        self.now += MS
        return value

    def advance(self, ms):
        self.now += ms * MS


def fake_steps(clock, annotate_ms=0):
    return {'read': lambda: b'jpeg', 'decode': lambda data: 'frame',
            'm1': lambda frame: 'boxes', 'm2_crops': lambda frame, det: ['item'],
            'annotate': lambda frame, items: clock.advance(annotate_ms) or 'drawn',
            'encode': lambda frame: b'encoded'}


class Boundaries(unittest.TestCase):
    """Verbatim cases from the frozen plan."""

    def test_each_stage_lasts_its_two_reads(self):
        out = measure([('a', lambda r: None), ('b', lambda r: None)], FakeClock())
        self.assertEqual(out['stages_ns'], {'a': MS, 'b': MS})
        self.assertEqual(sum(out['stages_ns'].values()), 2 * MS)

    def test_outer_time_uses_its_own_reads(self):
        out = measure([('a', lambda r: None), ('b', lambda r: None)], FakeClock())
        self.assertEqual(out['total_ns'], 5 * MS)  # never forced equal to the 2 ms sum
        self.assertGreater(out['total_ns'], sum(out['stages_ns'].values()))

    def test_stage_sees_earlier_results(self):
        out = measure([('a', lambda r: 2), ('b', lambda r: r['a'] + 1)], FakeClock())
        self.assertEqual(out['results'], {'a': 2, 'b': 3})

    def test_annotation_is_in_end_to_end_and_not_in_cascade(self):
        clock = FakeClock()
        wall = iteration(fake_steps(clock, annotate_ms=50), clock)['wall_ns']
        self.assertEqual(wall['annotate'], 51 * MS)
        self.assertLess(wall['cascade'], 50 * MS)
        self.assertGreaterEqual(wall['cascade'], wall['m1'] + wall['m2_crops'])
        self.assertGreaterEqual(wall['end_to_end'], sum(
            wall[s] for s in ('read', 'decode', 'cascade', 'annotate', 'encode')))

    def test_every_wall_is_measured_once(self):
        clock = FakeClock()
        out = iteration(fake_steps(clock), clock)
        self.assertEqual(tuple(out['wall_ns']), WALL)
        self.assertEqual(out['results']['encode'], b'encoded')
        # end_to_end: 2 own reads + 5 stages x 2; cascade: 2 own reads + 2 stages x 2
        self.assertEqual(clock.now, 18 * MS)


class Repetitions(unittest.TestCase):
    def test_warmups_never_appear_in_the_measured_records(self):
        calls = []
        out = run_image(lambda: calls.append(1) or {'wall_ns': {'end_to_end': len(calls)}},
                        warmups=10, iterations=100)
        self.assertEqual(len(calls), 110)
        self.assertEqual([m['repetition'] for m in out['measured']], list(range(1, 101)))
        self.assertEqual(out['measured'][0]['wall_ns']['end_to_end'], 11)
        self.assertEqual(out['first_warmup']['wall_ns']['end_to_end'], 1)

    def test_failures_are_kept_and_slow_runs_never_dropped(self):
        results = iter([{'wall_ns': {}}, RuntimeError('boom'), {'wall_ns': {'x': 10 ** 12}}])

        def one():
            value = next(results)
            if isinstance(value, Exception):
                raise value
            return value

        out = run_image(one, warmups=1, iterations=2)
        self.assertEqual([m['status'] for m in out['measured']], ['failed', 'ok'])
        self.assertIn('boom', out['measured'][0]['error'])
        self.assertEqual(out['measured'][1]['wall_ns']['x'], 10 ** 12)

    def test_raw_rows_label_internal_speed_apart_from_walls(self):
        ok = {'repetition': 1, 'status': 'ok', 'wall_ns': dict.fromkeys(WALL, 7),
              'n_predicted_fruits': 2, 'n_m2_calls': 2, 'internal_ms': {'m1.inference': 3.5}}
        failed = {'repetition': 2, 'status': 'failed', 'error': 'RuntimeError()'}
        rows = rows_for({'image_id': 'SRC-1', 'sha256': 'h', 'run_order': 1}, [ok, failed])
        walls = [r for r in rows if r['kind'] == 'wall' and r['status'] == 'ok']
        self.assertEqual([r['stage'] for r in walls], list(WALL))
        internal = [r for r in rows if r['kind'] == 'internal_ultralytics']
        self.assertEqual([(r['stage'], r['internal_ms'], r['wall_ns']) for r in internal],
                         [('m1.inference', 3.5, '')])
        self.assertEqual([(r['repetition'], r['status']) for r in rows if r['status'] != 'ok'],
                         [(2, 'failed')])


class Summary(unittest.TestCase):
    def test_fixture(self):
        s = summarize([1, 2, 3, 4])
        self.assertEqual((s['median'], s['mean'], s['min'], s['max'], s['n']), (2.5, 2.5, 1, 4, 4))
        self.assertAlmostEqual(s['p95'], 3.85)
        self.assertAlmostEqual(s['std'], 1.25 ** 0.5)  # population
        self.assertIn('population', s['definition'])

    def test_single_value(self):
        s = summarize([5])
        self.assertEqual((s['p95'], s['std'], s['n']), (5, 0, 1))

    def test_rejects_empty_and_negative(self):
        for bad in ([], [1, -1]):
            with self.assertRaises(ValueError):
                summarize(bad)


class CudaSync(unittest.TestCase):
    def test_synchronise_only_on_cuda(self):
        sync = mock.Mock()
        synced_clock('cpu', FakeClock(), sync)()
        sync.assert_not_called()
        clock = synced_clock('cuda:0', FakeClock(), sync)
        clock()
        clock()
        self.assertEqual(sync.call_count, 2)


class Pool(unittest.TestCase):
    def rows(self):
        # 40 validation images without Enfermo sort before the only one with it.
        rows = [{'image_id': f'SRC-{i:03d}', 'sha256': f'{i:064x}', 'proposed_split': 'valid'}
                for i in range(40)]
        rows.append({'image_id': 'SRC-900', 'sha256': 'f' * 64, 'proposed_split': 'valid'})
        rows.append({'image_id': 'SRC-901', 'sha256': '0' * 64, 'proposed_split': 'test'})
        return rows

    def labels(self):
        labels = {f'SRC-{i:03d}': ['Saludable'] for i in range(40)}
        labels['SRC-000'] = []
        labels.update({'SRC-900': ['Saludable', 'Enfermo'], 'SRC-901': ['Enfermo']})
        return labels

    def test_each_stratum_first_then_fill_in_hash_order(self):
        pool = select_pool(list(reversed(self.rows())), self.labels(), k=32)
        ids = [p['image_id'] for p in pool]
        self.assertEqual(len(pool), 32)
        self.assertNotIn('SRC-901', ids)  # never a test image
        self.assertIn('SRC-900', ids)  # the only Enfermo stratum member is kept
        self.assertEqual(ids[:31], [f'SRC-{i:03d}' for i in range(31)])  # fill stops at 30
        self.assertEqual(ids, sorted(ids, key=lambda i: next(
            p['sha256'] for p in pool if p['image_id'] == i)))
        self.assertEqual([p['run_order'] for p in pool], list(range(1, 33)))
        self.assertEqual({p['image_id']: p['reason'] for p in pool if p['reason'] != 'fill'},
                         {'SRC-000': 'first_of_stratum', 'SRC-900': 'first_of_stratum'})
        self.assertTrue(next(p for p in pool if p['image_id'] == 'SRC-900')['with_enfermo'])

    def test_ties_on_hash_break_by_image_id(self):
        rows = [{'image_id': i, 'sha256': 'a' * 64, 'proposed_split': 'valid'} for i in 'cab']
        pool = select_pool(rows, {i: [] for i in 'cab'}, k=2)
        self.assertEqual([p['image_id'] for p in pool], ['a', 'b'])

    def test_missing_label_is_rejected(self):
        with self.assertRaises(RunRejected):
            select_pool(self.rows(), {}, k=32)


class Config(unittest.TestCase):
    def test_shipped_config_carries_the_frozen_operating_point(self):
        """After the freeze, the shipped config is accepted and binds the sealed M1 threshold and
        checkpoint (audit A, AUDIT-A-LOW-01)."""
        config = read_config(CONFIG)
        frozen = json.loads((CONFIG.parent / 'evaluation_frozen.json').read_text(encoding='utf-8'))
        self.assertEqual(config['m1_conf'], frozen['threshold'])
        self.assertEqual(config['m1_weights']['sha256'], frozen['checkpoint_sha256'])

    def test_a_config_without_the_frozen_m1_threshold_is_refused(self):
        config = json.loads(CONFIG.read_text(encoding='utf-8'))
        config['m1_conf'] = None
        with TemporaryDirectory() as d:
            path = Path(d) / 'benchmark.json'
            path.write_text(json.dumps(config), encoding='utf-8')
            with self.assertRaisesRegex(RunRejected, 'M1'):
                read_config(path)

    def test_frozen_constants_are_enforced(self):
        config = json.loads(CONFIG.read_text(encoding='utf-8'))
        self.assertEqual((config['batch'], config['precision'], config['m1_imgsz'],
                          config['m2_imgsz'], config['warmups_per_image'],
                          config['iterations_per_image'], config['torch_threads'],
                          config['device'], config['m2_conf']),
                         (1, 'fp32', 640, 224, 10, 100, 1, 'cpu', 0.4))
        with TemporaryDirectory() as d:
            path = Path(d) / 'benchmark.json'
            config['warmups_per_image'] = 5
            path.write_text(json.dumps(config), encoding='utf-8')
            with self.assertRaisesRegex(RunRejected, 'warmups_per_image'):
                read_config(path)


if __name__ == '__main__':
    unittest.main()
