"""Blinding and recording contracts for the A/B visual adjudication."""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.leakage_audit.adjudication import build_candidates, record, render
from src.leakage_audit.audit import PENDING, AuditError

FORBIDDEN = ('train', 'valid', 'test', 'split', 'enfermo', 'saludable', 'class', 'label',
             'freshmango', 'sakit', '.jpg', 'src-', 'sha256', 'hamming', 'documentary',
             'control', 'category', 'reason')


def fixture(root: Path) -> tuple[dict, list]:
    from PIL import Image
    inventory = {}

    def add(sid, name, split, cls, hint=''):
        path = root / 'images' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new('RGB', (32, 32), (len(inventory) * 20 % 255, 80, 120)).save(path)
        inventory[sid] = {'relative_path': f'images/{name}', 'filename': name, 'split': split,
                          'class_names': cls, 'sequence_name_hint': hint,
                          'normalized_filename_base': name.split('_')[0]}

    for n in range(6):
        add(f'SRC-V{n}', f'sakit_mp4-{n:04d}_jpg.rf.x{n}.jpg', 'train' if n < 4 else 'test',
            'Enfermo', 'sakit_mp4')
    add('SRC-F1', 'freshMango-29-_png.rf.a.jpg', 'test', 'Saludable')
    add('SRC-F2', 'freshMango-29-_jpg.rf.b.jpg', 'valid', 'Saludable')
    for n in range(6):
        add(f'SRC-N{n}', f'other{n}_jpg.rf.n{n}.jpg', 'train',
            'Enfermo' if n % 2 else 'Saludable')
    pairs = [{'source_id_a': 'SRC-N0', 'source_id_b': 'SRC-N1', 'split_a': 'train',
              'split_b': 'valid', 'in_threshold': 'true', 'sensitivity_band': 'false',
              'distance': '2'}]
    return inventory, pairs


class Blinding(unittest.TestCase):
    def test_packets_leak_nothing_and_key_lives_outside(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            inventory, pairs = fixture(root)
            candidates = build_candidates(pairs, inventory, seed=7)
            key_path = root / 'key.json'
            render(candidates, inventory, root, root / 'packets', key_path, seed=7)
            for reviewer in ('a', 'b'):
                directory = root / 'packets' / reviewer
                for path in directory.iterdir():
                    self.assertRegex(path.name, r'^(Q-[0-9a-f]{10}\.png|questions\.json)$')
                text = (directory / 'questions.json').read_text(encoding='utf-8').lower()
                for token in FORBIDDEN:
                    with self.subTest(reviewer=reviewer, token=token):
                        self.assertNotIn(token, text)
            self.assertFalse((root / 'packets' / 'a' / 'key.json').exists())
            self.assertIn('SRC-F1', key_path.read_text(encoding='utf-8'))

    def test_reviewers_get_different_ids_and_orders(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            inventory, pairs = fixture(root)
            candidates = build_candidates(pairs, inventory, seed=7)
            key = render(candidates, inventory, root, root / 'packets', root / 'key.json', seed=7)
            self.assertFalse(set(key['reviewers']['a']) & set(key['reviewers']['b']))

    def test_candidate_numbers_do_not_encode_category(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            inventory, pairs = fixture(root)
            categories = [c['category'] for c in build_candidates(pairs, inventory, seed=7)]
            self.assertNotEqual(categories, sorted(categories))


class Recording(unittest.TestCase):
    def setUp(self):
        self.key = {'candidates': [
            {'candidate_id': 'CAND-001', 'category': 'threshold_cross_split',
             'member_ids': ['SRC-1', 'SRC-2'], 'reason': 'r'},
            {'candidate_id': 'CAND-002', 'category': 'documentary_family',
             'member_ids': ['SRC-3', 'SRC-4'], 'reason': 'r'}],
            'reviewers': {'a': {'QA1': {'candidate_id': 'CAND-001'},
                                'QA2': {'candidate_id': 'CAND-002'}},
                          'b': {'QB1': {'candidate_id': 'CAND-001'},
                                'QB2': {'candidate_id': 'CAND-002'}}}}
        self.names = {'a': 'reviewer-A', 'b': 'reviewer-B'}

    def answers(self, a2='UNRELATED', b2='UNRELATED'):
        base = {'rationale': 'x', 'confidence': 'high'}
        return {'a': {'QA1': {**base, 'decision': 'NEAR_DUPLICATE'}, 'QA2': {**base, 'decision': a2}},
                'b': {'QB1': {**base, 'decision': 'NEAR_DUPLICATE'}, 'QB2': {**base, 'decision': b2}}}

    def test_agreement_is_compared_and_disagreement_stays_pending(self):
        rows, pending = record(self.key, self.answers(b2='POSSIBLE_SEQUENCE_RELATION'),
                               self.names, '2026-09-22T00:00:00+00:00')
        self.assertEqual(rows[0]['agreement'], 'AGREE')
        self.assertEqual(rows[1]['agreement'], 'DISAGREE')
        self.assertEqual(rows[1]['final_adjudication'], PENDING)
        self.assertEqual([r['candidate_id'] for r in pending], ['CAND-002'])

    def test_visual_answer_may_not_claim_byte_identity_or_confirmation(self):
        for forbidden in ('EXACT_DUPLICATE', 'CONFIRMED_SEQUENCE_RELATION'):
            with self.subTest(forbidden=forbidden), self.assertRaises(AuditError):
                record(self.key, self.answers(a2=forbidden, b2=forbidden), self.names, 't')

    def test_missing_answer_fails(self):
        answers = self.answers()
        del answers['b']['QB2']
        with self.assertRaises(AuditError):
            record(self.key, answers, self.names, 't')


if __name__ == '__main__':
    unittest.main()
