"""TASK-04 contracts. These use fictitious bytes: no model is loaded or trained."""

import hashlib
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.evaluation.train_model1 import (
    TRAINED_M1_SHA256, RunRejected, epoch_record, prepare_run, select_checkpoint,
)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


class Selection(unittest.TestCase):
    """Verbatim cases from the frozen brief."""

    def records(self, root: Path, spec: list[tuple[int, float]]) -> list[dict]:
        out = []
        for epoch, fitness in spec:
            path = root / f'epoch{epoch}.pt'
            raw = f'weights-{epoch}-{fitness!r}'.encode()
            path.write_bytes(raw)
            out.append({'epoch': epoch, 'fitness': fitness, 'metrics': {'fitness': fitness},
                        'checkpoint_path': str(path), 'sha256': sha(raw)})
        return out

    def test_tie_selects_the_last_epoch(self):
        with TemporaryDirectory() as d:
            chosen = select_checkpoint(self.records(Path(d), [(95, .80005), (137, .80478),
                                                                (138, .80478)]))
            self.assertEqual(chosen['epoch'], 138)
            self.assertTrue(chosen['checkpoint_path'].endswith('epoch138.pt'))

    def test_unrounded_maximum_wins_even_if_earlier(self):
        """0.8047801 and 0.8047802 print identically at six significant figures."""
        with TemporaryDirectory() as d:
            chosen = select_checkpoint(self.records(Path(d), [(100, .8047802), (140, .8047801)]))
            self.assertEqual(chosen['epoch'], 100)

    def test_changed_hash_fails(self):
        with TemporaryDirectory() as d:
            records = self.records(Path(d), [(1, .5), (2, .6)])
            records[1]['sha256'] = '0' * 64
            with self.assertRaisesRegex(RunRejected, 'hash'):
                select_checkpoint(records)

    def test_missing_artifact_fails(self):
        with TemporaryDirectory() as d:
            records = self.records(Path(d), [(1, .5)])
            Path(records[0]['checkpoint_path']).unlink()
            with self.assertRaisesRegex(RunRejected, 'missing'):
                select_checkpoint(records)

    def test_non_finite_fitness_invalidates_the_run(self):
        with TemporaryDirectory() as d:
            records = self.records(Path(d), [(1, .5)])
            records[0]['fitness'] = float('nan')
            with self.assertRaisesRegex(RunRejected, 'finite'):
                select_checkpoint(records)


class Preparation(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.manifest = self.root / 'manifest.csv'
        self.manifest.write_text('image_id,proposed_split\nSRC-1,train\n', encoding='utf-8')
        self.sidecar = self.root / 'manifest.csv.sha256'
        self.sidecar.write_text(f'{sha(self.manifest.read_bytes())}  manifest.csv\n', encoding='ascii')
        self.base = self.root / 'yolo26n.pt'
        self.base.write_bytes(b'official base weights')
        self.config = {'experiment_id': 'EXP-T', 'base_checkpoint': str(self.base),
                       'base_checkpoint_sha256': sha(b'official base weights'),
                       'epochs': 150, 'patience': 100, 'batch': 16, 'imgsz': 640, 'seed': 0,
                       'optimizer': 'auto', 'device': 'cpu'}

    def tearDown(self):
        self.tmp.cleanup()

    def test_manifest_with_another_hash_is_rejected_before_any_import(self):
        self.manifest.write_text('image_id,proposed_split\nSRC-1,test\n', encoding='utf-8')
        import sys
        before = 'ultralytics' in sys.modules
        with self.assertRaisesRegex(RunRejected, 'manifest'):
            prepare_run(self.config, self.manifest, self.root / 'run')
        self.assertEqual('ultralytics' in sys.modules, before)

    def test_existing_run_is_rejected(self):
        (self.root / 'run').mkdir()
        with self.assertRaises(FileExistsError):
            prepare_run(self.config, self.manifest, self.root / 'run')

    def test_a_trained_m1_checkpoint_cannot_be_the_base(self):
        config = {**self.config, 'base_checkpoint_sha256': TRAINED_M1_SHA256}
        self.base.write_bytes(b'x')
        with self.assertRaisesRegex(RunRejected, 'trained'):
            prepare_run(config, self.manifest, self.root / 'run')

    def test_base_bytes_must_match_the_declared_hash(self):
        self.base.write_bytes(b'tampered')
        with self.assertRaisesRegex(RunRejected, 'base'):
            prepare_run(self.config, self.manifest, self.root / 'run')

    def test_frozen_hyperparameters_are_enforced(self):
        for key, bad in (('epochs', 100), ('batch', 32), ('seed', 1), ('imgsz', 512)):
            with self.subTest(key=key), self.assertRaisesRegex(RunRejected, key):
                prepare_run({**self.config, key: bad}, self.manifest, self.root / f'run-{key}')

    def test_valid_preparation_records_hashes(self):
        record = prepare_run(self.config, self.manifest, self.root / 'run')
        self.assertEqual(record['manifest_sha256'], sha(self.manifest.read_bytes()))
        self.assertEqual(record['base_checkpoint_sha256'], sha(b'official base weights'))
        self.assertTrue((self.root / 'run').is_dir())


class UnroundedFitness(unittest.TestCase):
    """Ultralytics 8.4.52 rounds trainer.fitness to 5 decimals (engine/validator.py:267).

    The frozen SPEC selects on UNROUNDED fitness, which the validator's DetMetrics keeps.
    """

    def test_epoch_record_uses_the_validator_metrics_not_the_rounded_value(self):
        class Metrics:
            fitness = 0.123456789
            results_dict = {'metrics/mAP50-95(B)': 0.123456789, 'fitness': 0.123456789}

        class Validator:
            metrics = Metrics()

        class Trainer:
            epoch = 4
            fitness = 0.12346
            metrics = {'metrics/mAP50-95(B)': 0.12346}
            validator = Validator()

        record = epoch_record(Trainer())
        self.assertEqual(record['epoch'], 5)
        self.assertEqual(record['fitness'], 0.123456789)
        self.assertEqual(record['fitness_native_rounded'], 0.12346)
        self.assertEqual(record['metrics']['metrics/mAP50-95(B)'], 0.123456789)


if __name__ == '__main__':
    unittest.main()
