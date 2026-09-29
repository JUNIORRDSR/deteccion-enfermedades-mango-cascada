"""Hardening contracts from the independent adversarial review of TASK-01.

Each test names the review finding it closes. These assert the METHOD, never a
desired scientific outcome.
"""

import hashlib
import json
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.evaluation.provenance import (
    InvalidInput, authenticate_root, authorized_root, canonical, check_output, create_run,
    require_schema, sanitize_obj, sanitize_text, validate_locations,
    validate_root_mapping, verify_environment, verify_sources,
)

ABC_HASH = 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'


FAKE_FREEZE = '{"fixture": true}'
FAKE_FREEZE_SHA = hashlib.sha256(FAKE_FREEZE.encode()).hexdigest()


def fake_checkout(root: Path) -> Path:
    """Fixture checkout. Authentication is by DIGEST, never by file name."""
    (root / 'provenance').mkdir(parents=True, exist_ok=True)
    (root / 'provenance' / 'protocol_freeze.json').write_text(FAKE_FREEZE, encoding='utf-8')
    return root


class CanonicalUniqueness(unittest.TestCase):
    """Finding 1 HIGH: uniqueness must hold on the resolved file, not CSV spelling."""

    def rows(self, first: str, second: str) -> tuple[list[dict], list[dict]]:
        manifest = [{'source_id': 'SRC-1', 'sha256': ABC_HASH},
                    {'source_id': 'SRC-2', 'sha256': ABC_HASH}]
        base = {'logical_root': 'legacy_corpus', 'sha256': ABC_HASH}
        sidecar = [{**base, 'source_id': 'SRC-1', 'logical_path': first},
                   {**base, 'source_id': 'SRC-2', 'logical_path': second}]
        return manifest, sidecar

    def test_dot_segment_alias_is_rejected(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / 'sub').mkdir()
            (root / 'sub' / 'a.bin').write_bytes(b'abc')
            manifest, sidecar = self.rows('sub/a.bin', 'sub/./a.bin')
            for row in sidecar:
                row['local_absolute_path'] = str(root / 'sub' / 'a.bin')
            with self.assertRaisesRegex(InvalidInput, 'ambiguous'):
                validate_locations(manifest, sidecar, roots={'legacy_corpus': str(root)})

    def test_backslash_and_case_alias_is_rejected(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / 'sub').mkdir()
            (root / 'sub' / 'a.bin').write_bytes(b'abc')
            for second in ('sub' + chr(92) + 'a.bin', 'SUB/A.BIN'):
                manifest, sidecar = self.rows('sub/a.bin', second)
                for row in sidecar:
                    row['local_absolute_path'] = str(root / 'sub' / 'a.bin')
                with self.subTest(second=second), self.assertRaisesRegex(InvalidInput, 'ambiguous'):
                    validate_locations(manifest, sidecar, roots={'legacy_corpus': str(root)})

    def test_two_roots_mapped_to_one_directory_is_rejected(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / 'a.bin').write_bytes(b'abc')
            manifest = [{'source_id': 'SRC-1', 'sha256': ABC_HASH},
                        {'source_id': 'SRC-2', 'sha256': ABC_HASH}]
            sidecar = [{'source_id': 'SRC-1', 'logical_root': 'one', 'logical_path': 'a.bin',
                        'sha256': ABC_HASH, 'local_absolute_path': str(root / 'a.bin')},
                       {'source_id': 'SRC-2', 'logical_root': 'two', 'logical_path': 'a.bin',
                        'sha256': ABC_HASH, 'local_absolute_path': str(root / 'a.bin')}]
            with self.assertRaisesRegex(InvalidInput, 'ambiguous'):
                validate_locations(manifest, sidecar,
                                   roots={'one': str(root), 'two': str(root)})

    def test_distinct_files_still_pass(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            for name in ('a.bin', 'b.bin'):
                (root / name).write_bytes(b'abc')
            manifest, sidecar = self.rows('a.bin', 'b.bin')
            for row, name in zip(sidecar, ('a.bin', 'b.bin')):
                row['local_absolute_path'] = str(root / name)
            validate_locations(manifest, sidecar, roots={'legacy_corpus': str(root)})

    def test_empty_manifest_is_not_a_clean_result(self):
        with self.assertRaisesRegex(InvalidInput, 'empty'):
            validate_locations([], [], roots={})


class WriteAuthorization(unittest.TestCase):
    """Finding 2 HIGH: writes must be authorized, not merely relative to the caller."""

    def test_protected_inputs_are_refused_as_output(self):
        with TemporaryDirectory() as d:
            root = fake_checkout(Path(d))
            (root / 'configs').mkdir(exist_ok=True)
            (root / 'configs' / 'root_mapping.json').write_text('{}', encoding='utf-8')
            for target in ('provenance/protocol_freeze.json', 'configs/root_mapping.json'):
                with self.subTest(target=target), self.assertRaisesRegex(InvalidInput, 'protected'):
                    check_output(root, root / target, FAKE_FREEZE_SHA)

    def test_reserved_device_names_are_refused(self):
        with TemporaryDirectory() as d:
            root = fake_checkout(Path(d))
            for name in ('NUL', 'nul.json', 'CON', 'COM1', 'reports/NUL'):
                with self.subTest(name=name), self.assertRaisesRegex(InvalidInput, 'reserved'):
                    check_output(root, root / name, FAKE_FREEZE_SHA)

    def test_trailing_dot_or_space_alias_is_refused(self):
        with TemporaryDirectory() as d:
            root = fake_checkout(Path(d))
            for name in ('report.json.', 'report.json '):
                with self.subTest(name=name), self.assertRaisesRegex(InvalidInput, 'alias'):
                    check_output(root, root / name, FAKE_FREEZE_SHA)

    def test_escape_still_refused_and_normal_output_allowed(self):
        with TemporaryDirectory() as d:
            root = fake_checkout(Path(d))
            with self.assertRaises(InvalidInput):
                check_output(root, root / '..' / 'outside', FAKE_FREEZE_SHA)
            self.assertEqual(check_output(root, root / 'reports' / 'ok.json', FAKE_FREEZE_SHA),
                             (root / 'reports' / 'ok.json').resolve())

    def test_create_run_enforces_containment(self):
        with TemporaryDirectory() as d, TemporaryDirectory() as outside:
            root = fake_checkout(Path(d))
            created = create_run(root, root / 'experiments' / 'EXP-T01', FAKE_FREEZE_SHA)
            self.assertTrue(created.is_dir())
            with self.assertRaises(FileExistsError):
                create_run(root, root / 'experiments' / 'EXP-T01', FAKE_FREEZE_SHA)
            with self.assertRaises(InvalidInput):
                create_run(root, Path(outside) / 'run', FAKE_FREEZE_SHA)

    def test_authorized_root_requires_the_freeze_digest_not_its_name(self):
        with TemporaryDirectory() as d:
            plain = Path(d) / 'nested' / 'deep'
            plain.mkdir(parents=True)
            with self.assertRaisesRegex(InvalidInput, 'authorized checkout'):
                authorized_root(plain, expected_sha256=FAKE_FREEZE_SHA)
            root = fake_checkout(Path(d))
            self.assertEqual(authorized_root(plain, expected_sha256=FAKE_FREEZE_SHA), root.resolve())
            # A file with the right NAME and the wrong bytes must not authenticate.
            (root / 'provenance' / 'protocol_freeze.json').write_text('{}', encoding='utf-8')
            with self.assertRaisesRegex(InvalidInput, 'does not authenticate'):
                authorized_root(plain, expected_sha256=FAKE_FREEZE_SHA)

    def test_canonical_collapses_aliases(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / 'a.bin').write_bytes(b'abc')
            self.assertEqual(canonical(root / 'a.bin'), canonical(root / '.' / 'a.bin'))


class ErrorClassification(unittest.TestCase):
    """Finding 4 and 5 MEDIUM: operational failure is not invalid scientific input."""

    def test_unexpected_oserror_propagates(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            target = root / 'a.bin'
            target.write_bytes(b'abc')
            row = {'source_id': 'SRC-1', 'sha256': ABC_HASH, 'local_absolute_path': str(target)}
            import src.evaluation.provenance as mod
            original = mod.sha256
            mod.sha256 = lambda p: (_ for _ in ()).throw(PermissionError('I/O denial'))
            try:
                with self.assertRaises(PermissionError):
                    verify_sources([row])
            finally:
                mod.sha256 = original

    def test_missing_source_is_a_discrepancy_not_a_crash(self):
        with TemporaryDirectory() as d:
            row = {'source_id': 'SRC-1', 'sha256': ABC_HASH,
                   'local_absolute_path': str(Path(d) / 'absent.bin')}
            issues = verify_sources([row])
            self.assertEqual([i['source_id'] for i in issues], ['SRC-1'])

    def test_root_mapping_must_be_a_string_map(self):
        for bad in ([], {'legacy_corpus': 5}, {'legacy_corpus': ''}, 'text', {5: 'x'}):
            with self.subTest(bad=bad), self.assertRaises(InvalidInput):
                validate_root_mapping(bad)
        validate_root_mapping({'legacy_corpus': 'C:/x'})


class SidecarSchema(unittest.TestCase):
    """Finding 8 MEDIUM: coverage may not be declared on an incomplete schema."""

    def test_missing_local_absolute_path_is_refused(self):
        row = {'source_id': 'SRC-1', 'logical_root': 'legacy_corpus',
               'logical_path': 'a.bin', 'sha256': ABC_HASH}
        with self.assertRaisesRegex(InvalidInput, 'local_absolute_path'):
            require_schema([row])

    def test_blank_value_and_bad_hash_are_refused(self):
        base = {'source_id': 'SRC-1', 'logical_root': 'legacy_corpus', 'logical_path': 'a.bin',
                'sha256': ABC_HASH, 'local_absolute_path': 'C:/x/a.bin'}
        with self.assertRaisesRegex(InvalidInput, 'logical_path'):
            require_schema([{**base, 'logical_path': '   '}])
        with self.assertRaisesRegex(InvalidInput, 'sha256'):
            require_schema([{**base, 'sha256': 'not-a-hash'}])
        require_schema([base])

    def test_local_absolute_path_must_match_the_resolved_target(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / 'a.bin').write_bytes(b'abc')
            (root / 'b.bin').write_bytes(b'abc')
            manifest = [{'source_id': 'SRC-1', 'sha256': ABC_HASH}]
            sidecar = [{'source_id': 'SRC-1', 'logical_root': 'legacy_corpus',
                        'logical_path': 'a.bin', 'sha256': ABC_HASH,
                        'local_absolute_path': str(root / 'b.bin')}]
            with self.assertRaisesRegex(InvalidInput, 'local_absolute_path'):
                validate_locations(manifest, sidecar, roots={'legacy_corpus': str(root)})


class Redaction(unittest.TestCase):
    """Finding 6 MEDIUM: redaction must be contract-enforcing, not input-contingent."""

    def test_header_and_bare_userinfo_forms_are_scrubbed(self):
        samples = ['Authorization: Bearer topsecret',
                   'proxy=alice:secret@proxy.example:8080',
                   'alice:secret@proxy.example:8080']
        for sample in samples:
            clean = sanitize_text(sample)
            with self.subTest(sample=sample):
                for secret in ('topsecret', 'secret'):
                    if secret in sample:
                        self.assertNotIn(secret, clean)
        self.assertIn('proxy.example', sanitize_text('proxy=alice:secret@proxy.example:8080'))

    def test_structured_secret_keys_are_scrubbed_by_key(self):
        payload = {'password': 'hunter2', 'nested': {'API_KEY': 'abc123', 'host': 'files.example'},
                   'items': [{'token': 'zzz'}]}
        clean = sanitize_obj(payload)
        text = json.dumps(clean)
        for secret in ('hunter2', 'abc123', 'zzz'):
            self.assertNotIn(secret, text)
        self.assertIn('files.example', text)


class EnvironmentIsolation(unittest.TestCase):
    """Finding 7 MEDIUM: verification must cover every isolation variable."""

    def test_non_path_isolation_variable_is_checked(self):
        with TemporaryDirectory() as d:
            root = fake_checkout(Path(d))
            before = dict(os.environ)
            try:
                from src.evaluation.provenance import configure_environment
                os.environ['TEMP'] = str(Path(d).parent)
                os.environ['TMP'] = str(Path(d).parent)
                configure_environment(root, FAKE_FREEZE_SHA)
                verify_environment(root, require_clean_import_state=False)
                os.environ['WANDB_MODE'] = 'online'
                with self.assertRaisesRegex(InvalidInput, 'WANDB_MODE'):
                    verify_environment(root, require_clean_import_state=False)
            finally:
                os.environ.clear()
                os.environ.update(before)


if __name__ == '__main__':
    unittest.main()
