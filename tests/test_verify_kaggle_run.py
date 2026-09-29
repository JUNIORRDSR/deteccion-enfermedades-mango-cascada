"""Round-7 N-07/NEW-M-01/H-03: every downloaded attempt, complete or cut, becomes a reconciled,
resumable record, and a retry renders only from that record."""

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.evaluation import kaggle_job as job

TASK04 = Path(__file__).resolve().parents[1] / 'provenance' / 'commands' / 'task04'
sys.path.insert(0, str(TASK04))
SPEC = importlib.util.spec_from_file_location('verify_kaggle_run', TASK04 / 'verify_kaggle_run.py')
verify = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def make_attempt(run: Path, mode='train', experiment='EXP-R01', status='FAILED', stage='download',
                 platform_status='ERROR', job_log=True, extra_outputs=()):
    """A downloaded attempt as the renderer, the job and the platform leave it."""
    run.mkdir(parents=True)
    payload = {'mode': mode, 'experiment_id': experiment}
    kernel = job.render(payload)
    (run / 'kernel.py').write_text(kernel, encoding='utf-8', newline='\n')
    payload_sha = sha(json.dumps(payload, sort_keys=True).encode())
    (run / 'render_record.json').write_text(json.dumps({
        'kernel_sha256': sha((run / 'kernel.py').read_bytes()),
        'kernel_source_sha256': job.source_sha256(kernel), 'payload_sha256': payload_sha,
        'manifest_sha256': 'm', 'mode': mode, 'experiment_id': experiment}), encoding='utf-8')
    (run / 'platform_log.json').write_text('[]', encoding='utf-8')
    (run / 'evidence').mkdir()
    (run / 'evidence' / 'pip_check.stdout.txt').write_text('', encoding='utf-8')
    outputs = ['evidence/pip_check.stdout.txt', 'receipt.json', *extra_outputs]
    if job_log:
        (run / 'job_log.txt').write_text('started\n', encoding='utf-8')
        outputs.append('job_log.txt')
    receipt = {'payload_sha256': payload_sha, 'kernel_source_sha256': job.source_sha256(kernel),
               'status': status, 'stage': stage, 'mode': mode, 'experiment_id': experiment,
               'inventory': {'evidence/pip_check.stdout.txt': sha(b'')}}
    (run / 'receipt.json').write_text(json.dumps(receipt), encoding='utf-8')
    (run / 'platform.json').write_text(json.dumps(
        {'version': int(run.name[1:]), 'status': platform_status, 'outputs': sorted(outputs),
         'docker_image': 'd'}), encoding='utf-8')
    return receipt


def set_outputs(run: Path, outputs):
    platform = json.loads((run / 'platform.json').read_text(encoding='utf-8'))
    platform['outputs'] = sorted(outputs)
    (run / 'platform.json').write_text(json.dumps(platform), encoding='utf-8')


class Reconcile(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.run = Path(self.tmp.name) / 'EXP-R01' / 'v1'

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_pre_model_failure_is_reconciled_as_retriable(self):
        make_attempt(self.run)
        outcome = verify.reconcile(self.run, 1)
        self.assertEqual((outcome['status'], outcome['retry_allowed']), ('FAILED', True))
        self.assertTrue(outcome['files']['evidence/pip_check.stdout.txt']['attested'])
        self.assertEqual(outcome['unattested'], ['job_log.txt', 'receipt.json'])
        self.assertEqual(outcome['experiment_id'], 'EXP-R01')

    def test_a_hard_cut_without_receipt_is_recorded_and_never_retried(self):
        make_attempt(self.run, job_log=False)
        (self.run / 'receipt.json').unlink()
        set_outputs(self.run, ['evidence/pip_check.stdout.txt'])
        outcome = verify.reconcile(self.run, 1)
        self.assertEqual((outcome['status'], outcome['retry_allowed']), ('NO_RECEIPT', False))

    def test_partial_artifacts_written_after_the_last_receipt_are_hashed(self):
        """Round-7 N-07: a hard cut after stage=training."""
        make_attempt(self.run, status='RUNNING', stage='training',
                     extra_outputs=('run/epoch_records.jsonl', 'run/train/weights/last.pt'))
        (self.run / 'run' / 'train' / 'weights').mkdir(parents=True)
        (self.run / 'run' / 'epoch_records.jsonl').write_text('{"epoch": 1}\n', encoding='utf-8')
        (self.run / 'run' / 'train' / 'weights' / 'last.pt').write_bytes(b'partial')
        outcome = verify.reconcile(self.run, 1)
        self.assertFalse(outcome['retry_allowed'])
        self.assertEqual(outcome['files']['run/train/weights/last.pt'],
                         {'sha256': sha(b'partial'), 'attested': False})
        self.assertIn('run/epoch_records.jsonl', outcome['unattested'])

    def test_every_platform_output_must_be_downloaded_and_nothing_else(self):
        make_attempt(self.run, extra_outputs=('run/weights/last.pt',))
        with self.assertRaisesRegex(SystemExit, 'not downloaded'):
            verify.reconcile(self.run, 1)
        set_outputs(self.run, ['evidence/pip_check.stdout.txt', 'receipt.json', 'job_log.txt'])
        (self.run / 'stray.txt').write_text('x', encoding='utf-8')
        with self.assertRaisesRegex(SystemExit, 'does not list'):
            verify.reconcile(self.run, 1)

    def test_a_receipt_needs_its_job_log(self):
        make_attempt(self.run, job_log=False)
        with self.assertRaisesRegex(SystemExit, 'job_log'):
            verify.reconcile(self.run, 1)

    def test_evidence_must_be_retained_and_match(self):
        receipt = make_attempt(self.run)
        receipt['inventory'] = {'evidence/pip_check.stdout.txt': sha(b'x')}
        (self.run / 'receipt.json').write_text(json.dumps(receipt), encoding='utf-8')
        with self.assertRaisesRegex(SystemExit, 'differs'):
            verify.reconcile(self.run, 1)
        receipt['inventory'] = {'evidence/pip_freeze.stdout.txt': sha(b'x')}
        (self.run / 'receipt.json').write_text(json.dumps(receipt), encoding='utf-8')
        with self.assertRaisesRegex(SystemExit, 'not retained'):
            verify.reconcile(self.run, 1)

    def test_a_complete_training_must_retain_its_epoch_records_and_checkpoint(self):
        make_attempt(self.run, status='COMPLETE', stage='done', platform_status='COMPLETE')
        with self.assertRaisesRegex(SystemExit, 'retain'):
            verify.reconcile(self.run, 1)

    def test_a_receipt_from_another_payload_or_version_is_rejected(self):
        receipt = make_attempt(self.run)
        (self.run / 'receipt.json').write_text(json.dumps({**receipt, 'payload_sha256': 'x'}),
                                               encoding='utf-8')
        with self.assertRaisesRegex(SystemExit, 'payload'):
            verify.reconcile(self.run, 1)
        (self.run / 'receipt.json').write_text(json.dumps(receipt), encoding='utf-8')
        with self.assertRaisesRegex(SystemExit, 'version'):
            verify.reconcile(self.run, 2)

    def test_only_the_kaggle_editor_cell_marker_may_precede_the_executed_source(self):
        """DECISION-039: a version saved from Kaggle's web editor runs the rendered text after
        one '# %% [code]' line; any other executed text is refused."""
        receipt = make_attempt(self.run)
        kernel = (self.run / 'kernel.py').read_text(encoding='utf-8')
        for prefix, accepted in (('# %% [code]\n', True), ('# %% [markdown]\n', False),
                                 ('# %% [code]\n# %% [code]\n', False), ('import os\n', False)):
            executed = {**receipt, 'kernel_source_sha256': job.source_sha256(prefix + kernel)}
            (self.run / 'receipt.json').write_text(json.dumps(executed), encoding='utf-8')
            with self.subTest(prefix=prefix):
                if accepted:
                    self.assertEqual(verify.reconcile(self.run, 1)['status'], 'FAILED')
                else:
                    with self.assertRaisesRegex(SystemExit, 'executed source'):
                        verify.reconcile(self.run, 1)


class Finalize(unittest.TestCase):
    """Round-7 NEW-M-01: an interruption at any write boundary is resumable."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.run = Path(self.tmp.name) / 'EXP-R01' / 'v1'
        make_attempt(self.run)
        self.outcome = verify.reconcile(self.run, 1)
        self.sealed = (self.run.parent / 'selection_record.json', {'selected_sha256': 'c'})

    def tearDown(self):
        self.tmp.cleanup()

    def test_an_interruption_after_each_write_resumes_to_the_same_bytes(self):
        reference = None
        for fail_at in (1, 2, 3):
            for name in ('reconciliation.json',):
                (self.run / name).unlink(missing_ok=True)
            for path in (self.run.parent / 'selection_record.json',
                         self.run.parent / 'attempts.jsonl'):
                path.unlink(missing_ok=True)
            calls = []

            def flaky(path, data, calls=calls, fail_at=fail_at):
                calls.append(path)
                if len(calls) == fail_at:
                    raise KeyboardInterrupt('cut')
                verify.atomic_write(path, data)

            with self.subTest(fail_at=fail_at):
                with self.assertRaises(KeyboardInterrupt):
                    verify.finalize(self.run, 1, self.outcome, self.sealed, write=flaky)
                entry = verify.finalize(self.run, 1, self.outcome, self.sealed)
                state = [(self.run / 'reconciliation.json').read_bytes(),
                         (self.run.parent / 'selection_record.json').read_bytes(),
                         (self.run.parent / 'attempts.jsonl').read_bytes()]
                reference = reference or state
                self.assertEqual(state, reference)
                self.assertEqual(verify.finalize(self.run, 1, self.outcome, self.sealed), entry)

    def test_bytes_that_differ_from_the_recomputation_stop_a_resume(self):
        verify.finalize(self.run, 1, self.outcome, self.sealed)
        (self.run.parent / 'selection_record.json').write_text('{}', encoding='utf-8')
        with self.assertRaisesRegex(SystemExit, 'selection_record'):
            verify.finalize(self.run, 1, self.outcome, self.sealed)


class RetryRender(unittest.TestCase):
    """Round-7 H-03: a retry renders only from the committed, re-derived reconciliation."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.exp = self.root / 'experiments' / 'model1' / 'EXP-R01'
        make_attempt(self.exp / 'v1')
        verify.finalize(self.exp / 'v1', 1, verify.reconcile(self.exp / 'v1', 1), None)
        self.git('init', '-q')
        self.git('-c', 'user.email=t@t', '-c', 'user.name=t', 'add', '-A')
        self.git('-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-qm', 'v1')
        import render_kaggle_job
        self.render = render_kaggle_job

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args):
        subprocess.run(['git', *args], cwd=self.root, check=True, capture_output=True)

    def attempt(self, mode='train', experiment='EXP-R01', version=2):
        return self.render.attempt_dir(self.root, mode, None, experiment, version)

    def test_a_clean_pre_model_failure_allows_version_two_only(self):
        self.assertEqual(self.attempt(), self.exp / 'v2')
        with self.assertRaises(SystemExit):
            self.attempt(version=3)

    def test_another_namespace_or_mode_is_refused(self):
        for mode, experiment in (('train', 'EXP-R01-copy'), ('capacity', 'EXP-R01')):
            with self.subTest(experiment=experiment), self.assertRaises(SystemExit):
                self.attempt(mode, experiment, version=1)

    def test_missing_or_altered_evidence_is_refused(self):
        for name in ('job_log.txt', 'reconciliation.json', 'platform_log.json'):
            path = self.exp / 'v1' / name
            backup = path.read_bytes()
            path.unlink()
            self.git('-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-qam', f'drop {name}')
            with self.subTest(missing=name), self.assertRaises(SystemExit):
                self.attempt()
            path.write_bytes(backup)
            self.git('-c', 'user.email=t@t', '-c', 'user.name=t', 'add', '-A')
            self.git('-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-qm', f'restore {name}')
        log = self.exp / 'v1' / 'job_log.txt'
        log.write_text('all  113  199  0.9  mAP50\n', encoding='utf-8')
        self.git('-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-qam', 'metric line')
        with self.assertRaisesRegex(SystemExit, 'differs'):
            self.attempt()

    def test_uncommitted_evidence_is_refused(self):
        (self.exp / 'v1' / 'job_log.txt').write_text('changed\n', encoding='utf-8')
        with self.assertRaisesRegex(SystemExit, 'committed'):
            self.attempt()


if __name__ == '__main__':
    unittest.main()
