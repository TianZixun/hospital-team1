# Hospital Team 1

This repository is a starter Python project that matches the general course
requirements from the provided PDF and is ready to be extended with the real
assignment logic.

## Included

- A Python package in `hospital_team1/`
- Unit tests in `tests/`
- Markdown documentation in `docs/`
- VSCode settings for Python and Code Runner
- A `.gitignore` file for common Python artifacts

## Project Structure

```text
hospital_team1/
tests/
docs/
main.py
test.py
README.md
pyproject.toml
```

## Run The Project

```bash
python main.py
```

## Run Tests

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## Optional Test Coverage

Install the optional dev dependency:

```bash
pip install -e .[dev]
```

Then run:

```bash
python -m coverage run -m unittest discover -s tests -p "test_*.py"
python -m coverage report
```

## Next Step

Replace the example calculator logic with the actual project requirements when
you receive the real assignment brief.
