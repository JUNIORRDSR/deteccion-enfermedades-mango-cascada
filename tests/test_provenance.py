import hashlib
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.evaluation.provenance import (  # noqa: F401
    check_output, configure_environment, create_run, resolve_source,
    sha256, verify_sources, redact_url, validate_locations, verify_environment,
    STATE_DIRS,
)


ABC_HASH = 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
FREEZE = '{"fixture": true}'
FREEZE_SHA = hashlib.sha256(FREEZE.encode()).hexdigest()


class ProvenanceTests(unittest.TestCase):
    def test_hash_and_output_boundaries(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / 'provenance').mkdir(parents=True, exist_ok=True)
            (root / 'provenance' / 'protocol_freeze.json').write_text(FREEZE, encoding='utf-8')
            p = root / 'input'
            p.write_bytes(b'abc')
            self.assertEqual(sha256(p), ABC_HASH)
            target = root / 'reports' / 'output'
            self.assertEqual(check_output(root, target, FREEZE_SHA), target.resolve())
            with self.assertRaises(ValueError):
                check_output(root, root / '..' / 'outside', FREEZE_SHA)
            create_run(root, root / 'experiments' / 'run', FREEZE_SHA)
            with self.assertRaises(FileExistsError):
                create_run(root, root / 'experiments' / 'run', FREEZE_SHA)

    def test_portable_resolution_and_identity(self):
        with TemporaryDirectory() as d:
            roots = [Path(d) / 'one', Path(d) / 'two']
            row = {'source_id': 'SRC-1', 'logical_root': 'legacy_corpus',
                   'logical_path': 'images/a.bin', 'sha256': ABC_HASH}
            for root in roots:
                (root / 'images').mkdir(parents=True)
                (root / 'images/a.bin').write_bytes(b'abc')
                self.assertEqual(sha256(resolve_source(row, {'legacy_corpus': str(root)})), ABC_HASH)
            for bad in ('../outside', '/absolute', 'C:/absolute'):
                with self.subTest(bad=bad), self.assertRaises(ValueError):
                    resolve_source({**row, 'logical_path': bad}, {'legacy_corpus': str(roots[0])})
            with self.assertRaisesRegex(ValueError, 'legacy_corpus'):
                resolve_source(row, {})
            with self.assertRaisesRegex(FileNotFoundError, 'SRC-1'):
                resolve_source({**row, 'logical_path': 'absent'}, {'legacy_corpus': str(roots[0])})
            (roots[0] / 'images/a.bin').write_bytes(b'abd')
            self.assertEqual(len(verify_sources([{**row, 'local_absolute_path': str(roots[0] / 'images/a.bin')}])) , 1)

    def test_manifest_coverage_and_duplicate_rejected(self):
        manifest = [{'source_id': 'SRC-1', 'sha256': ABC_HASH},
                    {'source_id': 'SRC-2', 'sha256': ABC_HASH}]
        sidecar = [{'source_id': 'SRC-1', 'sha256': ABC_HASH}]
        with self.assertRaisesRegex(ValueError, 'SRC-2'):
            validate_locations(manifest, sidecar)
        with self.assertRaisesRegex(ValueError, 'SRC-1'):
            validate_locations(manifest[:1], sidecar * 2)
        with self.assertRaisesRegex(ValueError, 'SRC-9'):
            validate_locations(manifest[:1], sidecar + [{'source_id': 'SRC-9', 'sha256': ABC_HASH}])

    def test_two_ids_cannot_map_one_logical_file(self):
        manifest = [{'source_id': x, 'sha256': ABC_HASH} for x in ('SRC-1', 'SRC-2')]
        sidecar = [{**row, 'logical_root': 'legacy_corpus', 'logical_path': 'same.bin'} for row in manifest]
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            validate_locations(manifest, sidecar)

    def test_redaction_preserves_host(self):
        clean = redact_url('https://alice:secret@example.org/simple?token=abc&plain=1')
        self.assertIn('example.org', clean)
        for secret in ('alice', 'secret', 'abc'):
            self.assertNotIn(secret, clean)

    def test_environment_rejects_external_path(self):
        with TemporaryDirectory() as d, TemporaryDirectory() as outside:
            (Path(d) / 'provenance').mkdir(parents=True, exist_ok=True)
            (Path(d) / 'provenance' / 'protocol_freeze.json').write_text(FREEZE, encoding='utf-8')
            before = os.environ.get('YOLO_CONFIG_DIR')
            try:
                os.environ['YOLO_CONFIG_DIR'] = outside
                with self.assertRaisesRegex(ValueError, 'YOLO_CONFIG_DIR'):
                    configure_environment(Path(d), FREEZE_SHA)
            finally:
                if before is None:
                    os.environ.pop('YOLO_CONFIG_DIR', None)
                else:
                    os.environ['YOLO_CONFIG_DIR'] = before

    def test_environment_initializes_system_temp_and_detects_missing_yolo(self):
        with TemporaryDirectory() as d:
            (Path(d) / 'provenance').mkdir(parents=True, exist_ok=True)
            (Path(d) / 'provenance' / 'protocol_freeze.json').write_text(FREEZE, encoding='utf-8')
            before = {key: os.environ.get(key) for key in STATE_DIRS}
            try:
                os.environ['TEMP'] = str(Path(d).parent)
                os.environ['TMP'] = str(Path(d).parent)
                os.environ.pop('YOLO_CONFIG_DIR', None)
                values = configure_environment(Path(d), FREEZE_SHA)
                self.assertEqual(values['TEMP'], str((Path(d) / 'provenance/runtime_state/tmp').resolve()))
                os.environ.pop('YOLO_CONFIG_DIR')
                with self.assertRaisesRegex(ValueError, 'YOLO_CONFIG_DIR'):
                    verify_environment(Path(d))
            finally:
                for key, value in before.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value


if __name__ == '__main__':
    unittest.main()
