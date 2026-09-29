"""Write the JSON sidecar of PROTOCOL-AMENDMENT-008 (current version) from the current files.

`approved_code` holds the hashes the renderer requires (round-5 H-02): changing the trainer or
the job changes them, and so needs a new version and a new review."""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.evaluation.authority import snapshot  # noqa: E402
from src.evaluation.kaggle_job import (  # noqa: E402
    CAPACITY_PREFIX, EXPERIMENT_OF, PIP_CHECK_OK, PIP_CHECK_ROOTS, RETRY_POLICY,
)
MD = 'provenance/protocol_amendments/PROTOCOL-AMENDMENT-008-kaggle-compute.md'


def sha(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main(review: str | None = None) -> int:
    reviews = [
        {'version': 1, 'report': 'reports/amendments/amendment-008-independent-review.md',
         'verdict': 'DO_NOT_APPROVE', 'high': 6, 'medium': 3},
        {'version': 2, 'report': 'reports/amendments/amendment-008-independent-rereview.md',
         'verdict': 'DO_NOT_APPROVE', 'high': 5, 'medium': 4},
        {'version': 3, 'report': 'reports/amendments/amendment-008-independent-review-round3.md',
         'verdict': 'DO_NOT_APPROVE', 'high': 2, 'medium': 3},
        {'version': 4, 'report': 'reports/amendments/amendment-008-independent-review-round4.md',
         'report_sha256': sha('reports/amendments/amendment-008-independent-review-round4.md'),
         'verdict': 'DO_NOT_APPROVE', 'high': 2, 'medium': 2},
        {'version': 5, 'report': 'reports/amendments/amendment-008-independent-review-round5.md',
         'report_sha256': sha('reports/amendments/amendment-008-independent-review-round5.md'),
         'verdict': 'DO_NOT_APPROVE', 'high': 2, 'medium': 3},
        {'version': 6, 'report': 'reports/amendments/gate-review-exp-r01.md',
         'report_sha256': sha('reports/amendments/gate-review-exp-r01.md'),
         'part': 'A', 'verdict': 'DO_NOT_APPROVE', 'high': 1, 'medium': 2, 'low': 1},
        {'version': 7, 'report': 'reports/amendments/amendment-008-independent-review-round7.md',
         'report_sha256': sha('reports/amendments/amendment-008-independent-review-round7.md'),
         'verdict': 'DO_NOT_APPROVE', 'high': 1, 'medium': 2, 'low': 1},
        {'version': 8, 'report': 'reports/amendments/amendment-008-independent-review-round8.md',
         'report_sha256': sha('reports/amendments/amendment-008-independent-review-round8.md'),
         'verdict': 'APPROVE_EXP_R01_TRAINING', 'high': 0, 'medium': 0, 'low': 2},
    ]
    record = {
        'amendment_id': 'PROTOCOL-AMENDMENT-008', 'version': 8,
        'title': 'Kaggle compute venue for M1 training and inference',
        'recorded_at': '2026-09-23T12:00:00+00:00', 'state': 'APPROVED',
        'execution_permitted': ('EXP-R01 training, non-scientific probes, and the TASK-05 '
                                'inference sequence for the snapshot below'),
        'inference_approved': True,
        'inference_approval': {'version': 10, 'section': '5.1', 'state': 'APPROVED',
                               'review': 'reports/execution/task-05-independent-review-round12.md',
                               'review_sha256': sha('reports/execution/task-05-independent-review-round12.md'),
                               'decision': 'docs/research/decision_log.md DECISION-037, DECISION-039',
                               'approved_by': ('principal investigator in the session chat, '
                                               '2026-09-28, after twelve independent TASK-05 '
                                               'rounds; re-approved the same day for the '
                                               'DECISION-039 snapshot'),
                               'residual': ('NEW-HIGH-05 (round 12) was a python._pth planted in '
                                            'the .venv; it is refused since 42270fa, which no '
                                            'independent round re-reviewed. DECISION-039 (the '
                                            'executed source may carry the one cell marker the '
                                            'Kaggle web editor prepends) was not independently '
                                            'reviewed either. Every other finding is closed. '
                                            'Further local tampering routes on this machine '
                                            'remain a declared limitation, not an observed '
                                            'effect.'),
                               'responds_to': ['reports/execution/task-05-independent-review-round4.md',
                                               'reports/execution/task-05-independent-review-round5.md',
                                               'reports/execution/task-05-independent-review-round6.md',
                                               'reports/execution/task-05-independent-review-round7.md',
                                               'reports/execution/task-05-independent-review-round8.md',
                                               'reports/execution/task-05-independent-review-round9.md',
                                               'reports/execution/task-05-independent-review-round10.md',
                                               'reports/execution/task-05-independent-review-round11.md',
                                               'reports/execution/task-05-independent-review-round12.md'],
                               'm1': snapshot(ROOT, 'm1'), 'm2': snapshot(ROOT, 'm2')},
        'approval': {'scope': 'EXP-R01 training', 'version': 8,
                     'review': 'reports/amendments/amendment-008-independent-review-round8.md',
                     'recorded_at': '2026-09-27',
                     'inference': ('approved for the section 5.1 snapshot by the principal '
                                   'investigator on 2026-09-28 (inference_approval, DECISION-037, '
                                   're-approved for DECISION-039)')},
        'approved_code': {'trainer': 'src/evaluation/train_model1.py',
                          'trainer_sha256': sha('src/evaluation/train_model1.py'),
                          'job': 'src/evaluation/kaggle_job.py',
                          'job_sha256': sha('src/evaluation/kaggle_job.py')},
        'trust_root': {'freeze_record': 'data/manifests/model1_clean_manifest.freeze.json',
                       'checked_by': 'check_bindings before rendering; verify_receipt after the run'},
        'session_limit': {'seconds': 43200, 'source': 'https://www.kaggle.com/docs/notebooks',
                          'accessed': '2026-09-23'},
        'approval_scope': ('EXP-R01 training; the TASK-05 inference sequence (EXP-V01, the '
                           'operating-point freeze, EXP-R02, EXP-R03 and the interval commands) '
                           'for the exact inference_approval snapshot'),
        'closure_authority': 'Only an independent review may record closure.',
        'base_protocol': {'protocol_id': 'ALBUS26-116-PROTOCOL-001',
                          'commit': '7d0f9985cce73740cfa2ae26154971b55282ad52',
                          'sha256_json': sha('provenance/protocol_freeze.json'),
                          'sha256_md': sha('provenance/protocol_freeze.md'),
                          'modified_by_this_amendment': False},
        'modifies': ['SPEC section 7: training environment inside the workspace',
                     'plan TASK-04: propose CPU if it is the only device'],
        'user_decision': ['DECISION-031', 'DECISION-033'],
        'local_cpu_viable': True,
        'local_cpu_evidence': 'DECISION-030, reports/execution/cpu_capacity_probe.json',
        'inputs': {'uploads': 0, 'attached_datasets_in_training': 0,
                   'source_repo': 'DANN-MAGE/SemilleroTI-Mangos',
                   'source_commit': '98614804dd967e19a77af9fc58c27364d2e43bc9',
                   'job': 'src/evaluation/kaggle_job.py', 'job_sha256': sha('src/evaluation/kaggle_job.py'),
                   'renderer': 'provenance/commands/task04/render_kaggle_job.py',
                   'renderer_sha256': sha('provenance/commands/task04/render_kaggle_job.py'),
                   'verifier': 'provenance/commands/task04/verify_kaggle_run.py',
                   'verifier_sha256': sha('provenance/commands/task04/verify_kaggle_run.py'),
                   'tests': 'tests/test_kaggle_job.py', 'tests_sha256': sha('tests/test_kaggle_job.py'),
                   'verifier_tests': 'tests/test_verify_kaggle_run.py',
                   'verifier_tests_sha256': sha('tests/test_verify_kaggle_run.py')},
        'base_checkpoint': {'artifact_id': 'ART-106',
                            'url': 'https://github.com/ultralytics/assets/releases/download/v8.4.0/yolo26n.pt',
                            'sha256': '9b09cc8bf347f0fc8a5f7657480587f25db09b34bf33b0652110fb03a8ad4fef',
                            'size': 5544453},
        'probe': {'experiment_id': 'KAGGLE-PROBE-001',
                  'kernel': 'jorgesolanodev/albus26-m1-kaggle-probe-001', 'kernel_id': 135462618,
                  'version': 1, 'status': 'COMPLETE', 'model_built': False, 'inference': False,
                  'receipt': 'experiments/model1/KAGGLE-PROBE-001/receipt.json',
                  'receipt_sha256': sha('experiments/model1/KAGGLE-PROBE-001/receipt.json'),
                  'deviation': ('run before approval, against the v4 text, at the explicit user '
                                'request to validate feasibility')},
        'test_discipline': {
            'custodian': None,
            'controls': ['no free parameter in the test session',
                         'sealed commit of configs/evaluation_frozen.json before the test kernel exists',
                         'single kernel albus26-m1-exp-r02; later versions only as retry_policy allows',
                         'account kernel list before and after', 'provenance/test_access_log.csv'],
            'residual': 'no independent custodian, identical to the local venue; declared as a limitation'},
        'retry_policy': RETRY_POLICY,
        'experiments': {'by_mode': EXPERIMENT_OF, 'capacity_prefix': CAPACITY_PREFIX},
        'attempt_layout': {'directory': 'experiments/model1/<EXP>/v<N>/',
                           'ledger': 'experiments/model1/<EXP>/attempts.jsonl',
                           'reconciled_by': 'provenance/commands/task04/verify_kaggle_run.py',
                           'enforced_by': 'render_kaggle_job.attempt_dir and kaggle_job.check_attempt'},
        'pip_check_rule': {'roots': list(PIP_CHECK_ROOTS),
                           'blocks': 'an unparsed line, or a conflict whose dependent package is '
                                     'in the dependency closure of the roots',
                           'exit_zero_accepts': ['', PIP_CHECK_OK],
                           'stage': 'environment, before any data download'},
        'capacity_evidence': {'dir': 'experiments/model1/KAGGLE-CAPACITY-001',
                              'retained': 'evidence/, platform.json, platform_log.json, attempts.jsonl',
                              'checked_by': 'render_kaggle_job.capacity_retained before EXP-R01'},
        'test_exposure': {'observed_before_freeze': True, 'log': 'provenance/test_access_log.csv'},
        'retired_v4_artifacts': ['src/evaluation/kaggle_inputs.py', 'tests/test_kaggle_inputs.py',
                                 'configs/kaggle_input_schema.json', 'configs/capacity_plan.json',
                                 'configs/prediction_transfer_schema.json'],
        'independent_reviews': reviews,
        'runs_must_cite': ['7d0f9985cce73740cfa2ae26154971b55282ad52',
                           'PROTOCOL-AMENDMENT-008 version 8'],
        'document': {'path': MD, 'sha256': sha(MD)},
    }
    (ROOT / 'provenance/protocol_amendments/PROTOCOL-AMENDMENT-008-kaggle-compute.json').write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(record['document']['sha256'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main(*sys.argv[1:]))
