import unittest

from power_calc import calculate_capacity


class TestPowerCalc(unittest.TestCase):
    def test_calculate_capacity_default_efficiency(self):
        result = calculate_capacity(flow=12.0, head=80.0)
        self.assertAlmostEqual(result, 9.81 * 12.0 * 80.0 * 0.85 / 1000.0)

    def test_calculate_capacity_custom_efficiency(self):
        result = calculate_capacity(flow=10.0, head=50.0, efficiency=0.9)
        self.assertAlmostEqual(result, 9.81 * 10.0 * 50.0 * 0.9 / 1000.0)

    def test_calculate_capacity_zero_values(self):
        result = calculate_capacity(flow=0.0, head=80.0)
        self.assertEqual(result, 0.0)


if __name__ == "__main__":
    unittest.main()
