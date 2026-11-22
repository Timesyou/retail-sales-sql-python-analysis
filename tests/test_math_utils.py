import unittest

from shelfsense.math_utils import abc_classes, population_stddev, round_up_to_multiple, service_level_z, weighted_moving_average, xyz_class


class MathUtilityTests(unittest.TestCase):
    def test_weighted_average_gives_newest_value_more_weight(self):
        self.assertAlmostEqual(weighted_moving_average([10, 20, 30]), 23.3333333333)

    def test_weighted_average_rejects_empty_series(self):
        with self.assertRaises(ValueError):
            weighted_moving_average([])

    def test_population_standard_deviation(self):
        self.assertAlmostEqual(population_stddev([2, 4, 4, 4, 5, 5, 7, 9]), 2.0)

    def test_service_level_quantile(self):
        self.assertAlmostEqual(service_level_z(0.95), 1.6448536269, places=8)

    def test_invalid_service_level_is_rejected(self):
        for value in (0.0, 1.0, -0.2, 1.1):
            with self.subTest(value=value), self.assertRaises(ValueError):
                service_level_z(value)

    def test_pack_rounding(self):
        self.assertEqual(round_up_to_multiple(17, 6), 18)
        self.assertEqual(round_up_to_multiple(0, 6), 0)

    def test_abc_is_deterministic(self):
        self.assertEqual(abc_classes({"B": 80, "A": 10, "C": 10}), {"B": "A", "A": "B", "C": "C"})

    def test_abc_zero_revenue_is_class_c(self):
        self.assertEqual(abc_classes({"A": 0, "B": 0}), {"A": "C", "B": "C"})

    def test_abc_large_first_item_is_not_left_without_an_a_class(self):
        self.assertEqual(abc_classes({"A": 90, "B": 5, "C": 5}), {"A": "A", "B": "B", "C": "C"})

    def test_xyz_boundaries(self):
        self.assertEqual(xyz_class(None), "N")
        self.assertEqual(xyz_class(0.5), "X")
        self.assertEqual(xyz_class(0.75), "Y")
        self.assertEqual(xyz_class(1.01), "Z")


if __name__ == "__main__":
    unittest.main()
