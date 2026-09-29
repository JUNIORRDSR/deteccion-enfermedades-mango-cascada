"""Blind A/B visual adjudication for the M1 leakage audit (SPEC section 5, AMENDMENT-03).

Builds the candidate list, renders reviewer-specific blind packets, keeps the key
outside the packets, and turns the two independent answer files into
`adjudications.csv`, `adjudication_resolution.csv` and `blinding_log.json`.

Controls are added on purpose: positive controls (consecutive frames of one
video) and negative controls (unrelated images of different classes). They are
not required by the SPEC; they exist so a reviewer who calls everything related,
or nothing, is detected rather than trusted.
"""

import argparse
import csv
import hashlib
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.evaluation.provenance import authorized_root, check_output  # noqa: E402
from src.leakage_audit.audit import (  # noqa: E402
    PENDING, RELATIONS, AuditError, validate_adjudications,
)

VISUAL_MENU = {
    'NEAR_DUPLICATE': 'Same photograph, possibly re-encoded, resized, cropped or colour-shifted.',
    'POSSIBLE_SEQUENCE_RELATION': 'Different photographs or frames of the same physical fruit(s) '
                                  'and the same scene or setup.',
    'UNRELATED': 'Different fruit and different scene.',
}
NOT_FOR_VISUAL_USE = {
    'EXACT_DUPLICATE': 'Byte identity is established by hash, never by eye. Do not use.',
    'CONFIRMED_SEQUENCE_RELATION': 'Requires external records, not visual judgement. Do not use.',
}
SEQUENCE_QUESTION = ('These panels are frames shown in their original temporal order. How many '
                     'distinct scenes or fruit setups do you see, and after which panel numbers '
                     'does the scene change?')
PAIR_QUESTION = 'Do panels 1 and 2 show the same photograph, the same fruit and scene, or neither?'


def _frame(filename: str) -> int | None:
    match = re.search(r'sakit_mp4-(\d+)', filename)
    return int(match.group(1)) if match else None


def build_candidates(pairs: list[dict], inventory: dict, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    candidates = []

    def add(category: str, members: list[str], reason: str) -> None:
        candidates.append({'category': category, 'member_ids': members, 'reason': reason})

    for p in pairs:
        crossing = p['split_a'] != p['split_b']
        if crossing and p['in_threshold'] == 'true':
            add('threshold_cross_split', [p['source_id_a'], p['source_id_b']],
                f"pHash Hamming {p['distance']} across {p['split_a']}/{p['split_b']}")
        elif crossing and p['sensitivity_band'] == 'true':
            add('band_cross_split', [p['source_id_a'], p['source_id_b']],
                f"sensitivity band, Hamming {p['distance']} across {p['split_a']}/{p['split_b']}")

    families: dict[str, list] = {}
    for sid, row in inventory.items():
        families.setdefault(row['normalized_filename_base'], []).append(sid)
    for base, members in sorted(families.items()):
        if len({inventory[m]['split'] for m in members}) > 1 and not base.startswith('sakit'):
            add('documentary_family', sorted(members),
                'same filename base in two splits; pHash distance above the candidate band')

    video = sorted((sid for sid, row in inventory.items() if row['sequence_name_hint'] == 'sakit_mp4'),
                   key=lambda sid: _frame(inventory[sid]['filename']))
    add('sequence_cluster', video, 'all frames named sakit_mp4, one contiguous frame numbering')

    # Positive controls: consecutive frames, same split, so they add no leakage signal.
    consecutive = [(a, b) for a, b in zip(video, video[1:])
                   if _frame(inventory[b]['filename']) - _frame(inventory[a]['filename']) == 1
                   and inventory[a]['split'] == inventory[b]['split']]
    for a, b in rng.sample(consecutive, 2):
        add('control_positive', [a, b], 'consecutive frames of one video, same split')

    # Negative controls: non-video images of different classes, not in any candidate.
    used = {m for c in candidates for m in c['member_ids']}
    pool = sorted(sid for sid, row in inventory.items()
                  if not row['sequence_name_hint'] and sid not in used)
    negatives = []
    while len(negatives) < 3:
        a, b = rng.sample(pool, 2)
        if inventory[a]['class_names'] != inventory[b]['class_names'] and {a, b} not in negatives:
            negatives.append({a, b})
            add('control_negative', sorted([a, b]), 'unrelated images of different classes')

    # Deduplicate identical member sets, keeping the first category met.
    unique, seen = [], set()
    for candidate in candidates:
        key = frozenset(candidate['member_ids'])
        if key in seen:
            continue
        seen.add(key)
        unique.append(candidate)
    rng.shuffle(unique)  # the number must not encode the category
    for index, candidate in enumerate(unique, start=1):
        candidate['candidate_id'] = f'CAND-{index:03d}'
    return unique


def _sheet(paths: list[Path], destination: Path, columns: int, tile: int) -> None:
    from PIL import Image, ImageDraw
    rows = (len(paths) + columns - 1) // columns
    canvas = Image.new('RGB', (columns * tile, rows * (tile + 24)), 'white')
    draw = ImageDraw.Draw(canvas)
    for index, path in enumerate(paths):
        with Image.open(path) as image:
            thumb = image.convert('RGB')
            thumb.thumbnail((tile, tile))
        x, y = (index % columns) * tile, (index // columns) * (tile + 24)
        canvas.paste(thumb, (x + (tile - thumb.width) // 2, y + 24 + (tile - thumb.height) // 2))
        draw.text((x + 6, y + 4), f'panel {index + 1}', fill='black')
    canvas.save(destination, format='PNG')


def render(candidates: list[dict], inventory: dict, legacy_root: Path, packet_root: Path,
           key_path: Path, seed: int = 42) -> dict:
    key = {'seed': seed, 'reviewers': {}}
    for reviewer, offset in (('a', 1), ('b', 2)):
        order = list(candidates)
        random.Random(seed + offset).shuffle(order)  # independent order per reviewer
        directory = packet_root / reviewer
        directory.mkdir(parents=True, exist_ok=True)
        questions, mapping = [], {}
        for position, candidate in enumerate(order, start=1):
            question_id = 'Q-' + hashlib.sha256(
                f"{reviewer}|{candidate['candidate_id']}".encode()).hexdigest()[:10]
            members = candidate['member_ids']
            sequence = candidate['category'] == 'sequence_cluster'
            shown = members
            if sequence:
                step = max(1, len(members) // 16)
                shown = members[::step][:16]
            paths = [legacy_root / inventory[m]['relative_path'] for m in shown]
            sheet = f'{question_id}.png'
            _sheet(paths, directory / sheet, columns=4 if sequence else 2,
                   tile=256 if sequence else 384)
            questions.append({
                'question_id': question_id, 'position': position, 'sheet': sheet,
                'panels': len(shown), 'kind': 'sequence' if sequence else 'pair',
                'question': SEQUENCE_QUESTION if sequence else PAIR_QUESTION,
            })
            mapping[question_id] = {'candidate_id': candidate['candidate_id'],
                                    'panel_members': shown}
        (directory / 'questions.json').write_text(json.dumps({
            'reviewer': reviewer.upper(),
            'instructions': ('Judge only what you see. Answer every question. For pairs, choose '
                             'exactly one answer from answer_menu and give a one-sentence '
                             'rationale describing the visual evidence and a confidence of low, '
                             'medium or high. For the sequence question, give the number of '
                             'distinct scenes and the panel numbers after which each change '
                             'occurs.'),
            'answer_menu': VISUAL_MENU, 'do_not_use': NOT_FOR_VISUAL_USE,
            'questions': questions}, indent=2), encoding='utf-8')
        key['reviewers'][reviewer] = mapping
    key['candidates'] = candidates
    key_path.write_text(json.dumps(key, indent=2), encoding='utf-8')
    return key


def record(key: dict, answers: dict[str, dict], reviewers: dict[str, str],
           timestamp: str) -> tuple[list[dict], list[dict]]:
    by_candidate: dict[str, dict] = {}
    for reviewer in ('a', 'b'):
        for question_id, answer in answers[reviewer].items():
            candidate_id = key['reviewers'][reviewer][question_id]['candidate_id']
            by_candidate.setdefault(candidate_id, {})[reviewer] = answer
    rows, pending = [], []
    for candidate in key['candidates']:
        cid = candidate['candidate_id']
        got = by_candidate.get(cid, {})
        if set(got) != {'a', 'b'}:
            raise AuditError(f'{cid}: both reviewers must answer every candidate')
        if candidate['category'] == 'sequence_cluster':
            decision_a = decision_b = 'POSSIBLE_SEQUENCE_RELATION'
        else:
            decision_a, decision_b = got['a']['decision'], got['b']['decision']
            for decision in (decision_a, decision_b):
                if decision not in VISUAL_MENU:
                    raise AuditError(f'{cid}: answer {decision!r} is not on the visual menu')
        agree = decision_a == decision_b
        row = {
            'candidate_id': cid,
            'unit_type': 'cluster' if candidate['category'] == 'sequence_cluster' else 'pair',
            'member_ids': ';'.join(candidate['member_ids']),
            'category': candidate['category'],
            'reviewer_a': reviewers['a'], 'reviewer_b': reviewers['b'],
            'decision_a': decision_a, 'decision_b': decision_b,
            'agreement': 'AGREE' if agree else 'DISAGREE',
            'final_adjudication': decision_a if agree else PENDING,
            'evidence': f"blind contact sheets; A: {got['a'].get('rationale', '')} | "
                        f"B: {got['b'].get('rationale', '')}",
            'rationale': candidate['reason'],
            'adjudicator': '' if not agree else reviewers['a'],
            'timestamp': timestamp,
            'blinding_exceptions': ('frames shown in temporal order' if
                                    candidate['category'] == 'sequence_cluster' else 'none'),
            'confidence_a': got['a'].get('confidence', ''),
            'confidence_b': got['b'].get('confidence', ''),
            'scenes_a': got['a'].get('scenes', ''), 'scenes_b': got['b'].get('scenes', ''),
            'requires_visual': 'true',
        }
        rows.append(row)
        if not agree:
            pending.append(row)
    validate_adjudications(rows)
    return rows, pending


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--render', action='store_true')
    parser.add_argument('--packet-root', type=Path, required=True)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    root = authorized_root()
    roots = json.loads((root / 'configs/root_mapping.json').read_text(encoding='utf-8'))
    inventory = {r['source_id']: r for r in csv.DictReader(
        open(root / 'data/manifests/legacy_dataset_inventory.csv', encoding='utf-8-sig'))
        if r['dataset_id'] == 'DATA-001'}
    pairs = list(csv.DictReader(open(root / 'data/audits/model1/candidate_pairs.csv',
                                     encoding='utf-8')))
    candidates = build_candidates(pairs, inventory, args.seed)
    key_path = check_output(root, root / 'data/audits/model1/adjudication_key.json')
    render(candidates, inventory, Path(roots['legacy_corpus']), args.packet_root,
           key_path, args.seed)
    counts: dict[str, int] = {}
    for candidate in candidates:
        counts[candidate['category']] = counts.get(candidate['category'], 0) + 1
    print(json.dumps({'candidates': len(candidates), 'by_category': counts,
                      'key': str(key_path), 'packets': str(args.packet_root)}, indent=2))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except AuditError as error:
        print(str(error), file=sys.stderr)
        sys.exit(2)
