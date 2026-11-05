# ADR-001: Supported Python versions

Status: Accepted | Date: 2026-10-31

## Context
The package is a Python library (NFR-001) whose concrete target consumer is a
Home Assistant Core integration (G-06). The minimum Python version determines
the available language features and tooling, and every supported version has to
be tested in CI. Home Assistant Core (development branch 2026.12) requires
Python `>=3.14.2`. Python 3.10 reached end of life on 2026-10-01; 3.11 follows in
2027-10; 3.14 and 3.15 are in bugfix status.

## Decision drivers
- Constraint NFR-001: Python package with an asynchronous interface.
- Constraint NFR-012: strict static type check of the public interface.
- G-06: usable by a Home Assistant Core integration.
- Definition of done: tests, lint and typecheck clean on every supported version.

## Considered options
1. Python ≥ 3.14
2. Python ≥ 3.13
3. Python ≥ 3.12
4. Python ≥ 3.11

## Decision
We support Python ≥ 3.14, because it matches Home Assistant Core's requirement
(G-06) with the smallest test matrix, and the brief names no consumer that needs
an older version. Python versions are dropped when they reach end of life, and
the newest released Python version is part of the test matrix.

## Consequences
- **Positive:** Small CI matrix (currently 3.14 and 3.15); the same runtime as
  Home Assistant; current language and typing features are available.
- **Negative:** Developers on older Python versions (e.g. distributions shipping
  3.12 or 3.13) cannot install the package.
- **Follow-ups:** Set `requires-python = ">=3.14"` and matching classifiers; CI
  matrix 3.14 and 3.15 (ADR-005). Lowering the minimum later is non-breaking if
  a need appears.

## Rejected options
**≥ 3.13 / ≥ 3.12:** Wider audience, but no consumer outside Home Assistant is
known (brief assumptions), and each version adds a CI matrix entry. Can still be
adopted later without breaking anyone.

**≥ 3.11:** Widest audience, but 3.11 reaches end of life in 2027-10, shortly
after a first release, which would force an early breaking bump.

## Sources
- https://github.com/home-assistant/core/blob/dev/pyproject.toml (`requires-python = ">=3.14.2"`)
- https://github.com/home-assistant/core/blob/dev/homeassistant/const.py (`REQUIRED_PYTHON_VER = (3, 14, 2)`)
- https://devguide.python.org/versions/
