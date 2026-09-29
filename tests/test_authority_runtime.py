"""TASK-05 round 7 NEW-HIGH-05: the code imported, not only the package names.

The real checks behind authority.check_environment; other test modules replace the slow or
checkout-dependent ones (tests/runtime_stub.py).
"""

import base64
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from importlib.metadata import distribution, distributions
from pathlib import Path
from unittest import mock

from src.evaluation import authority

ROOT = Path(__file__).resolve().parents[1]


def record_line(root: Path, relative: str) -> str:
    digest = base64.urlsafe_b64encode(hashlib.sha256((root / relative).read_bytes()).digest())
    return f"{relative},sha256={digest.rstrip(b'=').decode()},{(root / relative).stat().st_size}"


def fake_site(root: Path) -> Path:
    """One installed distribution 'fake' 1.0 with a correct RECORD."""
    (root / 'fake').mkdir()
    (root / 'fake' / '__init__.py').write_text('VALUE = 1\n', encoding='utf-8')
    info = root / 'fake-1.0.dist-info'
    info.mkdir()
    (info / 'METADATA').write_text('Metadata-Version: 2.1\nName: fake\nVersion: 1.0\n',
                                   encoding='utf-8')
    lines = [record_line(root, 'fake/__init__.py'), record_line(root, 'fake-1.0.dist-info/METADATA'),
             'fake-1.0.dist-info/RECORD,,']
    (info / 'RECORD').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return root


class Startup(unittest.TestCase):
    def test_a_clean_process_passes(self):
        authority.check_startup()

    def test_each_override_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'sitecustomize.py').write_text('', encoding='utf-8')
            cases = {
                'PYTHONPATH': mock.patch.dict(os.environ, {'PYTHONPATH': tmp}),
                'sitecustomize is loaded': mock.patch.dict(sys.modules,
                                                           {'sitecustomize': mock.Mock()}),
                'sitecustomize.py': mock.patch.object(sys, 'path', [*sys.path, tmp]),
                'import finder': mock.patch.object(sys, 'meta_path', [*sys.meta_path, object()]),
            }
            for label, patch in cases.items():
                with self.subTest(label), patch:
                    with self.assertRaisesRegex(authority.NotApproved, 'overridden'):
                        authority.check_startup()

    def test_the_round7_startup_hook_is_refused_in_a_literal_process(self):
        """The probe: an untracked sitecustomize.py on a checkout PYTHONPATH replaced
        Ultralytics before any check ran."""
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'sitecustomize.py').write_text(
                'import sys, types\nsys.modules["ultralytics"] = types.ModuleType("ultralytics")\n',
                encoding='utf-8')
            done = subprocess.run(
                [sys.executable, '-c', 'from src.evaluation import authority; '
                                       'authority.check_startup()'],
                cwd=ROOT, capture_output=True, text=True, env={**os.environ, 'PYTHONPATH': tmp})
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('overridden', done.stderr)
        self.assertIn('sitecustomize', done.stderr)


class Installed(unittest.TestCase):
    def test_recorded_files_pass_and_any_change_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = fake_site(Path(tmp))
            dists = lambda: list(distributions(path=[str(site)]))  # noqa: E731
            first = authority.verify_installed(dists(), [site])
            self.assertEqual(authority.verify_installed(dists(), [site]), first)
            (site / 'fake' / '__init__.py').write_text('VALUE = 2\n', encoding='utf-8')
            with self.assertRaisesRegex(authority.NotApproved, 'RECORD'):
                authority.verify_installed(dists(), [site])

    def test_unrecorded_code_and_missing_files_fail(self):
        for change in ('stray', 'package', 'missing'):
            with self.subTest(change), tempfile.TemporaryDirectory() as tmp:
                site = fake_site(Path(tmp))
                if change == 'stray':
                    (site / 'evil.pth').write_text('import os\n', encoding='utf-8')
                elif change == 'package':  # e.g. the .venv root, which is on sys.path
                    (site / 'yaml').mkdir()
                    (site / 'yaml' / '__init__.py').write_text('X = 1\n', encoding='utf-8')
                else:
                    (site / 'fake' / '__init__.py').unlink()
                with self.assertRaisesRegex(authority.NotApproved, 'RECORD'):
                    authority.verify_installed(list(distributions(path=[str(site)])), [site])

    def test_a_cache_that_would_be_read_must_be_its_source_compiled(self):
        """Round 11: a site-packages .pyc loaded at startup by a recorded .pth, whether RECORD
        omits it or lists it without a digest (pip writes 'path,,')."""
        import py_compile
        for listed in (False, True):
            with self.subTest(listed=listed), tempfile.TemporaryDirectory() as tmp, \
                    tempfile.TemporaryDirectory() as elsewhere:
                site = fake_site(Path(tmp))
                dists = lambda: list(distributions(path=[str(site)]))  # noqa: E731
                cache = Path(py_compile.compile(str(site / 'fake' / '__init__.py')))
                if listed:
                    record = site / 'fake-1.0.dist-info' / 'RECORD'
                    relative = cache.relative_to(site).as_posix()
                    record.write_text(record.read_text(encoding='utf-8') + f'{relative},,\n',
                                      encoding='utf-8')
                authority.verify_installed(dists(), [site])  # the genuine cache
                other = Path(elsewhere) / 'other.py'
                other.write_text('VALUE = 22\n', encoding='utf-8')
                forged = Path(py_compile.compile(str(other), cfile=str(Path(elsewhere) / 'o.pyc')))
                cache.write_bytes(cache.read_bytes()[:16] + forged.read_bytes()[16:])
                with self.assertRaisesRegex(authority.NotApproved, 'RECORD'):
                    authority.verify_installed(dists(), [site])

    def test_code_listed_without_a_digest_is_not_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = fake_site(Path(tmp))
            (site / 'fake' / 'extra.py').write_text('X = 1\n', encoding='utf-8')
            record = site / 'fake-1.0.dist-info' / 'RECORD'
            record.write_text(record.read_text(encoding='utf-8') + 'fake/extra.py,,\n',
                              encoding='utf-8')
            with self.assertRaisesRegex(authority.NotApproved, 'extra.py'):
                authority.verify_installed(list(distributions(path=[str(site)])), [site])

    def test_a_file_rewritten_with_its_record_changes_the_table(self):
        """Round 11: RECORD is not its own anchor; the committed table is."""
        with tempfile.TemporaryDirectory() as tmp:
            site = fake_site(Path(tmp))
            dists = lambda: list(distributions(path=[str(site)]))  # noqa: E731
            approved = authority.verify_installed(dists(), [site])
            (site / 'fake' / '__init__.py').write_text('VALUE = 2\n', encoding='utf-8')
            record = site / 'fake-1.0.dist-info' / 'RECORD'
            lines = record.read_text(encoding='utf-8').splitlines()
            lines[0] = record_line(site, 'fake/__init__.py')
            record.write_text('\n'.join(lines) + '\n', encoding='utf-8')
            rewritten = authority.verify_installed(dists(), [site])  # consistent with itself
            self.assertNotEqual(rewritten, approved)
            (Path(tmp) / 'runtime.txt').write_text(approved, encoding='utf-8')
            with mock.patch.object(authority, 'RUNTIME_RECORD', 'runtime.txt'):
                with mock.patch.object(authority, 'runtime_table', return_value=rewritten):
                    with self.assertRaisesRegex(authority.NotApproved, 'installed files differ'):
                        authority.check_runtime(Path(tmp))
                with mock.patch.object(authority, 'runtime_table', return_value=approved):
                    authority.check_runtime(Path(tmp))

    def test_a_real_distribution_of_the_venv_verifies(self):
        table = authority.verify_installed([distribution('pip')], [])
        self.assertRegex(table, r'^pip==\S+ [0-9a-f]{64}\n$')


class Sources(unittest.TestCase):
    def git(self, root, *args):
        subprocess.run(['git', '-c', 'user.email=t@t', '-c', 'user.name=t', *args], cwd=root,
                       check=True, capture_output=True)

    def checkout(self, tmp) -> Path:
        root = Path(tmp)
        (root / '.gitignore').write_text('/.venv/\nlocal.py\n__pycache__/\n*.pyc\n',
                                         encoding='utf-8')
        (root / 'a.py').write_text('A = 1\n', encoding='utf-8')
        self.git(root, 'init', '-q')
        self.git(root, 'add', '-A')
        self.git(root, 'commit', '-qm', 'clean')
        (root / '.venv').mkdir()
        (root / '.venv' / 'lib.py').write_text('', encoding='utf-8')
        return root

    def test_untracked_modified_or_ignored_code_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.checkout(tmp)
            with mock.patch.object(authority, 'CODE', root):
                authority.check_sources()  # the venv is verified by RECORD instead
                for change in ('untracked', 'modified', 'ignored', 'sourceless', 'extension',
                               'uppercase'):
                    with self.subTest(change):
                        target = {'untracked': root / 'b.py', 'modified': root / 'a.py',
                                  'ignored': root / 'local.py', 'sourceless': root / 'csv.pyc',
                                  'extension': root / 'csv.pyd',
                                  'uppercase': root / 'csv.PYC'}[change]
                        target.write_text('B = 2\n', encoding='utf-8')
                        with self.assertRaisesRegex(authority.NotApproved, 'modified code'):
                            authority.check_sources()
                        if change == 'modified':
                            self.git(root, 'checkout', '--', 'a.py')
                        else:
                            target.unlink()

    def test_code_inside_an_embedded_repository_or_behind_a_link_is_refused(self):
        """Round 10: git lists an untracked embedded repository as one entry, csv/."""
        import shutil
        import stat
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            root = self.checkout(tmp)
            package = root / 'csv'
            package.mkdir()
            self.git(package, 'init', '-q')
            (package / '__init__.py').write_text('X = 1\n', encoding='utf-8')
            with mock.patch.object(authority, 'CODE', root):
                with self.assertRaisesRegex(authority.NotApproved, 'csv/__init__.py'):
                    authority.check_sources()
                shutil.rmtree(package, onerror=lambda f, p, e: (os.chmod(p, stat.S_IWRITE), f(p)))
                authority.check_sources()
                (Path(outside) / '__init__.py').write_text('X = 1\n', encoding='utf-8')
                subprocess.run(['cmd', '/c', 'mklink', '/J', str(root / 'csv'), outside],
                               check=True, capture_output=True)
                try:
                    with self.assertRaisesRegex(authority.NotApproved, 'link csv'):
                        authority.check_sources()
                finally:
                    os.rmdir(root / 'csv')
                shutil.rmtree(root / '.venv')  # a .venv junction is pinned by sys.prefix instead
                subprocess.run(['cmd', '/c', 'mklink', '/J', str(root / '.venv'), outside],
                               check=True, capture_output=True)
                try:
                    authority.check_sources()
                finally:
                    os.rmdir(root / '.venv')

    def test_the_round10_embedded_csv_package_is_refused_in_a_literal_process(self):
        """The package wraps DictReader and claims the standard library as its origin."""
        import csv
        with tempfile.TemporaryDirectory() as tmp:
            root = self.checkout(tmp)
            package = root / 'csv'
            package.mkdir()
            self.git(package, 'init', '-q')
            (package / '__init__.py').write_text(
                'import importlib.util, sys\n'
                f'_spec = importlib.util.spec_from_file_location("_stdlib_csv", {csv.__file__!r})\n'
                '_real = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_real)\n'
                'globals().update({k: v for k, v in vars(_real).items() if not k.startswith("__")})\n'
                'class DictReader(_real.DictReader):\n'
                '    def __next__(self):\n'
                '        row = super().__next__()\n'
                '        return {**row, "class_name": "Saludable"} if "class_name" in row else row\n'
                f'__spec__.origin = __file__ = {csv.__file__!r}\n'
                '__spec__.loader.path = __file__\n', encoding='utf-8')
            driver = (f'import sys; sys.path.append({str(ROOT)!r}); import csv, io; '
                      'print("WRAPPED", next(csv.DictReader(io.StringIO("class_name\\nCostras\\n")))); '
                      'from pathlib import Path; from src.evaluation import authority; '
                      f'authority.CODE = Path({str(root)!r}); authority.check_sources()')
            done = subprocess.run([sys.executable, '-c', driver], cwd=root, capture_output=True,
                                  text=True)
        self.assertIn("WRAPPED {'class_name': 'Saludable'}", done.stdout)
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('csv/__init__.py', done.stderr)

    def test_index_flags_and_staged_code_are_refused(self):
        """Round-9 NEW-HIGH-07: git status hides a change behind an index flag."""
        with tempfile.TemporaryDirectory() as tmp:
            root = self.checkout(tmp)
            with mock.patch.object(authority, 'CODE', root):
                for flag in ('--assume-unchanged', '--skip-worktree'):
                    with self.subTest(flag):
                        self.git(root, 'update-index', flag, 'a.py')
                        (root / 'a.py').write_text('A = 9\n', encoding='utf-8')
                        with self.assertRaisesRegex(authority.NotApproved, 'flagged a.py'):
                            authority.check_sources()
                        self.git(root, 'update-index', flag.replace('--', '--no-'), 'a.py')
                        self.git(root, 'checkout', '--', 'a.py')
                (root / 'b.py').write_text('B = 1\n', encoding='utf-8')
                self.git(root, 'add', 'b.py')
                with self.assertRaisesRegex(authority.NotApproved, 'not committed b.py'):
                    authority.check_sources()

    def test_a_cache_is_refused_only_when_it_would_be_read_and_differs(self):
        import py_compile
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as elsewhere:
            root = self.checkout(tmp)
            cache = Path(py_compile.compile(str(root / 'a.py')))  # __pycache__, this interpreter
            other = Path(elsewhere) / 'other.py'
            other.write_text('A = 22\n', encoding='utf-8')  # another size: its header never fits a.py
            forged = Path(py_compile.compile(str(other), cfile=str(Path(elsewhere) / 'x.pyc')))
            forged = forged.read_bytes()
            with mock.patch.object(authority, 'CODE', root):
                authority.check_sources()  # the genuine cache
                cache.write_bytes(cache.read_bytes()[:16] + forged[16:])  # a.py's header, other code
                with self.assertRaisesRegex(authority.NotApproved, 'a.cpython'):
                    authority.check_sources()
                cache.write_bytes(forged)  # another source's header: never read for a.py
                authority.check_sources()
                (root / 'a.py').unlink()  # an orphan cache is never read either
                self.git(root, 'rm', '-q', 'a.py')
                self.git(root, 'commit', '-qm', 'drop a')
                authority.check_sources()


class Loaded(unittest.TestCase):
    """Round 8: what was actually loaded, whatever file type put it there."""

    def test_the_interpreter_library_and_installed_distributions_pass(self):
        import json
        import pip
        authority.check_loaded({'json': json, 'pip': pip})

    def test_a_sourceless_pyc_on_the_path_is_refused(self):
        import importlib
        import py_compile
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'shadowmod.py'
            source.write_text('VALUE = 1\n', encoding='utf-8')
            py_compile.compile(str(source), cfile=str(Path(tmp) / 'shadowmod.pyc'))
            source.unlink()
            with mock.patch.object(sys, 'path', [tmp, *sys.path]), \
                    mock.patch.dict(sys.modules):
                module = importlib.import_module('shadowmod')
                self.assertTrue(module.__spec__.origin.endswith('shadowmod.pyc'))
                with self.assertRaisesRegex(authority.NotApproved, 'shadowmod'):
                    authority.check_loaded({'shadowmod': module})

    def test_a_module_without_a_verified_origin_is_refused(self):
        """Round 8: a shadowing module can erase its own __spec__."""
        import json
        import types
        erased = types.ModuleType('csv')
        erased.__spec__ = None
        child = types.ModuleType('json.generated')
        child.__spec__ = None
        orphan = types.ModuleType('nowhere.generated')
        orphan.__spec__ = None

        class Foreign:
            pass
        Foreign.__module__ = 'csv'
        for label, modules in (('csv', {'csv': erased}),
                               ('nowhere.generated', {'nowhere.generated': orphan}),
                               ('csv', {'csv': Foreign()})):
            with self.subTest(label), self.assertRaisesRegex(authority.NotApproved, label):
                authority.check_loaded(modules)
        authority.check_loaded({'json': json, 'json.generated': child})

    def test_the_round8_spec_erasing_csv_is_refused_in_a_literal_process(self):
        import csv
        import py_compile
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'csv.py'
            source.write_text(Path(csv.__file__).read_text(encoding='utf-8') + '\n__spec__ = None\n',
                              encoding='utf-8')
            py_compile.compile(str(source), cfile=str(Path(tmp) / 'csv.pyc'))
            source.unlink()
            driver = (f'import sys; sys.path.append({str(ROOT)!r}); import csv; '
                      'print(csv.__spec__, csv.__file__); '
                      'from src.evaluation import authority; authority.check_loaded()')
            done = subprocess.run([sys.executable, '-c', driver], cwd=tmp, capture_output=True,
                                  text=True)
        self.assertIn('csv.pyc', done.stdout)  # the substitute was loaded, spec erased
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("csv: no verified origin", done.stderr)

    def test_an_origin_that_is_not_the_loaded_file_is_refused(self):
        import importlib.util
        import json
        import types
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp) / 'json.pyc'
            fake.write_bytes(b'')
            module = types.ModuleType('json')
            module.__spec__ = importlib.util.spec_from_file_location('json', fake)
            module.__spec__.origin = json.__spec__.origin  # claims the standard library
            module.__file__ = json.__file__
            with self.assertRaisesRegex(authority.NotApproved, 'not the file its loader read'):
                authority.check_loaded({'json': module})

    def test_the_round9_uppercase_spoofing_csv_is_refused_in_a_literal_process(self):
        """Windows imports csv.PYC for csv.pyc; the module claims the standard library."""
        import csv
        import py_compile
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'csv.py'
            spoof = (f'\n__spec__.origin = {csv.__file__!r}\n__file__ = __spec__.origin\n')
            source.write_text(Path(csv.__file__).read_text(encoding='utf-8') + spoof,
                              encoding='utf-8')
            py_compile.compile(str(source), cfile=str(Path(tmp) / 'csv.PYC'))
            source.unlink()
            driver = (f'import sys; sys.path.append({str(ROOT)!r}); import csv; '
                      'print("LOADED", csv.__spec__.loader.path); '
                      'from src.evaluation import authority; authority.check_loaded()')
            done = subprocess.run([sys.executable, '-c', driver], cwd=tmp, capture_output=True,
                                  text=True)
        self.assertIn('LOADED', done.stdout)
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('not the file its loader read', done.stderr)

    def test_a_cache_that_is_not_the_tracked_source_compiled_is_refused(self):
        import importlib.util
        import py_compile
        import types
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'mod.py'
            source.write_text('VALUE = 1\n', encoding='utf-8')
            for args in (['init', '-q'], ['add', '-A'], ['commit', '-qm', 'mod']):
                subprocess.run(['git', '-c', 'user.email=t@t', '-c', 'user.name=t', *args],
                               cwd=root, check=True, capture_output=True)
            module = types.ModuleType('mod')
            module.__spec__ = importlib.util.spec_from_file_location('mod', source)
            cached = Path(module.__spec__.cached)
            with mock.patch.object(authority, 'CODE', root):
                py_compile.compile(str(source), cfile=str(cached))
                authority.check_loaded({'mod': module})
                genuine = cached.read_bytes()
                other = root / 'other.py'
                other.write_text('VALUE = 2\n', encoding='utf-8')
                py_compile.compile(str(other), cfile=str(cached))
                cached.write_bytes(genuine[:16] + cached.read_bytes()[16:])  # mod.py's header
                with self.assertRaisesRegex(authority.NotApproved, 'not its source compiled'):
                    authority.check_loaded({'mod': module})
                module.__spec__.cached = None  # round 11: the claim is not what is checked
                with self.assertRaisesRegex(authority.NotApproved, 'not its source compiled'):
                    authority.check_loaded({'mod': module})


class Committed(unittest.TestCase):
    """Round-9 NEW-HIGH-07: committed means the working bytes are the HEAD blob."""

    def git(self, root, *args):
        subprocess.run(['git', '-c', 'user.email=t@t', '-c', 'user.name=t', *args], cwd=root,
                       check=True, capture_output=True)

    def test_hidden_or_uncommitted_changes_are_not_clean(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as other:
            root = Path(tmp)
            (root / 'approval.json').write_text('{"approved": false}\n', encoding='utf-8')
            self.git(root, 'init', '-q')
            self.git(root, 'add', '-A')
            self.git(root, 'commit', '-qm', 'proposed')
            self.assertTrue(authority.committed_clean(root, 'approval.json'))
            for flag in ('--assume-unchanged', '--skip-worktree'):
                with self.subTest(flag):
                    self.git(root, 'update-index', flag, 'approval.json')
                    (root / 'approval.json').write_text('{"approved": true}\n', encoding='utf-8')
                    self.assertFalse(authority.committed_clean(root, 'approval.json'))
                    self.git(root, 'update-index', flag.replace('--', '--no-'), 'approval.json')
                    self.git(root, 'checkout', '--', 'approval.json')
            (root / 'new.json').write_text('{}\n', encoding='utf-8')
            self.assertFalse(authority.committed_clean(root, 'approval.json', 'new.json'))
            # a GIT_DIR pointing at a repository that committed the change is not followed
            self.git(other, 'init', '-q')
            (Path(other) / 'approval.json').write_text('{"approved": true}\n', encoding='utf-8')
            self.git(other, 'add', '-A')
            self.git(other, 'commit', '-qm', 'approved')
            (root / 'approval.json').write_text('{"approved": true}\n', encoding='utf-8')
            with mock.patch.dict(os.environ, {'GIT_DIR': str(Path(other) / '.git')}):
                self.assertFalse(authority.committed_clean(root, 'approval.json'))


class Interpreter(unittest.TestCase):
    """Round 12: the base library root comes from committed evidence, not sys.base_prefix."""

    def clean_path(self) -> list[str]:
        base = authority.recorded_base()
        venv = ROOT / '.venv'
        zipped = f'python{sys.version_info[0]}{sys.version_info[1]}.zip'
        return [str(ROOT), str(base / zipped), str(base / 'DLLs'), str(base / 'Lib'), str(base),
                str(venv), str(venv / 'Lib' / 'site-packages')]

    def test_the_recorded_interpreter_passes_and_each_departure_fails(self):
        with mock.patch.object(sys, 'path', self.clean_path()):
            authority.check_interpreter(ROOT)
        with tempfile.TemporaryDirectory() as outside:
            with mock.patch.object(sys, 'path', [*self.clean_path(), outside]):
                with self.assertRaisesRegex(authority.NotApproved, 'sys.path entry'):
                    authority.check_interpreter(ROOT)
            with mock.patch.object(sys, 'path', self.clean_path()), \
                    mock.patch.object(sys, 'base_prefix', outside):
                with self.assertRaisesRegex(authority.NotApproved, 'sys.base_prefix'):
                    authority.check_interpreter(ROOT)
            record = Path(outside) / authority.INTERPRETER_RECORD
            record.parent.mkdir(parents=True)
            record.write_text(json.dumps({'base_prefix': outside, 'version': sys.version}),
                              encoding='utf-8')
            with mock.patch.object(sys, 'path', self.clean_path()):
                with self.assertRaisesRegex(authority.NotApproved, 'pyvenv.cfg home'):
                    authority.check_interpreter(Path(outside))

    def test_the_round12_pth_route_is_refused_in_a_literal_process(self):
        """A python._pth beside a venv launcher adds an external directory whose csv.py claims
        the standard library and rewrites sys.base_prefix to the recorded interpreter."""
        import csv
        base = authority.recorded_base()
        with tempfile.TemporaryDirectory() as tmp:
            venv, outside = Path(tmp) / 'venv', Path(tmp) / 'outside'
            subprocess.run([sys.executable, '-m', 'venv', '--without-pip', str(venv)], check=True,
                           capture_output=True)
            outside.mkdir()
            (outside / 'csv.py').write_text(
                Path(csv.__file__).read_text(encoding='utf-8')
                + f'\nimport sys\nsys.base_prefix = sys.base_exec_prefix = {str(base)!r}\n'
                + f'__spec__.origin = __file__ = {csv.__file__!r}\n', encoding='utf-8')
            zipped = f'python{sys.version_info[0]}{sys.version_info[1]}.zip'
            (venv / 'Scripts' / 'python._pth').write_text('\n'.join(
                [str(outside), str(base / zipped), str(base / 'DLLs'), str(base / 'Lib'),
                 str(base), 'import site']) + '\n', encoding='utf-8')
            driver = (f'import sys; import csv; print("CSV", csv.__spec__.loader.path); '
                      f'sys.path.append({str(ROOT)!r}); from pathlib import Path; '
                      'from src.evaluation import authority; '
                      f'authority.check_interpreter(Path({str(ROOT)!r}))')
            done = subprocess.run([str(venv / 'Scripts' / 'python.exe'), '-c', driver], cwd=ROOT,
                                  capture_output=True, text=True)
            stray = subprocess.run(
                [sys.executable, '-c', f'import sys; sys.path.insert(0, {str(ROOT)!r}); '
                 'from pathlib import Path; from src.evaluation import authority; '
                 f'authority.verify_installed([], [Path({str(venv)!r})])'],
                capture_output=True, text=True)
        self.assertIn(str(outside / 'csv.py'), done.stdout)  # the substitute was loaded
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('sys.path entry', done.stderr)
        self.assertNotEqual(stray.returncode, 0)
        self.assertIn('python._pth', stray.stderr)


class Git(unittest.TestCase):
    def test_a_git_inside_the_checkout_is_never_run(self):
        """Windows runs an executable of the current directory before PATH."""
        real = authority._git.__wrapped__()
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'git.exe').write_bytes(b'')
            path = os.pathsep.join([tmp, os.path.dirname(real)])
            with mock.patch.object(authority, 'CODE', Path(tmp)), \
                    mock.patch.dict(os.environ, {'PATH': path}):
                self.assertEqual(authority._git.__wrapped__(), real)
            with mock.patch.object(authority, 'CODE', Path(tmp)), \
                    mock.patch.dict(os.environ, {'PATH': tmp}):
                with self.assertRaisesRegex(authority.NotApproved, 'git is not on PATH'):
                    authority._git.__wrapped__()


class Bytecode(unittest.TestCase):
    def test_later_imports_use_an_empty_bytecode_directory_in_the_workspace(self):
        """Round-8 NEW-LOW-02: inside the checkout's runtime state, not the system temp."""
        before = sys.pycache_prefix
        try:
            prefix = Path(authority.fresh_bytecode.__wrapped__())
            self.assertEqual(sys.pycache_prefix, str(prefix))
            self.assertEqual(list(prefix.iterdir()), [])
            self.assertEqual(prefix.parent, (ROOT / authority.PYCACHE_DIR))
            authority.check_startup()  # our own prefix
        finally:
            sys.pycache_prefix = before
            authority._FRESH.remove(str(prefix))
            prefix.rmdir()

    def test_a_foreign_bytecode_prefix_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(sys, 'pycache_prefix', tmp):
            with self.assertRaisesRegex(authority.NotApproved, 'bytecode is read from'):
                authority.check_startup()


if __name__ == '__main__':
    unittest.main()
