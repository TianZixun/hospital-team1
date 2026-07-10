import unittest

from hospital_team1.models_part1 import TriageLevel


class TestTriageLevel(unittest.TestCase):
    def test_from_integer_returns_matching_level(self) -> None:
        self.assertEqual(TriageLevel.from_integer(1), TriageLevel.CRITICAL)
        self.assertEqual(TriageLevel.from_integer(2), TriageLevel.URGENT)
        self.assertEqual(TriageLevel.from_integer(3), TriageLevel.SEMI_URGENT)
        self.assertEqual(TriageLevel.from_integer(4), TriageLevel.NON_URGENT)

    def test_from_integer_rejects_invalid_value(self) -> None:
        with self.assertRaises(ValueError):
            TriageLevel.from_integer(9)


if __name__ == "__main__":
    unittest.main()
