# ADR-004: Development toolchain

Status: Proposed | Date: 2026-10-31

## Context
The project needs tooling for environments and dependency locking, building
source distributions and wheels, testing, linting/formatting and static type
checking. Tests must exercise the delicate behavior of UC-004 realistically
(time limit, exactly one request, HTTP 429/5xx, connection failures, station
code encoding) without calling the real SLF Measurement API. Development tools
are not runtime dependencies, so NFR-010 does not apply to them. Current
versions: uv 0.13.6 (with `uv_build`), hatchling 1.33.0, Poetry 2.5.1, ruff
0.17.3, mypy 2.4.1, pytest 9.2.0, pytest-asyncio 1.4.1, pytest-aiohttp 1.1.1,
aioresponses 0.7.9. Home Assistant Core uses ruff, mypy and pytest.

## Decision drivers
- Constraint NFR-011: every release includes a source distribution.
- Constraint NFR-012: 0 errors from a strict static type check.
- NFR-004, NFR-006, FR-015, FR-017: must be verifiable by tests.
- Definition of done: tests referencing FR/UC IDs, lint and typecheck clean.
- Brief constraint: the SLF infrastructure must not be loaded by tests.

## Considered options
1. uv + hatchling, pytest with pytest-aiohttp (local test server), ruff, mypy --strict
2. As option 1, but HTTP mocking with aioresponses instead of a local server
3. Poetry with poetry-core, otherwise as option 1
4. pip/venv + setuptools without lock file

## Decision
We use uv for environments, locking and building, hatchling as build backend,
pytest with pytest-aiohttp running tests against a local test server, ruff for
linting and formatting, and mypy in strict mode, because a local server
exercises real delays, status codes, dropped connections and request counts
(NFR-004, NFR-006, FR-015, FR-017) without touching the SLF API, mypy strict
verifies NFR-012, and the tools match those of Home Assistant Core.

## Consequences
- **Positive:** One tool for environment, lock file and build; realistic tests
  of the error model; the same lint and type tools as Home Assistant.
- **Negative:** Contributors need uv installed; tests with a real local server
  are slightly slower and more involved than pure mocks.
- **Follow-ups:** Commands in architecture.md section 9; test fixtures derived
  from real SLF responses need a CC BY 4.0 attribution note in the repository;
  timeout tests use a short configured limit to keep the suite fast.

## Rejected options
**aioresponses:** Simpler, but timeouts and connection failures are only
simulated as raised exceptions, so NFR-006 and FR-015 are not exercised end to
end.

**Poetry:** Equally capable, but adds its own project conventions; no advantage
for this project.

**pip/venv + setuptools:** Simplest, but no lock file and more manual steps;
builds are less reproducible.

## Sources
- https://pypi.org/project/uv/
- https://pypi.org/project/hatchling/
- https://pypi.org/project/ruff/
- https://pypi.org/project/mypy/
- https://pypi.org/project/pytest/
- https://pypi.org/project/pytest-aiohttp/
- https://pypi.org/project/aioresponses/
