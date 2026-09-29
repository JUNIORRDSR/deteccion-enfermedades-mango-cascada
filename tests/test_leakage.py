"""TASK-02 contracts: reproducible leakage audit for M1 and M2.

Every test asserts a METHOD required by the frozen SPEC section 5. None asserts
a scientific outcome: the number of pairs found is an observation, and zero
pairs would not prove biological independence.
"""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.leakage_audit.audit import (
    RELATIONS, AuditError, blind_packet, components, cross_split, duplicate_structure,
    hamming, needs_visual_adjudication, relation_label, validate_adjudications,
)

EXPECTED = {'a': 'a', 'b': 'a', 'c': 'a', 'd': 'd'}


class HammingAndComponents(unittest.TestCase):
    """Verbatim RED from the frozen brief, plus the boundary the SPEC fixes."""

    def test_brief_assertions(self):
        self.assertEqual(hamming(0, 15), 4)
        self.assertEqual(hamming(0, 31), 5)
        self.assertTrue(hamming(0, 15) < 5)
        self.assertFalse(hamming(0, 31) < 5)

    def test_distance_exactly_five_is_outside_the_threshold(self):
        """SPEC: 'Distancia exactamente 5 queda fuera del umbral.'"""
        self.assertFalse(hamming(0, 31) < 5)

    def test_hash_range_is_validated(self):
        for bad in (-1, 2 ** 64, 2 ** 70):
            with self.subTest(bad=bad), self.assertRaises(AuditError):
                hamming(0, bad)

    def test_components_are_deterministic_regardless_of_input_order(self):
        self.assertEqual(components(['d', 'b', 'a', 'c'], [('a', 'b'), ('b', 'c')]), EXPECTED)
        self.assertEqual(components(['a', 'b', 'c', 'd'], [('c', 'b'), ('b', 'a')]), EXPECTED)

    def test_singleton_keeps_itself_as_representative(self):
        self.assertEqual(components(['z'], []), {'z': 'z'})

    def test_every_id_appears_even_when_isolated(self):
        """SPEC: clusters include all images, even isolated ones."""
        result = components(['a', 'b', 'c'], [('a', 'b')])
        self.assertEqual(set(result), {'a', 'b', 'c'})

    def test_edge_with_unknown_id_is_rejected(self):
        with self.assertRaises(AuditError):
            components(['a'], [('a', 'ghost')])


class RelationLabels(unittest.TestCase):
    """SPEC: pHash similarity is never promoted to a confirmed sequence."""

    def test_identical_bytes_are_exact_duplicates(self):
        self.assertEqual(relation_label(distance=0, same_sha=True, documented_group=None),
                         'EXACT_DUPLICATE')

    def test_phash_zero_without_identical_bytes_is_not_exact(self):
        """Hamming 0 is not byte identity; the manuscript conflated them."""
        self.assertEqual(relation_label(distance=0, same_sha=False, documented_group=None),
                         'NEAR_DUPLICATE')

    def test_documented_group_takes_priority_over_visual_similarity(self):
        self.assertEqual(relation_label(distance=9, same_sha=False, documented_group='video-7'),
                         'CONFIRMED_SEQUENCE_RELATION')

    def test_undocumented_sequence_hint_stays_possible(self):
        self.assertEqual(
            relation_label(distance=3, same_sha=False, documented_group=None,
                           sequence_hint='sakit_mp4'),
            'POSSIBLE_SEQUENCE_RELATION')

    def test_band_five_to_ten_is_not_automatic_equivalence(self):
        self.assertEqual(relation_label(distance=7, same_sha=False, documented_group=None),
                         'UNRELATED')


class VisualAdjudicationTriggers(unittest.TestCase):
    def test_cross_split_and_conflict_and_sequence_require_visual_passes(self):
        for case in ({'cross_split': True}, {'conflicting_classes': True},
                     {'possible_sequence': True}, {'sensitivity_band': True}):
            with self.subTest(case=case):
                self.assertTrue(needs_visual_adjudication(cluster_size=2, **case))

    def test_cluster_of_ten_triggers_and_nine_does_not_by_that_criterion(self):
        self.assertTrue(needs_visual_adjudication(cluster_size=10))
        self.assertFalse(needs_visual_adjudication(cluster_size=9))
        # but the other reasons remain active at size 9
        self.assertTrue(needs_visual_adjudication(cluster_size=9, cross_split=True))

    def test_verifiable_sha_equality_needs_no_invented_visual_need(self):
        """SPEC: evidence-adjudicated cases must not manufacture a visual pass."""
        self.assertFalse(needs_visual_adjudication(cluster_size=2, cross_split=True,
                                                   exact_sha_equality=True))


class BlindPackets(unittest.TestCase):
    FORBIDDEN = ('split', 'path', 'filename', 'class', 'label', 'map', 'f1',
                 'decision_a', 'reviewer_a', 'sha256', 'consequence')

    def sample(self) -> dict:
        return {'candidate_id': 'CAND-001', 'unit_type': 'pair',
                'member_ids': ['SRC-1', 'SRC-2'],
                'split': 'train|test', 'paths': ['a/b.jpg', 'c/d.jpg'],
                'filenames': ['b.jpg', 'd.jpg'], 'classes': ['Enfermo', 'Saludable'],
                'sha256': ['aa', 'bb'], 'map50': 0.93, 'decision_a': 'NEAR_DUPLICATE',
                'consequence': 'would force a resplit'}

    def test_packet_hides_everything_the_spec_forbids(self):
        packet = blind_packet(self.sample(), reviewer='a')
        text = json.dumps(packet).lower()
        for forbidden in self.FORBIDDEN:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, text)

    def test_packet_b_does_not_contain_the_a_decision(self):
        packet = blind_packet(self.sample(), reviewer='b')
        # allowed_answers is the fixed menu, identical for every candidate, so it
        # carries no information about what reviewer A answered. Everything else
        # in the packet must be free of A's decision.
        menu = packet.pop('allowed_answers')
        self.assertEqual(menu, list(RELATIONS))
        self.assertNotIn('NEAR_DUPLICATE', json.dumps(packet))

    def test_packet_never_carries_a_per_candidate_prior(self):
        """The menu must not be narrowed per candidate, which would hint an answer."""
        first = blind_packet(self.sample(), reviewer='b')['allowed_answers']
        other = blind_packet({**self.sample(), 'candidate_id': 'CAND-002',
                              'decision_a': 'UNRELATED'}, reviewer='b')['allowed_answers']
        self.assertEqual(first, other)

    def test_packet_keeps_opaque_ids_and_image_references(self):
        packet = blind_packet(self.sample(), reviewer='a')
        self.assertEqual(packet['candidate_id'], 'CAND-001')
        self.assertEqual(len(packet['items']), 2)
        for item in packet['items']:
            self.assertRegex(item['opaque_id'], r'^ITEM-[0-9a-f]{12}$')

    def test_opaque_ids_differ_between_reviewers(self):
        """A shared opaque id would let one reviewer's notes leak to the other."""
        a = blind_packet(self.sample(), reviewer='a')
        b = blind_packet(self.sample(), reviewer='b')
        self.assertNotEqual([i['opaque_id'] for i in a['items']],
                            [i['opaque_id'] for i in b['items']])


class Adjudications(unittest.TestCase):
    def row(self, **overrides) -> dict:
        row = {'candidate_id': 'CAND-001', 'unit_type': 'pair',
               'member_ids': 'SRC-1;SRC-2', 'reviewer_a': 'agent-A', 'reviewer_b': 'agent-B',
               'decision_a': 'NEAR_DUPLICATE', 'decision_b': 'NEAR_DUPLICATE',
               'agreement': 'AGREE', 'final_adjudication': 'NEAR_DUPLICATE',
               'evidence': 'contact sheet CS-001', 'rationale': 'same fruit, same background',
               'adjudicator': 'agent-A', 'timestamp': '2026-09-22T00:00:00+00:00',
               'blinding_exceptions': 'none', 'requires_visual': 'true'}
        row.update(overrides)
        return row

    def test_valid_row_passes(self):
        validate_adjudications([self.row()])

    def test_visual_candidate_without_b_fails(self):
        with self.assertRaisesRegex(AuditError, 'reviewer_b'):
            validate_adjudications([self.row(reviewer_b='', decision_b='')])

    def test_same_reviewer_identity_for_a_and_b_fails(self):
        with self.assertRaisesRegex(AuditError, 'independent'):
            validate_adjudications([self.row(reviewer_b='agent-A')])

    def test_agreement_must_match_the_two_decisions(self):
        with self.assertRaisesRegex(AuditError, 'agreement'):
            validate_adjudications([self.row(decision_b='UNRELATED', agreement='AGREE')])

    def test_disagreement_without_separate_adjudication_fails(self):
        with self.assertRaisesRegex(AuditError, 'PENDING_SEPARATE_ADJUDICATION'):
            validate_adjudications([self.row(decision_b='UNRELATED', agreement='DISAGREE',
                                             final_adjudication='NEAR_DUPLICATE')])

    def test_disagreement_resolved_by_a_third_party_passes(self):
        validate_adjudications([self.row(decision_b='UNRELATED', agreement='DISAGREE',
                                         final_adjudication='PENDING_SEPARATE_ADJUDICATION',
                                         adjudicator='')])

    def test_third_adjudicator_may_not_be_either_reviewer(self):
        with self.assertRaisesRegex(AuditError, 'adjudicator'):
            validate_adjudications([self.row(decision_b='UNRELATED', agreement='DISAGREE',
                                             final_adjudication='UNRELATED',
                                             adjudicator='agent-B')])

    def test_missing_evidence_or_rationale_fails(self):
        for field in ('evidence', 'rationale'):
            with self.subTest(field=field), self.assertRaisesRegex(AuditError, field):
                validate_adjudications([self.row(**{field: ''})])

    def test_cluster_record_needs_complete_membership_not_n_squared_rows(self):
        row = self.row(unit_type='cluster', member_ids=';'.join(f'SRC-{n}' for n in range(12)),
                       candidate_id='CAND-CLUSTER')
        validate_adjudications([row])
        with self.assertRaisesRegex(AuditError, 'member_ids'):
            validate_adjudications([self.row(unit_type='cluster', member_ids='SRC-1')])

    def test_evidence_adjudicated_case_does_not_require_two_visual_passes(self):
        validate_adjudications([self.row(requires_visual='false', reviewer_b='', decision_b='',
                                         agreement='NOT_APPLICABLE_EVIDENCE_ADJUDICATED',
                                         evidence='sha256 equality verified')])


class DuplicateStructure(unittest.TestCase):
    """Brief fixture: four images, three SHA, two clusters of sizes 3 and 1."""

    def test_fixture_counts_exactly(self):
        rows = [{'source_id': 'SRC-1', 'sha256': 'aa', 'cluster': 'c1', 'group_id': 'g1'},
                {'source_id': 'SRC-2', 'sha256': 'aa', 'cluster': 'c1', 'group_id': 'g1'},
                {'source_id': 'SRC-3', 'sha256': 'bb', 'cluster': 'c1', 'group_id': 'g1'},
                {'source_id': 'SRC-4', 'sha256': 'cc', 'cluster': 'c2', 'group_id': 'g2'}]
        result = duplicate_structure(rows)
        self.assertEqual(result['n_images'], 4)
        self.assertEqual(result['n_unique_sha'], 3)
        self.assertEqual(result['n_clusters'], 2)
        self.assertEqual(result['n_groups'], 2)
        self.assertEqual(result['cluster_size_distribution'], {1: 1, 3: 1})
        self.assertEqual(result['min_cluster_size'], 1)
        self.assertEqual(result['max_cluster_size'], 3)
        self.assertEqual(result['median_cluster_size'], 2)

    def test_counts_are_not_labelled_biologically_independent(self):
        rows = [{'source_id': 'SRC-1', 'sha256': 'aa', 'cluster': 'c1', 'group_id': 'g1'}]
        result = duplicate_structure(rows)
        self.assertIn('interpretation', result)
        self.assertIn('operational', result['interpretation'].lower())
        self.assertNotIn('biolog', json.dumps(
            {k: v for k, v in result.items() if k != 'interpretation'}).lower())

    def test_discordant_classes_for_one_sha_are_reported(self):
        rows = [{'source_id': 'SRC-1', 'sha256': 'aa', 'cluster': 'c1', 'group_id': 'g1',
                 'class_name': 'Enfermo'},
                {'source_id': 'SRC-2', 'sha256': 'aa', 'cluster': 'c1', 'group_id': 'g1',
                 'class_name': 'Saludable'}]
        self.assertEqual(duplicate_structure(rows)['discordant_class_sha'], ['aa'])


class CrossSplit(unittest.TestCase):
    def test_pairs_are_reported_once_with_their_split_shape(self):
        rows = [{'source_id': 'SRC-1', 'split': 'train', 'cluster': 'c1'},
                {'source_id': 'SRC-2', 'split': 'test', 'cluster': 'c1'},
                {'source_id': 'SRC-3', 'split': 'train', 'cluster': 'c2'}]
        result = cross_split(rows)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['cluster'], 'c1')
        self.assertEqual(result[0]['splits'], ['test', 'train'])

    def test_cluster_inside_one_split_is_not_cross_split(self):
        rows = [{'source_id': 'SRC-1', 'split': 'train', 'cluster': 'c1'},
                {'source_id': 'SRC-2', 'split': 'train', 'cluster': 'c1'}]
        self.assertEqual(cross_split(rows), [])


class DecodeFailures(unittest.TestCase):
    def test_a_corrupt_image_aborts_the_audit_with_a_list(self):
        """SPEC: a decode error aborts with the list; the image is never skipped."""
        from src.leakage_audit.audit import hash_images
        with TemporaryDirectory() as d:
            good = Path(d) / 'good.png'
            good.write_bytes(bytes.fromhex(
                '89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4'
                '890000000a49444154789c6300010000050001' + '0d0a2db4' + '0000000049454e44ae426082'))
            bad = Path(d) / 'bad.png'
            bad.write_bytes(b'not an image at all')
            with self.assertRaises(AuditError) as caught:
                hash_images([{'source_id': 'SRC-1', 'path': str(good)},
                             {'source_id': 'SRC-2', 'path': str(bad)}])
            self.assertIn('SRC-2', str(caught.exception))


class RotationInvariance(unittest.TestCase):
    """PROTOCOL-AMENDMENT-009: pHash is not rotation invariant, and a blind reviewer
    found the same mango rotated 180 degrees inside the montage."""

    def image(self):
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (64, 64), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle((4, 4, 30, 50), fill='black')
        draw.ellipse((36, 10, 60, 30), fill='gray')
        return img

    def test_rotated_copy_is_far_for_plain_phash_and_near_for_the_invariant(self):
        from src.leakage_audit.audit import dihedral_hashes, rotation_invariant_distance
        import imagehash
        base = self.image()
        rotated = base.rotate(180)
        plain = imagehash.phash(base, hash_size=8, highfreq_factor=4) -             imagehash.phash(rotated, hash_size=8, highfreq_factor=4)
        self.assertGreater(plain, 10)
        self.assertEqual(rotation_invariant_distance(dihedral_hashes(base),
                                                     dihedral_hashes(rotated)), 0)

    def test_mirror_is_covered(self):
        from src.leakage_audit.audit import dihedral_hashes, rotation_invariant_distance
        from PIL import ImageOps
        base = self.image()
        self.assertEqual(rotation_invariant_distance(dihedral_hashes(base),
                                                     dihedral_hashes(ImageOps.mirror(base))), 0)

    def test_eight_transforms_and_identity_first(self):
        from src.leakage_audit.audit import dihedral_hashes
        import imagehash
        base = self.image()
        hashes = dihedral_hashes(base)
        self.assertEqual(len(hashes), 8)
        self.assertEqual(hashes[0], int(str(imagehash.phash(base, hash_size=8,
                                                             highfreq_factor=4)), 16))


if __name__ == '__main__':
    unittest.main()
