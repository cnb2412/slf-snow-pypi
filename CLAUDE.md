# CLAUDE.md

## Project
`slf-snow`: async Python client for the SLF Snow API
(https://measurement-api.slf.ch). Used as a dependency of a thin Home Assistant
integration.

## Way of working (mandatory)
- Spec-driven: always read the matching file in `docs/specs/` before writing
  code. If the implementation diverges from the spec, update the spec first.
- Test-driven: write pytest tests first/alongside every function. HTTP is mocked
  with `aioresponses` and fixtures from `tests/fixtures/` — NEVER call the real
  API in tests.
- No `home-assistant` imports. No own event loop. No blocking I/O.
- Use the project's own exceptions (see `src/slf_snow/exceptions.py`).
- Everything typed; `mypy --strict` must be green.

## Commands (in the Zed in-container terminal; outside Zed via `devcontainer exec --workspace-folder . …`)
- Setup:      `uv sync`
- Tests:      `uv run pytest`
- Lint:       `uv run ruff check . && uv run ruff format --check .`
- Typecheck:  `uv run mypy`
- Smoke:      `uv run python examples/run.py WFJ2`

## Definition of Done
ruff, mypy, pytest green; coverage ≥ 90 %; spec updated; CHANGELOG amended.
