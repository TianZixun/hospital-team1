from datetime import datetime
import unittest

from hospital_team1.analysis.performance import benchmark_priority_queues
from hospital_team1.analysis.predictor import predict_overtime_patients


class TestPredictorAndPerformance(unittest.TestCase):
    def test_predict_overtime_patients_returns_list(self) -> None:
        details = predict_overtime_patients(datetime(2026, 6, 30, 10, 0, 0))

        self.assertIsInstance(details, list)

    def test_benchmark_priority_queues_returns_loaded_rows(self) -> None:
        result = benchmark_priority_queues()

        self.assertIn("rows", result)
        self.assertIn("csv_path", result)
        self.assertIn("image_path", result)
        self.assertGreater(len(result["rows"]), 0)


if __name__ == "__main__":
    unittest.main()
