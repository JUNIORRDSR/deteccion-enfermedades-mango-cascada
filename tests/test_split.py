"""TASK-03 contracts: atomic group split with the single frozen algorithm (SPEC section 6)."""

import hashlib
import tempfile
import unittest
from pathlib import Path

from src.leakage_audit.split import (
    SplitBlocked, assign_groups, block_reasons, build_groups, preserve_membership,
    validate_group_atomicity, validate_split,
)


class BriefFixture(unittest.TestCase):
    """Verbatim RED from the frozen brief."""

    def test_group_crossing_split_is_rejected_with_exact_message(self):
        rows = [dict(image_id='a', group_id='g', cluster_id='c1', sequence_id='s',
                     proposed_split='train'),
                dict(image_id='b', group_id='g', cluster_id='c2', sequence_id='s',
                     proposed_split='test')]
        with self.assertRaises(ValueError) as caught:
            validate_group_atomicity(rows)
        self.assertEqual(str(caught.exception), 'GROUP_CROSSES_SPLIT:g')

    def test_assignment_does_not_depend_on_input_order(self):
        groups = [{'id': str(i), 'size': 1, 'class_counts': [1, 1]} for i in range(20)]
        self.assertEqual(assign_groups(groups, 42), assign_groups(list(reversed(groups)), 42))


class Atomicity(unittest.TestCase):
    def test_repeated_image_id_is_rejected(self):
        rows = [dict(image_id='a', group_id='g1', sequence_id='', proposed_split='train'),
                dict(image_id='a', group_id='g2', sequence_id='', proposed_split='train')]
        with self.assertRaisesRegex(ValueError, 'DUPLICATE_IMAGE_ID:a'):
            validate_group_atomicity(rows)

    def test_confirmed_sequence_cannot_be_split_even_across_groups(self):
        rows = [dict(image_id='a', group_id='g1', sequence_id='v', group_status='CONFIRMED',
                     proposed_split='train'),
                dict(image_id='b', group_id='g2', sequence_id='v', group_status='CONFIRMED',
                     proposed_split='valid')]
        with self.assertRaisesRegex(ValueError, 'SEQUENCE_CROSSES_SPLIT:v'):
            validate_group_atomicity(rows)

    def test_clean_rows_pass(self):
        validate_group_atomicity([dict(image_id='a', group_id='g', sequence_id='',
                                       proposed_split='train')])


class Algorithm(unittest.TestCase):
    def test_largest_group_goes_where_it_costs_least_and_is_never_broken(self):
        groups = ([{'id': 'big', 'size': 70, 'class_counts': [70, 0]}]
                  + [{'id': f'g{i}', 'size': 1, 'class_counts': [i % 2, 1 - i % 2]}
                     for i in range(30)])
        result = assign_groups(groups, 42)
        self.assertEqual(result['big'], 'train')
        self.assertEqual(set(result), {g['id'] for g in groups})

    def test_uses_the_whole_instance_vector_not_only_the_first_class(self):
        """A group with 5 Enfermo and 1 Saludable must count both."""
        groups = [{'id': 'a', 'size': 1, 'class_counts': [5, 1]},
                  {'id': 'b', 'size': 1, 'class_counts': [0, 6]}]
        self.assertEqual(len(assign_groups(groups, 42)), 2)

    def test_tie_order_is_train_then_valid_then_test(self):
        result = assign_groups([{'id': 'only', 'size': 1, 'class_counts': [0, 0]}], 42)
        self.assertEqual(result['only'], 'train')

    def test_same_input_same_output(self):
        groups = [{'id': f'g{i}', 'size': 1 + i % 3, 'class_counts': [i % 2, 1]} for i in range(40)]
        self.assertEqual(assign_groups(groups, 42), assign_groups(groups, 42))


class Blocks(unittest.TestCase):
    def test_class_absent_from_test_blocks(self):
        groups = [{'id': 'g1', 'size': 1, 'class_counts': [1, 0], 'split': 'train'},
                  {'id': 'g2', 'size': 1, 'class_counts': [0, 1], 'split': 'test'},
                  {'id': 'g3', 'size': 1, 'class_counts': [0, 1], 'split': 'test'},
                  {'id': 'g4', 'size': 1, 'class_counts': [1, 1], 'split': 'valid'},
                  {'id': 'g5', 'size': 1, 'class_counts': [1, 1], 'split': 'valid'}]
        self.assertIn('CLASS_ABSENT:test:0', block_reasons(groups, n_classes=2))

    def test_fewer_than_two_independent_groups_per_class_blocks(self):
        groups = [{'id': 'g1', 'size': 1, 'class_counts': [1, 1], 'split': 'test'},
                  {'id': 'g2', 'size': 1, 'class_counts': [0, 1], 'split': 'test'},
                  {'id': 'g3', 'size': 1, 'class_counts': [1, 1], 'split': 'valid'},
                  {'id': 'g4', 'size': 1, 'class_counts': [1, 1], 'split': 'valid'}]
        self.assertIn('FEWER_THAN_TWO_GROUPS:test:0', block_reasons(groups, n_classes=2))

    def test_sufficient_partition_has_no_block(self):
        groups = [{'id': f'{sp}{i}', 'size': 1, 'class_counts': [1, 1], 'split': sp}
                  for sp in ('train', 'valid', 'test') for i in range(2)]
        self.assertEqual(block_reasons(groups, n_classes=2), [])

    def test_blocked_partition_raises_rather_than_retrying_seeds(self):
        self.assertTrue(issubclass(SplitBlocked, Exception))


class GroupBuilding(unittest.TestCase):
    def test_sequence_hint_and_accepted_relations_are_merged(self):
        images = [{'image_id': i, 'cluster_id': i, 'sequence_hint': h}
                  for i, h in (('a', 'vid'), ('b', 'vid'), ('c', ''), ('d', ''), ('e', ''))]
        relations = [('c', 'd', 'NEAR_DUPLICATE'), ('d', 'e', 'UNRELATED')]
        groups = build_groups(images, relations)
        self.assertEqual(groups['a'], groups['b'])
        self.assertEqual(groups['c'], groups['d'])
        self.assertNotEqual(groups['d'], groups['e'])

    def test_option_b_does_not_merge_a_montage_by_its_container_name(self):
        images = [{'image_id': i, 'cluster_id': i, 'sequence_hint': 'vid'} for i in 'abc']
        groups = build_groups(images, [('a', 'b', 'NEAR_DUPLICATE')], merge_sequence_hint=False)
        self.assertEqual(groups['a'], groups['b'])
        self.assertNotEqual(groups['a'], groups['c'])

    def test_pending_adjudication_blocks_the_freeze(self):
        images = [{'image_id': i, 'cluster_id': i, 'sequence_hint': ''} for i in 'ab']
        with self.assertRaisesRegex(SplitBlocked, 'PENDING'):
            build_groups(images, [('a', 'b', 'PENDING_SEPARATE_ADJUDICATION')])



def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class FreezeValidation(unittest.TestCase):
    """SPEC section 6 freeze tests: paths, hashes, labels, schema, before anything is written."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        (root / 'd/images').mkdir(parents=True)
        (root / 'd/labels').mkdir(parents=True)
        self.rows = []
        for name, split in (('a', 'train'), ('b', 'test')):
            image, label = f'd/images/{name}.jpg', f'd/labels/{name}.txt'
            (root / image).write_bytes(name.encode())
            (root / label).write_bytes(b'0 0.5 0.5 0.2 0.2\n')
            self.rows.append({'image_id': f'SRC-{name}', 'path': image, 'label': label,
                              'sha256': _sha(name.encode()), 'phash': '0', 'source': 's',
                              'sequence_id': '', 'cluster_id': name, 'original_split': split,
                              'proposed_split': split, 'label_sha256': _sha(b'0 0.5 0.5 0.2 0.2\n'),
                              'group_id': name, 'group_status': 'SINGLETON',
                              'logical_root': 'legacy_corpus', 'logical_path': image,
                              'local_absolute_path': str(root / image)})

    def tearDown(self):
        self.tmp.cleanup()

    def test_valid_rows_pass(self):
        validate_split(self.rows)

    def test_altered_image_hash_fails(self):
        self.rows[0]['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'IMAGE_HASH:SRC-a'):
            validate_split(self.rows)

    def test_missing_path_fails(self):
        self.rows[1]['local_absolute_path'] += '.missing'
        with self.assertRaisesRegex(ValueError, 'MISSING_FILE:SRC-b'):
            validate_split(self.rows)

    def test_invalid_label_line_fails(self):
        label = Path(self.rows[0]['local_absolute_path']).parents[1] / 'labels/a.txt'
        label.write_bytes(b'7 0.5 0.5 0.2\n')
        self.rows[0]['label_sha256'] = _sha(b'7 0.5 0.5 0.2\n')
        with self.assertRaisesRegex(ValueError, 'LABEL_INVALID:SRC-a'):
            validate_split(self.rows)

    def test_same_file_twice_fails(self):
        self.rows[1]['path'] = self.rows[0]['path']
        with self.assertRaisesRegex(ValueError, 'DUPLICATE_PATH'):
            validate_split(self.rows)

    def test_missing_schema_field_fails(self):
        del self.rows[0]['phash']
        with self.assertRaisesRegex(ValueError, 'SCHEMA:SRC-a'):
            validate_split(self.rows)


class PreserveMembership(unittest.TestCase):
    """M2 is frozen as it is: DATA-005 ids, groups transferred from the DATA-004 audit."""

    @staticmethod
    def inv(sid, dataset, split, cls, name, digest):
        return {'source_id': sid, 'dataset_id': dataset, 'split': split, 'class_names': cls,
                'filename': name, 'sha256': digest, 'relative_path': f'{dataset}/{split}/{name}'}

    def setUp(self):
        self.inventory = [
            self.inv('S4a', 'DATA-004', 'valid', 'An', 'x.jpg', 'h1'),
            self.inv('S4b', 'DATA-004', 'test', 'An', 'y.jpg', 'h1'),
            self.inv('S5a', 'DATA-005', 'val', 'An', 'x.jpg', 'h1'),
            self.inv('S5b', 'DATA-005', 'test', 'An', 'y.jpg', 'h1')]
        self.clusters = {'S4a': {'cluster': 'c1', 'group_id': 'g1', 'split': 'valid'},
                         'S4b': {'cluster': 'c2', 'group_id': 'g2', 'split': 'test'}}

    def test_duplicates_map_one_to_one_with_split_alias(self):
        rows = preserve_membership(self.inventory, self.clusters, 'DATA-005')
        self.assertEqual([(r['image_id'], r['data004_id'], r['split'], r['group_id']) for r in rows],
                         [('S5a', 'S4a', 'val', 'g1'), ('S5b', 'S4b', 'test', 'g2')])

    def test_member_without_counterpart_blocks(self):
        with self.assertRaisesRegex(SplitBlocked, 'UNMATCHED'):
            preserve_membership(self.inventory[:3], self.clusters, 'DATA-005')

    def test_group_across_splits_blocks(self):
        self.clusters['S4b']['group_id'] = 'g1'
        with self.assertRaisesRegex(SplitBlocked, 'GROUP_CROSSES_SPLIT'):
            preserve_membership(self.inventory, self.clusters, 'DATA-005')


if __name__ == '__main__':
    unittest.main()
