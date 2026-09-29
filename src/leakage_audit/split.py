"""TASK-03: atomic group split with the single algorithm frozen in SPEC section 6.

One deterministic assignment, no seed sweep. Groups are never broken to hit a
ratio. If a class is absent from validation or test, or a class has fewer than
two independent groups there, the partition is BLOCKED and documented instead of
being adjusted until it passes.
"""

import argparse
import csv
import hashlib
import json
import random
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.evaluation.provenance import authorized_root, check_output, sha256  # noqa: E402

SPLITS = ('train', 'valid', 'test')
CLASSES = ('Enfermo', 'Saludable')
RELATED = {'NEAR_DUPLICATE', 'POSSIBLE_SEQUENCE_RELATION', 'EXACT_DUPLICATE',
           'CONFIRMED_SEQUENCE_RELATION'}
PENDING = 'PENDING_SEPARATE_ADJUDICATION'
MANIFEST_FIELDS = ('image_id', 'path', 'label', 'sha256', 'phash', 'source', 'sequence_id',
                   'cluster_id', 'original_split', 'proposed_split', 'label_sha256', 'group_id',
                   'group_status', 'logical_root', 'logical_path', 'local_absolute_path')
SOURCE = 'mangoUnhealty v2, Roboflow jairos-workspace-cbeeq/mangounhealty/2, CC BY 4.0'


class SplitBlocked(Exception):
    """The frozen rules forbid this partition. Documented, never retried with another seed."""


def validate_group_atomicity(rows: list[dict]) -> None:
    seen: set[str] = set()
    for row in rows:
        if row['image_id'] in seen:
            raise ValueError(f"DUPLICATE_IMAGE_ID:{row['image_id']}")
        seen.add(row['image_id'])
    for field, message in (('group_id', 'GROUP_CROSSES_SPLIT'),
                           ('sequence_id', 'SEQUENCE_CROSSES_SPLIT')):
        placement: dict[str, set] = {}
        for row in rows:
            key = row.get(field) or ''
            if not key:
                continue
            if field == 'sequence_id' and row.get('group_status') not in ('CONFIRMED',
                                                                            'CONFIRMED_SEQUENCE_RELATION'):
                continue
            placement.setdefault(key, set()).add(row['proposed_split'])
        for key in sorted(placement):
            if len(placement[key]) > 1:
                raise ValueError(f'{message}:{key}')


def _label_valid(data: bytes, n_classes: int) -> bool:
    for line in data.decode('utf-8').splitlines():
        parts = line.split()
        if not parts:
            continue
        if len(parts) != 5 or not parts[0].isdigit() or int(parts[0]) >= n_classes:
            return False
        try:
            values = [float(v) for v in parts[1:]]
        except ValueError:
            return False
        if not all(0.0 <= v <= 1.0 for v in values):
            return False
    return True


def validate_split(rows: list[dict]) -> None:
    """SPEC section 6 freeze tests; raises before anything is written."""
    paths: set[str] = set()
    for row in rows:
        where = row.get('image_id', 'UNKNOWN')
        if set(MANIFEST_FIELDS) - set(row):
            raise ValueError(f'SCHEMA:{where}')
        if row['path'] in paths:
            raise ValueError(f"DUPLICATE_PATH:{row['path']}")
        paths.add(row['path'])
        image = Path(row['local_absolute_path'])
        root = Path(str(image)[:-len(row['logical_path'])]) if str(image).replace(
            '\\', '/').endswith(row['logical_path']) else None
        label = root / row['label'] if root else None
        if not image.is_file() or label is None or not label.is_file():
            raise ValueError(f'MISSING_FILE:{where}')
        if sha256(image) != row['sha256']:
            raise ValueError(f'IMAGE_HASH:{where}')
        if sha256(label) != row['label_sha256']:
            raise ValueError(f'LABEL_HASH:{where}')
        if not _label_valid(label.read_bytes(), len(CLASSES)):
            raise ValueError(f'LABEL_INVALID:{where}')
    validate_group_atomicity(rows)


def preserve_membership(inventory: list[dict], clusters: dict[str, dict],
                        dataset_id: str = 'DATA-005') -> list[dict]:
    """Freeze M2 as trained: each DATA-005 image maps to exactly one audited DATA-004 image.

    Matched by (split with valid==val, class, filename, SHA256), never by hash alone,
    because byte-identical copies exist. The audited group is transferred to the DATA-005 id.
    """
    def key(row):
        return (row['split'].replace('valid', 'val'), row['class_names'], row['filename'],
                row['sha256'])

    source = {}
    for row in inventory:
        if row['dataset_id'] == 'DATA-004':
            if key(row) in source:
                raise SplitBlocked(f'AMBIGUOUS:{key(row)}')
            source[key(row)] = row
    rows, used = [], set()
    for row in sorted((r for r in inventory if r['dataset_id'] == dataset_id),
                      key=lambda r: r['source_id']):
        match = source.get(key(row))
        if match is None or match['source_id'] in used:
            raise SplitBlocked(f"UNMATCHED:{row['source_id']}")
        used.add(match['source_id'])
        audited = clusters[match['source_id']]
        rows.append({'image_id': row['source_id'], 'data004_id': match['source_id'],
                     'path': row['relative_path'], 'class_name': row['class_names'],
                     'sha256': row['sha256'], 'split': row['split'],
                     'cluster_id': audited['cluster'], 'group_id': audited['group_id'],
                     'logical_root': 'legacy_corpus', 'logical_path': row['relative_path']})
    if len(used) != len(source):
        raise SplitBlocked(f'UNMATCHED:{sorted(set(r["source_id"] for r in source.values()) - used)[:3]}')
    placement: dict[str, set] = {}
    for row in rows:
        placement.setdefault(row['group_id'], set()).add(row['split'])
    crossing = sorted(g for g, s in placement.items() if len(s) > 1)
    if crossing:
        raise SplitBlocked(f'GROUP_CROSSES_SPLIT:{crossing[:3]}')
    return rows


def assign_groups(groups: list[dict], seed: int = 42,
                  ratios: tuple[float, float, float] = (0.70, 0.15, 0.15)) -> dict[str, str]:
    """Greedy global-cost assignment. Ties go train, then valid, then test."""
    if not groups:
        return {}
    k = len(groups[0]['class_counts'])
    dims = 1 + k

    def vector(group):
        return [group['size'], *group['class_counts']]

    totals = [sum(vector(g)[d] for g in groups) for d in range(dims)]
    targets = {split: [totals[d] * ratio for d in range(dims)]
               for split, ratio in zip(SPLITS, ratios)}
    ids = sorted(g['id'] for g in groups)
    random.Random(seed).shuffle(ids)
    rank = {identifier: index for index, identifier in enumerate(ids)}
    ordered = sorted(groups, key=lambda g: (-g['size'], rank[g['id']]))

    current = {split: [0.0] * dims for split in SPLITS}

    def cost(state):
        return sum(((state[s][d] - targets[s][d]) / max(targets[s][d], 1)) ** 2
                   for s in SPLITS for d in range(dims))

    result = {}
    for group in ordered:
        best_split, best_cost = None, None
        for split in SPLITS:
            trial = {s: list(v) for s, v in current.items()}
            trial[split] = [a + b for a, b in zip(trial[split], vector(group))]
            value = cost(trial)
            if best_cost is None or value < best_cost - 1e-12:
                best_split, best_cost = split, value
        current[best_split] = [a + b for a, b in zip(current[best_split], vector(group))]
        result[group['id']] = best_split
    return result


def block_reasons(groups: list[dict], n_classes: int) -> list[str]:
    reasons = []
    for split in ('valid', 'test'):
        members = [g for g in groups if g['split'] == split]
        for c in range(n_classes):
            instances = sum(g['class_counts'][c] for g in members)
            carrying = sum(1 for g in members if g['class_counts'][c] > 0)
            if instances == 0:
                reasons.append(f'CLASS_ABSENT:{split}:{c}')
            elif carrying < 2:
                reasons.append(f'FEWER_THAN_TWO_GROUPS:{split}:{c}')
    return reasons


def build_groups(images: list[dict], relations: list[tuple[str, str, str]],
                 merge_sequence_hint: bool = True) -> dict[str, str]:
    parent = {img['image_id']: img['image_id'] for img in images}

    def find(item):
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    def union(a, b):
        a, b = find(a), find(b)
        if a != b:
            low, high = sorted((a, b))
            parent[high] = low

    keys = ('cluster_id', 'sequence_hint') if merge_sequence_hint else ('cluster_id',)
    for key in keys:
        first: dict[str, str] = {}
        for img in images:
            value = img.get(key) or ''
            if not value:
                continue
            if value in first:
                union(first[value], img['image_id'])
            else:
                first[value] = img['image_id']
    for a, b, decision in relations:
        if decision == PENDING:
            raise SplitBlocked(f'PENDING adjudication between {a} and {b} blocks the freeze')
        if decision in RELATED:
            union(a, b)
    return {identifier: find(identifier) for identifier in parent}


def _instances(value: str) -> list[int]:
    counts = [0] * len(CLASSES)
    for item in (value or '').split(';'):
        item = item.strip()
        if item in CLASSES:
            counts[CLASSES.index(item)] += 1
    return counts


def _relations(audit: Path, include_container_records: bool = True) -> list[tuple[str, str, str]]:
    """Pairwise grouping edges from the adjudication.

    Under option B a container-level record (the whole montage judged as one possible
    sequence) is evidence, not an edge: using it would re-merge the montage that B
    splits by visual identity.
    """
    path = audit / 'adjudications.csv'
    if not path.is_file():
        raise SplitBlocked('adjudications.csv is missing; the audit verdict is not documented')
    finals = {r['candidate_id']: r for r in csv.DictReader(open(path, encoding='utf-8'))}
    resolution = audit / 'adjudication_resolution.csv'
    if resolution.is_file():
        for r in csv.DictReader(open(resolution, encoding='utf-8')):
            if r.get('final'):
                finals[r['candidate_id']] = {**finals[r['candidate_id']],
                                             'final_adjudication': r['final']}
    relations = []
    for row in finals.values():
        if not include_container_records and row.get('category') == 'sequence_cluster':
            continue
        members = [m for m in row['member_ids'].split(';') if m]
        for other in members[1:]:
            relations.append((members[0], other, row['final_adjudication']))
    return relations


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--audit', type=Path, required=True)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--ratios', type=float, nargs=3, default=(0.70, 0.15, 0.15))
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--proposal', type=Path)
    parser.add_argument('--group-montage-by-identity', action='store_true',
                        help='PROTOCOL-AMENDMENT-009 option B (withdrawn): do not merge a whole '
                             'montage by its container name; group by visual identity')
    parser.add_argument('--extra-relations', type=Path,
                        help='CSV with source_id_a,source_id_b,final of adjudicated extra relations')
    parser.add_argument('--preserve-membership', action='store_true',
                        help='freeze M2 membership as trained, without reassignment')
    parser.add_argument('--dataset-id', default='DATA-005')
    args = parser.parse_args()
    root = authorized_root()
    roots = json.loads((root / 'configs/root_mapping.json').read_text(encoding='utf-8'))
    legacy = Path(roots['legacy_corpus'])
    if args.preserve_membership:
        parameters = json.loads((args.audit / 'audit_parameters.json').read_text(encoding='utf-8'))
        if parameters['n_cross_split_clusters'] != 0:
            raise SplitBlocked('the M2 audit does not allow reusing its membership')
        audited = {r['source_id']: r for r in csv.DictReader(
            open(args.audit / 'clusters.csv', encoding='utf-8'))}
        everything = list(csv.DictReader(open(root / 'data/manifests/legacy_dataset_inventory.csv',
                                              encoding='utf-8-sig')))
        rows = preserve_membership(everything, audited, args.dataset_id)
        for row in rows:
            if sha256(legacy / row['path']) != row['sha256']:
                raise SplitBlocked(f"IMAGE_HASH:{row['image_id']}")
            row['local_absolute_path'] = str(legacy / row['path'])
        out = check_output(root, args.out)
        with out.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
        digest = sha256(out)
        check_output(root, out.with_suffix(out.suffix + '.sha256')).write_text(
            f'{digest}  {out.name}\n', encoding='ascii')
        counts: dict[str, int] = {}
        for row in rows:
            counts[row['split']] = counts.get(row['split'], 0) + 1
        print(json.dumps({'status': 'FROZEN_AS_TRAINED', 'sha256': digest, 'counts': counts,
                          'groups_in_test': len({r['group_id'] for r in rows
                                                 if r['split'] == 'test'})}, indent=2))
        return 0
    if args.proposal is None:
        parser.error('--proposal is required unless --preserve-membership')
    inventory = {r['source_id']: r for r in csv.DictReader(
        open(root / 'data/manifests/legacy_dataset_inventory.csv', encoding='utf-8-sig'))
        if r['dataset_id'] == 'DATA-001'}
    clusters = {r['source_id']: r for r in csv.DictReader(
        open(args.audit / 'clusters.csv', encoding='utf-8'))}

    images = [{'image_id': sid, 'cluster_id': clusters[sid]['cluster'],
               'sequence_hint': inventory[sid]['sequence_name_hint']} for sid in sorted(inventory)]
    relations = _relations(args.audit,
                           include_container_records=not args.group_montage_by_identity)
    if args.extra_relations:
        relations += [(r['source_id_a'], r['source_id_b'], r['final'])
                      for r in csv.DictReader(open(args.extra_relations, encoding='utf-8'))]
    group_of = build_groups(images, relations,
                            merge_sequence_hint=not args.group_montage_by_identity)
    members: dict[str, list] = {}
    for sid, gid in group_of.items():
        members.setdefault(gid, []).append(sid)
    groups = [{'id': gid, 'size': len(ids),
               'class_counts': [sum(_instances(inventory[s]['instance_classes'])[c] for s in ids)
                                for c in range(len(CLASSES))]}
              for gid, ids in sorted(members.items())]
    assignment = assign_groups(groups, args.seed, tuple(args.ratios))
    for group in groups:
        group['split'] = assignment[group['id']]
    reasons = block_reasons(groups, len(CLASSES))

    rows = []
    for sid in sorted(inventory):
        record = inventory[sid]
        gid = group_of[sid]
        hint = record['sequence_name_hint']
        status = ('POSSIBLE_SEQUENCE_RELATION' if hint else
                  'MULTI_MEMBER_GROUP' if len(members[gid]) > 1 else 'SINGLETON')
        rows.append({
            'image_id': sid, 'path': record['relative_path'], 'label': record['label_path'],
            'sha256': record['sha256'], 'phash': clusters[sid]['phash'], 'source': SOURCE,
            'sequence_id': hint, 'cluster_id': clusters[sid]['cluster'],
            'original_split': record['split'], 'proposed_split': assignment[gid],
            'label_sha256': record['label_sha256'], 'group_id': gid, 'group_status': status,
            'logical_root': 'legacy_corpus', 'logical_path': record['relative_path'],
            'local_absolute_path': str(legacy / record['relative_path'])})
    validate_split(rows)

    summary = {split: {'images': 0, 'groups': 0, 'instances': [0] * len(CLASSES),
                       'groups_per_class': [0] * len(CLASSES)} for split in SPLITS}
    for group in groups:
        s = summary[group['split']]
        s['images'] += group['size']
        s['groups'] += 1
        for c in range(len(CLASSES)):
            s['instances'][c] += group['class_counts'][c]
            s['groups_per_class'][c] += group['class_counts'][c] > 0
    moved = sum(1 for r in rows if r['proposed_split'] != r['original_split'])
    new_test = [r for r in rows if r['proposed_split'] == 'test']
    test_history = {
        'new_test_images': len(new_test),
        'previously_in_historical_train': sum(r['original_split'] == 'train' for r in new_test),
        'previously_in_historical_valid': sum(r['original_split'] == 'valid' for r in new_test),
        'previously_in_historical_test': sum(r['original_split'] == 'test' for r in new_test),
        'note': ('The published M1 weights were trained on the historical train split, so they '
                 'cannot be evaluated as a holdout on the new test. Retraining is required.')}

    proposal = check_output(root, args.proposal)
    lines = ['# Propuesta de partición M1 — TASK-03', '',
             f'Algoritmo único de la SPEC §6, seed {args.seed}, objetivo {list(args.ratios)}, sin barrido de semillas.', '',
             '| split | imágenes | grupos | inst. Enfermo | inst. Saludable | grupos con Enfermo | grupos con Saludable |',
             '|---|---|---|---|---|---|---|']
    for split in SPLITS:
        s = summary[split]
        lines.append(f"| {split} | {s['images']} | {s['groups']} | {s['instances'][0]} | "
                     f"{s['instances'][1]} | {s['groups_per_class'][0]} | {s['groups_per_class'][1]} |")
    lines += ['', f'Imágenes que cambian de split: {moved} de {len(rows)}.',
              f'`requires_retraining`: {str(moved > 0).lower()}', '',
              '`test_history`:', '```json', json.dumps(test_history, indent=2), '```', '']
    if reasons:
        lines += ['## BLOQUEADA', '', 'La congelación no procede: ' + ', '.join(reasons) + '.',
                  'No se ajusta la seed ni se rompen grupos para que pase.']
        proposal.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        print(json.dumps({'status': 'BLOCKED', 'reasons': reasons}, indent=2))
        return 2

    out = check_output(root, args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=MANIFEST_FIELDS, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    digest = sha256(out)
    check_output(root, out.with_suffix(out.suffix + '.sha256')).write_text(
        f'{digest}  {out.name}\n', encoding='ascii')
    lines += [f'Manifiesto: `{out.relative_to(root).as_posix()}`, SHA256 `{digest}`.', '',
              'Estado: **PROPUESTA**. La congelación se revisa antes de TASK-04.']
    proposal.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'PROPOSED', 'sha256': digest, 'moved': moved,
                      'summary': summary, 'test_history': test_history}, indent=2))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except SplitBlocked as error:
        print(f'BLOCKED: {error}', file=sys.stderr)
        sys.exit(2)
