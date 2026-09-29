"""TASK-07: cascade ground truth contract and joint scoring. Fictitious fixtures only;
no independent disease-specific GT exists yet for the current corpora (SPEC section 9)."""

import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.evaluation.cascade import (
    ABSTAIN, DISEASES, HEALTHY, INDEPENDENT, check_availability, score_cascade,
    validate_ground_truth,
)

ROOT = Path(__file__).resolve().parents[1]
D1, D2 = DISEASES[0], DISEASES[1]


def gt_row(**over):
    row = {'image_id': 'a' * 64, 'fruit_id': 'F1', 'bbox_xyxy': [0.0, 0.0, 10.0, 10.0],
          'disease_label': D1, 'healthy_or_diseased': 'diseased',
          'adjudication_status': INDEPENDENT, 'annotator_id': 'AG-1',
          'diagnostic_method': 'agronomist_visual_inspection', 'date': '2026-09-20',
          'group_id': 'GRP-1', 'source': 'field_survey_2026'}
    row.update(over)
    return row


def pred_row(**over):
    row = {'image_id': 'a' * 64, 'bbox_xyxy': [0.0, 0.0, 10.0, 10.0], 'predicted_label': D1}
    row.update(over)
    return row


def run_cli(*args):
    return subprocess.run([sys.executable, '-m', 'src.evaluation.cascade', *map(str, args)],
                          cwd=ROOT, capture_output=True, text=True)


class PlanRedFixtures(unittest.TestCase):
    """Verbatim from the plan's RED step."""

    def test_two_diseased_gt_one_correct_detection_gives_half_recall(self):
        gt = [gt_row(fruit_id='F1'), gt_row(fruit_id='F2', bbox_xyxy=[100.0, 100.0, 110.0, 110.0])]
        pred = [pred_row(predicted_label=D1)]  # only matches F1
        self.assertEqual(score_cascade(gt, pred)['joint_recall']['value'], 0.5)

    def test_wrong_diagnosis_on_the_only_detection_gives_zero_recall(self):
        gt = [gt_row(fruit_id='F1'), gt_row(fruit_id='F2', bbox_xyxy=[100.0, 100.0, 110.0, 110.0])]
        pred = [pred_row(predicted_label=D2)]  # detected F1 but the wrong disease
        self.assertEqual(score_cascade(gt, pred)['joint_recall']['value'], 0.0)

    def test_two_predictions_on_the_same_gt_leave_one_fp(self):
        gt = [gt_row(fruit_id='F1')]
        pred = [pred_row(predicted_label=D1), pred_row(predicted_label=D1,
                                                        bbox_xyxy=[0.0, 0.0, 10.0, 9.0])]
        result = score_cascade(gt, pred)
        precision = result['per_disease_precision'][D1]
        self.assertEqual((precision['tp'], precision['fp']), (1, 1))

    def test_diagnostic_method_model_prediction_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'MODEL_PREDICTION_REJECTED'):
            validate_ground_truth([gt_row(diagnostic_method='model_prediction')])

    def test_m2_abstention_on_a_diseased_fruit_counts_as_fn(self):
        gt = [gt_row(fruit_id='F1')]
        pred = [pred_row(predicted_label=ABSTAIN)]
        self.assertEqual(score_cascade(gt, pred)['joint_recall'],
                         {'successes': 0, 'denominator': 1, 'value': 0.0})


class ValidateGroundTruth(unittest.TestCase):
    def test_valid_row_passes(self):
        validate_ground_truth([gt_row()])

    def test_missing_field_is_rejected(self):
        row = gt_row()
        del row['source']
        with self.assertRaisesRegex(ValueError, 'SCHEMA'):
            validate_ground_truth([row])

    def test_bad_bbox_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'BAD_BBOX'):
            validate_ground_truth([gt_row(bbox_xyxy=[10.0, 0.0, 0.0, 10.0])])

    def test_unknown_disease_label_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'BAD_DISEASE_LABEL'):
            validate_ground_truth([gt_row(disease_label='Roya')])

    def test_ambiguous_and_undiagnosed_labels_are_kept_not_rejected(self):
        for label in ('AMBIGUOUS', 'UNDIAGNOSED'):
            with self.subTest(label=label):
                validate_ground_truth([gt_row(disease_label=label, healthy_or_diseased='diseased')])

    def test_inconsistent_health_status_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'INCONSISTENT_HEALTH_STATUS'):
            validate_ground_truth([gt_row(disease_label=HEALTHY, healthy_or_diseased='diseased')])

    def test_unknown_adjudication_status_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'BAD_ADJUDICATION_STATUS'):
            validate_ground_truth([gt_row(adjudication_status='SELF_ADJUDICATED')])

    def test_duplicate_fruit_id_within_image_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'DUPLICATE_OR_MISSING_FRUIT_ID'):
            validate_ground_truth([gt_row(fruit_id='F1'), gt_row(fruit_id='F1')])

    def test_same_fruit_id_in_different_images_is_allowed(self):
        validate_ground_truth([gt_row(fruit_id='F1', image_id='a' * 64),
                               gt_row(fruit_id='F1', image_id='b' * 64)])

    def test_bad_date_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'BAD_DATE'):
            validate_ground_truth([gt_row(date='20-09-2026')])

    def test_bad_image_id_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'BAD_IMAGE_ID'):
            validate_ground_truth([gt_row(image_id='not-a-sha')])


class ScoreCascade(unittest.TestCase):
    def test_non_independent_gt_is_excluded_from_denominator_and_reported(self):
        gt = [gt_row(fruit_id='F1', adjudication_status='PENDING_ADJUDICATION')]
        result = score_cascade(gt, [pred_row(predicted_label=D1)])
        self.assertEqual(result['joint_recall'], {'successes': 0, 'denominator': 0, 'value': None})
        self.assertEqual(result['excluded']['non_independent_count'], 1)
        # the matched prediction is excluded, never counted as a false positive either
        self.assertEqual(result['per_disease_precision'][D1]['fp'], 0)

    def test_ambiguous_gt_is_excluded_with_explicit_count(self):
        gt = [gt_row(fruit_id='F1', disease_label='AMBIGUOUS')]
        result = score_cascade(gt, [pred_row(predicted_label=D1)])
        self.assertEqual(result['joint_recall']['denominator'], 0)
        self.assertEqual(result['excluded']['ambiguous_or_undiagnosed_count'], 1)
        self.assertEqual(result['per_disease_precision'][D1]['fp'], 0)

    def test_healthy_fruit_never_counts_toward_disease_recall(self):
        gt = [gt_row(fruit_id='F1', disease_label=HEALTHY, healthy_or_diseased='healthy')]
        result = score_cascade(gt, [pred_row(predicted_label=HEALTHY)])
        self.assertEqual(result['joint_recall']['denominator'], 0)

    def test_m1_predicting_healthy_on_a_diseased_fruit_is_a_failure(self):
        gt = [gt_row(fruit_id='F1')]
        result = score_cascade(gt, [pred_row(predicted_label=HEALTHY)])
        self.assertEqual(result['joint_recall'], {'successes': 0, 'denominator': 1, 'value': 0.0})

    def test_healthy_fruit_misdiagnosed_as_diseased_is_a_false_positive(self):
        gt = [gt_row(fruit_id='F1', disease_label=HEALTHY, healthy_or_diseased='healthy')]
        result = score_cascade(gt, [pred_row(predicted_label=D1)])
        self.assertEqual(result['per_disease_precision'][D1], {'tp': 0, 'fp': 1,
                                                               'precision': 0.0,
                                                               'precision_denominator': 1})

    def test_undetected_diseased_fruit_is_a_failure_in_the_denominator(self):
        gt = [gt_row(fruit_id='F1')]
        result = score_cascade(gt, [])
        self.assertEqual(result['joint_recall'], {'successes': 0, 'denominator': 1, 'value': 0.0})

    def test_extra_prediction_with_no_nearby_gt_at_all_is_a_false_positive(self):
        gt = [gt_row(fruit_id='F1', image_id='a' * 64)]
        pred = [pred_row(predicted_label=D1, image_id='a' * 64),
               pred_row(predicted_label=D2, image_id='b' * 64, bbox_xyxy=[5.0, 5.0, 15.0, 15.0])]
        result = score_cascade(gt, pred)
        self.assertEqual(result['per_disease_precision'][D2]['fp'], 1)

    def test_conditional_classification_and_abstention_rate_have_explicit_denominators(self):
        gt = [gt_row(fruit_id='F1'), gt_row(fruit_id='F2', bbox_xyxy=[100.0, 100.0, 110.0, 110.0])]
        pred = [pred_row(predicted_label=D1),  # F1: correct
               pred_row(predicted_label=ABSTAIN, bbox_xyxy=[100.0, 100.0, 110.0, 110.0])]  # F2
        result = score_cascade(gt, pred)
        conditional = result['secondary']['conditional_classification_given_detected']
        abstention = result['secondary']['m2_abstention_rate']
        self.assertEqual(conditional, {'correct': 1, 'denominator': 2, 'accuracy': 0.5})
        self.assertEqual(abstention, {'abstained': 1, 'denominator': 2, 'rate': 0.5})

    def test_never_multiplies_marginal_recalls(self):
        """A perfect detector (recall 1.0) feeding a classifier that is always wrong on
        this fixture must give joint recall 0.0, not 1.0 * something: the two stages are
        never combined as independent probabilities."""
        gt = [gt_row(fruit_id='F1'), gt_row(fruit_id='F2', bbox_xyxy=[100.0, 100.0, 110.0, 110.0],
                                            disease_label=D2)]
        pred = [pred_row(predicted_label=D2),  # F1 is D1, predicted D2: wrong
               pred_row(predicted_label=D1, bbox_xyxy=[100.0, 100.0, 110.0, 110.0])]  # F2 wrong too
        self.assertEqual(score_cascade(gt, pred)['joint_recall']['value'], 0.0)

    def test_rejects_invalid_ground_truth_before_scoring(self):
        with self.assertRaises(ValueError):
            score_cascade([gt_row(diagnostic_method='model_prediction')], [])

    def test_rejects_prediction_with_unknown_label(self):
        with self.assertRaises(ValueError):
            score_cascade([gt_row()], [pred_row(predicted_label='Roya')])


class CheckAvailability(unittest.TestCase):
    def test_data001_and_data005_have_incompatible_class_names_and_no_shared_boxes(self):
        summary = check_availability(ROOT / 'data' / 'manifests' / 'legacy_dataset_inventory.csv')
        self.assertGreater(summary['DATA-001']['n_rows'], 0)
        self.assertGreater(summary['DATA-005']['n_rows'], 0)
        self.assertTrue(summary['DATA-001']['has_boxes'])
        self.assertFalse(summary['DATA-005']['has_boxes'])
        self.assertNotEqual(set(summary['DATA-001']['class_names']),
                            set(summary['DATA-005']['class_names']))


class Cli(unittest.TestCase):
    def test_check_availability_writes_a_blocked_assessment_with_no_metrics(self):
        with TemporaryDirectory(dir=ROOT / 'reports') as tmp:
            out = Path(tmp) / 'assessment.md'
            done = run_cli('--check-availability', '--out', out)
            self.assertEqual(done.returncode, 0, done.stderr)
            text = out.read_text(encoding='utf-8')
            self.assertIn('BLOCKED_BY_GROUND_TRUTH', text)
            self.assertIn('DATA-001', text)
            self.assertIn('DATA-005', text)
            self.assertFalse(any(p.suffix == '.csv' for p in Path(tmp).iterdir()))

    def test_scoring_cli_writes_json_from_jsonl_inputs(self):
        with TemporaryDirectory(dir=ROOT / 'reports') as tmp:
            tmp = Path(tmp)
            annotations = tmp / 'gt.jsonl'
            predictions = tmp / 'pred.jsonl'
            annotations.write_text(json.dumps(gt_row(fruit_id='F1')) + '\n', encoding='utf-8')
            predictions.write_text(json.dumps(pred_row(predicted_label=D1)) + '\n', encoding='utf-8')
            out = tmp / 'scored.json'
            done = run_cli('--annotations', annotations, '--predictions', predictions, '--out', out)
            self.assertEqual(done.returncode, 0, done.stderr)
            result = json.loads(out.read_text(encoding='utf-8'))
            self.assertEqual(result['joint_recall'], {'successes': 1, 'denominator': 1, 'value': 1.0})

    def test_scoring_cli_rejects_model_prediction_ground_truth(self):
        with TemporaryDirectory(dir=ROOT / 'reports') as tmp:
            tmp = Path(tmp)
            annotations = tmp / 'gt.jsonl'
            predictions = tmp / 'pred.jsonl'
            annotations.write_text(
                json.dumps(gt_row(diagnostic_method='model_prediction')) + '\n', encoding='utf-8')
            predictions.write_text('', encoding='utf-8')
            out = tmp / 'scored.json'
            done = run_cli('--annotations', annotations, '--predictions', predictions, '--out', out)
            self.assertEqual(done.returncode, 2)
            self.assertIn('MODEL_PREDICTION_REJECTED', done.stderr)
            self.assertFalse(out.exists())

    def test_scoring_without_annotations_is_a_usage_error(self):
        with TemporaryDirectory(dir=ROOT / 'reports') as tmp:
            done = run_cli('--out', Path(tmp) / 'scored.json')
            self.assertEqual(done.returncode, 2)


if __name__ == '__main__':
    unittest.main()
