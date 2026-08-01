# 🧪 Tests

## Purpose

This directory contains the **pytest test suite** for ColonSightAI.

## Structure

```
tests/
├── __init__.py
├── conftest.py             ← Shared fixtures (app, client, runner, temp dirs)
├── test_config.py          ← Configuration loading tests
├── test_utils.py           ← Validator and helper function tests
└── test_ai_pipeline.py     ← AI pipeline config and interface tests
```

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ --cov=app --cov-report=html

# Run a specific test file
python -m pytest tests/test_utils.py -v

# Run a specific test class
python -m pytest tests/test_utils.py::TestFileValidation -v
```

## Writing New Tests

1. Place test files in this directory, prefixed with `test_`.
2. Use fixtures from `conftest.py` for app, client, and temp directories.
3. Follow the `TestClassName` → `test_method_name` convention.
