"""Additional validation and cleaning regressions; reference suite unchanged."""
import unittest
from problem5 import clean_and_aggregate


class TestAggregatorRegressions(unittest.TestCase):
    def test_non_list_containers_are_rejected(self):
        for records in (None, {}, (), ({'g': 'A', 'v': 1},)):
            with self.subTest(records=records):
                with self.assertRaises(TypeError):
                    clean_and_aggregate(records, 'g', 'v')

    def test_record_and_metric_validation(self):
        for records, error in (([1], TypeError), ([{'g': 'A'}], ValueError),
                               ([{'v': 1}], ValueError),
                               ([{'g': 'A', 'v': True}], TypeError)):
            with self.subTest(records=records):
                with self.assertRaises(error):
                    clean_and_aggregate(records, 'g', 'v')

    def test_cleaning_filtering_and_case_normalization(self):
        records = [{'g': 1, 'v': -2}, {'g': 1, 'v': 4}, {'g': 2, 'v': None}]
        self.assertEqual(clean_and_aggregate(records, 'g', 'v', 'MEAN'), {'1': 1.0})
        self.assertEqual(clean_and_aggregate(records, 'g', 'v', 'min'), {'1': -2.0})
        self.assertEqual(clean_and_aggregate(records, 'g', 'v', 'max'), {'1': 4.0})
        self.assertEqual(clean_and_aggregate(records, 'g', 'v', filter_fn=lambda r: False), {})
        self.assertEqual(clean_and_aggregate([{'g': 1, 'v': None}], 'g', 'v'), {})


if __name__ == '__main__':
    unittest.main()
