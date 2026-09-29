"""EXP-R03 contract: classes by name, top-1 without rejection. No model is loaded."""

import unittest

from src.evaluation.predict_model2 import CLASS_NAMES, RunRejected, classification_record

ROW = {'image_id': 'SRC-1', 'sha256': 'h', 'cluster_id': 'c', 'group_id': 'g', 'split': 'test',
       'class_name': 'Costras'}


class Record(unittest.TestCase):
    def test_model_index_order_is_mapped_by_name(self):
        names = {0: 'Saludable', 1: 'Costras', 2: 'Antracnosis', 3: 'Cancro_bacteriano',
                 4: 'Podredumbre_Extremo_tallo'}
        record = classification_record(ROW, [0.1, 0.6, 0.1, 0.1, 0.1], names)
        self.assertEqual(record['pred'], 'Costras')
        self.assertEqual(record['probs']['Saludable'], 0.1)
        self.assertEqual(list(record['probs']), list(CLASS_NAMES))

    def test_top1_has_no_rejection_even_when_uncertain(self):
        names = dict(enumerate(CLASS_NAMES))
        record = classification_record(ROW, [0.21, 0.2, 0.2, 0.2, 0.19], names)
        self.assertEqual(record['pred'], 'Antracnosis')

    def test_unexpected_model_classes_are_rejected(self):
        with self.assertRaises(RunRejected):
            classification_record(ROW, [1.0], {0: 'Other'})


    def test_records_carry_model_names_in_index_order(self):
        names = {0: 'Saludable', 1: 'Costras', 2: 'Antracnosis', 3: 'Cancro_bacteriano',
                 4: 'Podredumbre_Extremo_tallo'}
        record = classification_record(ROW, [0.1, 0.6, 0.1, 0.1, 0.1], names)
        self.assertEqual(record['class_names'], [names[i] for i in range(5)])

    def test_exact_tie_follows_model_index_order(self):
        names = {0: 'Saludable', 1: 'Antracnosis', 2: 'Costras', 3: 'Cancro_bacteriano',
                 4: 'Podredumbre_Extremo_tallo'}
        record = classification_record(ROW, [0.3, 0.3, 0.2, 0.1, 0.1], names)
        self.assertEqual(record['pred'], 'Saludable')

    def test_sensitivity_reads_the_class_names_from_the_records(self):
        from src.statistics.intervals import _class_names
        names = dict(enumerate(CLASS_NAMES))
        record = classification_record(ROW, [0.1, 0.1, 0.6, 0.1, 0.1], names)
        self.assertEqual(_class_names(None, [record]), list(CLASS_NAMES))


class ProducerGates(unittest.TestCase):
    """TASK-05 round 6: EXP-R03 never starts without approval or with shadowed libraries."""

    def test_no_test_byte_is_read_before_the_m2_approval(self):
        import tempfile
        from pathlib import Path
        from unittest import mock

        from src.evaluation import authority, predict_model2
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
                authority, 'approved_inference', side_effect=authority.NotApproved('not yet')), \
                mock.patch.object(predict_model2, 'csv') as reader:
            run_dir = Path(tmp) / 'EXP-R03'
            with self.assertRaisesRegex(RunRejected, 'not yet'):
                predict_model2.run(Path(tmp) / 'm.csv', Path(tmp) / 'w.pt', run_dir,
                                   config=Path(tmp) / 'c.json')
            self.assertFalse(run_dir.exists())
            reader.DictReader.assert_not_called()

    def test_an_unfrozen_config_is_refused_before_any_test_byte(self):
        """Round-7 NEW-HIGH-05: a committed `{}` at the canonical path is not a freeze."""
        import tempfile
        from pathlib import Path
        from unittest import mock

        from src.evaluation import authority, predict_model2
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / predict_model2.M2_CONTRACT['config']
            config.parent.mkdir(parents=True)
            config.write_text('{}', encoding='utf-8')
            run_dir = root / 'experiments' / 'model2' / 'EXP-R03'
            with mock.patch('src.evaluation.provenance.authorized_root', return_value=root), \
                    mock.patch.object(authority, 'approved_inference', return_value={}), \
                    mock.patch.object(predict_model2, 'csv') as reader:
                with self.assertRaisesRegex(RunRejected, 'frozen M1 operating point'):
                    predict_model2.run(root / 'm.csv', root / 'w.pt', run_dir, config=config)
            self.assertFalse(run_dir.exists())
            reader.DictReader.assert_not_called()

    def test_a_library_not_loaded_from_an_installed_distribution_is_refused(self):
        """Round 7: the spec origin must be a recorded file of this interpreter (json is
        stdlib, pip an installed distribution)."""
        import json  # noqa: F401
        import pip  # noqa: F401

        from src.evaluation import authority
        with self.assertRaisesRegex(authority.NotApproved, 'json'):
            authority.check_imported('json')
        self.assertTrue(authority.check_imported('pip')['pip'].endswith('pip/__init__.py'))


if __name__ == '__main__':
    unittest.main()
