"""Regenerate the machine-readable amendment sidecar for version 3.

Addresses N-02: the sidecar must not assert closure. Remediation is recorded as
claimed and pending independent review; closure is recorded only from a review
outcome, with its report hash and counts.
"""

import csv
import datetime
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.evaluation.provenance import authorized_root, check_output  # noqa: E402

BASE = '7d0f9985cce73740cfa2ae26154971b55282ad52'
DOC = 'provenance/protocol_amendments/PROTOCOL-AMENDMENT-008-kaggle-compute.md'
REVIEW_V1 = 'reports/amendments/amendment-008-independent-review.md'
REVIEW_V2 = 'reports/amendments/amendment-008-independent-rereview.md'
REVIEW_V3 = 'reports/amendments/amendment-008-independent-review-round3.md'


def sha(relative: str) -> str:
    return hashlib.sha256(Path(relative).read_bytes()).hexdigest()


def main() -> int:
    accesses = list(csv.DictReader(open('provenance/test_access_log.csv', encoding='utf-8-sig')))
    record = {
        'amendment_id': 'PROTOCOL-AMENDMENT-008',
        'version': 4,
        'title': 'Sede de computo para entrenamiento e inferencia',
        'recorded_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'state': 'PROPOSED_V4',
        'execution_permitted': False,
        'closure_authority': ('Only an independent review may record closure. Fields below record '
                              'CLAIMED remediation, pending that review (finding N-02).'),
        'base_protocol': {
            'protocol_id': 'ALBUS26-116-PROTOCOL-001', 'commit': BASE,
            'sha256_json': sha('provenance/protocol_freeze.json'),
            'sha256_md': sha('provenance/protocol_freeze.md'),
            'modified_by_this_amendment': False},
        'material_change': {
            'is_material': True,
            'what': 'Execution venue for TASK-04 training and TASK-05 GPU inference moves to Kaggle.',
            'unchanged': ['seeds', 'checkpoint selection rule', 'operating point from validation F2',
                          'single test evaluation', 'no metric floor in software tests',
                          'failures preserved', 'SPEC section 11 stop rules']},
        'test_exposure': {
            'observed_before_freeze': True,
            'new_access_since_freeze': False,
            'log': 'provenance/test_access_log.csv',
            'existing_entries': [row['access_id'] for row in accesses]},
        'user_decision': {
            'decision_id': 'DECISION-028', 'date': '2026-09-21',
            'record': 'provenance/authorizations/2026-09-21-kaggle-compute-authorization.md',
            'sha256': sha('provenance/authorizations/2026-09-21-kaggle-compute-authorization.md'),
            'satisfies': 'SPEC section 11 global stop rule 1, external action'},
        'independent_reviews': [
            {'version_reviewed': 1, 'report': REVIEW_V1, 'sha256': sha(REVIEW_V1),
             'verdict': 'DO NOT APPROVE', 'open_findings': {'HIGH': 6, 'MEDIUM': 3, 'LOW': 0}},
            {'version_reviewed': 2, 'report': REVIEW_V2, 'sha256': sha(REVIEW_V2),
             'verdict': 'DO NOT APPROVE', 'open_findings': {'HIGH': 5, 'MEDIUM': 4, 'LOW': 0},
             'new_findings': {'N-01': 'HIGH, historical Kaggle venue promoted beyond the evidence',
                              'N-02': 'MEDIUM, machine-readable record declared closure before review'},
             'closed_by_reviewer': ['H-04']},
            {'version_reviewed': 3, 'report': REVIEW_V3, 'sha256': sha(REVIEW_V3),
             'verdict': 'DO NOT APPROVE', 'open_findings': {'HIGH': 2, 'MEDIUM': 3, 'LOW': 0},
             'new_findings': {'N-03': 'MEDIUM, CPU context probe reported PASS despite a failed probe'},
             'closed_by_reviewer': ['H-01', 'H-04', 'H-05', 'H-06', 'N-01', 'N-02']},
            {'version_reviewed': 4, 'report': None, 'verdict': 'PENDING'}],
        'claimed_remediation_pending_independent_review': {
            'H-01': 'formal record plus this sidecar; v2 review outcome now recorded; state stays PROPOSED',
            'H-02': 'the schema, validator and 15 positive/negative fixtures NOW EXIST and are runnable: '
                    'configs/kaggle_input_schema.json, src/evaluation/kaggle_inputs.py, '
                    'tests/test_kaggle_inputs.py. Closed root contract, closed indirection grammar, '
                    'null effective version fatal, unknown extension rejected not ignored',
            'H-03': 'no custodian is designated and no signing key is configured, so the TASK-05 test phase '
                    'is declared BLOCKED_BY_CUSTODIAN rather than pretending an approved procedure exists. '
                    'Signed annotated git tag with exact seal and verify commands. Retry taxonomy narrowed to '
                    'two causes, both requiring external evidence; quota exhaustion removed as a retry cause. '
                    'Platform reconciliation claim narrowed to what the public interface exposes, plus an '
                    'independently retained launch and access log',
            'H-04': 'CLOSED by the version 2 independent review',
            'H-05': 'upload remains blocked; opaque filenames, sanitized archive members and sidecars, '
                    'explicit EXIF/IPTC/XMP removal, visual review, byte-for-byte upload receipt',
            'H-06': 'historical venue downgraded to unverified; see N-01',
            'M-01': 'configs/capacity_plan.json freezes the workload, measured epochs, warm-up exclusion, '
                    'estimator, safety factor 1.35 fixed before measuring, three pass/fail inequalities, '
                    'variance and preemption handling, probe model discard rule, and the API scope check; '
                    'a denied datasets.get scope is already recorded as a capacity fact',
            'M-02': 'configs/prediction_transfer_schema.json serialises coordinates, dtypes, NaN/Inf as fatal, '
                    'post-NMS authority, score floor, class order, completeness with explicit no-detection '
                    'records, binding hashes and tolerances, and names one authoritative evaluator while '
                    'declaring the framework built-in non-authoritative',
            'M-03': 'cpu_topology_probe.json preserves command, exit code, stderr and raw output per probe '
                    'with MEASURED or UNAVAILABLE state',
            'N-03': 'the probe now fails on empty stdout or non-empty stderr, runs with ErrorActionPreference '
                    'Stop, and reports PARTIAL with exit 1 because the power plan query returns empty on this '
                    'host; it is declared UNAVAILABLE instead of counted as success',
            'N-01': 'historical execution venue reclassified as UNVERIFIED; Kaggle-shaped paths in saved '
                    'configuration are CIRCUMSTANTIAL only; the venue argument is no longer used as a '
                    'justification for the amendment',
            'N-02': 'this sidecar no longer asserts closure; the headings say responde a, not cierra'},
        'evidence': {
            'local_gpu_absent': {'source': 'provenance/environment/hardware.json',
                                 'torch': '2.12.0+cpu', 'cuda_available': False, 'status': 'OBSERVED'},
            'local_cpu': {'source': 'provenance/environment/cpu_topology_probe.json',
                          'processor_name_string': 'AMD Ryzen 5 7520U with Radeon Graphics',
                          'physical_cores': 4, 'logical_cores': 8,
                          'raw_output_preserved': True, 'status': 'OBSERVED'},
            'kaggle_quota': {'source': 'provenance/environment/kaggle_capability.json',
                             'gpu_seconds_available': 108000, 'status': 'OBSERVED_NOT_DURABLE'},
            'historical_venue': {
                'kaggle_shaped_paths_in_saved_config': True,
                'sources': ['provenance/experiment_registry.csv EXP-001 dataset field',
                            'reports/experiments/checkpoint_static_metadata.json train_args',
                            'reports/experiments/SemilleroTI-Mangos_best_pickle_opcodes.txt'],
                'status': 'CIRCUMSTANTIAL',
                'execution_venue_status': 'UNVERIFIED',
                'correction': ('Version 2 classified this as OBSERVED and used it as a justification. '
                               'That was an overreach, symmetric to the version 1 error about the 2xT4. '
                               'A saved path is configuration provenance, not authenticated execution '
                               'provenance, and the original notebook, manifest, invocation, environment '
                               'and hardware log are all recorded as missing.'),
                'promotion_requires': ['authenticated Kaggle kernel or notebook id and version',
                                       'attached dataset version', 'platform execution log']},
            'historical_accelerator': {
                'source': 'provenance/experiment_registry.csv EXP-001 hardware field',
                'verified': 'device=0,1', 'claimed_only': '2 x NVIDIA T4 / Kaggle, per the PDF',
                'status': 'UNVERIFIED'},
            'ultralytics_network_probe_at_import': {
                'source': 'provenance/environment/runtime_path_report.json', 'value': True,
                'mitigation': 'YOLO_OFFLINE=true recorded for the run; is_online returns false rather '
                              'than aborting import'},
            'ultralytics_yaml_can_execute_code': {
                'source': 'ultralytics/data/utils.py in the pinned 8.4.52',
                'value': True,
                'mitigation': 'generated yaml has no download field, validator rejects it, '
                              'autodownload disabled, containment checked before any resolver side effect'}},
        'blocking_prerequisites': [
            'independent review of version 3 with zero open HIGH and MEDIUM',
            'DATA-001 licence coverage and DATA-004/005 identity resolved before any upload',
            'TASK-02 audit verdict on whether retraining is warranted',
            'non-test capacity preflight plus the pass/fail rule of section 7.2'],
        'artifact_ids': {'base_checkpoint': 'ART-106',
                         'note': 'ART-005 proposed in version 1 is the historical args.yaml; corrected'},
        'runs_must_cite': [BASE, 'PROTOCOL-AMENDMENT-008 version 3'],
    }
    record['frozen_mechanisms'] = {
        name: {'path': name, 'sha256': sha(name)} for name in (
            'configs/kaggle_input_schema.json', 'src/evaluation/kaggle_inputs.py',
            'tests/test_kaggle_inputs.py', 'configs/capacity_plan.json',
            'configs/prediction_transfer_schema.json')}
    record['blocking_prerequisites'].append(
        'designate a custodian and signing key, or the TASK-05 test phase stays BLOCKED_BY_CUSTODIAN')
    record['runs_must_cite'] = [BASE, 'PROTOCOL-AMENDMENT-008 version 4']
    record['document'] = {'path': DOC, 'sha256': sha(DOC)}
    out = check_output(authorized_root(),
                       Path('provenance/protocol_amendments/PROTOCOL-AMENDMENT-008-kaggle-compute.json'))
    out.write_text(json.dumps(record, indent=2, ensure_ascii=False) + chr(10), encoding='utf-8')
    print(json.dumps({'state': record['state'], 'execution_permitted': record['execution_permitted'],
                      'venue_status': record['evidence']['historical_venue']['execution_venue_status'],
                      'document_sha256': record['document']['sha256']}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
