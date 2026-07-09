# Development Rules For This Repo

Use this file as the placement contract for future changes.

## Future change routing

- If the request is about patient fields, triage rules, comparison logic, or
  model validation:
  - edit `hospital_team1/models/`
- If the request is about linked lists, waiting-room storage, insert/delete/find
  operations, or current queue contents:
  - edit `hospital_team1/structures/`
- If the request is about heap behavior, queue ordering, enqueue/dequeue, peek,
  or comparing two queue implementations:
  - edit `hospital_team1/queues/`
- If the request is about CSV generation, CSV import, fake data creation, or
  dataset configuration:
  - edit `hospital_team1/data/`
  - write generated files into `datasets/`
- If the request is about duty-shift simulation, service intervals, waiting
  times, compliance rules, or final simulation metrics:
  - edit `hospital_team1/simulation/`
- If the request is about benchmarking, anomaly detection, wait-time estimation,
  or overtime prediction:
  - edit `hospital_team1/analysis/`
- If the request is about tree display, waiting-room display, GUI interaction,
  or step-by-step animation:
  - edit `hospital_team1/visualization/`
- If the request is about helper constants or time calculations:
  - edit `hospital_team1/utils/`
- If the request is about report writing:
  - edit `docs/`
- If the request is about slides or presentation materials:
  - edit `slides/`

## Test rule

Every new logic file should get a matching test file under `tests/`.

Examples:

- `hospital_team1/models/patient.py` -> `tests/test_models/test_patient.py`
- `hospital_team1/queues/heap_priority_queue.py` ->
  `tests/test_queues/test_heap_priority_queue.py`
- `hospital_team1/simulation/engine.py` ->
  `tests/test_simulation/test_engine.py`

## Root directory rule

Do not place new business logic directly in the repository root unless it is:

- `main.py`
- `test.py`
- `README.md`
- `pyproject.toml`

Everything else should go into a feature module.
