"""The inference authorities and their approval snapshot (TASK-05 round 5).

The committed git repository is the root of trust (PROTOCOL-AMENDMENT-008 section 4: no
independent custodian). An independent review approves inference for one exact snapshot: the
SHA256 of every file that decides what M1 or M2 inference means. PROTOCOL-AMENDMENT-008 JSON
records that snapshot next to `inference_approved`; every consumer requires the files to be
committed, unmodified and byte-equal to it, so a later commit that changes any authority
needs a new review. Standard library only.
"""

import atexit
import base64
import csv
import functools
import hashlib
import json
import marshal
import os
import shutil
import subprocess
import sys
import tempfile
import types
from pathlib import Path

AMENDMENT = 'provenance/protocol_amendments/PROTOCOL-AMENDMENT-008-kaggle-compute.json'
EVALUATION_CONFIG = 'configs/evaluation.json'
M1_MANIFEST = 'data/manifests/model1_clean_manifest.csv'
FREEZE_RECORD = 'data/manifests/model1_clean_manifest.freeze.json'
SELECTION_RECORD = 'experiments/model1/EXP-R01/selection_record.json'
VERIFIER = 'provenance/commands/task04/verify_kaggle_run.py'
JOB = 'src/evaluation/kaggle_job.py'
M2_PRODUCER = 'src/evaluation/predict_model2.py'
# TASK-05 round 7: the local interpreter every inference step runs in, as installed packages.
ENVIRONMENT_RECORD = 'provenance/environment/inference_environment.txt'
# Round 11: the SHA256 of every distribution's RECORD, so the installed files are anchored to
# the approved snapshot and not only to their own RECORD.
RUNTIME_RECORD = 'provenance/environment/inference_runtime.txt'
# Round 12: the base interpreter the .venv was made from, as committed evidence, so that the
# trusted library root never comes from the mutable sys.base_prefix.
INTERPRETER_RECORD = 'provenance/environment/inference_interpreter.json'
CODE = Path(__file__).resolve().parents[2]
SEALED_CODE = ('src/evaluation/evaluate.py', 'src/statistics/intervals.py', JOB,
               'src/evaluation/authority.py', VERIFIER)
# TASK-05 round 7 NEW-HIGH-05: the code imported, not only the package names. A clean process
# of the recorded .venv has no startup hook, these import finders only, and every installed
# file equal to its wheel RECORD hash. PYTHONUSERBASE is not listed: configure_environment sets
# it to the runtime state, and the user site it would add is refused by verify_environment.
STARTUP_VARIABLES = ('PYTHONPATH', 'PYTHONHOME', 'PYTHONSTARTUP', 'PYTHONPLATLIBDIR',
                     'PYTHONPYCACHEPREFIX', 'PYTHONCASEOK')
STARTUP_HOOKS = ('sitecustomize', 'usercustomize')
IMPORT_FINDERS = frozenset({'_distutils_hack.DistutilsMetaFinder',
                            '_frozen_importlib.BuiltinImporter',
                            '_frozen_importlib.FrozenImporter',
                            '_frozen_importlib_external.PathFinder'})
CODE_SUFFIXES = ('.py', '.pyw', '.pyc', '.pyo', '.pth', '._pth', '.pyd', '.dll', '.so')
# Round 8: fresh bytecode lives in the workspace; old directories there are never read again.
PYCACHE_DIR = 'provenance/runtime_state/pycache'
# Modules that C extensions or Cython create without a spec (a probe of the approved .venv
# after importing torch, Ultralytics and OpenCV); any other spec-less module is refused.
SPECLESS = frozenset({'__main__', '__mp_main__', 'cython_runtime'})
_FRESH = []


class NotApproved(Exception):
    """Inference is not approved for the files in the tree."""


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@functools.cache
def _git() -> str:
    """git from PATH, never from the checkout or its .venv: Windows runs an executable found in
    the current directory before PATH, so a local git.exe could hide untracked code."""
    inside = (_key(CODE) + os.sep,)
    for folder in os.environ.get('PATH', '').split(os.pathsep):
        for name in ('git.exe', 'git'):
            candidate = os.path.join(folder, name) if folder else ''
            if candidate and os.path.isfile(candidate) and not _key(candidate).startswith(inside):
                return os.path.abspath(candidate)
    raise NotApproved('git is not on PATH outside the checkout')


def _run_git(root: Path, *args: str) -> bytes:
    """git without replace objects, fsmonitor or the untracked cache, and without any GIT_*
    variable that could point it at another repository or configuration."""
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith('GIT_')}
    return subprocess.run([_git(), '--no-replace-objects', '-c', 'core.fsmonitor=false',
                           '-c', 'core.untrackedCache=false', *args], cwd=root, env=env,
                          capture_output=True, check=True).stdout


def _blob_id(data: bytes) -> str:
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


def _crlf(root: Path) -> bool:
    """Whether git stores CRLF files as LF here (core.autocrlf true or input). This repository
    sets it false, so its committed blobs are exactly the working bytes."""
    try:
        value = _run_git(root, 'config', '--get', 'core.autocrlf').strip().lower()
    except subprocess.CalledProcessError:
        return False
    return value in (b'true', b'input')


def _committed_bytes(path: Path, blob: str | None, crlf: bool) -> bool:
    """The working file is that HEAD blob, hashed here (no index, stat cache or filter)."""
    if blob is None or not path.is_file():
        return False
    data = path.read_bytes()
    return _blob_id(data) == blob or crlf and _blob_id(data.replace(b'\r\n', b'\n')) == blob


def _head_blobs(root: Path) -> dict[str, str]:
    """Every file of HEAD, relative path -> blob id."""
    entries = {}
    for item in _run_git(root, 'ls-tree', '-r', '-z', '--full-tree', 'HEAD').split(b'\0'):
        meta, _, name = item.partition(b'\t')
        if meta.split()[1:2] == [b'blob']:
            entries[name.decode('utf-8')] = meta.split()[2].decode()
    return entries


def committed_clean(root: Path, *paths: str) -> bool:
    """Every path is a file of HEAD whose working bytes are that blob. The bytes are hashed
    here, so index flags (assume-unchanged, skip-worktree), stat caches and fsmonitor cannot
    hide a local change (round-9 NEW-HIGH-07)."""
    head, crlf = _head_blobs(Path(root)), _crlf(Path(root))
    return bool(paths) and all(_committed_bytes(Path(root) / name, head.get(Path(name).as_posix()),
                                                crlf) for name in paths)


def environment_lines() -> str:
    """The installed distributions of this interpreter, one 'Name==version' per line."""
    from importlib.metadata import distributions
    return ''.join(sorted({f"{d.metadata['Name']}=={d.version}\n" for d in distributions()},
                          key=str.lower))


def _finder(finder) -> str:
    cls = finder if isinstance(finder, type) else type(finder)
    return f'{cls.__module__}.{cls.__qualname__}'


def check_startup() -> None:
    """Nothing replaced the import system: no path/startup variable, no sitecustomize or
    usercustomize loaded or reachable on sys.path, and only the standard import finders."""
    import importlib.machinery
    found = [f'{name} is set' for name in STARTUP_VARIABLES if os.environ.get(name)]
    found += [f'{name} is loaded' for name in STARTUP_HOOKS if name in sys.modules]
    found += [str(path) for entry in sys.path if entry for name in STARTUP_HOOKS
              for path in (Path(entry) / name, *(Path(entry) / f'{name}{suffix}' for suffix in
                                                 importlib.machinery.all_suffixes()))
              if path.exists()]
    found += [f'import finder {name}' for name in map(_finder, sys.meta_path)
              if name not in IMPORT_FINDERS]
    if sys.pycache_prefix and sys.pycache_prefix not in _FRESH:
        found.append(f'bytecode is read from {sys.pycache_prefix}')
    if found:
        raise NotApproved(f'the import system is overridden at startup: {found}')


def _loadable(source: str, cache: str) -> bool:
    """This interpreter would read the cache instead of compiling the source: its magic number
    and either a timestamp header equal to the source's or a hash-based header."""
    import importlib.util
    head = Path(cache).read_bytes()[:16]
    if len(head) < 16 or head[:4] != importlib.util.MAGIC_NUMBER:
        return False
    flags = int.from_bytes(head[4:8], 'little')
    if flags & 1:  # hash-based: unchecked ones are always read, checked ones when they match
        return not flags & 2 or head[8:16] == importlib.util.source_hash(Path(source).read_bytes())
    stat = os.stat(source)
    return head[8:16] == (int(stat.st_mtime) & 0xFFFFFFFF).to_bytes(4, 'little') + \
        (stat.st_size & 0xFFFFFFFF).to_bytes(4, 'little')


def _code(name: str) -> bool:
    """An importable code file, whatever the case of its extension (Windows imports csv.PYC
    for csv.pyc: round 9)."""
    return Path(name).suffix.lower() in CODE_SUFFIXES and Path(name).suffix.lower() != '.pth'


def _bad_cache(path: Path) -> bool:
    """A file that is importable code of its own, or a cache under __pycache__ that this
    interpreter would read for its source and that is not that source compiled. Caches of
    other interpreters, of removed sources or with an outdated header are never read."""
    path = Path(path)
    tag = f'.{sys.implementation.cache_tag}.pyc'
    in_cache = path.parent.name.lower() == '__pycache__'
    if not in_cache or not path.name.lower().endswith(tag):
        return not in_cache  # sourceless or extension code of its own
    source = path.parent.parent / (path.name[:-len(tag)] + '.py')
    return source.is_file() and _loadable(str(source), str(path)) \
        and not _same_code(str(source), str(path))


def _pycache_of(source: str) -> str:
    """The __pycache__ file this interpreter reads for a source without a bytecode prefix,
    derived from the source path, not from the module's mutable spec.cached (round 11)."""
    path = Path(source)
    return str(path.parent / '__pycache__' / f'{path.stem}.{sys.implementation.cache_tag}.pyc')


def recorded_base(root: Path | None = None) -> Path:
    """The committed base-interpreter root (INTERPRETER_RECORD) of the checkout this code runs
    from, unless another root is named."""
    root = Path(root) if root else Path(__file__).resolve().parents[2]
    record = json.loads((root / INTERPRETER_RECORD).read_text(encoding='utf-8'))
    return Path(record['base_prefix'])


def check_interpreter(root: Path) -> None:
    """Round 12: the base interpreter is the recorded one, and sys.path holds only the checkout
    (the .venv included) and that interpreter's own library. sys.base_prefix is mutable, so it
    is compared with the committed record and with the .venv's pyvenv.cfg on disk; a
    python._pth that adds another directory is refused here by its entry, and by the .venv
    scan by its presence."""
    record = json.loads((Path(root) / INTERPRETER_RECORD).read_text(encoding='utf-8'))
    base = Path(record['base_prefix'])
    found = [f'sys.{name} is {getattr(sys, name)}' for name in ('base_prefix', 'base_exec_prefix')
             if _key(getattr(sys, name)) != _key(base)]
    config = (CODE / '.venv' / 'pyvenv.cfg').read_text(encoding='utf-8').splitlines()
    home = [line.split('=', 1)[1].strip() for line in config if line.split('=', 1)[0].strip() == 'home']
    if [_key(h) for h in home] != [_key(base)]:
        found.append(f'pyvenv.cfg home is {home}')
    if sys.version != record['version']:
        found.append(f'Python {sys.version} is not the recorded {record["version"]}')
    library = {_key(base / name) for name in
               (f'python{sys.version_info[0]}{sys.version_info[1]}.zip', 'DLLs', 'Lib', '.')}
    code = _key(CODE)
    found += [f'sys.path entry {entry!r}' for entry in sys.path
              if not ((key := _key(entry or os.getcwd())) in library or key == code
                      or key.startswith(code + os.sep))]
    if found:
        raise NotApproved(f'the interpreter is not the recorded one: {found[:10]}')


def _stale_cache(relative: str) -> bool:
    return _bad_cache(CODE / relative)


def _checkout_files(code: Path) -> tuple[list[str], list[str]]:
    """(files, links) of the checkout as they are on disk, relative. Walked here, not listed
    by git, which collapses an untracked embedded repository to one entry (round 10). The
    .venv (verified by RECORD), the fresh bytecode directory and .git directories are
    skipped; symlinks and junctions are listed, never followed."""
    skip = {_key(code / '.venv'), _key(code / PYCACHE_DIR)}  # the .venv may be a junction:
    files, links, stack = [], [], [Path(code)]              # sys.prefix pins and RECORD verifies it
    while stack:
        with os.scandir(stack.pop()) as entries:
            for entry in entries:
                relative = Path(entry.path).relative_to(code).as_posix()
                if _key(entry.path) in skip:
                    continue
                if entry.is_symlink() or entry.is_junction():
                    links.append(relative)
                elif entry.is_dir(follow_symlinks=False):
                    if entry.name.lower() != '.git':
                        stack.append(Path(entry.path))
                else:
                    files.append(relative)
    return files, links


def check_sources() -> None:
    """No importable code in the checkout except the files of HEAD with their committed bytes
    (round 9: compared byte by byte, not through git status). Refused: any index entry
    flagged assume-unchanged or skip-worktree; any code staged but not committed; any
    committed code whose bytes differ; any symlink or junction; and every other file on disk
    with a .py/.pyc/.pyd/.dll/.so extension in any case (round 8: a sourceless csv.pyc in the
    root loads before the standard library; round 10: inside an untracked embedded
    repository), except caches this interpreter would read that are their source compiled.
    The .venv is verified by RECORD instead."""
    head = _head_blobs(CODE)
    index = _run_git(CODE, 'ls-files', '-v', '-z').decode('utf-8').split('\0')
    found = [f'flagged {line[2:]}' for line in index if line and (line[0].islower() or line[0] == 'S')]
    found += [f'not committed {line[2:]}' for line in index
              if line and _code(line[2:]) and line[2:] not in head]
    crlf = _crlf(CODE)
    found += [f'modified {name}' for name in head if _code(name) and (CODE / name).is_file()
              and not _committed_bytes(CODE / name, head[name], crlf)]
    files, links = _checkout_files(CODE)
    committed = {name.lower() for name in head}
    found += [f'link {name}' for name in links]
    found += [name for name in files
              if _code(name) and name.lower() not in committed and _stale_cache(name)]
    if found:
        raise NotApproved(f'the checkout has untracked, ignored or modified code: {found[:10]}')


def _key(path) -> str:
    """One spelling per file, without touching the disk (Windows paths are case-blind)."""
    return os.path.normcase(os.path.abspath(path))


def _record(dist) -> list[tuple[str, str]]:
    """(path key, 'mode=value' or '') per RECORD line, parsed from the text: Distribution.files
    silently drops files that no longer exist."""
    base = Path(dist.locate_file(''))
    rows = csv.reader((dist.read_text('RECORD') or '').splitlines())
    return [(_key(base / row[0]), row[1] if len(row) > 1 else '') for row in rows if row]


def verify_installed(dists, site_dirs) -> str:
    """Every file of every distribution equals its RECORD hash; under site_dirs, every code
    file must be listed in a RECORD with a digest, and every __pycache__ cache that this
    interpreter would read must be its source compiled, whether RECORD omits it or lists it
    without a digest as pip does (round 11: a replaced cache of _distutils_hack, loaded at
    startup by a recorded .pth, kept its genuine header and its ',,' RECORD line). Returns
    the table 'Name==version <SHA256 of RECORD>', one line per distribution, sorted: the
    RECORD files themselves are then checked against the committed table (check_runtime)."""
    hashed, wrong, lines = set(), [], []
    for dist in dists:
        for path, digest in _record(dist):
            if not digest:
                continue
            hashed.add(path)
            mode, _, value = digest.partition('=')
            try:
                actual = hashlib.new(mode, Path(path).read_bytes()).digest()
            except FileNotFoundError:
                wrong.append(f'missing {path}')
                continue
            if base64.urlsafe_b64encode(actual).rstrip(b'=').decode() != value:
                wrong.append(path)
        record = dist.read_text('RECORD') or ''
        lines.append(f"{dist.metadata['Name']}=={dist.version} "
                     f"{hashlib.sha256(record.encode()).hexdigest()}\n")
    def suspect(p: Path) -> bool:
        if p.suffix.lower() in ('.pyc', '.pyo') and p.parent.name.lower() == '__pycache__':
            # ponytail: compiles every source once per process (~3 min for the 9,018 caches of
            # the approved .venv); a process pool if that ever becomes the bottleneck.
            return _bad_cache(p)  # recorded or not: a cache that would be read is its source
        return _key(p) not in hashed

    stray = [str(p) for d in site_dirs for p in Path(d).rglob('*')
             if p.suffix.lower() in CODE_SUFFIXES and p.is_file() and suspect(p)]
    if wrong or stray:
        raise NotApproved(f'installed files differ from their RECORD: {(wrong + stray)[:10]}')
    return ''.join(sorted(lines))


@functools.cache
def _recorded_files() -> frozenset[str]:
    from importlib.metadata import distributions
    return frozenset(path for dist in distributions() for path, _ in _record(dist))


def _tracked(code: Path) -> frozenset[str]:
    """The files of HEAD (check_sources has compared their bytes)."""
    return frozenset(_key(Path(code) / name) for name in _head_blobs(Path(code)))


def _same_code(source: str, cached: str) -> bool:
    """The cached bytecode is what the source compiles to (header: 16 bytes)."""
    try:
        loaded = marshal.loads(Path(cached).read_bytes()[16:])
        return loaded == compile(Path(source).read_bytes(), source, 'exec', dont_inherit=True)
    except (EOFError, ValueError, TypeError, SyntaxError):
        return False


def check_loaded(modules=None) -> None:
    """Every module loaded so far comes from the interpreter's own library, a recorded file of
    an installed distribution or a tracked source of the checkout, and any cached bytecode it
    may have been read from compiles from that source. A module without a file location is
    accepted only when built-in, frozen, a namespace package over verified directories, one
    of the C/Cython runtime modules, or created by an already verified parent (round 8: a
    shadowing module that erases its own __spec__ is refused)."""
    import _imp
    modules = dict(sys.modules if modules is None else modules)
    base, code = _key(recorded_base()) + os.sep, _key(CODE) + os.sep
    fresh = _key(sys.pycache_prefix) + os.sep if sys.pycache_prefix else None
    recorded, tracked = _recorded_files(), _tracked(CODE)

    def verified_file(path: str) -> bool:
        return path.startswith(base) and not path.startswith(code) or path in recorded \
            or path in tracked and path.endswith('.py')

    def verified_dir(path: str) -> bool:
        path = _key(path) + os.sep
        return path.startswith(base) and not path.startswith(code) \
            or path.startswith(_key(CODE / '.venv') + os.sep) or any(t.startswith(path) for t in tracked)

    verified, wrong, rest = set(), [], []
    for name, module in modules.items():
        spec = getattr(module, '__spec__', None) if isinstance(module, types.ModuleType) else None
        if spec is None or not spec.has_location or not spec.origin:
            rest.append(name)
            continue
        origin = _key(spec.origin)
        claimed = [getattr(spec.loader, 'path', None), getattr(module, '__file__', None)]
        if any(isinstance(path, str) and _key(path) != origin for path in claimed):
            wrong.append(f'{name}: origin {spec.origin} is not the file its loader read')
        elif not verified_file(origin):
            wrong.append(f'{name}: {spec.origin}')
        elif origin.endswith('.py') and any(
                os.path.isfile(cache) and not (fresh and _key(cache).startswith(fresh))
                and _loadable(spec.origin, cache) and not _same_code(spec.origin, cache)
                for cache in {spec.cached, _pycache_of(spec.origin)} if cache):
            wrong.append(f'{name}: its cached bytecode is not its source compiled')
        else:
            verified.add(name)
    for name in sorted(rest, key=lambda n: n.count('.')):  # parents before children
        module = modules[name]
        spec = getattr(module, '__spec__', None) if isinstance(module, types.ModuleType) else None
        if not isinstance(module, types.ModuleType):
            ok = type(module).__module__ in verified  # e.g. typing.io, a typing object
        elif name in sys.builtin_module_names or _imp.is_frozen(name) or name in SPECLESS \
                or name.startswith('_cython_') and name[8:].replace('_', '').isdigit():
            ok = True
        elif spec is not None and spec.origin is None and spec.submodule_search_locations is not None:
            ok = all(verified_dir(path) for path in spec.submodule_search_locations)
        else:
            ok = name.rpartition('.')[0] in verified
        if ok:
            verified.add(name)
        else:
            wrong.append(f'{name}: no verified origin')
    if wrong:
        raise NotApproved(f'modules loaded from outside the verified code: {wrong[:10]}')


@functools.cache
def runtime_table() -> str:
    """verify_installed for this interpreter, once per process. The whole .venv is scanned, not
    only site-packages: the .venv root is itself on sys.path, ahead of site-packages."""
    from importlib.metadata import distributions
    return verify_installed(list(distributions()), [CODE / '.venv'])


def runtime_identity() -> str:
    """The SHA256 of the runtime table, recorded in run_record.json."""
    return hashlib.sha256(runtime_table().encode()).hexdigest()


def check_runtime(root: Path) -> None:
    """The installed files are those of the committed runtime table (round 11: a package file
    replaced together with its RECORD changes the table)."""
    if runtime_table() != (Path(root) / RUNTIME_RECORD).read_text(encoding='utf-8'):
        raise NotApproved(f'the installed files differ from {RUNTIME_RECORD}')


@functools.cache
def fresh_bytecode() -> str:
    """Later imports compile from the verified sources: cached bytecode is read and written only
    under a new empty directory of the workspace (round-8 NEW-LOW-02), removed at exit, so a
    stale or foreign .pyc is never loaded."""
    parent = CODE / PYCACHE_DIR
    parent.mkdir(parents=True, exist_ok=True)
    fresh = tempfile.mkdtemp(prefix='run-', dir=parent)
    _FRESH.append(fresh)
    atexit.register(shutil.rmtree, fresh, ignore_errors=True)
    sys.pycache_prefix = fresh
    return fresh


def check_imported(*modules: str) -> dict[str, str]:
    """After the scientific imports: every loaded module passes check_loaded, and each named one
    was loaded from a recorded file of its own distribution in this interpreter."""
    from importlib.metadata import distribution, packages_distributions
    check_loaded()
    prefix = _key(CODE / '.venv') + os.sep
    owners = packages_distributions()
    out = {}
    for name in modules:
        spec = getattr(sys.modules.get(name), '__spec__', None)
        origin = _key(spec.origin) if spec and spec.origin else None
        files = {path for owner in owners.get(name, ()) for path, _ in _record(distribution(owner))}
        if origin is None or origin not in files or not origin.startswith(prefix):
            raise NotApproved(f'{name} was not loaded from an installed distribution: {origin}')
        out[name] = Path(os.path.relpath(spec.origin, CODE / '.venv')).as_posix()
    return out


def check_environment(root: Path) -> None:
    """The interpreter is this checkout's .venv, its packages are the approved record, nothing
    overrides the import system, the checkout's Python is committed and every installed file
    is the one its wheel recorded."""
    if Path(sys.prefix).resolve() != (CODE / '.venv').resolve():
        raise NotApproved(f'inference runs only in {CODE / ".venv"}, not {sys.prefix}')
    if environment_lines() != (Path(root) / ENVIRONMENT_RECORD).read_text(encoding='utf-8'):
        raise NotApproved(f'the installed packages differ from {ENVIRONMENT_RECORD}')
    check_startup()
    check_interpreter(root)
    check_sources()
    check_runtime(root)
    check_loaded()
    fresh_bytecode()


def authorities(scope: str) -> tuple[str, ...]:
    """m1: what EXP-V01, the freeze, EXP-R02 and the M1 intervals depend on; m2: EXP-R03."""
    if scope == 'm1':
        return (EVALUATION_CONFIG, M1_MANIFEST, M1_MANIFEST + '.sha256', FREEZE_RECORD,
                SELECTION_RECORD, ENVIRONMENT_RECORD, RUNTIME_RECORD, INTERPRETER_RECORD,
                *SEALED_CODE)
    from src.evaluation.predict_model2 import M2_CONTRACT
    return (M2_CONTRACT['manifest'], M2_CONTRACT['manifest'] + '.sha256', M2_PRODUCER,
            ENVIRONMENT_RECORD, RUNTIME_RECORD, INTERPRETER_RECORD, 'src/statistics/intervals.py',
            'src/evaluation/authority.py')


def snapshot(root: Path, scope: str) -> dict[str, str]:
    return {name: sha(Path(root) / name) for name in authorities(scope)}


def approved_inference(root: Path, scope: str) -> dict:
    """The amendment approves inference, for exactly the committed files in the tree."""
    root = Path(root)
    paths = authorities(scope)
    if not committed_clean(root, AMENDMENT, *paths):
        raise NotApproved(f'the amendment and the {scope} authorities must be committed and '
                          'unmodified')
    amendment = json.loads((root / AMENDMENT).read_text(encoding='utf-8'))
    approval = amendment.get('inference_approval') or {}
    if amendment.get('state') != 'APPROVED' or amendment.get('inference_approved') is not True \
            or approval.get('state') != 'APPROVED':
        raise NotApproved('inference needs PROTOCOL-AMENDMENT-008 APPROVED with an approved '
                          'inference snapshot')
    if scope == 'm1' and amendment.get('approved_code', {}).get('job_sha256') != sha(root / JOB):
        raise NotApproved('the job in the tree is not the approved job')
    if approval.get(scope) != snapshot(root, scope):
        raise NotApproved(f'the {scope} authorities differ from the snapshot the review approved')
    check_environment(root)
    return approval
