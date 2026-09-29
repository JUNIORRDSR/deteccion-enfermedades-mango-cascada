"""Record the supplementary blind adjudication (DECISION-034) under the SPEC section 5 contract.

record  : both answer files -> supplementary_adjudications.csv, controls, blinding log, and a
          third-adjudicator packet (reviewer c) holding ONLY the disagreements.
resolve : reviewer c answers -> supplementary_resolution.csv and supplementary_relations.csv,
          the pairwise edges passed to the split (PENDING rows would block it).

Original A/B decisions are never overwritten; the third decision is stored beside them.
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

from src.leakage_audit.adjudication import (  # noqa: E402
    NOT_FOR_VISUAL_USE, PAIR_QUESTION, VISUAL_MENU, _sheet, record,
)
from src.leakage_audit.audit import PENDING  # noqa: E402

AUDIT = ROOT / 'data/audits/model1'
REVIEWERS = {'a': 'reviewer-A (claude-opus subagent)', 'b': 'reviewer-B (claude-sonnet subagent)',
             'c': 'reviewer-C (fresh claude-opus subagent, no access to A or B), third adjudicator'}
RELATED = {'NEAR_DUPLICATE', 'POSSIBLE_SEQUENCE_RELATION'}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def do_record(packets: Path) -> int:
    key = json.loads((AUDIT / 'supplementary_key.json').read_text(encoding='utf-8'))
    answers = {r: json.loads((packets / r / 'answers.json').read_text(encoding='utf-8'))['answers']
               for r in ('a', 'b')}
    for r in ('a', 'b'):
        if set(answers[r]) != set(key['reviewers'][r]):
            raise SystemExit(f'reviewer {r} did not answer every question')
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    rows, pending = record(key, answers, {r: REVIEWERS[r] for r in 'ab'}, stamp)
    write_csv(AUDIT / 'supplementary_adjudications.csv', rows)

    calibration = {}
    for r in ('a', 'b'):
        column = f'decision_{r}'
        pos = [row[column] in RELATED for row in rows if row['category'] == 'control_positive']
        neg = [row[column] == 'UNRELATED' for row in rows if row['category'] == 'control_negative']
        calibration[r] = {'positive_called_related': sum(pos), 'positive_total': len(pos),
                          'negative_called_unrelated': sum(neg), 'negative_total': len(neg)}

    kept = AUDIT / 'supplementary_packets'
    hashes = {}
    for r in ('a', 'b'):
        (kept / r).mkdir(parents=True, exist_ok=True)
        for item in sorted((packets / r).iterdir()):
            if not item.is_file():  # reviewer working folders (zoomed crops) are not evidence
                continue
            hashes[f'{r}/{item.name}'] = sha(item)
            if item.suffix == '.json':
                shutil.copyfile(item, kept / r / item.name)

    # Third adjudicator packet: only the disagreements, new opaque ids, fresh order.
    inventory = {row['source_id']: row for row in csv.DictReader(
        open(ROOT / 'data/manifests/legacy_dataset_inventory.csv', encoding='utf-8-sig'))}
    legacy = Path(json.loads((ROOT / 'configs/root_mapping.json').read_text(encoding='utf-8'))
                  ['legacy_corpus'])
    third = packets / 'c'
    third.mkdir(parents=True, exist_ok=True)
    questions, mapping = [], {}
    for position, row in enumerate(sorted(pending, key=lambda x: hashlib.sha256(
            f"c|{x['candidate_id']}".encode()).hexdigest()), start=1):
        qid = 'Q-' + hashlib.sha256(f"c|{row['candidate_id']}".encode()).hexdigest()[:10]
        members = row['member_ids'].split(';')
        _sheet([legacy / inventory[m]['relative_path'] for m in members], third / f'{qid}.png',
               columns=2, tile=384)
        questions.append({'question_id': qid, 'position': position, 'sheet': f'{qid}.png',
                          'panels': 2, 'kind': 'pair', 'question': PAIR_QUESTION})
        mapping[qid] = row['candidate_id']
    (third / 'questions.json').write_text(json.dumps({
        'reviewer': 'C',
        'instructions': ('Judge only what you see. Answer every question with exactly one '
                         'answer from answer_menu, a one-sentence rationale naming the visual '
                         'evidence, and a confidence of low, medium or high.'),
        'answer_menu': VISUAL_MENU, 'do_not_use': NOT_FOR_VISUAL_USE,
        'questions': questions}, indent=2), encoding='utf-8')
    log = {'recorded_utc': stamp, 'reviewers': REVIEWERS, 'units': len(rows),
           'agree': len(rows) - len(pending), 'disagree': len(pending),
           'calibration_against_prior_adjudication': calibration,
           'third_adjudicator_key': mapping,
           'blinding_exceptions': [
               'Reviewers are agents with filesystem access; blinding by instruction and by '
               'packets outside the repository, not by access control.',
               'Controls are consistency checks against earlier two-reviewer decisions, not '
               'biological ground truth.',
               'The coordinator rendered the sheets and did not view reviewer answers before '
               'both files were complete.'],
           'packet_sha256': hashes}
    (AUDIT / 'supplementary_blinding_log.json').write_text(json.dumps(log, indent=2) + '\n',
                                                           encoding='utf-8')
    print(json.dumps({k: log[k] for k in ('units', 'agree', 'disagree',
                                          'calibration_against_prior_adjudication')}, indent=2))
    return 0


def do_resolve(packets: Path) -> int:
    log = json.loads((AUDIT / 'supplementary_blinding_log.json').read_text(encoding='utf-8'))
    rows = list(csv.DictReader(open(AUDIT / 'supplementary_adjudications.csv', encoding='utf-8')))
    mapping = log['third_adjudicator_key']
    finals = {}
    if mapping:
        answers = json.loads((packets / 'c' / 'answers.json').read_text(encoding='utf-8'))['answers']
        if set(answers) != set(mapping):
            raise SystemExit('reviewer c did not answer every question')
        resolution = []
        for qid, cid in sorted(mapping.items(), key=lambda kv: kv[1]):
            answer = answers[qid]
            if answer['decision'] not in VISUAL_MENU:
                raise SystemExit(f'{cid}: {answer["decision"]!r} is not on the visual menu')
            row = next(r for r in rows if r['candidate_id'] == cid)
            finals[cid] = answer['decision']
            resolution.append({'candidate_id': cid, 'category': row['category'],
                               'decision_a': row['decision_a'], 'decision_b': row['decision_b'],
                               'status': 'RESOLVED_BY_THIRD_ADJUDICATION',
                               'third_adjudicator': REVIEWERS['c'], 'final': answer['decision'],
                               'evidence': f"blind sheet {qid}: {answer.get('rationale', '')}",
                               'rationale': f"confidence {answer.get('confidence', '')}"})
        write_csv(AUDIT / 'supplementary_resolution.csv', resolution)
        (AUDIT / 'supplementary_packets' / 'c').mkdir(parents=True, exist_ok=True)
        shutil.copyfile(packets / 'c' / 'answers.json',
                        AUDIT / 'supplementary_packets' / 'c' / 'answers.json')
    edges = list(csv.DictReader(open(AUDIT / 'extra_relations.csv', encoding='utf-8')))
    for row in rows:
        if row['category'].startswith('control'):
            continue
        final = finals.get(row['candidate_id'], row['final_adjudication'])
        a, b = row['member_ids'].split(';')
        edges.append({'source_id_a': a, 'source_id_b': b, 'final': final,
                      'evidence': f"{row['candidate_id']} supplementary adjudication"})
    if any(e['final'] == PENDING for e in edges):
        raise SystemExit('a supplementary relation is still pending')
    write_csv(AUDIT / 'supplementary_relations.csv', edges)
    counts = {}
    for e in edges:
        counts[e['final']] = counts.get(e['final'], 0) + 1
    print(json.dumps(counts, indent=2))
    return 0


if __name__ == '__main__':
    mode, packets = sys.argv[1], Path(sys.argv[2])
    raise SystemExit(do_record(packets) if mode == 'record' else do_resolve(packets))
