"""Reproducible leakage audit for M1 and M2.

Implements the frozen SPEC section 5. The union-find is the algorithm used by
`legacy_corpus:Mango-vision/src/data_prep/dedup_and_resplit.py`, reimplemented
here without its legacy side effects (it copied files and rewrote splits) and
with attribution.

What this module does NOT do, by design:

- It never promotes perceptual similarity to a confirmed sequence relation.
- It never resolves a class conflict by cluster majority.
- It never treats a Hamming distance of 0 as byte identity.
- It reports counts of operational dependence; it does not claim biological
  independence, and zero detected pairs is not evidence of its absence.
"""

import argparse
import csv
import hashlib
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.evaluation.provenance import (  # noqa: E402
    authorized_root, check_output, configure_environment, verify_environment,
)

HASH_BITS = 64
LARGE_CLUSTER = 10
RELATIONS = ('EXACT_DUPLICATE', 'NEAR_DUPLICATE', 'POSSIBLE_SEQUENCE_RELATION',
             'CONFIRMED_SEQUENCE_RELATION', 'UNRELATED')
ADJUDICATION_FIELDS = ('candidate_id', 'unit_type', 'member_ids', 'reviewer_a', 'reviewer_b',
                       'decision_a', 'decision_b', 'agreement', 'final_adjudication',
                       'evidence', 'rationale', 'adjudicator', 'timestamp',
                       'blinding_exceptions')
PENDING = 'PENDING_SEPARATE_ADJUDICATION'


class AuditError(Exception):
    """A condition that must stop the audit rather than be worked around."""


def hamming(a: int, b: int) -> int:
    for value in (a, b):
        if not isinstance(value, int) or isinstance(value, bool):
            raise AuditError(f'hash is not an integer: {value!r}')
        if value < 0 or value >= 2 ** HASH_BITS:
            raise AuditError(f'hash outside the {HASH_BITS}-bit range: {value}')
    return (a ^ b).bit_count()


def components(ids: list[str], edges: list[tuple[str, str]]) -> dict[str, str]:
    """Union-find whose representative is the minimum ID, so order cannot matter.

    Attribution: union-find structure from the legacy dedup_and_resplit.py.
    """
    unique = sorted(set(ids))
    if len(unique) != len(ids):
        raise AuditError('duplicate id in the component input')
    parent = {identifier: identifier for identifier in unique}

    def find(item: str) -> str:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    for left, right in edges:
        for endpoint in (left, right):
            if endpoint not in parent:
                raise AuditError(f'edge references an unknown id: {endpoint}')
        a, b = find(left), find(right)
        if a != b:
            # Minimum ID wins, so the result does not depend on edge order.
            low, high = (a, b) if a < b else (b, a)
            parent[high] = low
    resolved = {identifier: find(identifier) for identifier in unique}
    # Second pass: the representative must be the minimum member of its component.
    lowest: dict[str, str] = {}
    for identifier, root in resolved.items():
        if root not in lowest or identifier < lowest[root]:
            lowest[root] = identifier
    return {identifier: lowest[root] for identifier, root in resolved.items()}


def relation_label(distance: int, same_sha: bool, documented_group: str | None,
                   sequence_hint: str | None = None, hamming_lt: int = 5) -> str:
    if documented_group:
        return 'CONFIRMED_SEQUENCE_RELATION'
    if same_sha:
        return 'EXACT_DUPLICATE'
    if distance < hamming_lt:
        # A perceptual hint without a verifiable source stays POSSIBLE, never CONFIRMED.
        return 'POSSIBLE_SEQUENCE_RELATION' if sequence_hint else 'NEAR_DUPLICATE'
    return 'UNRELATED'


def needs_visual_adjudication(cluster_size: int, cross_split: bool = False,
                              conflicting_classes: bool = False, possible_sequence: bool = False,
                              sensitivity_band: bool = False,
                              exact_sha_equality: bool = False) -> bool:
    """SPEC: verifiable evidence is adjudicated as evidence, without inventing a visual need."""
    if exact_sha_equality:
        return False
    return bool(cross_split or conflicting_classes or possible_sequence
                or sensitivity_band or cluster_size >= LARGE_CLUSTER)


def _opaque(reviewer: str, candidate_id: str, member_id: str) -> str:
    seed = f'{reviewer}|{candidate_id}|{member_id}'.encode()
    return 'ITEM-' + hashlib.sha256(seed).hexdigest()[:12]


def blind_packet(candidate: dict, reviewer: str) -> dict:
    """Only opaque ids and images. Everything the SPEC forbids is dropped, not renamed."""
    if reviewer not in ('a', 'b'):
        raise AuditError(f'unknown reviewer {reviewer!r}')
    members = candidate.get('member_ids') or []
    if isinstance(members, str):
        members = [item for item in members.split(';') if item]
    if not members:
        raise AuditError(f"{candidate.get('candidate_id', 'UNKNOWN')}: no members to review")
    items = []
    for member in members:
        opaque = _opaque(reviewer, candidate['candidate_id'], member)
        items.append({'opaque_id': opaque, 'asset': f'{opaque}.png'})
    return {'candidate_id': candidate['candidate_id'],
            'unit_type': candidate.get('unit_type', 'pair'),
            'reviewer': reviewer,
            'question': 'Are these images of the same fruit, scene or acquisition sequence?',
            'allowed_answers': list(RELATIONS),
            'items': items}


def validate_adjudications(rows: list[dict]) -> None:
    if not rows:
        raise AuditError('no adjudication rows to validate')
    for row in rows:
        where = row.get('candidate_id', 'UNKNOWN')
        for field in ADJUDICATION_FIELDS:
            if field not in row:
                raise AuditError(f'{where}: missing field {field}')
        for field in ('evidence', 'rationale'):
            if not str(row[field]).strip():
                raise AuditError(f'{where}: {field} must not be empty')
        members = [item for item in str(row['member_ids']).split(';') if item.strip()]
        if row['unit_type'] == 'cluster' and len(members) < 2:
            raise AuditError(f'{where}: a cluster record needs complete member_ids, '
                             f'got {len(members)}')
        if not members:
            raise AuditError(f'{where}: member_ids must not be empty')

        requires_visual = str(row.get('requires_visual', 'true')).strip().lower() != 'false'
        if not requires_visual:
            continue

        if not str(row['reviewer_b']).strip() or not str(row['decision_b']).strip():
            raise AuditError(f'{where}: a visual candidate needs reviewer_b and decision_b')
        if str(row['reviewer_a']).strip() == str(row['reviewer_b']).strip():
            raise AuditError(f'{where}: reviewer_a and reviewer_b must be independent identities')
        for field in ('decision_a', 'decision_b'):
            if row[field] not in RELATIONS:
                raise AuditError(f'{where}: {field} is not one of {RELATIONS}')
        expected = 'AGREE' if row['decision_a'] == row['decision_b'] else 'DISAGREE'
        if row['agreement'] != expected:
            raise AuditError(f'{where}: agreement is {row["agreement"]!r} but the two decisions '
                             f'imply {expected!r}; it is compared, never inferred')
        if expected == 'DISAGREE' and row['final_adjudication'] != PENDING:
            adjudicator = str(row['adjudicator']).strip()
            reviewers = {str(row['reviewer_a']).strip(), str(row['reviewer_b']).strip()}
            if not adjudicator or adjudicator in reviewers:
                raise AuditError(
                    f'{where}: a disagreement stays {PENDING} until a third adjudicator, '
                    'distinct from both reviewers, resolves it with evidence')


def cross_split(rows: list[dict]) -> list[dict]:
    clusters: dict[str, set] = {}
    members: dict[str, list] = {}
    for row in rows:
        clusters.setdefault(row['cluster'], set()).add(row['split'])
        members.setdefault(row['cluster'], []).append(row['source_id'])
    result = []
    for cluster in sorted(clusters):
        splits = sorted(clusters[cluster])
        if len(splits) > 1:
            result.append({'cluster': cluster, 'splits': splits,
                           'member_ids': sorted(members[cluster]),
                           'n_members': len(members[cluster])})
    return result


def duplicate_structure(rows: list[dict]) -> dict:
    sizes: dict[str, int] = {}
    shas, groups = set(), set()
    classes_by_sha: dict[str, set] = {}
    for row in rows:
        sizes[row['cluster']] = sizes.get(row['cluster'], 0) + 1
        shas.add(row['sha256'])
        groups.add(row.get('group_id') or row['cluster'])
        if row.get('class_name'):
            classes_by_sha.setdefault(row['sha256'], set()).add(row['class_name'])
    distribution: dict[int, int] = {}
    for size in sizes.values():
        distribution[size] = distribution.get(size, 0) + 1
    values = sorted(sizes.values())
    return {
        'n_images': len(rows), 'n_unique_sha': len(shas),
        'n_clusters': len(sizes), 'n_groups': len(groups),
        'cluster_size_distribution': dict(sorted(distribution.items())),
        'min_cluster_size': min(values) if values else 0,
        'median_cluster_size': statistics.median(values) if values else 0,
        'max_cluster_size': max(values) if values else 0,
        'discordant_class_sha': sorted(sha for sha, names in classes_by_sha.items()
                                       if len(names) > 1),
        'interpretation': ('These counts describe operational dependence between files. '
                           'They are not a demonstrated effective sample size, and a cluster '
                           'count is not an independence count.'),
    }


def hash_images(rows: list[dict]) -> list[dict]:
    """Fixed pHash parameters. A decode failure aborts with the full list."""
    from PIL import Image
    import imagehash

    results, failures = [], []
    for row in rows:
        try:
            with Image.open(row['path']) as image:
                # SPEC: no EXIF orientation, no automatic crop.
                value = imagehash.phash(image.convert('RGB'), hash_size=8, highfreq_factor=4)
        except Exception as error:  # decode, truncation, permissions: all fatal
            failures.append(f"{row['source_id']}: {type(error).__name__}: {error}")
            continue
        results.append({**row, 'phash': int(str(value), 16)})
    if failures:
        raise AuditError('images that could not be decoded; the audit stops rather than '
                         'silently skipping them:\n  ' + '\n  '.join(failures))
    return results


def dihedral_hashes(image) -> list[int]:
    """pHash of the 8 rotations and reflections, identity first.

    PROTOCOL-AMENDMENT-009: plain pHash is not rotation invariant, and a blind
    reviewer found the same mango rotated 180 degrees inside the montage.
    """
    import imagehash
    from PIL import Image

    base = image.convert('RGB')
    variants = [base, base.transpose(Image.Transpose.ROTATE_90),
                base.transpose(Image.Transpose.ROTATE_180),
                base.transpose(Image.Transpose.ROTATE_270)]
    mirrored = base.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    variants += [mirrored, mirrored.transpose(Image.Transpose.ROTATE_90),
                 mirrored.transpose(Image.Transpose.ROTATE_180),
                 mirrored.transpose(Image.Transpose.ROTATE_270)]
    return [int(str(imagehash.phash(v, hash_size=8, highfreq_factor=4)), 16) for v in variants]


def rotation_invariant_distance(hashes_a: list[int], hashes_b: list[int]) -> int:
    """The dihedral group is closed, so comparing every transform of A with the
    identity of B covers every relative rotation or reflection between them."""
    return min(hamming(value, hashes_b[0]) for value in hashes_a)


def build_pairs(items: list[dict], hamming_lt: int, candidate_max: int) -> list[dict]:
    """Quadratic comparison, each unordered pair once. Acceptable at this corpus size."""
    pairs = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            left, right = items[i], items[j]
            distance = hamming(left['phash'], right['phash'])
            if distance > candidate_max:
                continue
            same_sha = left['sha256'] == right['sha256']
            hint = left.get('sequence_name_hint') or right.get('sequence_name_hint')
            documented = (left.get('documented_group')
                          if left.get('documented_group') == right.get('documented_group')
                          else None)
            pairs.append({
                'pair_id': f'PAIR-{len(pairs) + 1:05d}',
                'source_id_a': left['source_id'], 'source_id_b': right['source_id'],
                'phash_a': f"{left['phash']:016x}", 'phash_b': f"{right['phash']:016x}",
                'sha256_a': left['sha256'], 'sha256_b': right['sha256'],
                'distance': distance,
                'split_a': left.get('split', ''), 'split_b': right.get('split', ''),
                'class_a': left.get('class_names', ''), 'class_b': right.get('class_names', ''),
                'same_sha': str(same_sha).lower(),
                'in_threshold': str(distance < hamming_lt).lower(),
                'sensitivity_band': str(hamming_lt <= distance <= candidate_max).lower(),
                'relation': relation_label(distance, same_sha, documented, hint, hamming_lt),
                'evidence': ('identical SHA256' if same_sha else
                             f'pHash64 Hamming {distance}' +
                             (f'; filename hint {hint}' if hint else '')),
                'review_decision': 'PENDING_ADJUDICATION',
            })
    return pairs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset-id', required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--phash-bits', type=int, default=64)
    parser.add_argument('--hamming-lt', type=int, default=5)
    parser.add_argument('--candidate-max', type=int, default=10)
    parser.add_argument('--roots', type=Path, default=Path('configs/root_mapping.json'))
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()

    root = authorized_root()
    configure_environment(root)
    verify_environment(root)
    if args.phash_bits != HASH_BITS:
        raise AuditError(f'this audit fixes {HASH_BITS}-bit pHash; got {args.phash_bits}')
    if args.hamming_lt > args.candidate_max:
        raise AuditError('hamming-lt must not exceed candidate-max')

    roots = json.loads(args.roots.read_text(encoding='utf-8'))
    roots['revision'] = str(root)
    with args.manifest.open(encoding='utf-8-sig', newline='') as stream:
        rows = [row for row in csv.DictReader(stream) if row['dataset_id'] == args.dataset_id]
    if not rows:
        raise AuditError(f'no manifest rows for dataset {args.dataset_id}')

    prepared = []
    for row in rows:
        base = Path(roots['legacy_corpus']) / row['relative_path']
        prepared.append({**row, 'path': str(base),
                         'documented_group': row.get('documented_group') or ''})
    items = hash_images(prepared)

    pairs = build_pairs(items, args.hamming_lt, args.candidate_max)
    edges = [(p['source_id_a'], p['source_id_b']) for p in pairs if p['in_threshold'] == 'true']
    cluster_of = components([item['source_id'] for item in items], edges)
    enriched = [{'source_id': item['source_id'], 'sha256': item['sha256'],
                 'split': item.get('split', ''), 'cluster': cluster_of[item['source_id']],
                 'group_id': item.get('sequence_name_hint') or cluster_of[item['source_id']],
                 'class_name': item.get('class_names', ''),
                 'phash': f"{item['phash']:016x}",
                 'relative_path': item.get('relative_path', '')}
                for item in items]

    out = check_output(root, args.out, allow_directory=True)
    out.mkdir(parents=True, exist_ok=True)

    def write_csv(name: str, records: list[dict]) -> None:
        destination = check_output(root, out / name)
        if not records:
            destination.write_text('', encoding='utf-8')
            return
        with destination.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)

    crossing = cross_split(enriched)
    write_csv('candidate_pairs.csv', pairs)
    write_csv('clusters.csv', enriched)
    write_csv('cross_split_summary.csv',
              [{**row, 'member_ids': ';'.join(row['member_ids']),
                'splits': ';'.join(row['splits'])} for row in crossing])
    structure = duplicate_structure(enriched)
    check_output(root, out / 'duplicate_structure.json').write_text(
        json.dumps(structure, indent=2) + '\n', encoding='utf-8')
    write_csv('cluster_size_distribution.csv',
              [{'cluster_size': size, 'frequency': count}
               for size, count in structure['cluster_size_distribution'].items()])

    manifest_digest = hashlib.sha256(args.manifest.read_bytes()).hexdigest()
    import imagehash
    import PIL
    parameters = {
        'dataset_id': args.dataset_id, 'algorithm_version': 1,
        'phash': {'library': 'ImageHash', 'version': imagehash.__version__,
                  'pillow': PIL.__version__, 'hash_size': 8, 'highfreq_factor': 4,
                  'convert': 'RGB', 'exif_orientation_applied': False, 'autocrop': False},
        'hamming_lt': args.hamming_lt, 'candidate_max': args.candidate_max,
        'manifest_sha256': manifest_digest,
        'n_images': len(items), 'n_pairs_within_threshold': len(edges),
        'n_candidates_in_band': sum(1 for p in pairs if p['sensitivity_band'] == 'true'),
        'n_cross_split_clusters': len(crossing),
        'limits': ['zero detected pairs would not prove biological independence',
                   'a cluster is an operational grouping, not a demonstrated independent unit',
                   'Hamming 0 is not byte identity; SHA256 equality is reported separately'],
    }
    check_output(root, out / 'audit_parameters.json').write_text(
        json.dumps(parameters, indent=2) + '\n', encoding='utf-8')
    print(f"dataset={args.dataset_id} images={len(items)} pairs_in_threshold={len(edges)} "
          f"band={parameters['n_candidates_in_band']} cross_split_clusters={len(crossing)} "
          f"out={out}")
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except AuditError as error:
        print(str(error), file=sys.stderr)
        sys.exit(2)
