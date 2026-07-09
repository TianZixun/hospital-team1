import unittest

from hospital_team1.simulation.report import build_shift_report


class TestShiftReport(unittest.TestCase):
    def test_build_shift_report_handles_empty_input(self) -> None:
        report = build_shift_report({"records": [], "untreated": [1, 2]})

        self.assertEqual(report["treated_patients"], 0)
        self.assertEqual(report["untreated_patients"], 2)

    def test_build_shift_report_aggregates_metrics(self) -> None:
        report = build_shift_report(
            {
                "records": [
                    {"wait_minutes": 5.0, "within_threshold": True},
                    {"wait_minutes": 25.0, "within_threshold": False},
                ],
                "untreated": [1],
            }
        )

        self.assertEqual(report["treated_patients"], 2)
        self.assertEqual(report["average_wait_minutes"], 15.0)
        self.assertEqual(report["compliance_rate"], 50.0)
        self.assertEqual(report["max_wait_minutes"], 25.0)
        self.assertEqual(report["untreated_patients"], 1)


if __name__ == "__main__":
    unittest.main()
