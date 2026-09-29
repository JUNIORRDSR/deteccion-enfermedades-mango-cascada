"""TASK-05: Wilson intervals, the M2 duplicate sensitivity and the paired group bootstrap.

SPEC section 7, AMENDMENT-04. Standard library only: every function here is testable
without a model runtime. The M1 metric functions live in src/evaluation/evaluate.py and
are imported lazily, only by the M1 CLI path.

Undefined is None with a reason, never zero. Groups and clusters are operational
dependence units, never demonstrated biological independence.
"""

import argparse
import csv
import hashlib
import json
import math
import random
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.evaluation.provenance import InvalidInput, authorized_root, check_output, sha256  # noqa: E402
from src.leakage_audit.audit import duplicate_structure  # noqa: E402

Z95 = 1.959963984540054
PRINCIPAL = 'image_weighted'
SCHEMES = (PRINCIPAL, 'exact_sha_dedup', 'cluster_weighted')
RECORD_FIELDS = ('image_id', 'sha256', 'cluster_id', 'group_id', 'truth', 'pred')
MANIFEST_FIELDS = ('image_id', 'sha256', 'cluster_id', 'group_id')
DRAW_METHOD = ('random.Random(seed).choices(sorted unique group_ids, k=n_groups) per draw; '
               'occurrence_id = position of the group in its draw')
INDEPENDENCE = ('n clusters and n groups describe operational dependence; they are not '
                'demonstrated biological independence nor an effective sample size.')


class EstimandBlocked(ValueError):
    """A predefined sensitivity cannot be computed. Never resolved by majority."""


class ResamplingBlocked(ValueError):
    """A SHA or cluster crosses group_id, so no group bootstrap is valid."""


def wilson(k: int, n: int, z: float = Z95) -> tuple[float, float]:
    """Wilson score interval; only for proportions of independent Bernoulli trials."""
    if any(type(x) is not int for x in (k, n)):
        raise ValueError('Wilson needs integer counts of Bernoulli trials')
    if not (isinstance(z, (int, float)) and not isinstance(z, bool) and math.isfinite(z) and z > 0):
        raise ValueError(f'z must be a positive finite number, got {z!r}')
    if n <= 0 or not 0 <= k <= n:
        raise ValueError(f'undefined proportion {k}/{n}')
    p, z2 = k / n, z * z
    scale = 1 + z2 / n
    centre = (p + z2 / (2 * n)) / scale
    half = z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / scale
    return max(0.0, centre - half), min(1.0, centre + half)


# --- weighted confusion and metrics (SPEC section 7) -------------------------------

def weighted_confusion(records: list[dict], class_names: list[str],
                       weights: list[float]) -> list[list[float]]:
    """C[i][j] = sum of weights with truth i and pred j. fsum makes it order invariant."""
    index = {name: i for i, name in enumerate(class_names)}
    cells = [[[] for _ in class_names] for _ in class_names]
    for record, weight in zip(records, weights):
        if weight:
            cells[index[record['truth']]][index[record['pred']]].append(weight)
    return [[math.fsum(cell) for cell in line] for line in cells]


def weighted_metrics(cm: list[list[float]], class_names: list[str]) -> dict:
    """Accuracy, per-class P/R/F1 and macro F1 over ALL fixed classes, with denominators."""
    size = len(class_names)
    undefined = {}
    total = math.fsum(value for line in cm for value in line)
    accuracy = math.fsum(cm[i][i] for i in range(size)) / total if total > 0 else None
    if accuracy is None:
        undefined['accuracy'] = 'no weight: sum(C) is zero'
    per_class = {}
    for i, name in enumerate(class_names):
        tp = cm[i][i]
        fp = math.fsum(cm[j][i] for j in range(size) if j != i)
        fn = math.fsum(cm[i][j] for j in range(size) if j != i)
        values = {'tp': tp, 'fp': fp, 'fn': fn, 'precision_denominator': tp + fp,
                  'recall_denominator': tp + fn, 'f1_denominator': 2 * tp + fp + fn,
                  'precision': tp / (tp + fp) if tp + fp > 0 else None,
                  'recall': tp / (tp + fn) if tp + fn > 0 else None,
                  # With GT support the F1 denominator is positive, so F1 may be 0.
                  'f1': 2 * tp / (2 * tp + fp + fn) if tp + fn > 0 else None}
        if values['precision'] is None:
            undefined[f'precision[{name}]'] = 'no predictions of the class (TP+FP=0)'
        for key in ('recall', 'f1'):
            if values[key] is None:
                undefined[f'{key}[{name}]'] = 'no GT support (TP+FN=0)'
        per_class[name] = values
    missing = [name for name in class_names if per_class[name]['f1'] is None]
    macro = None if missing else math.fsum(per_class[n]['f1'] for n in class_names) / size
    if missing:
        undefined['macro_f1'] = f'F1 undefined for: {", ".join(missing)}'
    return {'accuracy': accuracy, 'accuracy_denominator': total, 'macro_f1': macro,
            'per_class': per_class, 'undefined': undefined}


# --- the three predefined estimands (AMENDMENT-04) ---------------------------------

def scheme_weights(records: list[dict], scheme: str) -> list[float]:
    """Weight per record. Keys carry the bootstrap occurrence, so copies never collapse."""
    def key(record, field):
        return record.get('occurrence_id'), record[field]

    if scheme == 'image_weighted':
        return [1.0] * len(records)
    if scheme == 'cluster_weighted':
        sizes = Counter(key(r, 'cluster_id') for r in records)
        return [1 / sizes[key(r, 'cluster_id')] for r in records]
    if scheme == 'exact_sha_dedup':
        chosen, truths = {}, {}
        for position, record in enumerate(records):
            k = key(record, 'sha256')
            truths.setdefault(k, set()).add(record['truth'])
            if k not in chosen or record['image_id'] < records[chosen[k]]['image_id']:
                chosen[k] = position
        conflicts = sorted({k[1] for k, names in truths.items() if len(names) > 1})
        if conflicts:
            raise EstimandBlocked(f'SHA copies with inconsistent GT, not resolved by majority: '
                                  f'{conflicts}')
        keep = set(chosen.values())
        return [1.0 if i in keep else 0.0 for i in range(len(records))]
    raise ValueError(f'unknown scheme {scheme!r}')


def _validate(records: list[dict], class_names: list[str]) -> None:
    if not class_names or len(set(class_names)) != len(class_names):
        raise ValueError('class_names must be the unique, non-empty model.names order')
    if not records:
        raise ValueError('no records')
    seen = set()
    for record in records:
        missing = [field for field in RECORD_FIELDS if not record.get(field)]
        if missing:
            raise ValueError(f'record {record.get("image_id")!r} lacks {missing}')
        key = (record.get('occurrence_id'), record['image_id'])
        if key in seen:
            raise ValueError(f'image_id {record["image_id"]!r} is repeated')
        seen.add(key)
        for field in ('truth', 'pred'):
            if record[field] not in class_names:
                raise ValueError(f'{field} {record[field]!r} of {record["image_id"]!r} '
                                 'is not in model.names')


def _estimands(records: list[dict], class_names: list[str]) -> dict:
    out = {}
    for scheme in SCHEMES:
        try:
            weights = scheme_weights(records, scheme)
        except EstimandBlocked as error:
            out[scheme] = {'blocked': True, 'reason': str(error), 'n_records_used': None,
                           'weight_total': None, 'confusion': None, 'metrics': None}
            continue
        confusion = weighted_confusion(records, class_names, weights)
        out[scheme] = {'blocked': False, 'reason': None,
                       'n_records_used': sum(1 for w in weights if w),
                       'weight_total': math.fsum(weights), 'confusion': confusion,
                       'metrics': weighted_metrics(confusion, class_names)}
    return out


def _metric_names(class_names: list[str]) -> list[tuple[str, tuple]]:
    """Reported metrics and the classes whose group support each CI requires."""
    names = [('accuracy', tuple(class_names)), ('macro_f1', tuple(class_names))]
    return names + [(f'{key}[{c}]', (c,)) for c in class_names
                    for key in ('precision', 'recall', 'f1')]


def _flat(estimand: dict, class_names: list[str]) -> dict:
    if estimand['blocked']:
        return {name: None for name, _ in _metric_names(class_names)}
    metrics = estimand['metrics']
    out = {'accuracy': metrics['accuracy'], 'macro_f1': metrics['macro_f1']}
    for c in class_names:
        for key in ('precision', 'recall', 'f1'):
            out[f'{key}[{c}]'] = metrics['per_class'][c][key]
    return out


def _why(estimand: dict, name: str) -> str | None:
    return estimand['reason'] if estimand['blocked'] else estimand['metrics']['undefined'].get(name)


def delta(secondary: float | None, principal: float | None) -> float | None:
    """secondary - principal; undefined when either of the two metrics is."""
    return None if secondary is None or principal is None else secondary - principal


def paired_delta(secondary, principal):
    """A metric computing secondary - principal on the same resample."""
    return lambda rows: delta(secondary(rows), principal(rows))


def m2_sensitivity(records: list[dict], class_names: list[str]) -> dict:
    """Principal image-weighted estimand, both predefined secondaries and their deltas."""
    _validate(records, class_names)
    estimands = _estimands(records, class_names)
    principal = _flat(estimands[PRINCIPAL], class_names)
    deltas = {}
    for scheme in SCHEMES[1:]:
        secondary = _flat(estimands[scheme], class_names)
        deltas[scheme] = {}
        for name, _ in _metric_names(class_names):
            units = delta(secondary[name], principal[name])
            reasons = [f'{label}: {why}' for label, est in (('secondary', estimands[scheme]),
                                                             ('principal', estimands[PRINCIPAL]))
                       if (why := _why(est, name))]
            deltas[scheme][name] = {'units': units,
                                    'percentage_points': None if units is None else 100 * units,
                                    'reason': '; '.join(reasons) if units is None else None}
    predictions = {}
    for record in records:
        predictions.setdefault(record['sha256'], []).append((record['image_id'], record['pred']))
    conflicts = [{'sha256': sha, 'image_ids': sorted(i for i, _ in pairs),
                  'preds': sorted({p for _, p in pairs})}
                 for sha, pairs in sorted(predictions.items()) if len({p for _, p in pairs}) > 1]
    undefined = sorted(f'{scheme}.{name}: {why}' for scheme in SCHEMES
                       for name, _ in _metric_names(class_names)
                       if (why := _why(estimands[scheme], name)))
    structure = duplicate_structure([{'cluster': r['cluster_id'], 'sha256': r['sha256'],
                                      'group_id': r['group_id'], 'class_name': r['truth']}
                                     for r in records])
    return {'class_names': list(class_names), 'principal': PRINCIPAL, 'estimands': estimands,
            'deltas': deltas, 'structure': structure, 'sha_prediction_conflicts': conflicts,
            'undefined': undefined}


# --- group bootstrap ----------------------------------------------------------------

def draw_groups(group_ids, seed: int = 42, n_resamples: int = 2000) -> list[list[str]]:
    """Reconstructible draws with replacement over the sorted unique group ids."""
    universe = sorted(set(group_ids))
    rng = random.Random(seed)
    return [rng.choices(universe, k=len(universe)) for _ in range(n_resamples)]


def draws_sha256(draws: list[list[str]]) -> str:
    return hashlib.sha256(json.dumps(draws, separators=(',', ':')).encode('utf-8')).hexdigest()


def _groups(records: list[dict]) -> dict[str, list[dict]]:
    groups, owner = {}, {}
    for record in records:
        gid = record.get('group_id')
        if not gid:
            raise ValueError(f'record {record.get("image_id")!r} has no group_id')
        groups.setdefault(gid, []).append(record)
        for field in ('sha256', 'cluster_id'):
            if value := record.get(field):
                first = owner.setdefault((field, value), gid)
                if first != gid:
                    raise ResamplingBlocked(f'{field} {value} crosses group_id {first} and {gid}')
    return groups


def _resample(groups: dict, draw: list[str]) -> list[dict]:
    return [{**record, 'occurrence_id': k} for k, gid in enumerate(draw) for record in groups[gid]]


def resample(records: list[dict], draw: list[str]) -> list[dict]:
    """All records of every drawn group; each position of the draw is its own occurrence."""
    return _resample(_groups(records), draw)


def _class_groups(groups: dict, class_key: str) -> dict[str, int]:
    counts = Counter()
    for members in groups.values():
        present = set()
        for record in members:
            value = record.get(class_key)
            present.update(value if isinstance(value, (list, tuple, set)) else [value])
        counts.update(present - {None, ''})
    return dict(sorted(counts.items()))


def _summarize(estimate, values, n_groups, class_counts, required) -> dict:
    defined = [v for v in values if v is not None]
    undefined = len(values) - len(defined)
    reasons = []
    if n_groups < 2:
        reasons.append(f'{n_groups} group(s); at least 2 are required')
    short = [c for c in required if class_counts.get(c, 0) < 2]
    if short:
        reasons.append(f'fewer than 2 groups with GT support for: {", ".join(short)}')
    if undefined * 20 > len(values):
        reasons.append(f'{undefined} of {len(values)} draws undefined (>5%)')
    if len(defined) < 2:
        reasons.append('fewer than 2 defined draws')
    ci = None
    if not reasons:
        cuts = statistics.quantiles(defined, n=40, method='inclusive')  # linear, like numpy
        ci = [cuts[0], cuts[-1]]
    return {'estimate': estimate, 'ci95': ci, 'percentiles': [2.5, 97.5],
            'n_resamples': len(values), 'n_defined': len(defined), 'undefined_count': undefined,
            'undefined_fraction': undefined / len(values) if values else None,
            'n_groups': n_groups, 'blocked': bool(reasons), 'reason': '; '.join(reasons) or None}


def bootstrap_groups(records: list[dict], metric, seed: int = 42, n_resamples: int = 2000,
                     required_classes=None, class_key=None, draws=None) -> dict:
    """Percentile CI over group_id draws. Undefined draws are counted, never zeroed."""
    if required_classes and not class_key:
        raise ValueError('required_classes needs a class_key')
    groups = _groups(records)
    if draws is None:
        draws = draw_groups(groups, seed, n_resamples)
    elif any(len(d) != len(groups) or not set(d) <= groups.keys() for d in draws):
        raise ValueError('a precomputed draw does not match the groups of this sample')
    values = [metric(_resample(groups, draw)) for draw in draws]
    counts = _class_groups(groups, class_key) if class_key else {}
    return {**_summarize(metric(records), values, len(groups), counts, required_classes or ()),
            'class_group_counts': counts if class_key else None, 'seed': seed,
            'draws': draws, 'draws_sha256': draws_sha256(draws), 'values': values}


def intervals_for(records: list[dict], metrics: dict, seed: int = 42,
                  n_resamples: int = 2000) -> dict:
    """Several metrics on one shared set of draws. A spec is a callable or a dict."""
    groups = _groups(records)
    draws = draw_groups(groups, seed, n_resamples)
    out = {}
    for name, spec in metrics.items():
        spec = spec if isinstance(spec, dict) else {'metric': spec}
        result = bootstrap_groups(records, spec['metric'], seed, n_resamples,
                                  spec.get('required_classes'), spec.get('class_key'), draws)
        out[name] = {k: v for k, v in result.items() if k not in ('draws', 'values')}
    return {'seed': seed, 'n_resamples': n_resamples, 'n_groups': len(groups),
            'group_ids': sorted(groups), 'method': DRAW_METHOD, 'draws': draws,
            'draws_sha256': draws_sha256(draws), 'metrics': out}


def m2_bootstrap(records: list[dict], class_names: list[str], seed: int = 42,
                 n_resamples: int = 2000) -> dict:
    """The three schemes and their paired deltas, all on the same draws."""
    _validate(records, class_names)
    groups = _groups(records)
    draws = draw_groups(groups, seed, n_resamples)
    digest = draws_sha256(draws)
    point = _estimands(records, class_names)
    flat = {s: _flat(point[s], class_names) for s in SCHEMES}
    per_draw = [{s: _flat(e, class_names) for s, e in
                 _estimands(_resample(groups, draw), class_names).items()} for draw in draws]
    counts = _class_groups(groups, 'truth')

    def summary(scheme, estimate, values, required):
        if point[scheme]['blocked']:
            return {'estimate': None, 'ci95': None, 'blocked': True,
                    'reason': point[scheme]['reason'], 'draws_sha256': digest}
        return {**_summarize(estimate, values, len(groups), counts, required),
                'draws_sha256': digest}

    intervals = {s: {name: summary(s, flat[s][name], [d[s][name] for d in per_draw], required)
                     for name, required in _metric_names(class_names)} for s in SCHEMES}
    deltas = {s: {name: summary(s, delta(flat[s][name], flat[PRINCIPAL][name]),
                                [delta(d[s][name], d[PRINCIPAL][name]) for d in per_draw],
                                required)
                  for name, required in _metric_names(class_names)} for s in SCHEMES[1:]}
    return {'seed': seed, 'n_resamples': n_resamples, 'n_groups': len(groups),
            'group_ids': sorted(groups), 'method': DRAW_METHOD, 'class_group_counts': counts,
            'draws': draws, 'draws_sha256': digest, 'intervals': intervals,
            'delta_intervals': deltas}


# --- CLI ----------------------------------------------------------------------------

def join_manifest(predictions: list[dict], manifest_rows: list[dict]) -> list[dict]:
    """Total, unique correspondence by image_id. An equal hash never stands in for an ID."""
    if not manifest_rows:
        raise InvalidInput('the manifest has no rows')
    split_key = next((k for k in ('proposed_split', 'split') if k in manifest_rows[0]), None)
    splits = {p.get('split') for p in predictions} - {None, ''}
    if len(splits) > 1:
        raise InvalidInput(f'predictions mix splits {sorted(splits)}')
    split = splits.pop() if splits else 'test'
    by_id = {}
    for record in manifest_rows:
        if record['image_id'] in by_id:
            raise InvalidInput(f'the manifest repeats image_id {record["image_id"]}')
        by_id[record['image_id']] = record
    evaluated = {i: r for i, r in by_id.items() if split_key is None or r[split_key] == split}
    counts = Counter(str(p.get('image_id') or '') for p in predictions)
    problems = [f'{label} ({len(ids)}): {ids[:5]}' for label, ids in (
        ('repeated', sorted(i for i, n in counts.items() if n > 1)),
        ('missing', sorted(evaluated.keys() - counts.keys())),
        ('foreign', sorted(counts.keys() - evaluated.keys()))) if ids]
    if problems:
        raise InvalidInput('predictions and manifest rows of split '
                           f'{split!r} do not correspond one to one by image_id; '
                           + '; '.join(problems))
    if split_key:
        for field in ('cluster_id', 'group_id'):
            inside = {r[field] for r in evaluated.values()} - {''}
            crossing = sorted({r[field] for r in by_id.values()
                               if r[split_key] != split and r[field] in inside})
            if crossing:
                raise InvalidInput(f'{field} crosses the {split} split: {crossing[:5]}')
    joined = []
    for prediction in predictions:
        record = evaluated[prediction['image_id']]
        declared = prediction.get('sha256') or prediction.get('hash')
        if declared and declared != record['sha256']:
            raise InvalidInput(f'prediction hash of {prediction["image_id"]} differs from the '
                               'manifest')
        joined.append({**prediction, **{f: record[f] for f in MANIFEST_FIELDS}})
    return joined


def _read_predictions(path: Path) -> list[dict]:
    rows = []
    for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise InvalidInput(f'{path}:{number}: {error}') from None
    if not rows:
        raise InvalidInput(f'no predictions in {path}')
    return rows


def _read_manifest(path: Path) -> list[dict]:
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        missing = [f for f in MANIFEST_FIELDS if f not in (reader.fieldnames or [])]
        if missing:
            raise InvalidInput(f'manifest {path} lacks columns {missing}')
        rows = list(reader)
    sidecar = path.with_name(path.name + '.sha256')
    if sidecar.is_file() and sidecar.read_text(encoding='ascii').split()[0] != sha256(path):
        raise InvalidInput(f'manifest bytes differ from its sidecar {sidecar}')
    return rows


def _class_names(option: str | None, records: list[dict]) -> list[str]:
    def as_list(names):
        if isinstance(names, dict):  # model.names is {index: name}
            return [names[k] for k in sorted(names, key=int)]
        return list(names)

    # Every record must declare the same ordered list (review round 2 NEW-LOW-01); no option
    # can supply or replace it after the test observation.
    if any(not r.get('class_names') for r in records):
        raise InvalidInput('class names unknown: every prediction must carry class_names')
    declared = {tuple(as_list(r['class_names'])) for r in records}
    if len(declared) > 1:
        raise InvalidInput('predictions declare different class_names')
    return list(declared.pop())


def _fresh(root: Path, path: Path) -> Path:
    target = check_output(root, path)
    if target.exists():
        raise InvalidInput(f'output exists, refusing to overwrite: {target}')
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def _dump(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def _csv_rows(result: dict, boot: dict) -> list[dict]:
    rows = []
    for kind, table, schemes in (('estimate', 'intervals', SCHEMES),
                                 ('delta', 'delta_intervals', SCHEMES[1:])):
        for scheme in schemes:
            estimand = result['estimands'][scheme]
            for name, _ in _metric_names(result['class_names']):
                ci = boot.get(table, {}).get(scheme, {}).get(name, {})
                row = {'kind': kind, 'scheme': scheme if kind == 'estimate'
                       else f'{scheme}-{PRINCIPAL}', 'metric': name}
                if kind == 'estimate':
                    row['value'] = _flat(estimand, result['class_names'])[name]
                    row['reason'] = _why(estimand, name)
                    row['denominator'] = _denominator(estimand, name)
                else:
                    change = result['deltas'][scheme][name]
                    row.update(value=change['units'], percentage_points=change['percentage_points'],
                               reason=change['reason'])
                low, high = ci.get('ci95') or (None, None)
                row.update(ci_low=low, ci_high=high, n_defined=ci.get('n_defined'),
                           undefined_count=ci.get('undefined_count'),
                           ci_blocked=ci.get('blocked', boot.get('blocked')),
                           ci_reason=ci.get('reason', boot.get('reason')))
                rows.append(row)
    return rows


def _denominator(estimand: dict, name: str):
    if estimand['blocked'] or name == 'macro_f1':
        return None
    metrics = estimand['metrics']
    if name == 'accuracy':
        return metrics['accuracy_denominator']
    key, c = name[:-1].split('[', 1)
    return metrics['per_class'][c][f'{key}_denominator']


def _pct(value) -> str:
    return 'undefined' if value is None else f'{100 * value:.2f}'


def _ci(summary: dict) -> str:
    if not summary:
        return 'not computed'
    if summary.get('blocked'):
        return f'blocked: {summary["reason"]}'
    low, high = summary['ci95']
    return f'{100 * low:.2f} to {100 * high:.2f} ({summary["undefined_count"]} undefined)'


def _report(result: dict, boot: dict, inputs: dict) -> str:
    """Rounded once, here, from full-precision values."""
    s = result['structure']
    lines = ['# M2 duplicate sensitivity (AMENDMENT-04)', '',
             f'Principal estimand: `{PRINCIPAL}` (weight 1 per file of the frozen test). '
             'Predefined secondaries on the same predictions: `exact_sha_dedup` (minimum '
             'image_id per SHA256) and `cluster_weighted` (1/n per cluster). No scheme is '
             'selected by performance.', '',
             f'Predictions `{inputs["predictions"]}` sha256 `{inputs["predictions_sha256"]}`; '
             f'manifest `{inputs["manifest"]}` sha256 `{inputs["manifest_sha256"]}`.', '',
             f'Structure: {s["n_images"]} images, {s["n_unique_sha"]} unique SHA256, '
             f'{s["n_clusters"]} clusters, {s["n_groups"]} groups. {INDEPENDENCE}', '',
             '| scheme | accuracy % | CI95 | macro F1 % | CI95 |', '|---|---|---|---|---|']
    for scheme in SCHEMES:
        values = _flat(result['estimands'][scheme], result['class_names'])
        ci = boot.get('intervals', {}).get(scheme, {})
        lines.append(f'| {scheme} | {_pct(values["accuracy"])} | {_ci(ci.get("accuracy"))} | '
                     f'{_pct(values["macro_f1"])} | {_ci(ci.get("macro_f1"))} |')
    lines += ['', '| secondary - principal | accuracy pp | CI95 pp | macro F1 pp | CI95 pp |',
              '|---|---|---|---|---|']
    for scheme in SCHEMES[1:]:
        change = result['deltas'][scheme]
        ci = boot.get('delta_intervals', {}).get(scheme, {})
        lines.append(f'| {scheme} | {_pct(change["accuracy"]["units"])} | '
                     f'{_ci(ci.get("accuracy"))} | {_pct(change["macro_f1"]["units"])} | '
                     f'{_ci(ci.get("macro_f1"))} |')
    lines += ['', f'Bootstrap: group_id resampled with replacement, seed {inputs["seed"]}, '
              f'{inputs["resamples"]} draws shared by every scheme and delta, percentiles '
              f'2.5/97.5 over defined draws. Draws sha256 `{boot.get("draws_sha256")}`.']
    if boot.get('blocked'):
        lines.append(f'Resampling blocked: {boot["reason"]}.')
    if result['sha_prediction_conflicts']:
        lines.append('SHA copies with different predictions (investigate before interpreting '
                     f'the difference): {[c["sha256"] for c in result["sha_prediction_conflicts"]]}.')
    lines += ['', 'Undefined values:', ''] + [f'- {u}' for u in result['undefined'] or ['none']]
    return '\n'.join(lines) + '\n'


def _run_m2(root: Path, args, records: list[dict], inputs: dict) -> int:
    names = _class_names(None, records)
    targets = {'json': args.out, 'csv': args.out.with_suffix('.csv'),
               'confusions': args.out.with_name('model2_sensitivity_confusions.json'),
               'draws': args.out.with_name('model2_bootstrap_draws.json'),
               'report': Path('reports') / 'model2_duplicate_sensitivity.md'}
    targets = {k: _fresh(root, v) for k, v in targets.items()}
    result = m2_sensitivity(records, names)
    try:
        boot = m2_bootstrap(records, names, args.seed, args.resamples)
    except ResamplingBlocked as error:
        boot = {'blocked': True, 'reason': str(error)}
        print(f'CI BLOCKED: {error}', file=sys.stderr)
    _dump(targets['draws'], {'seed': args.seed, 'n_resamples': args.resamples,
                             'python': sys.version, **{k: v for k, v in boot.items()
                                                       if k not in ('intervals',
                                                                    'delta_intervals')}})
    _dump(targets['confusions'], {'class_names': names, 'rows': 'truth', 'columns': 'pred',
                                  **{s: {'confusion': e['confusion'], 'reason': e['reason']}
                                     for s, e in result['estimands'].items()}})
    summary = {k: v for k, v in boot.items() if k != 'draws'}
    _dump(targets['json'], {'inputs': inputs, **result, 'bootstrap': summary,
                            'draws_file': targets['draws'].name, 'notes': [INDEPENDENCE]})
    rows = _csv_rows(result, boot)
    fields = ['kind', 'scheme', 'metric', 'value', 'percentage_points', 'denominator', 'reason',
              'ci_low', 'ci_high', 'n_defined', 'undefined_count', 'ci_blocked', 'ci_reason']
    with targets['csv'].open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    targets['report'].write_text(_report(result, boot, inputs), encoding='utf-8')
    return 0


def m2_pred(probs: dict, class_names: list[str]) -> str:
    """The EXP-R03 rule: top-1 without rejection; an exact tie goes to the first model index."""
    return max(class_names, key=lambda name: (probs[name], -class_names.index(name)))


def authenticate_m2(predictions: Path, manifest: Path, manifest_rows: list[dict],
                    records: list[dict], root: Path) -> dict:
    """EXP-R03 artifacts only (TASK-05 round-3 MEDIUM-01): the canonical manifest by path and
    hash, the canonical predictions, mandatory sidecars, every immutable run-record field of
    M2_CONTRACT, complete test coverage, truth equal to the manifest class_name, the declared
    model class order and each prediction re-derived from its probabilities."""
    from src.evaluation import authority, predict_model2
    contract = predict_model2.M2_CONTRACT
    # TASK-05 round-5 NEW-HIGH-05: the approved M2 snapshot (producer, manifest, this code) and
    # a committed EXP-R03 run whose record names the approved producer by hash.
    try:
        authority.approved_inference(root, 'm2')
    except authority.NotApproved as error:
        raise InvalidInput(str(error)) from None
    run_files = [(Path(predictions).parent / name).resolve().relative_to(Path(root).resolve())
                 .as_posix() for name in ('predictions.jsonl', 'predictions.jsonl.sha256',
                                          'run_record.json')]
    if not authority.committed_clean(root, *run_files):
        raise InvalidInput('the EXP-R03 predictions, sidecar and run record must be committed')
    if Path(manifest).resolve() != (root / contract['manifest']).resolve() \
            or sha256(manifest) != contract['manifest_sha256']:
        raise InvalidInput('only the committed frozen M2 manifest is accepted')
    if Path(predictions).resolve() != (root / contract['predictions']).resolve():
        raise InvalidInput('only the EXP-R03 predictions are accepted')
    for path in (predictions, manifest):
        sidecar = path.with_name(path.name + '.sha256')
        if not sidecar.is_file() or sidecar.read_text(encoding='ascii').split()[:1] != [sha256(path)]:
            raise InvalidInput(f'{path.name} needs a matching .sha256 sidecar')
    record_path = predictions.with_name('run_record.json')
    if not record_path.is_file():
        raise InvalidInput('the M2 predictions need the run_record.json of EXP-R03')
    run = json.loads(record_path.read_text(encoding='utf-8'))
    expected = {k: contract[k] for k in ('experiment_id', 'weights_sha256', 'manifest_sha256',
                                         'imgsz', 'rule', 'input_contract')}
    expected['producer_sha256'] = authority.sha(root / authority.M2_PRODUCER)
    # TASK-05 rounds 6-7: the recorded runtime is the verified one of this interpreter and the
    # config is the M1 operating-point freeze, validated as M1 validates it.
    from src.evaluation import evaluate
    try:
        evaluate.sealed_config(root / contract['config'], root / evaluate.M1_MANIFEST, root)
    except evaluate.RunRejected as error:
        raise InvalidInput(f'EXP-R03 needs the frozen M1 operating point: {error}') from None
    expected.update({'ultralytics': contract['ultralytics'], 'config': contract['config'],
                     'config_sha256': authority.sha(root / contract['config']),
                     'dependencies_outside_checkout': True,
                     'environment': contract['environment'],
                     'environment_sha256': authority.sha(root / contract['environment']),
                     'runtime_sha256': authority.runtime_identity()})
    wrong = sorted(k for k, v in expected.items() if run.get(k) != v)
    if sorted(run.get('runtime_modules') or {}) != ['torch', 'ultralytics']:
        wrong.append('runtime_modules')
    if wrong or run.get('predictions_sha256') != sha256(predictions):
        raise InvalidInput(f'the run record does not bind these predictions to EXP-R03: {wrong}')
    names = run.get('model_names') or {}
    order = [names[k] for k in sorted(names, key=int)]
    if sorted(order) != sorted(contract['class_names']):
        raise InvalidInput(f'the run record declares other classes: {order}')
    split_key = 'split' if 'split' in manifest_rows[0] else 'proposed_split'
    tested = [r for r in manifest_rows if r.get(split_key) == 'test']
    if run.get('images') != len(records) or len(records) != len(tested):
        raise InvalidInput('the run record, the predictions and the test rows differ in number')
    truth = {r['image_id']: r.get('class_name') for r in manifest_rows}
    wrong = sorted(r['image_id'] for r in records if truth.get(r['image_id']) != r.get('truth'))
    if wrong:
        raise InvalidInput(f'truth differs from the manifest class_name: {wrong[:5]}')
    if any(not r.get('class_names') for r in records):
        raise InvalidInput('class names unknown: every prediction must carry class_names')
    wrong = sorted(r['image_id'] for r in records
                   if r.get('class_names') != order or not isinstance(r.get('probs'), dict)
                   or set(r['probs']) != set(order) or r.get('pred') != m2_pred(r['probs'], order))
    if wrong:
        raise InvalidInput(f'predictions do not follow the recorded class order and rule: {wrong[:5]}')
    return run


def _run_m2_intervals(root: Path, args, records: list[dict], inputs: dict) -> int:
    """The frozen primary M2 command (plan TASK-05): image-weighted estimand with the group
    bootstrap; the sensitivity command adds the secondary schemes on the same draws."""
    target = _fresh(root, args.out)
    names = _class_names(None, records)
    try:
        boot = m2_bootstrap(records, names, args.seed, args.resamples)
    except ResamplingBlocked as error:
        boot = {'blocked': True, 'reason': str(error)}
        print(f'CI BLOCKED: {error}', file=sys.stderr)
    point = _estimands(records, names)[PRINCIPAL]
    _dump(target, {'inputs': inputs, 'estimand': PRINCIPAL, 'class_names': names,
                   'point': _flat(point, names), 'blocked': point['blocked'],
                   'reason': point['reason'],
                   'intervals': boot.get('intervals', {}).get(PRINCIPAL),
                   'bootstrap': {k: boot.get(k) for k in ('seed', 'n_resamples', 'n_groups',
                                                          'method', 'draws_sha256', 'blocked',
                                                          'reason')},
                   'notes': [INDEPENDENCE]})
    return 0


def _run_m1(root: Path, args, records: list[dict], inputs: dict, paths: dict) -> int:
    target = _fresh(root, args.out)
    from src.evaluation.provenance import configure_environment, verify_environment
    configure_environment(root)
    verify_environment(root)
    try:
        from src.evaluation import evaluate
    except ModuleNotFoundError as error:
        if error.name not in ('src.evaluation.evaluate', None):
            raise
        raise InvalidInput(f'M1 intervals need src.evaluation.evaluate: {error}') from None
    # The frozen command names no config: the operating point is the committed frozen config,
    # validated by the scorer's own validator, and the predictions must be the ones verified
    # for it (TASK-05 review round 2 NEW-HIGH-02). No option can substitute a threshold.
    frozen = root / evaluate.FROZEN_CONFIG
    try:
        config = evaluate.sealed_config(frozen, paths['groups'])
        evaluate.verified_provenance(paths['predictions'], frozen, paths['groups'], 'test')
        evaluate.imported_runtime()
    except evaluate.RunRejected as error:
        raise InvalidInput(str(error)) from None
    names = config['class_names']
    for record in records:
        record['gt_classes'] = sorted({names[g['class_id']] for g in record['gt']})
    inputs['config_sha256'] = sha256(frozen)
    _dump(target, {'inputs': inputs, **intervals_for(records, evaluate.interval_metrics(config),
                                                     args.seed, args.resamples),
                   'notes': [INDEPENDENCE]})
    return 0


def main(argv: list[str] | None = None, root: Path | None = None) -> int:
    parser = argparse.ArgumentParser(description='TASK-05 intervals and M2 sensitivity')
    parser.add_argument('--predictions', type=Path, required=True)
    parser.add_argument('--groups', type=Path, required=True,
                        help='manifest with image_id,sha256,cluster_id,group_id[,split]')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--resamples', type=int, default=2000)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--m2-sensitivity', action='store_true')
    argv = sys.argv[1:] if argv is None else argv
    args = parser.parse_args(argv)
    try:
        root = Path(root) if root else authorized_root()
        paths = {'predictions': args.predictions, 'groups': args.groups}
        paths = {k: p if p.is_absolute() else root / p for k, p in paths.items()}
        for path in paths.values():
            if not path.is_file():
                raise InvalidInput(f'input missing: {path}')
        if args.resamples < 1:
            raise InvalidInput('--resamples must be positive')
        manifest_rows = _read_manifest(paths['groups'])
        records = join_manifest(_read_predictions(paths['predictions']), manifest_rows)
        inputs = {'predictions': str(args.predictions),
                  'predictions_sha256': sha256(paths['predictions']),
                  'manifest': str(args.groups), 'manifest_sha256': sha256(paths['groups']),
                  'seed': args.seed, 'resamples': args.resamples,
                  'command': 'python -m src.statistics.intervals ' + ' '.join(argv)}
        # The model follows from the manifest, so the frozen primary M2 command (no flag) runs
        # the M2 path (TASK-05 round-3 NEW-MEDIUM-01).
        from src.evaluation.predict_model2 import M2_CONTRACT
        if paths['groups'].resolve() == (root / M2_CONTRACT['manifest']).resolve():
            inputs['run_record'] = authenticate_m2(paths['predictions'], paths['groups'],
                                                   manifest_rows, records, root)
            if args.m2_sensitivity:
                return _run_m2(root, args, records, inputs)
            return _run_m2_intervals(root, args, records, inputs)
        if args.m2_sensitivity:
            raise InvalidInput('--m2-sensitivity needs the frozen M2 manifest')
        return _run_m1(root, args, records, inputs, paths)
    except ValueError as error:  # InvalidInput and invalid records alike
        print(f'INVALID INPUT: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
