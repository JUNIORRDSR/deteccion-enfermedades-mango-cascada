"""TASK-06: verifiable latency of the M1 -> crops -> M2 cascade (SPEC section 8).

Wall boundaries, each timed with its own clock reads (perf_counter_ns), never derived by
summing other walls: read (file bytes), decode, m1 (full M1 call), m2_crops (crops + M2
calls), annotate, encode (JPEG in memory); cascade = m1 + m2_crops without decode;
end_to_end = file read -> annotated JPEG encoded, models already resident. Weight loading and
the first call after it (cold start) are recorded apart. Ultralytics .speed is recorded as
internal time in ms and never added to any wall. Network, SQLite and frontend are not measured.
"""

import argparse
import csv
import datetime
import json
import math
import os
import platform
import statistics
import sys
import time
from pathlib import Path

from src.evaluation.evaluate import (
    VALIDATION_SPLIT, RunRejected, read_manifest, yolo_labels_to_gt,
)
from src.evaluation.predict_model2 import ART002_SHA256, CLASS_NAMES as M2_CLASS_NAMES

FROZEN = {'batch': 1, 'precision': 'fp32', 'm1_imgsz': 640, 'm2_imgsz': 224,
          'warmups_per_image': 10, 'iterations_per_image': 100, 'torch_threads': 1,
          'torch_interop_threads': 1, 'opencv_threads': 1, 'processes': 1, 'device': 'cpu',
          'pool_size': 32, 'class_names': ['Enfermo', 'Saludable'],
          'manifest': 'data/manifests/model1_clean_manifest.csv', 'm2_conf': 0.4,
          'raspberry_pi_4': 'BLOCKED_BY_HARDWARE'}
STRATUM_CLASS = 'Enfermo'
WALL = ('read', 'decode', 'm1', 'm2_crops', 'annotate', 'encode', 'cascade', 'end_to_end')
SUMMARY_DEFINITION = (
    'benchmark-summary-v1: mean = arithmetic mean; median = middle value, or mean of the two '
    'middle values; std = population standard deviation (ddof=0, statistics.pstdev); p95 = '
    'linear interpolation between order statistics at 0-based rank (n-1)*0.95 (Hyndman-Fan '
    'type 7, NumPy default "linear"); min, max and n over the successful measured repetitions')
FIELDS = ('image_id', 'sha256', 'run_order', 'repetition', 'stage', 'kind', 'wall_ns',
          'internal_ms', 'n_predicted_fruits', 'n_m2_calls', 'status', 'error')
POOL_FIELDS = ('run_order', 'image_id', 'sha256', 'label_sha256', 'with_enfermo', 'reason',
               'logical_root', 'logical_path')


def summarize(times_ns: list[int]) -> dict:
    """Descriptive summary; the definitions travel with the numbers."""
    if not times_ns:
        raise ValueError('no times to summarise: n=0')
    if any(not t >= 0 for t in times_ns):  # also rejects NaN
        raise ValueError('times must be non-negative')
    ordered = sorted(times_ns)
    rank = (len(ordered) - 1) * 0.95
    low = math.floor(rank)
    high = min(low + 1, len(ordered) - 1)
    return {'n': len(ordered), 'mean': statistics.fmean(ordered),
            'median': statistics.median(ordered), 'std': statistics.pstdev(ordered),
            'p95': ordered[low] + (rank - low) * (ordered[high] - ordered[low]),
            'min': ordered[0], 'max': ordered[-1], 'definition': SUMMARY_DEFINITION}


def measure(stages: list[tuple[str, callable]], clock) -> dict:
    """Each stage between its own two reads; the total between two outer reads of its own.

    A stage callable receives the results of the earlier stages by name.
    """
    start = clock()
    stages_ns, results = {}, {}
    for name, stage in stages:
        before = clock()
        results[name] = stage(results)
        stages_ns[name] = clock() - before
    return {'stages_ns': stages_ns, 'total_ns': clock() - start, 'results': results}


def synced_clock(device: str, clock=time.perf_counter_ns, synchronize=None):
    """On CUDA, wait for queued GPU work before every read; elsewhere the clock is unchanged."""
    if not str(device).startswith('cuda'):
        return clock

    def read():
        synchronize()
        return clock()
    return read


def iteration(steps: dict, clock) -> dict:
    """One pass from file bytes to encoded JPEG; cascade is an inner measure without decode."""
    inner = {}

    def cascade(r):
        inner.update(measure([('m1', lambda c: steps['m1'](r['decode'])),
                              ('m2_crops', lambda c: steps['m2_crops'](r['decode'], c['m1']))],
                             clock))
        return inner['results']['m2_crops']

    outer = measure([('read', lambda r: steps['read']()),
                     ('decode', lambda r: steps['decode'](r['read'])),
                     ('cascade', cascade),
                     ('annotate', lambda r: steps['annotate'](r['decode'], r['cascade'])),
                     ('encode', lambda r: steps['encode'](r['annotate']))], clock)
    wall = {**outer['stages_ns'], **inner['stages_ns'],
            'cascade': inner['total_ns'], 'end_to_end': outer['total_ns']}
    return {'wall_ns': {stage: wall[stage] for stage in WALL},
            'results': {**outer['results'], **inner['results']}}


def run_image(one, warmups: int, iterations: int) -> dict:
    """Warm-ups run the same pass and are never recorded as measurements. Every measured
    repetition is kept: failures with their error, slow runs as they are."""
    first, warmup_failures = None, []
    for n in range(warmups):
        try:
            result = one()
        except Exception as error:  # a failure is data, not a reason to stop
            result = {'status': 'failed', 'error': repr(error)}
            warmup_failures.append(repr(error))
        if n == 0:
            first = result
    measured = []
    for repetition in range(1, iterations + 1):
        try:
            measured.append({'repetition': repetition, 'status': 'ok', **one()})
        except Exception as error:
            measured.append({'repetition': repetition, 'status': 'failed', 'error': repr(error)})
    return {'first_warmup': first, 'warmup_failures': warmup_failures, 'measured': measured}


def rows_for(image: dict, measured: list[dict]) -> list[dict]:
    """One raw row per repetition x stage; a failed repetition keeps one failure row."""
    rows = []
    for m in measured:
        base = {'image_id': image['image_id'], 'sha256': image['sha256'],
                'run_order': image['run_order'], 'repetition': m['repetition'],
                'n_predicted_fruits': m.get('n_predicted_fruits', ''),
                'n_m2_calls': m.get('n_m2_calls', ''), 'status': m['status'],
                'error': m.get('error', ''), 'wall_ns': '', 'internal_ms': ''}
        if m['status'] != 'ok':
            rows.append({**base, 'stage': 'end_to_end', 'kind': 'wall'})
            continue
        rows += [{**base, 'stage': s, 'kind': 'wall', 'wall_ns': m['wall_ns'][s]} for s in WALL]
        rows += [{**base, 'stage': s, 'kind': 'internal_ultralytics', 'internal_ms': v}
                 for s, v in m['internal_ms'].items()]
    return rows


def select_pool(rows: list[dict], labels_by_id: dict, k: int = 32) -> list[dict]:
    """Validation only, ordered by (sha256, image_id): the first image of each available
    stratum (with / without Enfermo), then the rest in that order up to k; run in that order."""
    valid = [r for r in rows if r['proposed_split'] == VALIDATION_SPLIT]
    ids = [r['image_id'] for r in valid]
    if len(set(ids)) != len(ids):
        raise RunRejected('the manifest repeats a validation image_id')
    missing = [i for i in ids if i not in labels_by_id]
    if missing:
        raise RunRejected(f'{len(missing)} validation images have no label, first {missing[0]}')
    ordered = sorted(valid, key=lambda r: (r['sha256'], r['image_id']))
    firsts = {}
    for r in ordered:
        firsts.setdefault(STRATUM_CLASS in labels_by_id[r['image_id']], r['image_id'])
    seeds = set(firsts.values())
    chosen = ([r for r in ordered if r['image_id'] in seeds]
              + [r for r in ordered if r['image_id'] not in seeds])[:k]
    chosen.sort(key=lambda r: (r['sha256'], r['image_id']))
    return [{**r, 'with_enfermo': STRATUM_CLASS in labels_by_id[r['image_id']],
             'reason': 'first_of_stratum' if r['image_id'] in seeds else 'fill', 'run_order': n}
            for n, r in enumerate(chosen, 1)]


def read_config(path: Path) -> dict:
    """Frozen constants first; the CLI refuses while the M1 checkpoint or threshold is null."""
    try:
        config = json.loads(Path(path).read_text(encoding='utf-8'))
    except json.JSONDecodeError as error:
        raise RunRejected(f'config is not JSON: {error}') from None
    for key, value in FROZEN.items():
        if config.get(key) != value:
            raise RunRejected(f'{key} is {config.get(key)!r}; the frozen protocol fixes {value!r}')
    if (config.get('m2_weights') or {}).get('sha256') != ART002_SHA256:
        raise RunRejected('M2 weights must be ART-002 by hash')
    m1 = config.get('m1_weights') or {}
    if not m1.get('logical_root') or not m1.get('logical_path') or not m1.get('sha256'):
        raise RunRejected('M1 weights are not frozen yet: m1_weights path and sha256 are null')
    conf = config.get('m1_conf')
    if not isinstance(conf, (int, float)) or isinstance(conf, bool) or not 0 < conf < 1:
        raise RunRejected(f'M1 operating point is not frozen yet: m1_conf is {conf!r}')
    return config


def _resolve(source_id: str, logical_root: str, logical_path: str, digest: str,
             roots: dict) -> Path:
    """Root mapping, no escape, bytes equal to the declared hash."""
    from src.evaluation.provenance import resolve_source
    try:
        return resolve_source({'source_id': source_id, 'logical_root': logical_root,
                               'logical_path': logical_path, 'sha256': digest}, roots)
    except FileNotFoundError as error:
        raise RunRejected(str(error)) from None


def _cpu_name() -> str:
    if sys.platform == 'win32':
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r'HARDWARE\DESCRIPTION\System\CentralProcessor\0') as key:
            return str(winreg.QueryValueEx(key, 'ProcessorNameString')[0]).strip()
    try:
        for line in Path('/proc/cpuinfo').read_text(encoding='utf-8').splitlines():
            if line.startswith('model name'):
                return line.split(':', 1)[1].strip()
    except OSError:
        pass
    return platform.processor()


def _environment(torch, cv2, ultralytics_version: str, device: str) -> dict:
    import numpy
    import psutil
    return {'cpu_name': _cpu_name(), 'machine': platform.machine(),
            'physical_cores': psutil.cpu_count(logical=False), 'logical_cores': os.cpu_count(),
            'ram_bytes': psutil.virtual_memory().total, 'os': platform.platform(),
            'python': sys.version, 'executable': sys.executable, 'torch': torch.__version__,
            'ultralytics': ultralytics_version, 'opencv': cv2.__version__,
            'numpy': numpy.__version__, 'torch_threads': torch.get_num_threads(),
            'torch_interop_threads': torch.get_num_interop_threads(),
            'opencv_threads': cv2.getNumThreads(), 'cuda_available': torch.cuda.is_available(),
            'device': device, 'thread_env': {name: os.environ.get(name) for name in (
                'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
                'CUDA_VISIBLE_DEVICES')}}


def _ms(value) -> str:
    return f'{value / 1e6:.3f}'


def _table(title: str, samples: dict, scale) -> list[str]:
    lines = [f'### {title}', '', '| stage | n | mean | median | std | p95 | min | max |',
             '|---|---|---|---|---|---|---|---|']
    for stage, values in samples.items():
        if not values:
            lines.append(f'| {stage} | 0 | undefined | | | | | |')
            continue
        s = summarize(values)
        lines.append(f"| {stage} | {s['n']} | " + ' | '.join(
            scale(s[key]) for key in ('mean', 'median', 'std', 'p95', 'min', 'max')) + ' |')
    return lines + ['']


def render_report(run: dict, results: list[tuple[dict, dict]]) -> str:
    """Pooled distribution, per-image summaries, internal times apart, and the Pi block."""
    ok = [(image, m) for image, r in results for m in r['measured'] if m['status'] == 'ok']
    failures = sum(m['status'] != 'ok' for _, r in results for m in r['measured'])
    env, cold = run['environment'], run['cold_start_ns']
    lines = ['# Benchmark report (TASK-06)', '',
             f"Recorded {run['recorded_at']}. Command: `{run['command']}`.", '',
             '## Protocol', '',
             *[f'- {key}: {value}' for key, value in run['protocol'].items()],
             f"- summary definitions: {SUMMARY_DEFINITION}", '',
             '## Boundaries', '', __doc__.strip(), '',
             '## Hardware and runtime', '',
             *[f'- {key}: {value}' for key, value in env.items()], '',
             '## Pool', '',
             f"{len(results)} validation images, file `{run['pool_file']}` "
             f"(sha256 {run['pool_sha256']}), saved before any timing. "
             f"With Enfermo: {sum(i['with_enfermo'] for i, _ in results)}; "
             f"without: {sum(not i['with_enfermo'] for i, _ in results)}.", '',
             '## Cold start (recorded apart, not in any distribution)', '',
             *[f'- {key}: {_ms(value)} ms' if isinstance(value, int) else f'- {key}: {value}'
               for key, value in cold.items()], '',
             '## Distribution over all images and repetitions', '',
             f"Measured repetitions: {len(ok) + failures}; failed: {failures}; warm-up "
             f"failures: {sum(len(r['warmup_failures']) for _, r in results)}. "
             'No run is dropped for being slow.', '',
             *_table('Wall time (ms)', {s: [m['wall_ns'][s] for _, m in ok] for s in WALL}, _ms),
             *_table('Ultralytics internal .speed (ms; internal, never added to wall)',
                     {k: [m['internal_ms'][k] for _, m in ok]
                      for k in (ok[0][1]['internal_ms'] if ok else {})},
                     lambda v: f'{v:.3f}'),
             '## Per image (wall ms)', '',
             '| run | image_id | Enfermo | fruits | M2 calls | failed | cascade median | '
             'cascade p95 | end_to_end median | end_to_end p95 | end_to_end max |',
             '|---|---|---|---|---|---|---|---|---|---|---|']
    for image, r in results:
        good = [m for m in r['measured'] if m['status'] == 'ok']
        fruits = sorted({m['n_predicted_fruits'] for m in good})
        calls = sorted({m['n_m2_calls'] for m in good})
        cells = []
        for stage in ('cascade', 'end_to_end'):
            s = summarize([m['wall_ns'][stage] for m in good]) if good else None
            keys = ('median', 'p95') + (('max',) if stage == 'end_to_end' else ())
            cells += [_ms(s[k]) if s else 'undefined' for k in keys]
        lines.append(f"| {image['run_order']} | {image['image_id']} | {image['with_enfermo']} | "
                     f"{'/'.join(map(str, fruits))} | {'/'.join(map(str, calls))} | "
                     f"{len(r['measured']) - len(good)} | " + ' | '.join(cells) + ' |')
    lines += ['', '## Raspberry Pi 4: BLOCKED_BY_HARDWARE', '',
              'No physical device or measurement environment was available as evidence, so no '
              'Pi row exists and the CPU numbers above do not stand in for it. Protocol to run '
              'when real access is given: the same command, config and pool on the device, '
              'with its hardware, OS and runtime recorded; batch 1, FP32, M1 640 / M2 224, '
              '10 warm-ups and 100 measured repetitions per image, one process, threads 1.', '',
              '## Not measured', '', 'Network, SQLite and frontend are outside every boundary.', '']
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    config = read_config(args.config)  # stdlib only, before any scientific import

    from src.evaluation.provenance import (
        authorized_root, check_output, configure_environment, lock_ultralytics, sha256,
        validate_root_mapping, verify_environment,
    )
    root = authorized_root()
    configure_environment(root)
    verify_environment(root)
    out, report = check_output(root, args.out), check_output(root, args.report)
    pool_file = check_output(root, out.with_name(out.stem + '_pool.csv'))
    run_file = check_output(root, out.with_name(out.stem + '_run.json'))
    for target in (out, report, pool_file, run_file):
        if target.exists():
            raise RunRejected(f'output already exists and is never overwritten: {target}')
    roots = validate_root_mapping(json.loads((root / 'configs' / 'root_mapping.json')
                                             .read_text(encoding='utf-8')))

    manifest = root / config['manifest']
    sidecar = manifest.with_name(manifest.name + '.sha256')
    if not manifest.is_file() or not sidecar.is_file():
        raise RunRejected(f'frozen manifest or its sidecar is missing: {manifest}')
    manifest_sha = sha256(manifest)
    if sidecar.read_text(encoding='ascii').split()[:1] != [manifest_sha]:
        raise RunRejected('manifest differs from its frozen sidecar')
    weights = {name: _resolve(name.upper(), config[f'{name}_weights']['logical_root'],
                              config[f'{name}_weights']['logical_path'],
                              config[f'{name}_weights']['sha256'], roots)
               for name in ('m1', 'm2')}

    names = config['class_names']
    rows = read_manifest(manifest)
    labels_by_id = {}
    for row in rows:
        if row['proposed_split'] != VALIDATION_SPLIT:
            continue
        label = _resolve(row['image_id'], row['logical_root'], row['label'],
                         row['label_sha256'], roots)
        ids = [g['class_id'] for g in yolo_labels_to_gt(label.read_text(encoding='utf-8'), 1, 1)]
        if any(i >= len(names) for i in ids):
            raise RunRejected(f"{row['image_id']}: label class outside {names}")
        labels_by_id[row['image_id']] = [names[i] for i in ids]
    pool = select_pool(rows, labels_by_id, config['pool_size'])
    paths = {p['image_id']: _resolve(p['image_id'], p['logical_root'], p['logical_path'],
                                     p['sha256'], roots) for p in pool}
    pool_file.parent.mkdir(parents=True, exist_ok=True)
    with pool_file.open('x', encoding='utf-8', newline='') as stream:  # before any timing
        writer = csv.DictWriter(stream, POOL_FIELDS, extrasaction='ignore', lineterminator='\n')
        writer.writeheader()
        writer.writerows(pool)

    os.environ['YOLO_OFFLINE'] = 'true'
    import torch
    torch.set_num_threads(config['torch_threads'])  # before any model load
    torch.set_num_interop_threads(config['torch_interop_threads'])
    import cv2
    cv2.setNumThreads(config['opencv_threads'])
    from ultralytics import SETTINGS, YOLO, __version__
    lock_ultralytics(SETTINGS, root)
    from src.cascade import runtime
    environment = _environment(torch, cv2, __version__, config['device'])
    if (environment['torch_threads'], environment['torch_interop_threads']) != (1, 1):
        raise RunRejected(f'torch threads are not 1: {environment}')

    device = config['device']
    clock = synced_clock(device, time.perf_counter_ns, torch.cuda.synchronize)
    cold = {}
    start = clock()
    detector = YOLO(str(weights['m1']))
    cold['load_m1_ns'] = clock() - start
    start = clock()
    classifier = YOLO(str(weights['m2']))
    cold['load_m2_ns'] = clock() - start
    if [detector.names[i] for i in sorted(detector.names)] != names:
        raise RunRejected(f'M1 classes {detector.names} differ from {names}')
    if sorted(classifier.names.values()) != sorted(M2_CLASS_NAMES):
        raise RunRejected(f'M2 classes {classifier.names} differ from {M2_CLASS_NAMES}')

    results = []
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('x', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, FIELDS, lineterminator='\n')
        writer.writeheader()
        for image in pool:
            path = paths[image['image_id']]
            steps = {'read': lambda: runtime.read_file(path), 'decode': runtime.decode,
                     'm1': lambda frame: runtime.detect(frame, detector, config['m1_conf'],
                                                        config['m1_imgsz'], device),
                     'm2_crops': lambda frame, det: runtime.classify_crops(
                         frame, det, classifier, config['m2_conf'], config['m2_imgsz'], device),
                     'annotate': runtime.annotate, 'encode': runtime.encode}

            def one():
                done = iteration(steps, clock)
                return {'wall_ns': done['wall_ns'], **runtime.describe(
                    done['results']['m1'], done['results']['m2_crops'])}

            result = run_image(one, config['warmups_per_image'], config['iterations_per_image'])
            writer.writerows(rows_for(image, result['measured']))
            stream.flush()
            os.fsync(stream.fileno())
            results.append((image, result))
            if 'first_call_after_load_end_to_end_ns' not in cold:
                first = result['first_warmup'] or {}
                cold['first_call_after_load_end_to_end_ns'] = \
                    (first.get('wall_ns') or {}).get('end_to_end', first.get('error'))

    run = {'task': 'TASK-06', 'recorded_at': datetime.datetime.now(datetime.timezone.utc)
           .isoformat(), 'command': ' '.join(sys.argv),
           'protocol': {key: config[key] for key in FROZEN} | {'m1_conf': config['m1_conf']},
           'config_sha256': sha256(args.config), 'manifest_sha256': manifest_sha,
           'weights': {name: {'path': str(path), 'sha256': sha256(path)}
                       for name, path in weights.items()},
           'pool_file': pool_file.relative_to(root).as_posix(), 'pool_sha256': sha256(pool_file),
           'raw_file': out.relative_to(root).as_posix(), 'raw_sha256': sha256(out),
           'channel_order': runtime.CHANNEL_ORDER, 'cascade_source': runtime.__doc__.strip(),
           'summary_definition': SUMMARY_DEFINITION, 'environment': environment,
           'cold_start_ns': cold,
           'warmup_failures': {i['image_id']: r['warmup_failures'] for i, r in results
                               if r['warmup_failures']}}
    run_file.write_text(json.dumps(run, indent=2) + '\n', encoding='utf-8')
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(render_report(run, results), encoding='utf-8')
    print(json.dumps({'images': len(results), 'raw_sha256': run['raw_sha256']}))
    return 0


if __name__ == '__main__':
    from src.evaluation.provenance import InvalidInput
    try:
        sys.exit(main())
    except (RunRejected, InvalidInput) as error:
        print(f'REJECTED: {error}', file=sys.stderr)
        sys.exit(2)
