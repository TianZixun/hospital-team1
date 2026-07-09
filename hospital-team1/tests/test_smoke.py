import unittest

from hospital_team1.analysis.performance import benchmark_priority_queues
from hospital_team1.data.dataset_generator import DatasetConfig
from hospital_team1.simulation.engine import SimulationConfig
from hospital_team1.visualization.cli_views import render_waiting_room_table


class TestScaffoldImports(unittest.TestCase):
    def test_scaffold_symbols_import(self) -> None:
        self.assertTrue(callable(benchmark_priority_queues))
        self.assertTrue(callable(render_waiting_room_table))
        self.assertIsNotNone(DatasetConfig)
        self.assertIsNotNone(SimulationConfig)


if __name__ == "__main__":
    unittest.main()
