# Development Guide

## Before changing code

1. Create a branch for the change.
2. Keep changes focused on one feature or fix.
3. Add or update tests when behavior changes.
4. Run the complete test suite before committing.

## Useful commands

```bash
python -m compileall .
pytest -q
python main.py
```

For Linux GUI testing without a physical display:

```bash
xvfb-run -a pytest -q
```

## Adding a new security module

Choose the domain directory that best matches the module's responsibility. If the module belongs to a new area, create a clearly named directory under `core/` and document it in `docs/architecture.md`.

Avoid placing unrelated functionality into `gui/app.py` when it can live in a reusable core module.
