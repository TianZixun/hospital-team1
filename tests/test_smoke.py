import unittest

from hospital_team1.analysis_part2.performance import benchmark_priority_queues
from hospital_team1.data_part1.dataset_generator import DatasetConfig
from hospital_team1.simulation_part2.engine import SimulationConfig
from hospital_team1.visualization_part2.cli_views import render_waiting_room_table


class TestScaffoldImports(unittest.TestCase):
    def test_scaffold_symbols_import(self) -> None:
        self.assertTrue(callable(benchmark_priority_queues))
        self.assertTrue(callable(render_waiting_room_table))
        self.assertIsNotNone(DatasetConfig)
        self.assertIsNotNone(SimulationConfig)


if __name__ == "__main__":
    unittest.main()
