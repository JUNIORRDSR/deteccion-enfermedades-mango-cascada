"""Contracts for each bypass the SECOND independent adversarial review demonstrated.

Every test here corresponds to a probe the reviewer actually ran against the
previous implementation and which then succeeded when it should have failed.
"""

import hashlib
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.evaluation.provenance import (
    InvalidInput, authenticate_root, check_output, file_identity, read_rows,
    require_schema, sanitize_obj, sanitize_text, validate_locations,
    verify_environment, MANIFEST_FIELDS, SIDECAR_FIELDS,
)

ABC_HASH = 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
FREEZE = '{"fixture": true}'
FREEZE_SHA = hashlib.sha256(FREEZE.encode()).hexdigest()


def checkout(root: Path) -> Path:
    (root / 'provenance').mkdir(parents=True, exist_ok=True)
    (root / 'provenance' / 'protocol_freeze.json').write_text(FREEZE, encoding='utf-8')
    return root


class HardlinkIdentity(unittest.TestCase):
    """Finding 1 round 2: realpath does not resolve hardlinks."""

    def test_two_source_ids_cannot_hardlink_to_one_file(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            original = root / 'a.bin'
            original.write_bytes(b'abc')
            link = root / 'b.bin'
            try:
                os.link(original, link)
            except (OSError, NotImplementedError) as error:
                self.skipTest(f'hardlinks unavailable on this host: {error}')
            self.assertNotEqual(str(original), str(link))
            self.assertEqual(file_identity(original), file_identity(link))
            manifest = [{'source_id': 'SRC-1', 'sha256': ABC_HASH},
                        {'source_id': 'SRC-2', 'sha256': ABC_HASH}]
            sidecar = [{'source_id': 'SRC-1', 'logical_root': 'r', 'logical_path': 'a.bin',
                        'sha256': ABC_HASH, 'local_absolute_path': str(original)},
                       {'source_id': 'SRC-2', 'logical_root': 'r', 'logical_path': 'b.bin',
                        'sha256': ABC_HASH, 'local_absolute_path': str(link)}]
            with self.assertRaisesRegex(InvalidInput, 'same physical file'):
                validate_locations(manifest, sidecar, roots={'r': str(root)})

    def test_file_identity_falls_back_for_missing_paths(self):
        with TemporaryDirectory() as d:
            kind, *_ = file_identity(Path(d) / 'absent.bin')
            self.assertEqual(kind, 'path')


class RootAndStreamAuthorization(unittest.TestCase):
    """Finding 2 round 2: any caller-selected root was authorized."""

    def test_arbitrary_system_root_is_refused(self):
        with self.assertRaisesRegex(InvalidInput, 'not an authorized checkout'):
            check_output(Path('C:/Windows'), Path('C:/Windows/Temp/out.json'))

    def test_root_with_wrong_freeze_digest_is_refused(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / 'provenance').mkdir(parents=True)
            (root / 'provenance' / 'protocol_freeze.json').write_text('{}', encoding='utf-8')
            with self.assertRaisesRegex(InvalidInput, 'does not authenticate'):
                authenticate_root(root, FREEZE_SHA)

    def test_alternate_data_stream_forms_are_refused(self):
        with TemporaryDirectory() as d:
            root = checkout(Path(d))
            for name in ('reports/ok.json:evil', 'NUL:$DATA',
                         'provenance/protocol_freeze.json:evil'):
                with self.subTest(name=name), self.assertRaisesRegex(InvalidInput, 'colon form'):
                    check_output(root, root / name, FREEZE_SHA)

    def test_code_and_test_trees_are_never_outputs(self):
        with TemporaryDirectory() as d:
            root = checkout(Path(d))
            for name in ('src/evaluation/provenance.py', 'tests/test_x.py', '.git/config'):
                with self.subTest(name=name), self.assertRaisesRegex(InvalidInput, 'never an output'):
                    check_output(root, root / name, FREEZE_SHA)

    def test_undeclared_subtree_is_refused(self):
        with TemporaryDirectory() as d:
            root = checkout(Path(d))
            with self.assertRaisesRegex(InvalidInput, 'declared output subtree'):
                check_output(root, root / 'scratch' / 'out.json', FREEZE_SHA)


class CsvValidation(unittest.TestCase):
    """Finding 5 and 8 round 2: DictReader silently tolerated malformed CSV."""

    def write(self, root: Path, text: str, name: str = 'rows.csv') -> Path:
        path = root / name
        path.write_text(text, encoding='utf-8')
        return path

    def test_duplicate_header_column_is_refused(self):
        with TemporaryDirectory() as d:
            path = self.write(Path(d), 'source_id,sha256,sha256\nSRC-1,' + ABC_HASH + ',' + ABC_HASH + '\n')
            with self.assertRaisesRegex(InvalidInput, 'duplicate header'):
                read_rows(path, MANIFEST_FIELDS, 'manifest')

    def test_short_row_is_refused_rather_than_yielding_none(self):
        with TemporaryDirectory() as d:
            header = ','.join(SIDECAR_FIELDS)
            path = self.write(Path(d), header + '\nSRC-1,r,a.bin,' + ABC_HASH + '\n')
            with self.assertRaisesRegex(InvalidInput, 'cells'):
                read_rows(path, SIDECAR_FIELDS, 'locations')

    def test_surplus_cells_are_refused(self):
        with TemporaryDirectory() as d:
            path = self.write(Path(d), 'source_id,sha256\nSRC-1,' + ABC_HASH + ',extra\n')
            with self.assertRaisesRegex(InvalidInput, 'cells'):
                read_rows(path, MANIFEST_FIELDS, 'manifest')

    def test_missing_required_column_is_refused(self):
        with TemporaryDirectory() as d:
            path = self.write(Path(d), 'source_id,other\nSRC-1,x\n')
            with self.assertRaisesRegex(InvalidInput, 'missing required columns'):
                read_rows(path, MANIFEST_FIELDS, 'manifest')

    def test_non_utf8_bytes_are_invalid_input_not_a_traceback(self):
        with TemporaryDirectory() as d:
            path = Path(d) / 'binary.csv'
            path.write_bytes(bytes([0xFF, 0xFE, 0x00, 0x41]))
            with self.assertRaisesRegex(InvalidInput, 'not valid UTF-8'):
                read_rows(path, MANIFEST_FIELDS, 'manifest')

    def test_header_only_file_is_refused(self):
        with TemporaryDirectory() as d:
            path = self.write(Path(d), 'source_id,sha256\n')
            with self.assertRaisesRegex(InvalidInput, 'no data rows'):
                read_rows(path, MANIFEST_FIELDS, 'manifest')

    def test_schema_rejects_none_and_non_string_values(self):
        base = {'source_id': 'SRC-1', 'logical_root': 'r', 'logical_path': 'a.bin',
                'sha256': ABC_HASH, 'local_absolute_path': 'C:/x/a.bin'}
        with self.assertRaisesRegex(InvalidInput, 'absent from this row'):
            require_schema([{**base, 'local_absolute_path': None}])
        with self.assertRaisesRegex(InvalidInput, 'not a string'):
            require_schema([{**base, 'logical_path': 5}])
        with self.assertRaisesRegex(InvalidInput, 'surplus cells'):
            require_schema([{**base, None: ['extra']}])


class SecretShapes(unittest.TestCase):
    """Finding 6 round 2: realistic secret shapes survived sanitisation."""

    def test_additional_key_names_are_scrubbed(self):
        payload = {'private_key': 'PRIV', 'access_key_id': 'AKID', 'auth': 'AUTHVAL',
                   'session_token': 'STOK', 'host': 'files.example'}
        text = str(sanitize_obj(payload))
        for secret in ('PRIV', 'AKID', 'AUTHVAL', 'STOK'):
            self.assertNotIn(secret, text)
        self.assertIn('files.example', text)

    def test_split_name_value_header_records_are_scrubbed(self):
        record = {'name': 'Authorization', 'value': 'Bearer abc123'}
        self.assertNotIn('abc123', str(sanitize_obj(record)))

    def test_cookie_and_signature_lines_are_scrubbed(self):
        for sample, secret in (('Cookie: session=deadbeef', 'deadbeef'),
                               ('Signature=AbCdEf123', 'AbCdEf123'),
                               ('private_key=SUPERSECRET', 'SUPERSECRET')):
            with self.subTest(sample=sample):
                self.assertNotIn(secret, sanitize_text(sample))


class ImportIsolation(unittest.TestCase):
    """Finding 7 round 2: a process was certifiable with PYTHONPATH=C:/Windows.

    The other tests here check sys.path, so they skip the import-state check, which a shared
    `unittest discover` process never satisfies; this one checks it with sys.modules isolated."""

    def test_preimported_scientific_module_fails_verification(self):
        import sys
        import types
        from unittest import mock

        from src.evaluation.provenance import SCIENTIFIC_MODULES, configure_environment
        with TemporaryDirectory() as d:
            root = checkout(Path(d))
            before_env = dict(os.environ)
            try:
                os.environ['TEMP'] = str(Path(d).parent)
                os.environ['TMP'] = str(Path(d).parent)
                configure_environment(root, FREEZE_SHA)
                clean = {k: v for k, v in sys.modules.items()
                         if k.split('.')[0] not in SCIENTIFIC_MODULES}
                with mock.patch.dict(sys.modules, clean, clear=True):
                    verify_environment(root)
                    sys.modules['torch'] = types.ModuleType('torch')
                    with self.assertRaisesRegex(InvalidInput, 'already imported'):
                        verify_environment(root)
            finally:
                os.environ.clear()
                os.environ.update(before_env)

    def test_external_sys_path_entry_fails_verification(self):
        import sys
        with TemporaryDirectory() as d, TemporaryDirectory() as outside:
            root = checkout(Path(d))
            from src.evaluation.provenance import configure_environment
            before_env, before_path = dict(os.environ), list(sys.path)
            try:
                os.environ['TEMP'] = str(Path(d).parent)
                os.environ['TMP'] = str(Path(d).parent)
                configure_environment(root, FREEZE_SHA)
                verify_environment(root, require_clean_import_state=False)
                sys.path.insert(0, outside)
                with self.assertRaisesRegex(InvalidInput, 'sys.path contains entries outside'):
                    verify_environment(root, require_clean_import_state=False)
            finally:
                sys.path[:] = before_path
                os.environ.clear()
                os.environ.update(before_env)


class RegistryIntegrity(unittest.TestCase):
    """Finding N2 round 2: ART-103 was registered with a stale size and hash."""

    def test_registry_is_structurally_valid_and_locally_consistent(self):
        """Finding N5: skipping unresolvable rows let the registry drift silently."""
        import csv
        registry = Path('provenance/artifact_registry.csv')
        if not registry.is_file():
            self.skipTest('registry not present in this checkout')
        with registry.open(encoding='utf-8-sig', newline='') as stream:
            reader = csv.DictReader(stream)
            rows = list(reader)
        problems, checked, reserved, unresolvable = [], 0, 0, 0
        ids, paths = set(), set()
        for row in rows:
            artifact = (row.get('artifact_id') or '').strip()
            path_text = (row.get('path') or '').strip()
            if not artifact:
                problems.append(('BLANK_ID', path_text)); continue
            if artifact in ids:
                problems.append(('DUPLICATE_ID', artifact))
            ids.add(artifact)
            if not path_text:
                problems.append(('BLANK_PATH', artifact)); continue
            if path_text == 'RESERVED_NOT_YET_ACQUIRED':
                reserved += 1
                # A reservation must be inert: no hash, no size, never consumable.
                if (row.get('sha256') or '').strip() or (row.get('size_bytes') or '').strip():
                    problems.append(('RESERVATION_CARRIES_IDENTITY', artifact))
                continue
            if path_text in paths:
                problems.append(('DUPLICATE_PATH', path_text))
            paths.add(path_text)
            declared = (row.get('sha256') or '').strip()
            path = Path(path_text)
            if not path.is_file():
                # Legacy rows point outside this checkout; they are counted, not skipped.
                unresolvable += 1
                continue
            if not declared:
                problems.append(('RESOLVABLE_BUT_NO_HASH', artifact)); continue
            raw = path.read_bytes()
            checked += 1
            if hashlib.sha256(raw).hexdigest() != declared:
                problems.append(('SHA256_MISMATCH', artifact))
            elif (row.get('size_bytes') or '').strip() and int(row['size_bytes']) != len(raw):
                problems.append(('SIZE_MISMATCH', artifact))
        self.assertEqual(problems, [], f'registry problems; checked={checked} '
                                       f'reserved={reserved} unresolvable={unresolvable}')
        self.assertGreater(checked, 0, 'no registry row was actually verified')
        # Coverage is asserted, not assumed: every row is accounted for in one bucket.
        self.assertEqual(checked + reserved + unresolvable, len(rows))


class Round3Contracts(unittest.TestCase):
    """Each defect the THIRD review demonstrated."""

    def test_frozen_design_documents_are_protected_from_the_guard(self):
        """The gravest round-3 finding: docs/ was an output subtree."""
        from src.evaluation.provenance import authorized_root
        try:
            root = authorized_root()
        except InvalidInput:
            self.skipTest('not running inside the authorized checkout')
        for frozen in ('docs/superpowers/specs/2026-09-17-albus26-major-revision-design.md',
                       'docs/superpowers/plans/2026-09-17-albus26-major-revision.md'):
            with self.subTest(frozen=frozen), self.assertRaisesRegex(InvalidInput, 'protected'):
                check_output(root, root / frozen)

    def test_quoted_newline_in_csv_is_preserved_not_silently_joined(self):
        """Finding N3: splitlines() turned a quoted newline into a different value."""
        with TemporaryDirectory() as d:
            path = Path(d) / 'rows.csv'
            body = ('source_id,sha256' + chr(10) + '"SRC-' + chr(10) + '1",' + ABC_HASH + chr(10))
            path.write_text(body, encoding='utf-8')
            rows = read_rows(path, MANIFEST_FIELDS, 'manifest')
            self.assertEqual(rows[0]['source_id'], 'SRC-' + chr(10) + '1')

    def test_nul_byte_and_stray_bom_are_refused(self):
        with TemporaryDirectory() as d:
            for name, text in (('nul.csv', 'source_id,sha256' + chr(10) + 'SRC' + chr(0) + '1,x'),
                               ('bom.csv', 'source_id,sha256' + chr(10) + chr(65279) + 'SRC-1,x')):
                path = Path(d) / name
                path.write_text(text, encoding='utf-8')
                with self.subTest(name=name), self.assertRaises(InvalidInput):
                    read_rows(path, MANIFEST_FIELDS, 'manifest')

    def test_unmatched_quote_is_refused(self):
        with TemporaryDirectory() as d:
            path = Path(d) / 'rows.csv'
            path.write_text('source_id,sha256' + chr(10) + '"SRC-1,' + ABC_HASH + chr(10),
                            encoding='utf-8')
            with self.assertRaises(InvalidInput):
                read_rows(path, MANIFEST_FIELDS, 'manifest')

    def test_sibling_prefix_path_is_not_inside_the_checkout(self):
        """Finding N4: '<checkout>-evil' passed a string-prefix check."""
        import sys
        with TemporaryDirectory() as d:
            root = checkout(Path(d))
            from src.evaluation.provenance import configure_environment
            before_env, before_path = dict(os.environ), list(sys.path)
            try:
                os.environ['TEMP'] = str(Path(d).parent)
                os.environ['TMP'] = str(Path(d).parent)
                configure_environment(root, FREEZE_SHA)
                verify_environment(root, require_clean_import_state=False)
                sys.path.insert(0, str(root) + '-evil')
                with self.assertRaisesRegex(InvalidInput, 'outside'):
                    verify_environment(root, require_clean_import_state=False)
            finally:
                sys.path[:] = before_path
                os.environ.clear()
                os.environ.update(before_env)

    def test_additional_runtime_modules_are_covered(self):
        from src.evaluation.provenance import SCIENTIFIC_MODULES
        for name in ('matplotlib', 'numba', 'torchvision', 'imagehash'):
            self.assertIn(name, SCIENTIFIC_MODULES)

    def test_directory_is_not_a_file_destination(self):
        with TemporaryDirectory() as d:
            root = checkout(Path(d))
            (root / 'reports').mkdir()
            with self.assertRaisesRegex(InvalidInput, 'existing directory'):
                check_output(root, root / 'reports', FREEZE_SHA)


if __name__ == '__main__':
    unittest.main()
