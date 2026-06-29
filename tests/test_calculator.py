import unittest

from hospital_team1 import Calculator


class TestCalculator(unittest.TestCase):
    def setUp(self) -> None:
        self.calc = Calculator()

    def test_add(self) -> None:
        self.assertEqual(self.calc.add(2, 3), 5)
        self.assertEqual(self.calc.add(-1, 1), 0)

    def test_subtract(self) -> None:
        self.assertEqual(self.calc.subtract(10, 4), 6)
        self.assertEqual(self.calc.subtract(-1, -1), 0)

    def test_multiply(self) -> None:
        self.assertEqual(self.calc.multiply(3, 4), 12)
        self.assertEqual(self.calc.multiply(10, 0), 0)

    def test_divide(self) -> None:
        self.assertEqual(self.calc.divide(8, 2), 4)
        self.assertAlmostEqual(self.calc.divide(7, 2), 3.5)

    def test_divide_by_zero_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.calc.divide(1, 0)


if __name__ == "__main__":
    unittest.main()
