---
type: auto
description: Apply when working on Python files. Enforce consistent coding style using Ruff, Poetry, isort, and PEP 8 conventions.
---

- Enforce code consistency style using Ruff. Use Poetry to run Ruff after all changes.
- Check coding style against the checks specified in `.pre-commit-config.yaml`.
- Prefer using classes to independent functions, unless there is a strong overriding reason to use a function.
- Use isort for import sorting.
- Follow PEP 8 naming conventions:
  - `snake_case` for functions and variables
  - `PascalCase` for classes
  - `UPPER_CASE` for constants
- Maximum line length of 88 characters.
- Use absolute imports over relative imports.
