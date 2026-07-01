# Hospital Team 1

This repository is now scaffolded for Project 1: hospital patient triage
scheduling system.

## Current Purpose

- Keep the project structure aligned with the assignment.
- Separate data structures, simulation logic, analysis, and visualization.
- Mirror every core module with tests.
- Keep written report materials under `docs/`.

## Project Structure

```text
hospital_team1/
  models/          Patient and triage enum
  structures/      Linked list and waiting room
  queues/          Heap queue and second queue implementation
  data/            CSV generation and import
  simulation/      Scheduling simulation and compliance logic
  analysis/        Performance and waiting-room analysis
  visualization/   CLI/GUI views and Flask dashboard
  utils/           Shared constants and time helpers
tests/
scripts/
datasets/
docs/
slides/
main.py
test.py
README.md
pyproject.toml
```

## What Goes Where

- Data model changes: `hospital_team1/models/`
- Linked-list and waiting room logic: `hospital_team1/structures/`
- Priority-queue implementations: `hospital_team1/queues/`
- CSV generation and loading: `hospital_team1/data/`
- Simulation rules and metrics: `hospital_team1/simulation/`
- Performance and insight analysis: `hospital_team1/analysis/`
- GUI and visual demos: `hospital_team1/visualization/`
- Tests: mirror the code structure under `tests/`
- Markdown report: `docs/`
- Presentation materials: `slides/`

## Run The Scaffold

```bash
python main.py
python test.py
python -m unittest discover -s tests -p "test_*.py"
```

## Run The Flask Dashboard

```bash
python scripts/launch_gui.py
```

Then open:

```text
http://127.0.0.1:5055
```

The current dashboard is a bilingual UI scaffold. All demo values are placed in
`hospital_team1/visualization/dashboard_data.py` so you can later replace them
with real queue, simulation, CSV, and analysis results.

## Persistent Placement Rules

Future placement rules for this repo are written in `docs/development_rules.md`.
When you ask for a new feature later, it should be added according to that map
instead of dropping code randomly into the root directory.
