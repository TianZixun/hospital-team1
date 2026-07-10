import unittest

from hospital_team1.simulation_part2.report import build_shift_report


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


    # ── 新增：边界与场景覆盖 ──────────────────────────────

    def test_all_compliant(self) -> None:
        """全部合规 → compliance_rate = 100.0。"""
        report = build_shift_report({
            "records": [
                {"wait_minutes": 5.0, "within_threshold": True},
                {"wait_minutes": 10.0, "within_threshold": True},
            ],
            "untreated": [],
        })
        self.assertEqual(report["compliance_rate"], 100.0)

    def test_all_noncompliant(self) -> None:
        """全部不合规 → compliance_rate = 0.0。"""
        report = build_shift_report({
            "records": [
                {"wait_minutes": 30.0, "within_threshold": False},
                {"wait_minutes": 50.0, "within_threshold": False},
            ],
            "untreated": [],
        })
        self.assertEqual(report["compliance_rate"], 0.0)

    def test_avg_wait_calculation(self) -> None:
        """两个病人等 10 和 20 分钟 → avg = 15.0。"""
        report = build_shift_report({
            "records": [
                {"wait_minutes": 10.0, "within_threshold": True},
                {"wait_minutes": 20.0, "within_threshold": True},
            ],
            "untreated": [],
        })
        self.assertEqual(report["average_wait_minutes"], 15.0)

    def test_max_wait_correct(self) -> None:
        """三个病人等 5、30、10 分钟 → max = 30.0。"""
        report = build_shift_report({
            "records": [
                {"wait_minutes": 5.0, "within_threshold": True},
                {"wait_minutes": 30.0, "within_threshold": False},
                {"wait_minutes": 10.0, "within_threshold": True},
            ],
            "untreated": [],
        })
        self.assertEqual(report["max_wait_minutes"], 30.0)

    def test_untreated_count(self) -> None:
        """untreated 人数正确传递到报告。"""
        report = build_shift_report({
            "records": [],
            "untreated": [1, 2, 3],
        })
        self.assertEqual(report["untreated_patients"], 3)


if __name__ == "__main__":
    unittest.main()
