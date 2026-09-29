"""TASK-04 on Kaggle: the job fetches only its phase's files and verifies every byte."""

import hashlib
import json
import unittest

from src.evaluation import kaggle_job as job


def blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


def tree(paths):
    entries = [{'path': p, 'type': 'blob', 'sha': blob_sha1(p.encode())} for p in paths]
    entries.append({'path': 'docs/MangosDataset', 'type': 'tree', 'sha': 'x'})
    entries.append({'path': 'docs/README.md', 'type': 'blob', 'sha': 'y'})
    return {'truncated': False, 'tree': entries}


IMAGES = ['docs/MangosDataset/test/images/a.jpg', 'docs/MangosDataset/train/images/b.jpg',
          'docs/MangosDataset/valid/images/c.png']


class Corpus(unittest.TestCase):
    def test_image_paths_are_the_sorted_images_of_the_three_splits_only(self):
        self.assertEqual(job.image_paths(tree(IMAGES + ['docs/MangosDataset/train/labels/b.txt'])),
                         sorted(IMAGES))

    def test_truncated_tree_is_rejected(self):
        with self.assertRaises(job.JobRejected):
            job.image_paths({'truncated': True, 'tree': []})

    def test_label_path_mirrors_the_image(self):
        self.assertEqual(job.label_path('docs/MangosDataset/valid/images/c.rf.1.png'),
                         'docs/MangosDataset/valid/labels/c.rf.1.txt')

    def test_crlf_label_hashes_like_its_lf_blob(self):
        self.assertEqual(job.lf(b'0 0.5 0.5 1 1\r\n1 0.2 0.2 0.1 0.1\r\n'),
                         b'0 0.5 0.5 1 1\n1 0.2 0.2 0.1 0.1\n')


class Selection(unittest.TestCase):
    def test_test_rows_are_never_selected(self):
        chosen = job.select(sorted(IMAGES), 'xtv')
        self.assertEqual(chosen, {IMAGES[1]: 'train', IMAGES[2]: 'val'})

    def test_split_string_must_cover_every_image(self):
        with self.assertRaises(job.JobRejected):
            job.select(sorted(IMAGES), 'xt')

    def test_unknown_split_code_is_rejected(self):
        with self.assertRaises(job.JobRejected):
            job.select(sorted(IMAGES), 'xtq')

    def test_run_length_split_round_trips_and_rejects_garbage(self):
        codes = 'xxxvt' + 't' * 376 + 'vx'
        self.assertEqual(job.rle(codes), 'x3v1t377v1x1')
        self.assertEqual(job.unrle(job.rle(codes)), codes)
        for bad in ('', 't0', 'T3', 't3v', '3t'):
            with self.subTest(bad=bad), self.assertRaises(job.JobRejected):
                job.unrle(bad)

    def test_digest_changes_with_any_byte(self):
        lines = [('p', 'a' * 64, 'b' * 64)]
        self.assertNotEqual(job.digest(lines), job.digest([('p', 'a' * 64, 'c' * 64)]))


class Verification(unittest.TestCase):
    def test_blob_sha1_mismatch_is_rejected(self):
        with self.assertRaises(job.JobRejected):
            job.check_blob('p', b'data', blob_sha1(b'other'))

    def test_blob_sha1_match_passes(self):
        job.check_blob('p', b'data', blob_sha1(b'data'))


class Payload(unittest.TestCase):
    ROWS = [
        {'path': 'SemilleroTI-Mangos/' + IMAGES[0], 'proposed_split': 'test'},
        {'path': 'SemilleroTI-Mangos/' + IMAGES[1], 'proposed_split': 'train'},
        {'path': 'SemilleroTI-Mangos/' + IMAGES[2], 'proposed_split': 'valid'},
    ]

    def test_split_string_follows_sorted_repository_paths(self):
        self.assertEqual(job.split_string(self.ROWS), 'xtv')

    def test_rendered_script_carries_no_test_path_and_compiles(self):
        payload = {'mode': 'train', 'split': job.split_string(self.ROWS)}
        script = job.render(payload)
        self.assertNotIn('a.jpg', script)
        compile(script, 'job.py', 'exec')
        self.assertIn(json.dumps(payload, sort_keys=True), script)

    def test_trainer_travels_as_plain_text_and_round_trips_byte_exact(self):
        trainer = 'x = "a\\\\n"\n\ndef f():\n    return 1\n'
        script = job.render({'mode': 'train'}, trainer_source=trainer)
        namespace = {}
        exec(compile(script.replace("\n\nif __name__ == '__main__':\n    main(PAYLOAD)\n", ''),
                     'kernel', 'exec'), namespace)
        self.assertEqual(namespace['TRAINER_SOURCE'], trainer)
        self.assertNotIn('trainer_source', json.dumps(job.payload_of(script)))
        for bad in ("s = '''x'''\n", 'a = 1\r\n', 'x = 1 \\'):
            with self.subTest(bad=bad), self.assertRaises(job.JobRejected):
                job.render({'mode': 'train'}, trainer_source=bad)

    def test_render_refuses_a_payload_with_test_paths(self):
        with self.assertRaises(job.JobRejected):
            job.render({'mode': 'train', 'split': 'xtv', 'note': IMAGES[0]}, forbidden=[IMAGES[0]])


class ReceiptVerification(unittest.TestCase):
    """Local, after the run: the receipt must name exactly the train/valid files of the manifest."""

    ROWS = Payload.ROWS

    def receipt(self, files):
        return {'payload_sha256': 'p', 'files': [
            {'path': p, 'image_sha256': 'i' + p, 'label_lf_sha256': 'l' + p, 'split': s}
            for p, s in files]}

    def expected(self):
        return {IMAGES[1]: ('train', 'i' + IMAGES[1], 'l' + IMAGES[1]),
                IMAGES[2]: ('val', 'i' + IMAGES[2], 'l' + IMAGES[2])}

    def test_exact_train_valid_receipt_passes(self):
        job.verify_receipt(self.receipt([(IMAGES[1], 'train'), (IMAGES[2], 'val')]),
                           self.expected(), 'p')

    def test_a_test_file_in_the_receipt_is_rejected(self):
        with self.assertRaisesRegex(job.JobRejected, 'differ'):
            job.verify_receipt(self.receipt([(IMAGES[0], 'train'), (IMAGES[1], 'train'),
                                             (IMAGES[2], 'val')]), self.expected(), 'p')

    def test_other_payload_is_rejected(self):
        with self.assertRaisesRegex(job.JobRejected, 'payload'):
            job.verify_receipt(self.receipt([(IMAGES[1], 'train'), (IMAGES[2], 'val')]),
                               self.expected(), 'q')


class Bindings(unittest.TestCase):
    """Round-5 H-02: the payload has a trusted root outside the caller's inputs."""

    APPROVED = {'manifest_path': 'data/manifests/model1_clean_manifest.csv',
                'manifest_sha256': 'm' * 64, 'trainer_sha256': 't' * 64, 'job_sha256': 'j' * 64}

    def test_frozen_manifest_and_approved_code_pass(self):
        job.check_bindings('data/manifests/model1_clean_manifest.csv', 'm' * 64, 't' * 64,
                           'j' * 64, self.APPROVED)

    def test_another_manifest_with_a_valid_sidecar_is_rejected(self):
        with self.assertRaisesRegex(job.JobRejected, 'manifest'):
            job.check_bindings('data/manifests/other.csv', 'm' * 64, 't' * 64, 'j' * 64,
                               self.APPROVED)
        with self.assertRaisesRegex(job.JobRejected, 'manifest'):
            job.check_bindings('data/manifests/model1_clean_manifest.csv', 'n' * 64, 't' * 64,
                               'j' * 64, self.APPROVED)

    def test_a_changed_trainer_with_a_matching_self_hash_is_rejected(self):
        with self.assertRaisesRegex(job.JobRejected, 'trainer'):
            job.check_bindings('data/manifests/model1_clean_manifest.csv', 'm' * 64, 'u' * 64,
                               'j' * 64, self.APPROVED)

    def test_a_changed_job_is_rejected(self):
        with self.assertRaisesRegex(job.JobRejected, 'job'):
            job.check_bindings('data/manifests/model1_clean_manifest.csv', 'm' * 64, 't' * 64,
                               'k' * 64, self.APPROVED)


class KernelSource(unittest.TestCase):
    """The executed source is hashed in the kernel and compared with the local render."""

    def test_normalisation_ignores_only_line_endings_and_trailing_newlines(self):
        self.assertEqual(job.source_sha256('a\r\nb\n\n'), job.source_sha256('a\nb'))
        self.assertNotEqual(job.source_sha256('a\nb'), job.source_sha256('a\nc'))

    def test_receipt_from_another_kernel_source_is_rejected(self):
        receipt = {'payload_sha256': 'p', 'kernel_source_sha256': job.source_sha256('x'),
                   'files': []}
        with self.assertRaisesRegex(job.JobRejected, 'kernel'):
            job.verify_receipt(receipt, {}, 'p', kernel_source='y')
        job.verify_receipt(receipt, {}, 'p', kernel_source='x')


class FailureRecord(unittest.TestCase):
    """Round-5 N-07: a failed or cut run still leaves a reconcilable record."""

    def test_receipt_is_written_with_stage_and_error_when_a_stage_fails(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            state = {'stage': 'start'}

            def body(receipt):
                state['stage'] = 'download'
                receipt['stage'] = 'download'
                raise job.JobRejected('boom')

            with self.assertRaises(job.JobRejected):
                job.run_recorded({'payload_sha256': 'p'}, out, body)
            receipt = json.loads((out / 'receipt.json').read_text(encoding='utf-8'))
            self.assertEqual(receipt['status'], 'FAILED')
            self.assertEqual(receipt['stage'], 'download')
            self.assertIn('boom', receipt['error'])

    def test_epoch_records_are_on_disk_before_training_ends(self):
        import tempfile
        from pathlib import Path

        from src.evaluation.train_model1 import append_record
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'epoch_records.jsonl'
            append_record(path, {'epoch': 1, 'fitness': 0.1})
            append_record(path, {'epoch': 2, 'fitness': 0.2})
            lines = path.read_text(encoding='utf-8').splitlines()
            self.assertEqual([json.loads(line)['epoch'] for line in lines], [1, 2])


class Capacity(unittest.TestCase):
    """Round-5 M-01: projection rule fixed before measuring."""

    def test_projection_excludes_warm_up_and_uses_the_maximum(self):
        verdict = job.capacity_verdict(epoch_seconds=[90.0, 40.0, 50.0], setup_seconds=100.0,
                                       epochs=150, safety=1.35, limit_seconds=43200)
        self.assertEqual(verdict['per_epoch_seconds'], 50.0)
        self.assertAlmostEqual(verdict['projected_seconds'], 100.0 + 50.0 * 150 * 1.35)
        self.assertTrue(verdict['fits'])

    def test_a_run_that_does_not_fit_is_reported(self):
        verdict = job.capacity_verdict([400.0, 300.0, 320.0], 100.0, 150, 1.35, 43200)
        self.assertFalse(verdict['fits'])


class Authorization(unittest.TestCase):
    """TASK-05 review round 2 HIGH-01: the amendment state and the checkpoint seal."""

    PROPOSED = {'state': 'PROPOSED_V6', 'execution_permitted': 'non_scientific_probes_only'}
    APPROVED = {'state': 'APPROVED', 'execution_permitted': 'EXP-R01'}

    def test_a_probe_is_allowed_while_proposed_and_training_is_not(self):
        job.authorize('capacity', self.PROPOSED)
        with self.assertRaisesRegex(job.JobRejected, 'APPROVED'):
            job.authorize('train', self.PROPOSED)
        job.authorize('train', self.APPROVED)

    def test_inference_needs_explicit_approval_and_the_sealed_checkpoint(self):
        with self.assertRaisesRegex(job.JobRejected, 'inference_approved'):
            job.authorize('predict', self.APPROVED, {'selected_sha256': 'c'}, 'c')
        approved = {**self.APPROVED, 'inference_approved': True}
        with self.assertRaisesRegex(job.JobRejected, 'sealed'):
            job.authorize('predict', approved, {'selected_sha256': 'c'}, 'd')
        with self.assertRaisesRegex(job.JobRejected, 'sealed'):
            job.authorize('predict', approved, None, 'c')
        job.authorize('predict', approved, {'selected_sha256': 'c'}, 'c')


class PredictionRun(unittest.TestCase):
    """TASK-05 review HIGH-04: a prediction run is bound to kernel, checkpoint and settings."""

    CONFIG = {'checkpoint_sha256': 'c' * 64, 'min_score': 0.001, 'nms_iou': 0.6,
              'max_det': 300, 'imgsz': 640}

    def setUp(self):
        self.payload = {'mode': 'predict', 'phase': 'valid', 'checkpoint_sha256': 'c' * 64,
                        'split': 'xpv', 'inference': {'min_score': 0.001, 'nms_iou': 0.6,
                                                      'max_det': 300, 'imgsz': 640},
                        'config_sha256': 'f' * 64, 'manifest_sha256': 'm' * 64,
                        'experiment_id': 'EXP-V01'}
        self.kernel = job.render(self.payload)
        self.expected = {IMAGES[1]: ('predict', 'i', 'l')}
        self.receipt = {
            'payload_sha256': job.sha256(json.dumps(self.payload, sort_keys=True).encode()),
            'kernel_source_sha256': job.source_sha256(self.kernel), 'status': 'COMPLETE',
            'mode': 'predict', 'phase': 'valid', 'checkpoint_sha256': 'c' * 64,
            'experiment_id': 'EXP-V01', 'stage': 'done', 'model_names': {0: 'Enfermo', 1: 'Saludable'},
            'predict_args': job.predict_args(self.payload['inference']),
            'predictions_raw_sha256': 'r' * 64, 'end2end': True, 'agnostic_nms': False,
            'single_cls': False, 'effective_suppression': job.suppression(True, 0.6),
            'input_contract': job.INPUT_CONTRACT,
            'files': [{'path': IMAGES[1], 'image_sha256': 'i', 'label_lf_sha256': 'l',
                       'split': 'predict'}]}

    def verify(self, receipt=None, kernel=None, config=None, phase='valid',
               config_sha256='f' * 64, manifest_sha256='m' * 64):
        return job.verify_prediction_run(receipt or self.receipt, kernel or self.kernel,
                                         config or self.CONFIG, phase, self.expected,
                                         config_sha256, manifest_sha256)

    def test_a_consistent_run_passes_and_returns_its_identities(self):
        identities = self.verify()
        self.assertEqual(identities['checkpoint_sha256'], 'c' * 64)
        self.assertEqual(identities['kernel_source_sha256'], job.source_sha256(self.kernel))
        self.assertEqual(identities['model_names'], job.M1_MODEL_NAMES)
        self.assertEqual(identities['predict_args'], job.predict_args(self.payload['inference']))

    def test_another_experiment_payload_is_rejected(self):
        payload = {**self.payload, 'experiment_id': 'OTHER-EXP'}
        kernel = job.render(payload)
        receipt = {**self.receipt, 'kernel_source_sha256': job.source_sha256(kernel),
                   'payload_sha256': job.sha256(json.dumps(payload, sort_keys=True).encode())}
        with self.assertRaisesRegex(job.JobRejected, 'EXP-V01'):
            self.verify(receipt=receipt, kernel=kernel)

    def test_a_failure_after_the_predictions_were_hashed_is_definitive_and_usable(self):
        """TASK-05 round-4 NEW-HIGH-04: amendment section 4 makes it definitive."""
        for status in ('FAILED', 'RUNNING'):
            receipt = {**self.receipt, 'status': status, 'stage': 'predictions_written',
                       'error': 'OSError: disk full' if status == 'FAILED' else None}
            identities = self.verify(receipt=receipt)
            self.assertEqual((identities['receipt_status'], identities['receipt_stage']),
                             (status, 'predictions_written'))

    def test_each_mismatch_is_rejected(self):
        cases = {
            'checkpoint': dict(receipt={**self.receipt, 'checkpoint_sha256': 'd' * 64}),
            'config checkpoint': dict(config={**self.CONFIG, 'checkpoint_sha256': 'd' * 64}),
            'phase': dict(phase='test'),
            'status': dict(receipt={**self.receipt, 'status': 'FAILED', 'stage': 'download'}),
            'setting': dict(config={**self.CONFIG, 'max_det': 100}),
            'kernel': dict(kernel=self.kernel.replace('PREFIX = ', 'PREFIX  = ')),
            'config hash': dict(config_sha256='g' * 64),
            'manifest hash': dict(manifest_sha256='n' * 64),
            'no end2end': dict(receipt={k: v for k, v in self.receipt.items() if k != 'end2end'}),
            'no contract': dict(receipt={**self.receipt, 'input_contract': ''}),
            'agnostic': dict(receipt={**self.receipt, 'agnostic_nms': True}),
            'no agnostic flag': dict(receipt={k: v for k, v in self.receipt.items()
                                              if k != 'agnostic_nms'}),
            'no single_cls flag': dict(receipt={k: v for k, v in self.receipt.items()
                                                if k != 'single_cls'}),
            'other contract': dict(receipt={**self.receipt, 'input_contract': 'file path'}),
            'wrong suppression': dict(receipt={**self.receipt,
                                               'effective_suppression': job.suppression(False, 0.6)}),
            'end2end false, consistent suppression': dict(receipt={
                **self.receipt, 'end2end': False,
                'effective_suppression': job.suppression(False, 0.6)}),
            'reversed names': dict(receipt={**self.receipt,
                                            'model_names': {0: 'Saludable', 1: 'Enfermo'}}),
            'other call': dict(receipt={**self.receipt, 'predict_args': {
                **job.predict_args(self.payload['inference']), 'half': True}}),
            'no call': dict(receipt={k: v for k, v in self.receipt.items() if k != 'predict_args'}),
            'other experiment': dict(receipt={**self.receipt, 'experiment_id': 'OTHER-EXP'}),
            'failed before predictions': dict(receipt={**self.receipt, 'status': 'FAILED',
                                                       'stage': 'predict'}),
            'no raw digest': dict(receipt={**self.receipt, 'predictions_raw_sha256': None}),
        }
        for name, kwargs in cases.items():
            with self.subTest(case=name), self.assertRaises(job.JobRejected):
                self.verify(**kwargs)


class PipCheck(unittest.TestCase):
    """Round-6 N-06: a conflict blocks only inside the pipeline's dependency closure."""

    REQUIRES = {'ultralytics': ['numpy>=1.23', 'torch>=1.8', 'pytest; extra == "dev"'],
                'torch': ['filelock', 'typing-extensions>=4'], 'numpy': [], 'filelock': [],
                'typing-extensions': [], 'torchvision': ['torch']}

    def closure(self):
        return job.dependency_closure(job.PIP_CHECK_ROOTS, self.REQUIRES.get)

    def test_closure_follows_requirements_but_not_extras(self):
        self.assertEqual(self.closure(), {'ultralytics', 'numpy', 'torch', 'filelock',
                                          'typing-extensions', 'torchvision'})

    def test_a_healthy_pip_check_passes_and_contradictory_success_output_blocks(self):
        """Round-7 NEW-L-01."""
        self.assertEqual(job.pip_check_verdict(0, 'No broken requirements found.\n',
                                               self.closure())['blocking'], [])
        self.assertEqual(job.pip_check_verdict(0, '', self.closure())['blocking'], [])
        stdout = 'No broken requirements found.\ntorch 2.10 requires x, which is not installed.\n'
        self.assertEqual(len(job.pip_check_verdict(0, stdout, self.closure())['blocking']), 1)

    def test_the_capacity_probe_conflicts_are_outside_the_closure(self):
        stdout = ('bigframes 2.39.0 requires google-cloud-bigquery-storage, which is not installed.\n'
                  'google-colab 1.0.0 has requirement pandas==2.2.2, but you have pandas 2.3.3.\n')
        verdict = job.pip_check_verdict(1, stdout, self.closure())
        self.assertEqual(verdict['blocking'], [])
        self.assertEqual(len(verdict['lines']), 2)

    def test_a_conflict_of_a_pipeline_package_or_an_unparsed_line_blocks(self):
        stdout = ('torch 2.10.0 has requirement filelock>=9, but you have filelock 3.0.\n'
                  'something unexpected\n')
        self.assertEqual(len(job.pip_check_verdict(1, stdout, self.closure())['blocking']), 2)
        self.assertEqual(len(job.pip_check_verdict(1, '', self.closure())['blocking']), 1)


class Attempts(unittest.TestCase):
    """Round-6 H-03: which failed versions may be followed by another."""

    FAILED = {'status': 'FAILED', 'stage': 'download', 'error': 'JobRejected: boom'}

    def test_a_failure_before_any_model_output_may_be_retried(self):
        self.assertTrue(job.retry_allowed('train', self.FAILED, 'ERROR', ['receipt.json'], [''])[0])

    def test_every_other_termination_is_never_retried(self):
        cases = {
            'no receipt': ('train', None, 'ERROR', [], []),
            'cancelled': ('train', self.FAILED, 'CANCEL_ACKNOWLEDGED', [], []),
            'hard cut': ('train', {**self.FAILED, 'status': 'RUNNING'}, 'ERROR', [], []),
            'training started': ('train', {**self.FAILED, 'stage': 'training'}, 'ERROR', [], []),
            'weights exist': ('train', self.FAILED, 'ERROR', ['run/weights/last.pt'], []),
            'predictions exist': ('predict', {**self.FAILED, 'stage': 'predict'}, 'ERROR',
                                  ['predictions_raw.jsonl'], []),
            'metric line': ('train', self.FAILED, 'ERROR', [], ['all  113  199  0.9  mAP50']),
            'complete': ('train', {**self.FAILED, 'status': 'COMPLETE'}, 'COMPLETE', [], []),
        }
        for name, args in cases.items():
            with self.subTest(case=name):
                self.assertFalse(job.retry_allowed(*args)[0])

    def test_each_mode_renders_only_its_experiment(self):
        """Round-7 H-03: no second namespace for a scientific run."""
        job.check_experiment('train', None, 'EXP-R01')
        job.check_experiment('predict', 'valid', 'EXP-V01')
        job.check_experiment('predict', 'test', 'EXP-R02')
        job.check_experiment('capacity', None, 'KAGGLE-CAPACITY-003')
        for mode, phase, name in (('train', None, 'EXP-R01-copy'), ('train', None, 'EXP-V01'),
                                  ('predict', 'test', 'EXP-V01'), ('predict', 'valid', 'EXP-R02'),
                                  ('capacity', None, 'EXP-R01'), ('probe', None, 'EXP-R01')):
            with self.subTest(mode=mode, name=name), self.assertRaises(job.JobRejected):
                job.check_experiment(mode, phase, name)

    def test_the_ledger_gates_every_later_version(self):
        job.check_attempt([], 1, None, 'train', 'EXP-R01')
        failed = {'version': 1, 'status': 'FAILED', 'retry_allowed': True, 'mode': 'train',
                  'experiment_id': 'EXP-R01'}
        job.check_attempt([failed], 2, (True, 'ok'), 'train', 'EXP-R01')
        with self.assertRaisesRegex(job.JobRejected, 'another mode'):
            job.check_attempt([failed], 2, (True, 'ok'), 'capacity', 'EXP-R01')
        with self.assertRaisesRegex(job.JobRejected, 'another mode'):
            job.check_attempt([{**failed, 'experiment_id': 'X'}], 2, (True, 'ok'), 'train', 'EXP-R01')
        cases = {
            'gap': ([failed], 3, (True, 'ok')),
            'first twice': ([failed], 1, None),
            're-derived refusal': ([failed], 2, (False, 'metric line')),
            'ledger refusal': ([{**failed, 'retry_allowed': False}], 2, (True, 'ok')),
            'after complete': ([{**failed, 'status': 'COMPLETE'}], 2, (True, 'ok')),
            'too many': ([failed, {**failed, 'version': 2}, {**failed, 'version': 3}], 4,
                         (True, 'ok')),
        }
        for name, (ledger, version, previous) in cases.items():
            with self.subTest(case=name), self.assertRaises(job.JobRejected):
                job.check_attempt(ledger, version, previous, 'train', 'EXP-R01')

    def test_the_json_policy_is_the_code_policy(self):
        from pathlib import Path
        amendment = json.loads((Path(__file__).resolve().parents[1] / 'provenance' /
                                'protocol_amendments' /
                                'PROTOCOL-AMENDMENT-008-kaggle-compute.json').read_text(encoding='utf-8'))
        self.assertEqual(amendment['retry_policy'], job.RETRY_POLICY)


class HardCut(unittest.TestCase):
    """Round-6 N-07: a session killed without running `finally` still leaves a receipt."""

    def test_a_cut_during_training_leaves_a_running_receipt_that_is_never_retried(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / 'evidence').mkdir()
            (out / 'evidence' / 'pip_freeze.stdout.txt').write_text('x==1\n', encoding='utf-8')
            (out / 'job_log.txt').write_text('epoch 1\n', encoding='utf-8')
            receipt = {'payload_sha256': 'p', 'mode': 'train'}
            job.set_stage(receipt, out, 'training')
            # the process dies here: no finally, no FAILED status
            on_disk = json.loads((out / 'receipt.json').read_text(encoding='utf-8'))
            self.assertEqual((on_disk['status'], on_disk['stage']), ('RUNNING', 'training'))
            self.assertEqual(set(on_disk['inventory']), {'evidence/pip_freeze.stdout.txt'})
            self.assertFalse((out / 'receipt.json.tmp').exists())
            self.assertFalse(job.retry_allowed('train', on_disk, 'ERROR', [], [])[0])


if __name__ == '__main__':
    unittest.main()
