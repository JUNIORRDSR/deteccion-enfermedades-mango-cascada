"""TASK-08: bidirectional citation check and bibliographic identity reconciliation."""

import csv
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from src.evaluation.document_checks import (
    citation_gaps, claim_language_issues, docx_paragraphs, fmt, identity_status, language_hits,
    number_issues,
)

ROOT = Path(__file__).resolve().parents[1]
W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'


def write_docx(path: Path, paragraphs: list[str], cell: str = '') -> Path:
    runs = ''.join(f'<w:p><w:r><w:t>{p}</w:t></w:r></w:p>' for p in paragraphs)
    table = f'<w:tbl><w:tr><w:tc><w:p><w:r><w:t>{cell}</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'
    with zipfile.ZipFile(path, 'w') as package:
        package.writestr('word/document.xml', f'<w:document xmlns:w="{W_NS}"><w:body>{runs}'
                                              f'{table}</w:body></w:document>')
    return path


class Numbers(unittest.TestCase):
    """TASK-09: printed numbers come from the metrics JSON without intermediate rounding."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / 'metrics.json').write_text(json.dumps(
            {'top1': 0.9094733437, 'f1': {'Costras': 0.8314606742}}), encoding='utf-8')

    def tearDown(self):
        self.tmp.cleanup()

    def row(self, anchor, path=('top1',), **extra):
        return {'id': 'NUM-X', 'source': 'metrics.json', 'path': list(path), 'digits': 3,
                'anchor': anchor, **extra}

    def test_plan_rounding(self):
        self.assertEqual(fmt(0.9094733437, 3, '.'), '0.909')
        self.assertEqual(fmt(0.8314606742, 3, '.'), '0.831')
        self.assertEqual(fmt(0.9094733437, 3), '0,909')

    def test_current_value_passes(self):
        paragraphs = ['La exactitud top-1 es 0,909 y el F1 de Costras 0,831.']
        rows = [self.row('exactitud top-1'), self.row('F1 de Costras', ('f1', 'Costras'))]
        self.assertEqual(number_issues(paragraphs, rows, self.root), [])

    def test_fictitious_claim_with_a_stale_value_is_rejected(self):
        issues = number_issues(['La exactitud top-1 es 0,935.'], [self.row('exactitud top-1')],
                               self.root)
        self.assertEqual([i['expected'] for i in issues], ['0,909'])

    def test_a_longer_number_is_not_a_match(self):
        self.assertTrue(number_issues(['La exactitud top-1 es 0,9091.'],
                                      [self.row('exactitud top-1')], self.root))

    def test_ambiguous_or_missing_anchor_and_missing_value(self):
        paragraphs = ['exactitud top-1 0,909', 'exactitud top-1 0,909']
        self.assertIn('2 paragraphs', number_issues(paragraphs, [self.row('exactitud top-1')],
                                                    self.root)[0]['issue'])
        self.assertIn('not found', number_issues(paragraphs, [self.row('x', ('nope',))],
                                                 self.root)[0]['issue'])

    def test_percent_scale(self):
        rows = [self.row('exactitud', digits=1, scale=100)]
        self.assertEqual(number_issues(['exactitud del 90,9 %'], rows, self.root), [])


class ClaimLanguage(unittest.TestCase):
    """TASK-09 plan line 392."""

    def row(self, location='Título', claim='EFICIENTE', text='sistema eficiente', quote='OWN',
            evidence='benchmark TASK-06 descriptivo de un modelo y un equipo', decision='KEEP'):
        return {'location': location, 'claim': claim, 'text': text, 'quote_status': quote,
                'evidence': evidence, 'decision': decision}

    def test_efficiency_without_prior_criterion_fails_in_each_of_the_four_locations(self):
        rows = [self.row(location=loc) for loc in ('Título', 'Resumen', 'Contribuciones',
                                                   'Conclusión')]
        issues = claim_language_issues(rows)
        self.assertEqual([i['location'] for i in issues],
                         ['Título', 'Resumen', 'Contribuciones', 'Conclusión'])

    def test_a_descriptive_benchmark_is_not_a_comparative_criterion(self):
        self.assertTrue(claim_language_issues([self.row()], criterion='CRIT-001'))
        self.assertEqual(claim_language_issues(
            [self.row(evidence='CRIT-001 fijado antes de medir, comparador YOLO11n')],
            criterion='CRIT-001'), [])

    def test_own_absolute_leakage_phrase_fails_attributed_history_may_stay(self):
        own = self.row(claim='libre de fuga', text='un conjunto libre de fuga')
        cited = self.row(claim='libre de fuga', text='«libre de fuga» (Autor, 2020)',
                         quote='ATTRIBUTED', decision='KEEP_ATTRIBUTED')
        self.assertEqual(len(claim_language_issues([own, cited])), 1)

    def test_replaced_claims_and_missing_fields(self):
        self.assertEqual(claim_language_issues([self.row(decision='REPLACE: «automatizada»')]), [])
        self.assertIn('missing', claim_language_issues([self.row(evidence='')])[0]['issue'])

    def test_lexical_hits_need_a_reviewed_row(self):
        editorial = [self.row(text='técnicas eficientes (Autor, 2020)', decision='KEEP_ATTRIBUTED')]
        hits = language_hits(['Según técnicas eficientes (Autor, 2020).',
                              'Un sistema de detección temprana.'], editorial)
        self.assertEqual([(h['paragraph'], h['reviewed']) for h in hits], [(0, True), (1, False)])

    def test_clean_as_a_leakage_verdict_is_a_hit_but_the_dataset_name_is_not(self):
        hits = language_hits(['Sobre la partición limpia.', 'Sobre MangoDHDS_clean.'], [])
        self.assertEqual([(h['paragraph'], h['match']) for h in hits], [(0, 'limpia')])


class Docx(unittest.TestCase):
    def test_paragraphs_include_table_cells(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = write_docx(Path(tmp) / 'a.docx', ['uno', 'dos'], cell='celda')
            self.assertEqual(docx_paragraphs(path), ['uno', 'dos', 'celda'])


class CitationGaps(unittest.TestCase):
    def test_plan_fixture(self):
        self.assertEqual(citation_gaps({'a', 'b'}, {'b', 'c'}), {'missing': ['a'], 'uncited': ['c']})

    def test_no_gaps(self):
        self.assertEqual(citation_gaps({'a'}, {'a'}), {'missing': [], 'uncited': []})


class IdentityStatus(unittest.TestCase):
    def test_doi_match_with_different_title_is_a_metadata_conflict(self):
        cited = {'doi': '10.1109/ACCESS.2023.3265195', 'title': 'AI-driven pheno-parenting'}
        primary = {'doi': '10.1109/access.2023.3265195',
                   'title': 'AI-Driven Pheno-Parenting: A Deep Learning Based Plant Phenotyping '
                            'Trait Analysis Model on a Novel Soilless Farming Dataset'}
        self.assertEqual(identity_status(cited, primary), 'METADATA_CONFLICT')

    def test_doi_and_title_match_modulo_case_and_punctuation(self):
        cited = {'doi': 'https://doi.org/10.1/X', 'title': 'Plant diseases: a review.'}
        primary = {'doi': '10.1/x', 'title': 'Plant Diseases - A Review'}
        self.assertEqual(identity_status(cited, primary), 'MATCH')

    def test_different_doi_is_never_a_match(self):
        cited = {'doi': '10.1/a', 'title': 'Same'}
        primary = {'doi': '10.1/b', 'title': 'Same'}
        self.assertEqual(identity_status(cited, primary), 'METADATA_CONFLICT')


class Cli(unittest.TestCase):
    def run_cli(self, references, links):
        with tempfile.TemporaryDirectory(dir=ROOT / 'reports') as tmp:
            tmp = Path(tmp)
            (tmp / 'refs.json').write_text(json.dumps(references), encoding='utf-8')
            with (tmp / 'links.csv').open('w', newline='', encoding='utf-8') as stream:
                writer = csv.DictWriter(stream, fieldnames=['citation_text', 'ref_id'])
                writer.writeheader()
                writer.writerows(links)
            out = tmp / 'check.json'
            result = subprocess.run(
                [sys.executable, '-m', 'src.evaluation.document_checks',
                 '--references', str(tmp / 'refs.json'), '--citations', str(tmp / 'links.csv'),
                 '--out', str(out)], cwd=ROOT, capture_output=True, text=True)
            report = json.loads(out.read_text(encoding='utf-8')) if out.exists() else None
        return result, report

    def entry(self, ref_id, status='VERIFIED'):
        return {'id': ref_id, 'status': status, 'apa7': 'x', 'evidence_url': 'https://doi.org/10.1/x'}

    def test_exit_0_without_gaps(self):
        result, report = self.run_cli([self.entry('a')], [{'citation_text': '(A, 2020)', 'ref_id': 'a'}])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report, {'missing': [], 'uncited': []})

    def test_exit_1_lists_gaps(self):
        result, report = self.run_cli([self.entry('b'), self.entry('c')],
                                      [{'citation_text': '(A)', 'ref_id': 'a'},
                                       {'citation_text': '(B)', 'ref_id': 'b'}])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report, {'missing': ['a'], 'uncited': ['c']})
        self.assertIn('a', result.stdout)

    def test_unverified_reference_is_invalid_input(self):
        result, _ = self.run_cli([self.entry('a', status='BLOCKED')],
                                 [{'citation_text': '(A)', 'ref_id': 'a'}])
        self.assertEqual(result.returncode, 2)


class ConsistencyCli(unittest.TestCase):
    def run_cli(self, printed: str):
        with tempfile.TemporaryDirectory(dir=ROOT / 'reports') as tmp:
            tmp = Path(tmp)
            write_docx(tmp / 'm.docx', [f'La exactitud top-1 es {printed}.'])
            (tmp / 'metrics.json').write_text(json.dumps({'top1': 0.9094733437}), encoding='utf-8')
            (tmp / 'numbers.json').write_text(json.dumps([{
                'id': 'NUM-1', 'source': (tmp / 'metrics.json').relative_to(ROOT).as_posix(),
                'path': ['top1'], 'digits': 3, 'anchor': 'exactitud top-1'}]), encoding='utf-8')
            for name, header, row in (
                    ('claims.csv', ['claim_id', 'status', 'revision_action'],
                     ['CLAIM-1', 'UNVERIFIED', 'Moderar']),
                    ('editorial.csv', ['location', 'claim', 'text', 'quote_status', 'evidence',
                                       'decision'],
                     ['Título', 'EFICIENTE', 'eficiente', 'OWN', 'sin criterio', 'REPLACE'])):
                with (tmp / name).open('w', newline='', encoding='utf-8') as stream:
                    csv.writer(stream).writerows([header, row])
            out = tmp / 'consistency.json'
            result = subprocess.run(
                [sys.executable, '-m', 'src.evaluation.document_checks', '--docx',
                 str(tmp / 'm.docx'), '--claims', str(tmp / 'claims.csv'), '--editorial',
                 str(tmp / 'editorial.csv'), '--numbers', str(tmp / 'numbers.json'),
                 '--metrics', str(tmp), '--out', str(out)], cwd=ROOT, capture_output=True,
                text=True)
            report = json.loads(out.read_text(encoding='utf-8')) if out.exists() else None
        return result, report

    def test_current_number_passes(self):
        result, report = self.run_cli('0,909')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(report['checked_numbers'], 1)

    def test_stale_number_fails(self):
        result, report = self.run_cli('0,935')
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report['numbers'][0]['expected'], '0,909')


if __name__ == '__main__':
    unittest.main()
