# Module Map

## Part 1: Core modules

- Patient model and triage enum:
  - `hospital_team1/models/patient.py`
  - `hospital_team1/models/triage.py`
- Waiting-room linked list:
  - `hospital_team1/structures/linked_list.py`
  - `hospital_team1/structures/waiting_room.py`
- Priority queues:
  - `hospital_team1/queues/heap_priority_queue.py`
  - `hospital_team1/queues/ordered_linked_priority_queue.py`

## Part 1: Dataset generation and import

- `hospital_team1/data/dataset_generator.py`
- `hospital_team1/data/csv_loader.py`
- `datasets/patients_dataset.csv`

## Part 2: Simulation and analysis

- Shift simulation:
  - `hospital_team1/simulation/engine.py`
  - `hospital_team1/simulation/compliance.py`
  - `hospital_team1/simulation/report.py`
- Performance comparison:
  - `hospital_team1/analysis/performance.py`
- Waiting-room analytics:
  - `hospital_team1/analysis/waiting_room_insights.py`
- Open challenge prediction:
  - `hospital_team1/analysis/predictor.py`

## Part 2: Visualization

- CLI views:
  - `hospital_team1/visualization/cli_views.py`
- Heap-tree view:
  - `hospital_team1/visualization/heap_tree.py`
- GUI:
  - `hospital_team1/visualization/gui.py`

## Tests

- `tests/test_models/`
- `tests/test_structures/`
- `tests/test_smoke.py`

Mirror future modules with tests under the same feature area.
