# ADR-008: Development toolchain

Status: Accepted | Date: 2026-11-05

Supersedes: ADR-004

## Context
The project needs tooling for environments and dependency locking, building
source distributions and wheels, testing, linting/formatting and static type
checking. Tests must exercise the delicate behavior of UC-004 realistically
(time limit, the allowed number of requests, HTTP 429/5xx, connection failures, station
code encoding) without calling the real SLF Measurement API. Development tools
are not runtime dependencies, so NFR-010 does not apply to them.

ADR-004 chose hatchling as build backend but did not weigh uv's own build
backend `uv_build` as a separate option. The package is pure Python with a src
layout, a static version, a `py.typed` marker and an SPDX license expression;
it needs no build scripts, generated files or extension modules. `uv_build`
is the default backend of `uv init --lib`, supports only pure Python, expects
`src/<package_name>/__init__.py` by default, and copies `project.license-files`
into sdist and wheel. Its documentation recommends an upper bound on its
version and names hatchling for projects that need build scripts or a more
flexible layout. Home Assistant Core builds with setuptools; the backend is
invisible to consumers because sdist and wheel formats are standardized.

Current versions: uv 0.13.7 (with `uv_build`), hatchling 1.33.0, Poetry 2.5.1,
ruff 0.17.3, mypy 2.4.1, pytest 9.2.0, pytest-asyncio 1.4.1, pytest-aiohttp
1.1.1, aioresponses 0.7.9. Home Assistant Core uses ruff, mypy and pytest.

## Decision drivers
- Constraint NFR-011: every release includes a source distribution.
- Constraint NFR-012: 0 errors from a strict static type check; the package
  ships `py.typed`.
- Constraint NFR-010: the license is stated in the package metadata.
- NFR-004, NFR-006, FR-015, FR-017: must be verifiable by tests.
- Definition of done: tests referencing FR/UC IDs, lint and typecheck clean.
- Brief constraint: the SLF infrastructure must not be loaded by tests.
- Learning goal of the owner: as few tools and configuration as possible.

## Considered options
1. uv with `uv_build`, pytest with pytest-aiohttp (local test server), ruff, mypy --strict
2. uv with hatchling, otherwise as option 1 (the decision of ADR-004)
3. As option 1, but HTTP mocking with aioresponses instead of a local server
4. Poetry with poetry-core, otherwise as option 1
5. pip/venv + setuptools without lock file

## Decision
We use uv for environments, locking and building, `uv_build` as build
backend, pytest with pytest-aiohttp running tests against a local test server,
ruff for linting and formatting, and mypy in strict mode, because one tool
covers environment, lock file and build without backend configuration, the
package needs nothing beyond a pure-Python src layout (NFR-011, NFR-012,
NFR-010), a local server exercises real delays, status codes, dropped
connections and request counts (NFR-004, NFR-006, FR-015, FR-017) without
touching the SLF API, mypy strict verifies NFR-012, and the lint and test
tools match those of Home Assistant Core.

## Consequences
- **Positive:** One tool and vendor for environment, lock file and build;
  minimal `pyproject.toml`; realistic tests of the error model; the same lint
  and type tools as Home Assistant.
- **Negative:** `uv_build` is younger than hatchling and has no build scripts
  or plugins (e.g. no version derived from the Git tag); the required upper
  bound (`uv_build>=0.13,<0.14`) has to be raised with uv minor releases;
  build tool and package manager come from the same vendor (Astral).
  Contributors need uv installed; tests with a real local server are slightly
  slower and more involved than pure mocks.
- **Follow-ups:** `[build-system]` with `requires = ["uv_build>=0.13.6,<0.14"]`
  and `build-backend = "uv_build"`; commands in architecture.md section 9; test
  fixtures derived from real SLF responses need a CC BY 4.0 attribution note in
  the repository; timeout tests use a short configured limit to keep the suite
  fast. Switching back to hatchling only changes `[build-system]` and needs a
  new ADR.

## Rejected options
**hatchling (ADR-004):** Mature, widely used and extensible through plugins and
build hooks, but this package needs none of that; it adds a second build tool
next to uv without a benefit today.

**aioresponses:** Simpler, but timeouts and connection failures are only
simulated as raised exceptions, so NFR-006 and FR-015 are not exercised end to
end.

**Poetry:** Equally capable, but adds its own project conventions; no advantage
for this project.

**pip/venv + setuptools:** Simplest, but no lock file and more manual steps;
builds are less reproducible.

## Sources
- https://docs.astral.sh/uv/concepts/build-backend/
- https://github.com/home-assistant/core/blob/dev/pyproject.toml (`build-backend = "setuptools.build_meta"`)
- https://pypi.org/project/uv/
- https://pypi.org/project/hatchling/
- https://pypi.org/project/ruff/
- https://pypi.org/project/mypy/
- https://pypi.org/project/pytest/
- https://pypi.org/project/pytest-aiohttp/
- https://pypi.org/project/aioresponses/
