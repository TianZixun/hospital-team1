# Project Documentation

## Overview

This document is the starter report for the Python course project. The current
implementation contains a small calculator example so that the repository has
working source code, unit tests, and documentation.

## Folder Layout

- `hospital_team1/`: the main project package
- `tests/`: unit tests written with `unittest`
- `docs/`: Markdown documentation for the final report
- `main.py`: a simple entry point for running the example
- `test.py`: a quick test program for VSCode run verification

## How To Run

```bash
python main.py
```

## How To Test

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## Coverage

After installing the optional dev dependency, use:

```bash
python -m coverage run -m unittest discover -s tests -p "test_*.py"
python -m coverage report
```

## What To Replace

- Replace the example calculator with the real project logic.
- Expand this document into the final report for the assignment.
- Add more tests as the project grows.
