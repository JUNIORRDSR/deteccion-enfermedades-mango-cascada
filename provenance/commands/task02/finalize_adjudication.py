"""Consolidate the two blind answer files into the SPEC section 5 adjudication artifacts.

Also measures reviewer calibration on the controls, and copies the packets and
answers into the repository with hashes so the review is reproducible.
"""

import csv
import datetime
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.evaluation.provenance import authorized_root, check_output  # noqa: E402
from src.leakage_audit.adjudication import record  # noqa: E402

RELATED = {'NEAR_DUPLICATE', 'POSSIBLE_SEQUENCE_RELATION'}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(packet_root: Path, reviewer_identities: dict) -> int:
    root = authorized_root()
    audit = root / 'data/audits/model1'
    key = json.loads((audit / 'adjudication_key.json').read_text(encoding='utf-8'))
    answers = {}
    for reviewer in ('a', 'b'):
        payload = json.loads((packet_root / reviewer / 'answers.json').read_text(encoding='utf-8'))
        answers[reviewer] = payload['answers']
        expected = set(key['reviewers'][reviewer])
        if set(answers[reviewer]) != expected:
            missing = sorted(expected - set(answers[reviewer]))
            extra = sorted(set(answers[reviewer]) - expected)
            raise SystemExit(f'reviewer {reviewer}: missing {missing} extra {extra}')

    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    rows, pending = record(key, answers, reviewer_identities, stamp)

    def write(name: str, records: list[dict]) -> None:
        destination = check_output(root, audit / name)
        fields = list(records[0]) if records else ['candidate_id']
        with destination.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(records)

    write('adjudications.csv', rows)
    write('adjudication_resolution.csv', [
        {'candidate_id': r['candidate_id'], 'category': r['category'],
         'decision_a': r['decision_a'], 'decision_b': r['decision_b'],
         'status': 'PENDING_SEPARATE_ADJUDICATION', 'third_adjudicator': '',
         'final': '', 'evidence': '', 'rationale': ''} for r in pending])

    calibration = {}
    for reviewer in ('a', 'b'):
        column = f'decision_{reviewer}'
        positives = [r for r in rows if r['category'] == 'control_positive']
        negatives = [r for r in rows if r['category'] == 'control_negative']
        calibration[reviewer] = {
            'positive_controls_called_related': sum(r[column] in RELATED for r in positives),
            'positive_controls_total': len(positives),
            'negative_controls_called_unrelated': sum(r[column] == 'UNRELATED' for r in negatives),
            'negative_controls_total': len(negatives)}
        calibration[reviewer]['passed'] = (
            calibration[reviewer]['positive_controls_called_related'] == len(positives)
            and calibration[reviewer]['negative_controls_called_unrelated'] == len(negatives))

    archive = check_output(root, audit / 'blind_packets', allow_directory=True)
    if archive.exists():
        shutil.rmtree(archive)
    shutil.copytree(packet_root, archive)
    packet_hashes = {str(p.relative_to(archive)).replace(chr(92), '/'): sha(p)
                     for p in sorted(archive.rglob('*')) if p.is_file()}

    log = {
        'recorded_utc': stamp,
        'reviewers': reviewer_identities,
        'independence': ('Two separate agent instances of different model families, separate '
                         'folders, reviewer-specific question ids and orders, no access to each '
                         'other or to the key.'),
        'blinding_exceptions': [
            'Reviewers are agents with filesystem access. Blinding was enforced by instruction and '
            'by placing packets outside the repository, not by access control.',
            'The sequence cluster is shown in temporal order, which is necessary to judge '
            'continuity and reveals that the panels are ordered frames.',
            'The coordinator viewed one sheet of packet A (the sequence sheet) for render quality '
            'control before dispatch. No judgement was recorded or communicated to reviewers.',
            'Image content itself is shown unaltered; no split, class, filename or metric is '
            'rendered on any sheet.'],
        'controls': {'positive': 2, 'negative': 3,
                     'note': 'Not required by the SPEC. Indistinguishable from candidates.'},
        'calibration': calibration,
        'counts': {'candidates': len(rows), 'agree': sum(r['agreement'] == 'AGREE' for r in rows),
                   'disagree': len(pending)},
        'packet_sha256': packet_hashes,
        'interpretation': ('Agent agreement is operational evidence for a grouping decision. It is '
                           'not a biological label and not ground truth (SPEC section 5).'),
    }
    check_output(root, audit / 'blinding_log.json').write_text(
        json.dumps(log, indent=2) + chr(10), encoding='utf-8')
    print(json.dumps({'candidates': len(rows), 'pending': len(pending),
                      'calibration': calibration}, indent=2))
    return 0


if __name__ == '__main__':
    packets = Path(sys.argv[1])
    identities = {'a': sys.argv[2], 'b': sys.argv[3]}
    raise SystemExit(main(packets, identities))
