"""Source identity and write containment for reconstructed evaluations.

Hardened across two independent adversarial review rounds. Contracts name the
finding they answer.

Round 2 established that pathname canonicalisation is NOT physical-file
identity: two hardlinks to one file have different realpaths. Existing files
are therefore compared by OS file identity (st_dev, st_ino) as well.

`create_run` takes the authorized root in addition to the target path. The
frozen brief sketches `create_run(path)`, but the frozen global constraint
requires every path consumer to refuse writes outside the authorized checkout.
The signature change is a documented refinement in favour of the binding
constraint, not a silent deviation.
"""

import argparse
import csv
import hashlib
import io
import json
import os
import re
import site
import sys
import traceback
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit, urlunsplit


STATE_DIRS = {
    'YOLO_CONFIG_DIR': 'ultralytics', 'PIP_CACHE_DIR': 'pip',
    'TORCH_HOME': 'torch', 'XDG_CACHE_HOME': 'cache',
    'MPLCONFIGDIR': 'matplotlib', 'TEMP': 'tmp', 'TMP': 'tmp',
    'HF_HOME': 'huggingface', 'NUMBA_CACHE_DIR': 'numba',
    'PYTHONUSERBASE': 'python_user',
}

ISOLATION_VALUES = {
    'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONNOUSERSITE': '1',
    'WANDB_DISABLED': 'true', 'WANDB_MODE': 'disabled', 'COMET_MODE': 'DISABLED',
}

ULTRALYTICS_OFF = ('sync', 'clearml', 'comet', 'dvc', 'hub', 'mlflow',
                   'neptune', 'raytune', 'tensorboard', 'wandb')

# The frozen protocol is immutable by construction, so its digest authenticates
# the checkout. Finding 2 round 2: existence of a file with the right NAME is not
# authentication.
FREEZE_RELATIVE = 'provenance/protocol_freeze.json'
FREEZE_SHA256 = '6d5aa3ff47cba97f8ecd0dd15683bb96f0d53146f3af1ce1e95bf24cec7cbc8b'

RESERVED_DEVICES = ({'CON', 'PRN', 'AUX', 'NUL', 'CLOCK$'}
                    | {f'COM{n}' for n in range(1, 10)}
                    | {f'LPT{n}' for n in range(1, 10)})

PROTECTED_RELATIVE = (
    'provenance/protocol_freeze.json', 'provenance/protocol_freeze.md',
    'provenance/protocol_freeze.sha256', 'provenance/source_manifest.csv',
    'provenance/source_locations.csv', 'provenance/test_access_log.csv',
    'configs/root_mapping.json', 'configs/inputs.json',
    'docs/superpowers/specs/2026-09-17-albus26-major-revision-design.md',
    'docs/superpowers/plans/2026-09-17-albus26-major-revision.md',
)

# Finding 2 round 2: an eight-name tuple is not an output policy. Writers are
# confined to declared output subtrees, and code/test trees are never outputs.
OUTPUT_SUBTREES = (
    'reports', 'artifacts', 'experiments', 'manuscript', 'configs',
    'data/derived', 'data/audits', 'data/manifests', 'data/splits',
    'provenance/environment', 'provenance/commands', 'provenance/incidents',
    'provenance/runtime_state', 'provenance/protocol_amendments',
    'provenance/authorizations',
    # Only the research notes under docs are writable. docs/superpowers holds the
    # FROZEN spec and plan, whose digests the protocol freeze records; round 3
    # showed the previous 'docs' entry let the guard overwrite them.
    'docs/research',
)
NEVER_OUTPUT_SUBTREES = ('src', 'tests', '.git', '.venv')

# Registries live beside the protected manifests and ARE meant to be updated.
OUTPUT_FILES = ('provenance/artifact_registry.csv', 'provenance/experiment_registry.csv')

SIDECAR_FIELDS = ('source_id', 'logical_root', 'logical_path', 'sha256', 'local_absolute_path')
MANIFEST_FIELDS = ('source_id', 'sha256')

# Finding 6 round 2: widen beyond the obvious four names.
SECRET_KEY = re.compile(
    r'(?i)(?:^|[_-])(password|passwd|secret|token|api[_-]?key|authorization|credential|'
    r'private[_-]?key|access[_-]?key|secret[_-]?key|signing[_-]?key|signature|'
    r'cookie|session|bearer|auth)(?:$|[_-])')
HASH_SYNTAX = re.compile(r'^[0-9a-f]{64}$')
SCIENTIFIC_MODULES = ('ultralytics', 'torch', 'torchvision', 'cv2', 'numpy', 'PIL',
                      'sklearn', 'matplotlib', 'numba', 'imagehash', 'scipy')


class InvalidInput(ValueError):
    """Invalid scientific input or malformed reference. Maps to CLI exit code 2.

    An operational I/O failure is NOT this; those propagate with traceback.
    """


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def canonical(path: Path) -> str:
    """Portable resolved pathname. NOT sufficient alone; see file_identity."""
    return os.path.normcase(os.path.realpath(str(path)))


def file_identity(path: Path) -> tuple:
    """OS identity of an existing file: hardlinks to one file share it.

    Finding 1 round 2: realpath does not resolve hardlinks, so two SRC-IDs could
    name one physical file and pass a pathname-only check. Falls back to the
    canonical pathname when the file does not exist.
    """
    try:
        stat = Path(path).stat()
    except OSError:
        return ('path', canonical(path))
    return ('inode', stat.st_dev, stat.st_ino)


def _reject_alias(path: Path) -> None:
    candidate = Path(path)
    parts = candidate.parts
    if candidate.anchor:
        parts = parts[1:]  # the drive/root anchor legitimately contains a colon
    for part in parts:
        # NTFS alternate data streams and drive-relative forms: NUL:$DATA and
        # protected.json:evil both defeated the previous spelling comparison.
        if ':' in part:
            raise InvalidInput(f'colon form or alternate data stream in output path: {part!r}')
        if part.split('.')[0].upper() in RESERVED_DEVICES:
            raise InvalidInput(f'reserved device name in output path: {part}')
        if part != part.rstrip('. ') and part not in ('.', '..'):
            raise InvalidInput(f'trailing dot or space alias in output path: {part!r}')


def authorized_root(start: Path | None = None, expected_sha256: str = FREEZE_SHA256) -> Path:
    """The checkout whose frozen protocol matches the expected digest."""
    current = Path(start or Path.cwd()).resolve()
    seen = []
    for candidate in (current, *current.parents):
        freeze = candidate / FREEZE_RELATIVE
        if not freeze.is_file():
            continue
        digest = sha256(freeze)
        if digest == expected_sha256:
            return candidate
        seen.append(f'{candidate}: freeze digest {digest}')
    if seen:
        raise InvalidInput('found a protocol freeze but its digest does not authenticate this '
                           f'checkout; expected {expected_sha256}; saw ' + '; '.join(seen))
    raise InvalidInput(f'not inside an authorized checkout: {current}')


def authenticate_root(root: Path, expected_sha256: str = FREEZE_SHA256) -> Path:
    """Finding 2 round 2: check_output authorized ANY caller-selected root."""
    root = Path(root).resolve()
    freeze = root / FREEZE_RELATIVE
    if not freeze.is_file():
        raise InvalidInput(f'root is not an authorized checkout, no {FREEZE_RELATIVE}: {root}')
    digest = sha256(freeze)
    if digest != expected_sha256:
        raise InvalidInput(f'root freeze digest {digest} does not authenticate {root}')
    return root


def check_output(root: Path, path: Path, expected_freeze: str = FREEZE_SHA256,
                 allow_directory: bool = False) -> Path:
    root = authenticate_root(root, expected_freeze)
    _reject_alias(path)
    candidate = Path(path)
    resolved = (candidate if candidate.is_absolute() else root / candidate).resolve()
    if resolved == root or not resolved.is_relative_to(root):
        raise InvalidInput(f'output outside workspace: {resolved}')
    identity = file_identity(resolved)
    for relative in PROTECTED_RELATIVE:
        protected = root / relative
        if identity == file_identity(protected) or canonical(resolved) == canonical(protected):
            raise InvalidInput(f'protected input refused as output: {relative}')
    relative_parts = resolved.relative_to(root).as_posix()
    for never in NEVER_OUTPUT_SUBTREES:
        if relative_parts == never or relative_parts.startswith(never + '/'):
            raise InvalidInput(f'{never}/ is never an output subtree: {relative_parts}')
    if resolved.is_dir() and not allow_directory:
        raise InvalidInput(f'output destination is an existing directory: {relative_parts}')
    if relative_parts in OUTPUT_FILES:
        return resolved
    if not any(relative_parts == allowed or relative_parts.startswith(allowed + '/')
               for allowed in OUTPUT_SUBTREES):
        raise InvalidInput(f'output is not inside a declared output subtree: {relative_parts}')
    return resolved


def create_run(root: Path, path: Path, expected_freeze: str = FREEZE_SHA256) -> Path:
    target = check_output(root, path, expected_freeze, allow_directory=True)
    target.mkdir(parents=True, exist_ok=False)
    return target


def configure_environment(root: Path, expected_freeze: str = FREEZE_SHA256) -> dict[str, str]:
    root = authenticate_root(root, expected_freeze)
    state = root / 'provenance' / 'runtime_state'
    result = {}
    for name, directory in STATE_DIRS.items():
        expected = check_output(root, state / directory, expected_freeze, allow_directory=True)
        existing = os.environ.get(name)
        if name not in ('TEMP', 'TMP') and existing and Path(existing).resolve() != expected:
            raise InvalidInput(f'{name} outside configured workspace: {existing}')
        expected.mkdir(parents=True, exist_ok=True)
        os.environ[name] = str(expected)
        result[name] = str(expected)
    for name, value in ISOLATION_VALUES.items():
        os.environ[name] = value
        result[name] = value
    return result


def verify_environment(root: Path, *, require_clean_import_state: bool = True) -> dict[str, str]:
    root = Path(root).resolve()
    result = {}
    for name, directory in STATE_DIRS.items():
        value = os.environ.get(name)
        expected = (root / 'provenance' / 'runtime_state' / directory).resolve()
        if not value:
            raise InvalidInput(f'{name} missing before scientific import')
        if Path(value).resolve() != expected:
            raise InvalidInput(f'{name} outside configured workspace: {value}')
        result[name] = str(expected)
    for name, expected_value in ISOLATION_VALUES.items():
        value = os.environ.get(name)
        if value != expected_value:
            raise InvalidInput(f'{name} is {value!r}, expected {expected_value!r}')
        result[name] = value
    if getattr(site, 'ENABLE_USER_SITE', False):
        raise InvalidInput('user site-packages is enabled in this interpreter')
    result['site.ENABLE_USER_SITE'] = str(site.ENABLE_USER_SITE)
    # Finding 7 round 2: a process was certifiable with PYTHONPATH=C:/Windows.
    # The module's own checkout is authorized too, so unit tests with a temporary
    # root do not report the real source tree as an external entry.
    prefixes = [Path(canonical(p)) for p in (root, Path(sys.prefix), Path(sys.base_prefix),
                                             Path(__file__).resolve().parents[2])]

    def contained(entry: str) -> bool:
        # Component-wise, not string prefix: '<checkout>-evil' is NOT inside '<checkout>'.
        resolved = Path(canonical(entry))
        return any(resolved == prefix or resolved.is_relative_to(prefix) for prefix in prefixes)

    external = [entry for entry in sys.path if entry and not contained(entry)]
    if external:
        raise InvalidInput(f'sys.path contains entries outside the checkout and interpreter: {external}')
    result['sys.path_external_entries'] = '0'
    if require_clean_import_state:
        already = [name for name in SCIENTIFIC_MODULES if name in sys.modules]
        if already:
            raise InvalidInput(f'scientific modules already imported before verification: {already}')
    result['preimported_scientific_modules'] = '0'
    return result


def _relative_path(value: str) -> Path:
    normalized = str(value).replace(chr(92), '/')
    path = PurePosixPath(normalized)
    if (not normalized or path.is_absolute() or '..' in path.parts
            or re.match(r'^[A-Za-z]:', normalized)):
        raise InvalidInput(f'invalid logical_path: {value}')
    return Path(*path.parts)


def resolve_source(row: dict, roots: dict[str, str]) -> Path:
    source_id = row['source_id']
    name = row['logical_root']
    if name not in roots:
        raise InvalidInput(f'{source_id}: missing root mapping {name}')
    root = Path(roots[name]).resolve()
    path = (root / _relative_path(row['logical_path'])).resolve()
    if not path.is_relative_to(root):
        raise InvalidInput(f'{source_id}: source escapes {name}')
    if not path.is_file():
        raise FileNotFoundError(f'{source_id}: missing source {path}')
    if sha256(path) != row['sha256']:
        raise InvalidInput(f'{source_id}: SHA256 mismatch {path}')
    return path


def verify_sources(rows: list[dict], roots: dict[str, str] | None = None) -> list[dict]:
    issues = []
    for row in rows:
        try:
            if roots is None:
                path = Path(row['local_absolute_path'])
                if not path.is_file():
                    raise FileNotFoundError(f"{row['source_id']}: missing source {path}")
                if sha256(path) != row['sha256']:
                    raise InvalidInput(f"{row['source_id']}: SHA256 mismatch {path}")
            else:
                resolve_source(row, roots)
        except (InvalidInput, FileNotFoundError, KeyError) as error:
            issues.append({'source_id': row.get('source_id', 'UNKNOWN'), 'error': str(error)})
    return issues


def require_schema(rows: list[dict], fields: tuple[str, ...] = SIDECAR_FIELDS) -> None:
    if not rows:
        raise InvalidInput('empty reference set is not a clean result')
    for row in rows:
        identifier = row.get('source_id', 'UNKNOWN')
        if None in row:
            raise InvalidInput(f'{identifier}: row has surplus cells beyond the header')
        for field in fields:
            if field not in row:
                raise InvalidInput(f'{identifier}: missing field {field}')
            value = row[field]
            # Finding 8 round 2: a short CSV row yields None, and str(None) is nonblank.
            if value is None:
                raise InvalidInput(f'{identifier}: field {field} is absent from this row')
            if not isinstance(value, str):
                raise InvalidInput(f'{identifier}: field {field} is not a string')
            if not value.strip():
                raise InvalidInput(f'{identifier}: blank field {field}')
        if not HASH_SYNTAX.match(row['sha256'].strip()):
            raise InvalidInput(f'{identifier}: sha256 is not 64 lowercase hex characters')


def read_rows(path: Path, fields: tuple[str, ...], label: str) -> list[dict]:
    """Read a CSV with header and row-width validation. Finding 5 round 2."""
    try:
        text = Path(path).read_text(encoding='utf-8-sig')
    except UnicodeDecodeError as error:
        raise InvalidInput(f'{label} is not valid UTF-8: {error}') from error
    except OSError:
        raise
    if chr(0) in text:
        raise InvalidInput(f'{label} contains a NUL byte')
    if text.find(chr(65279), 1) != -1:
        raise InvalidInput(f'{label} contains a byte order mark away from the start')
    rows_raw = []
    try:
        # Newline-preserving stream and strict parsing: splitlines() silently turned a
        # quoted field containing a newline into a different value (finding N3).
        reader = csv.reader(io.StringIO(text, newline=''), strict=True)
        for values in reader:
            rows_raw.append(values)
    except csv.Error as error:
        raise InvalidInput(f'{label} is not valid CSV: {error}') from error
    header = rows_raw[0] if rows_raw else None
    if not header:
        raise InvalidInput(f'{label} has no header row')
    if len(set(header)) != len(header):
        duplicates = sorted({name for name in header if header.count(name) > 1})
        raise InvalidInput(f'{label} has duplicate header columns: {duplicates}')
    missing = [name for name in fields if name not in header]
    if missing:
        raise InvalidInput(f'{label} is missing required columns: {missing}')
    rows = []
    for number, values in enumerate(rows_raw[1:], start=2):
        if not values:
            continue
        if len(values) != len(header):
            raise InvalidInput(f'{label} line {number} has {len(values)} cells, '
                               f'header declares {len(header)}')
        rows.append(dict(zip(header, values)))
    if not rows:
        raise InvalidInput(f'{label} contains no data rows')
    return rows


def validate_root_mapping(mapping: object) -> dict[str, str]:
    if not isinstance(mapping, dict) or not mapping:
        raise InvalidInput('root mapping must be a non-empty JSON object')
    for key, value in mapping.items():
        if not isinstance(key, str) or not key.strip():
            raise InvalidInput(f'root mapping has a non-string key: {key!r}')
        if not isinstance(value, str) or not value.strip():
            raise InvalidInput(f'root mapping value for {key} must be a non-empty string')
    return dict(mapping)


def validate_locations(manifest: list[dict], locations: list[dict],
                       roots: dict[str, str] | None = None,
                       enforce_schema: bool = True) -> None:
    if not manifest or not locations:
        raise InvalidInput('empty manifest or reference set is not a clean result')
    require_schema(manifest, MANIFEST_FIELDS)
    if enforce_schema and roots is not None:
        require_schema(locations)

    def indexed(rows):
        result = {}
        for row in rows:
            source_id = row['source_id']
            if source_id in result:
                raise InvalidInput(f'duplicate SRC-ID {source_id}')
            result[source_id] = row
        return result

    original, sidecar = indexed(manifest), indexed(locations)
    for source_id in sorted(original.keys() ^ sidecar.keys()):
        raise InvalidInput(f'missing or unknown SRC-ID {source_id}')
    for source_id, row in original.items():
        if row['sha256'] != sidecar[source_id]['sha256']:
            raise InvalidInput(f'{source_id}: sidecar SHA256 differs from manifest')

    spelled: dict[tuple[str, str], str] = {}
    resolved: dict[str, str] = {}
    identities: dict[tuple, str] = {}
    for source_id in sorted(sidecar):
        row = sidecar[source_id]
        key = (row.get('logical_root', ''), row.get('logical_path', ''))
        if key[1]:
            if key in spelled:
                raise InvalidInput(
                    f'ambiguous mapping: {spelled[key]} and {source_id} share the spelling '
                    f'{key[0]}/{key[1]}; one SRC-ID identifies one file')
            spelled[key] = source_id
        if roots is None or not key[1]:
            continue
        name = row['logical_root']
        if name not in roots:
            raise InvalidInput(f'{source_id}: missing root mapping {name}')
        target = Path(roots[name]).resolve() / _relative_path(row['logical_path'])
        identity = canonical(target)
        if identity in resolved:
            raise InvalidInput(
                f'ambiguous mapping: {resolved[identity]} and {source_id} resolve to the same '
                f'path {identity}; one SRC-ID identifies one file')
        resolved[identity] = source_id
        # Finding 1 round 2: hardlinks share a file but not a pathname.
        physical = file_identity(target)
        if physical[0] == 'inode':
            if physical in identities:
                raise InvalidInput(
                    f'ambiguous mapping: {identities[physical]} and {source_id} are the same '
                    f'physical file (device/inode {physical[1]}/{physical[2]}); '
                    'one SRC-ID identifies one file')
            identities[physical] = source_id
        declared = row.get('local_absolute_path')
        if declared and canonical(Path(declared)) != identity:
            raise InvalidInput(
                f'{source_id}: local_absolute_path {declared} does not match the resolved '
                f'target {identity}')


def redact_url(value: str) -> str:
    parsed = urlsplit(value)
    if not parsed.scheme or not parsed.netloc:
        return value
    host = parsed.hostname or ''
    if ':' in host:
        host = f'[{host}]'
    if parsed.port:
        host += f':{parsed.port}'
    return urlunsplit((parsed.scheme, host, parsed.path, '', ''))


def sanitize_text(value: str) -> str:
    value = re.sub(r'https?://[^\s"\'<>]+', lambda m: redact_url(m.group()), value)
    value = re.sub(r'(?i)\b(authorization|cookie|set-cookie|proxy-authorization)(\s*[:=]\s*)(.+)',
                   r'\1\2[REDACTED]', value)
    value = re.sub(r'(?i)\b(bearer|basic)\s+\S+', r'\1 [REDACTED]', value)
    value = re.sub(r'(?<![\w.-])[A-Za-z0-9._%+-]+:[^@\s/"\']+@([A-Za-z0-9.-]+(?::\d+)?)',
                   r'[REDACTED]@\1', value)
    return re.sub(
        r'(?i)\b(token|password|passwd|secret|api[_-]?key|credential|private[_-]?key|'
        r'access[_-]?key(?:[_-]?id)?|secret[_-]?key|signing[_-]?key|signature|session|auth)'
        r'(\s*[=:]\s*)([^\s,;&]+)', r'\1\2[REDACTED]', value)


def sanitize_obj(value):
    """Key-aware scrubbing, including split name/value header records."""
    if isinstance(value, dict):
        name = value.get('name') or value.get('key') or value.get('header')
        if isinstance(name, str) and SECRET_KEY.search(name):
            return {key: ('[REDACTED]' if key in ('value', 'val') else sanitize_obj(item))
                    for key, item in value.items()}
        return {key: ('[REDACTED]' if isinstance(key, str) and SECRET_KEY.search(key)
                      else sanitize_obj(item)) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [sanitize_obj(item) for item in value]
    if isinstance(value, str):
        return sanitize_text(value)
    return value


def lock_ultralytics(settings, root: Path) -> dict:
    root = Path(root).resolve()
    updates = {name: False for name in ULTRALYTICS_OFF}
    updates.update({
        'api_key': '', 'openai_api_key': '',
        'datasets_dir': str(root / 'data' / 'derived' / 'ultralytics_datasets'),
        'weights_dir': str(root / 'provenance' / 'runtime_state' / 'ultralytics' / 'weights'),
        'runs_dir': str(root / 'experiments' / 'ultralytics_runs'),
    })
    settings.update(updates)
    return updates


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-manifest', type=Path, required=True)
    parser.add_argument('--source-locations', type=Path, required=True)
    parser.add_argument('--root-mapping', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    root = authorized_root()
    configure_environment(root)
    verify_environment(root)
    manifest = read_rows(args.source_manifest, MANIFEST_FIELDS, 'source manifest')
    locations = read_rows(args.source_locations, SIDECAR_FIELDS, 'source locations')
    try:
        mapping = json.loads(args.root_mapping.read_text(encoding='utf-8'))
    except json.JSONDecodeError as error:
        raise InvalidInput(f'root mapping is not valid JSON: {error}') from error
    except UnicodeDecodeError as error:
        raise InvalidInput(f'root mapping is not valid UTF-8: {error}') from error
    roots = validate_root_mapping(mapping)
    roots['revision'] = str(root)
    validate_locations(manifest, locations, roots=roots)
    issues = verify_sources(locations, roots)
    output = {
        'manifest_count': len(manifest), 'checked_count': len(locations),
        'uniqueness_method': ('resolved pathname via os.path.normcase(os.path.realpath(...)) AND '
                              'OS file identity (st_dev, st_ino) for existing files'),
        'uniqueness_limits': [
            'SUBST, mapped network drives, 8.3 short-name aliases and unsupported reparse points '
            'were not exercised on this host and are not claimed',
            'identity is observed during validation and the hash is read again during verification; '
            'a replacement between those two observations is not detected (TOCTOU, declared residual)',
            'file_identity falls back to the canonical pathname on ANY OSError, not only on a missing '
            'file, so an operational stat failure degrades to a weaker comparison',
            'nonzero st_dev/st_ino are trusted without a capability check; on non-NTFS, network or '
            'synthetic-inode filesystems this may not be a physical identity',
            'the guard confines writers by path policy; it does not take an OS-level write inventory, '
            'so a writer that bypasses the helper is not detected by this report'],
        'schema_enforced': list(SIDECAR_FIELDS),
        'csv_validation': 'header required, unique, exact row width, no surplus or absent cells',
        'discrepancy_count': len(issues), 'discrepancies': issues}
    destination = check_output(root, args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
    print(f'checked={len(locations)} discrepancies={len(issues)} output={destination}')
    return 0 if not issues else 2


if __name__ == '__main__':
    try:
        sys.exit(main())
    except InvalidInput as error:
        print(sanitize_text(str(error)), file=sys.stderr)
        sys.exit(2)
    except (KeyError, UnicodeDecodeError, csv.Error, json.JSONDecodeError) as error:
        print(sanitize_text(f'invalid input: {type(error).__name__}: {error}'), file=sys.stderr)
        sys.exit(2)
    except Exception:
        traceback.print_exc()
        sys.exit(1)
