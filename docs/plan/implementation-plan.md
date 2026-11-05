# Implementation Plan: slf-snow-pypi

Status: Draft | Version: 0.2 | Date: 2026-11-05
Based on: Spec 2.2, Architecture 0.2

Legend: [ ] open · [~] in progress · [x] done · [-] dropped

Tags: **[manual]** = only the owner can do it (accounts, settings, approvals);
**[learning]** = owner learning session, no change to the repository;
**owner-paced** = Claude explains each file before creating it, the owner runs the commands.
Each step is sized for about one hour of owner review.

## Milestone 1: First PyPI release — station lists and current measured values
Releasable result: `slf-snow` 0.1.0 on PyPI with study-plot, IMIS and combined station
lists (UC-001), the current measured record of one station in either network (UC-002
single-station flows) and the complete error model (UC-004). Deferred to Milestone 2:
all-stations variants (FR-018) and modeled IMIS values (UC-003).

### [~] STEP-01: [learning] uv, uv_build and Python packaging
- **Goal:** The owner understands how a Python package is defined, locked, built and inspected before the skeleton is created.
- **Covers:** ADR-001, ADR-008 (preparation)
- **Depends on:** —
- **Done when:** In a scratch directory outside the repo, the owner has run `uv init --lib`, `uv add aiohttp`, `uv sync`, `uv build`, and inspected the sdist and wheel contents (`METADATA`, `py.typed`, license fields); open questions are answered.
- **Notes:** No commit. Topics: `pyproject.toml` sections, `requires-python`, lower-bound dependencies (ADR-002), `uv.lock`, build backends (`uv_build` vs. hatchling, ADR-008), src layout, SPDX license expression, PEP 561 `py.typed`.

### [ ] STEP-02: Walking skeleton — local toolchain and CI (owner-paced)
- **Goal:** An empty, typed `slf_snow` package whose commands from "Development & tooling" all work locally and in CI.
- **Covers:** ADR-001, ADR-008, ADR-005 (CI workflow), ADR-006, NFR-002, NFR-010, NFR-012
- **Depends on:** STEP-01
- **Done when:** `uv sync`, `uv run pytest` (one trivial test), `uv run ruff check`, `uv run ruff format --check`, `uv run mypy` (strict) pass locally; `uv build` produces sdist and wheel containing `py.typed`, `License-Expression: MIT` and `aiohttp` as the only runtime dependency (lower bound only); `.github/workflows/ci.yml` runs on Python 3.14 and 3.15 and is green on the pull request.
- **Notes:** Files: `pyproject.toml` (distribution `slf-snow`, `requires-python = ">=3.14"`, classifiers, build backend `uv_build` with upper bound, static version `0.0.1`), `src/slf_snow/__init__.py`, `src/slf_snow/py.typed`, `LICENSE` (MIT; owner confirms the copyright holder line), `tests/test_skeleton.py`, `uv.lock`. dev dependencies: pytest, pytest-aiohttp, ruff, mypy.

### [ ] STEP-03: [learning] Trusted Publishing and the release flow
- **Goal:** The owner understands the release path tag → build → TestPyPI → approval → PyPI before setting up accounts.
- **Covers:** ADR-005 (preparation)
- **Depends on:** STEP-02
- **Done when:** The owner can explain OIDC Trusted Publishing, pending publishers, GitHub environments with required reviewers, why TestPyPI is staging, and why a PyPI version can never be reused; Claude has walked through a draft of `release.yml` in chat (not committed).
- **Notes:** No commit. Sources: docs.pypi.org/trusted-publishers, Python Packaging guide on GitHub Actions publishing.

### [ ] STEP-04: [manual] Public repository, GitHub environments, PyPI and TestPyPI publishers
- **Goal:** Everything outside the repository that the release workflow needs exists.
- **Covers:** NFR-011, ADR-005
- **Depends on:** STEP-03
- **Done when:** The owner confirms each item below in chat.
- **Owner provides / does:**
  1. GitHub `cnb2412/slf-snow-pypi`: change visibility to **Public** and enable **Issues** (NFR-011; required reviewers on environments are free only for public repos).
  2. GitHub environment `testpypi` (deployment tag rule `v*`).
  3. GitHub environment `pypi` (deployment tag rule `v*`, required reviewer: `cnb2412`, "Prevent self-review" off, since the tag is pushed with the owner's account).
  4. Account on https://test.pypi.org and on https://pypi.org (separate accounts), 2FA enabled on both.
  5. Pending trusted publisher on **TestPyPI**: project `slf-snow`, owner `cnb2412`, repository `slf-snow-pypi`, workflow `release.yml`, environment `testpypi`.
  6. Pending trusted publisher on **PyPI**: same values, environment `pypi`.
  7. Recommended (brief risk mitigation, not blocking): subscribe to SLF's "Live measurement and model data" mailing list (data@slf.ch).
- **Notes:** No secrets are created (Trusted Publishing).

### [ ] STEP-05: Walking skeleton — release dry run to TestPyPI (owner-paced)
- **Goal:** Prove the release pipeline end to end with the empty package, without a production release.
- **Covers:** ADR-005, NFR-010, NFR-011
- **Depends on:** STEP-04
- **Done when:** `.github/workflows/release.yml` (build once, tag-equals-version check, publish to TestPyPI, install check from TestPyPI, `pypi` job gated by environment) is merged; tag `v0.0.1` publishes sdist and wheel with attestations to TestPyPI; the install check passes; the `pypi` job waits for approval and the owner **rejects** it; a deliberately wrong tag fails the version check (tested on a throwaway tag, then deleted).
- **Notes:** Claude pushes the tag; only the owner acts on the `pypi` environment. Risk: a pending publisher does not reserve the name `slf-snow` on PyPI; the owner may decide here to approve 0.0.1 to PyPI to claim it.

### [ ] STEP-06: [learning] asyncio and aiohttp
- **Goal:** The owner understands the async building blocks of the client before it is built.
- **Covers:** ADR-002, ADR-008 (preparation)
- **Depends on:** STEP-02
- **Done when:** In a scratch script the owner has used `aiohttp.ClientSession` (own vs. supplied), `ClientTimeout`, a local aiohttp test server with a request counter (pytest-aiohttp), `asyncio.TaskGroup` with `asyncio.timeout`, and seen how an `ExceptionGroup` arises and is unwrapped.
- **Notes:** No commit.

### [ ] STEP-07: Client core and study-plot station list (UC-001 main, owner-paced)
- **Goal:** `SlfSnowClient.get_study_plot_stations()` returns typed `Station` objects through an own or supplied session.
- **Covers:** UC-001 (main, A2, A3), FR-001, FR-009, FR-020, NFR-001, NFR-003, NFR-004, NFR-005, NFR-009, NFR-012, ADR-002, ADR-003
- **Depends on:** STEP-06
- **Done when:** Tests for UC-001-AC1, UC-001-AC3, UC-001-AC4 pass against the local test server (request counter = 1); test: no request after constructing the client (NFR-005); test: a supplied session is used and still open after `close()`, an own session is closed (NFR-009); DoD from CLAUDE.md met.
- **Notes:** Creates `client.py`, `_http.py`, `_parse.py`, `models.py` (`Network`, `Station`), `exceptions.py` (full hierarchy), test-server fixture, `tests/fixtures/` with a CC BY 4.0 note (`tests/fixtures/README.md`). Base URL overridable only through an internal parameter.

### [ ] STEP-08: Error model on station lists (UC-001 E1/E2, UC-004)
- **Goal:** Every transport, status and content failure of a station-list call maps to exactly one package error, without retries and within the time limit.
- **Covers:** UC-001 (E1, E2), UC-004 (main, A1, E1–E7), FR-014, FR-015, FR-016, NFR-004, NFR-006
- **Depends on:** STEP-07
- **Done when:** Tests for UC-001-AC5, UC-001-AC6, UC-004-AC1, UC-004-AC2, UC-004-AC6, UC-004-AC7, UC-004-AC8, UC-004-AC9, UC-004-AC10, UC-004-AC12 pass; redirects (3xx) are not followed and raise *invalid response*; each error keeps the original exception as `__cause__`; timeout tests use a short limit (default 10 s asserted by configuration, not by waiting); DoD met.
- **Notes:** Error tests are parametrized over the operations so later steps extend them to each new operation.

### [ ] STEP-09: IMIS and combined station list (UC-001 A1, A4, E3)
- **Goal:** `get_imis_stations()` and `get_all_stations()` (two concurrent requests, all or nothing, one time limit).
- **Covers:** UC-001 (A1, A4, E3), FR-002, FR-019, FR-020, FR-014, NFR-004, NFR-006
- **Depends on:** STEP-08
- **Done when:** Tests for UC-001-AC2, UC-001-AC7, UC-001-AC8 pass; test: no `ExceptionGroup` reaches the caller; test: the combined call ends within the limit counted from its first request; UC-004 error tests extended to both new operations; DoD met.

### [ ] STEP-10: Current measured record of a station — main flow (UC-002 main, A1)
- **Goal:** `get_current_measurement(network, code)` returns the current `StudyPlotRecord` or `ImisRecord` with UTC timestamp.
- **Covers:** UC-002 (main, A1), FR-008, FR-009, FR-017, FR-020, FR-021, NFR-003, NFR-004, ADR-007
- **Depends on:** STEP-08
- **Done when:** Tests for UC-002-AC1, UC-002-AC2, UC-002-AC3, UC-002-AC8, UC-002-AC11, UC-002-AC12 pass; tests for timestamps with and without `Z`, a tie on the latest timestamp (first delivered wins) and an empty timestamp (never current); request uses `period_in_days=1`; DoD met.

### [ ] STEP-11: Current measured record — no record and error flows (UC-002 A2, E1–E4)
- **Goal:** Missing data returns `None`; unknown and empty codes and API failures raise the defined package errors.
- **Covers:** UC-002 (A2, E1–E4), UC-004 (A2–A4, E6, E8, E9), FR-010, FR-011, FR-014, FR-015, FR-016, FR-017
- **Depends on:** STEP-10
- **Done when:** Tests for UC-002-AC4, UC-002-AC6, UC-002-AC7, UC-002-AC9, UC-002-AC10, UC-002-AC13, UC-002-AC15, UC-002-AC16, UC-004-AC3, UC-004-AC4, UC-004-AC5, UC-004-AC11, UC-004-AC13, UC-004-AC14 pass; UC-004 error tests extended to `get_current_measurement`; DoD met.

### [ ] STEP-12: README — usage, errors and data attribution
- **Goal:** A consumer can install and use the package from the README alone.
- **Covers:** NFR-007, NFR-003, NFR-009 (documented usage)
- **Depends on:** STEP-09, STEP-11
- **Done when:** README covers installation, a usage example per M1 operation, supplied session and time limit, "no record" vs. errors, the CC BY 4.0 notice and the required SLF attribution with link to www.slf.ch (NFR-007), and the not-yet-available operations; the owner has reviewed the attribution text; the README is the long description in the package metadata.

### [ ] STEP-13: Release 0.1.0 to TestPyPI
- **Goal:** Version 0.1.0 is built by public CI and proven on TestPyPI.
- **Covers:** NFR-008, NFR-011, NFR-010
- **Depends on:** STEP-05, STEP-12
- **Done when:** Version bump to `0.1.0` merged; tag `v0.1.0` pushed; TestPyPI shows 0.1.0 with sdist and wheel; install check passes; the `pypi` job waits for approval.

### [ ] STEP-14: [manual] Approve the PyPI release of 0.1.0
- **Goal:** Version 0.1.0 is live on PyPI.
- **Covers:** NFR-008, ADR-005
- **Depends on:** STEP-13
- **Done when:** PyPI shows `slf-snow` 0.1.0 and `pip install slf-snow==0.1.0` works in a clean environment (checked by Claude after approval).
- **Owner provides / does:** In GitHub Actions, run "Release" for `v0.1.0` → "Review deployments" → environment `pypi` → **Approve**. Claude never approves this.

## Milestone 2: All-stations and modeled values
Releasable result: `slf-snow` 0.2.0 on PyPI covering the complete spec 2.2.

### [ ] STEP-15: Current measured records of all stations (UC-002 A3, A4)
- **Goal:** `get_current_study_plot_measurements()` and `get_current_imis_measurements()`.
- **Covers:** UC-002 (A3, A4), FR-018, FR-020, NFR-003, NFR-004
- **Depends on:** STEP-11
- **Done when:** Tests for UC-002-AC5, UC-002-AC14 pass; test: stations without a current record are omitted; UC-004 error tests extended to both operations; DoD met.

### [ ] STEP-16: Current modeled record of an IMIS station (UC-003 main, A1, A3, E1)
- **Goal:** `get_current_modeled(code)` returns a `ModeledRecord` or `None`.
- **Covers:** UC-003 (main, A1, A3, E1), FR-005, FR-007, FR-008, FR-009, FR-010, FR-017, NFR-003, NFR-004
- **Depends on:** STEP-11
- **Done when:** Tests for UC-003-AC2, UC-003-AC5, UC-003-AC9, UC-003-AC12 pass; test: `ModeledRecord` is not an instance of either measured record type (FR-007); UC-004 error tests extended; DoD met.

### [ ] STEP-17: Current modeled records of all IMIS stations (UC-003 A2, E2, E3)
- **Goal:** `get_current_modeled_all()`.
- **Covers:** UC-003 (A2, E2, E3), FR-018, FR-007, FR-015, FR-016
- **Depends on:** STEP-16
- **Done when:** Tests for UC-003-AC7, UC-003-AC10, UC-003-AC11 pass; UC-004 error tests extended; DoD met.

### [ ] STEP-18: README update and release 0.2.0 to TestPyPI
- **Goal:** Complete documentation and 0.2.0 proven on TestPyPI.
- **Covers:** NFR-007, NFR-008, NFR-011
- **Depends on:** STEP-14, STEP-15, STEP-17
- **Done when:** README documents the M2 operations and modeled vs. measured values; version bump to `0.2.0` merged; tag `v0.2.0` on TestPyPI with install check passing; `pypi` job waiting.

### [ ] STEP-19: [manual] Approve the PyPI release of 0.2.0
- **Goal:** Version 0.2.0 is live on PyPI.
- **Covers:** NFR-008, ADR-005
- **Depends on:** STEP-18
- **Done when:** PyPI shows 0.2.0; clean install works.
- **Owner provides / does:** Approve environment `pypi` for the `v0.2.0` run, as in STEP-14.

## Coverage
| ID | Step(s) |
|----|---------|
| FR-001 | STEP-07 |
| FR-002 | STEP-09 |
| FR-005 | STEP-16 |
| FR-007 | STEP-16, STEP-17 |
| FR-008 | STEP-10, STEP-16 |
| FR-009 | STEP-07, STEP-10, STEP-11, STEP-16 |
| FR-010 | STEP-11, STEP-16 |
| FR-011 | STEP-11 |
| FR-014 | STEP-08, STEP-09, STEP-11 |
| FR-015 | STEP-08, STEP-11, STEP-17 |
| FR-016 | STEP-08, STEP-11, STEP-17 |
| FR-017 | STEP-10, STEP-11, STEP-16 |
| FR-018 | STEP-15, STEP-17 |
| FR-019 | STEP-09 |
| FR-020 | STEP-07, STEP-09, STEP-10, STEP-15 |
| FR-021 | STEP-10 |
| UC-001-AC1, AC3, AC4 | STEP-07 |
| UC-001-AC5, AC6 | STEP-08 |
| UC-001-AC2, AC7, AC8 | STEP-09 |
| UC-002-AC1, AC2, AC3, AC8, AC11, AC12 | STEP-10 |
| UC-002-AC4, AC6, AC7, AC9, AC10, AC13, AC15, AC16 | STEP-11 |
| UC-002-AC5, AC14 | STEP-15 |
| UC-003-AC2, AC5, AC9, AC12 | STEP-16 |
| UC-003-AC7, AC10, AC11 | STEP-17 |
| UC-003-AC1, AC3, AC4, AC6, AC8 | — (moved to UC-002, spec 2.0) |
| UC-004-AC1, AC2, AC6, AC7, AC8, AC9, AC10, AC12 | STEP-08 |
| UC-004-AC3, AC4, AC5, AC11, AC13, AC14 | STEP-11 |
| NFR-001 | STEP-07 |
| NFR-002 | STEP-02 |
| NFR-003 | STEP-07, STEP-09, STEP-10, STEP-12, STEP-15, STEP-16 |
| NFR-004 | STEP-07, STEP-08, STEP-09, STEP-10, STEP-15, STEP-16 |
| NFR-005 | STEP-07 |
| NFR-006 | STEP-08, STEP-09 |
| NFR-007 | STEP-12, STEP-18 |
| NFR-008 | STEP-13, STEP-14, STEP-18, STEP-19 |
| NFR-009 | STEP-07 |
| NFR-010 | STEP-02, STEP-05, STEP-13 |
| NFR-011 | STEP-04, STEP-05, STEP-13, STEP-18 |
| NFR-012 | STEP-02, STEP-07 (mypy strict in every later step) |

## Discovered work

## Changelog
| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-11-03 | Initial plan; Milestone-1 cut and learning steps decided by the owner |
| 0.2 | 2026-11-05 | ADR-008 supersedes ADR-004 (build backend `uv_build`): STEP-01, STEP-02 and STEP-06 updated |
