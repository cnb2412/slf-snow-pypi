# slf-snow — Documentation

`slf-snow` is an asynchronous Python client for the SLF / WSL snow measurement
API (automated **IMIS** stations). It exposes typed, current measurements (snow
depth, new snow and accompanying weather readings) and is built to serve as the
foundation for a future Home Assistant integration. This page is the entry point
to the project's documentation and tracks how far the MVP has been implemented.

## Document index

| Document | Purpose |
| --- | --- |
| [discovery/01_raw_idea.md](discovery/01_raw_idea.md) | Project concept, vision, scope and non-goals (Phase 1). |
| [discovery/02_functional_requirements.md](discovery/02_functional_requirements.md) | Functional requirements FR-1…FR-7, functional decisions D1…D8, user journeys. |
| [discovery/03_requirements.md](discovery/03_requirements.md) | User stories US-001…US-007, NFR-001…NFR-006, traceability matrix. |
| [discovery/decisions/](discovery/decisions/README.md) | Architecture Decision Records (ADR-0001…ADR-0009) with traceability. |
| [specs/0001-requirements.md](specs/0001-requirements.md) | Technical spec for the client surface (`list_stations`, `get_station_measurements`). |
| [../CHANGELOG.md](../CHANGELOG.md) | Release notes (Keep a Changelog). |

### Architecture Decision Records

| ADR | Title |
| --- | --- |
| [0001](discovery/decisions/0001-async-http-client-foundation.md) | Async HTTP Client Foundation |
| [0002](discovery/decisions/0002-domain-data-model-technology.md) | Domain Data Model Technology |
| [0003](discovery/decisions/0003-generic-measurement-model.md) | Generic Per-Parameter Measurement Model |
| [0004](discovery/decisions/0004-missing-vs-zero.md) | Representing Missing vs. Zero |
| [0005](discovery/decisions/0005-endpoint-composition-and-current-reduction.md) | Endpoint Composition and "Current" Reduction |
| [0006](discovery/decisions/0006-multi-station-batch-strategy.md) | Multi-Station Batch Strategy |
| [0007](discovery/decisions/0007-error-and-exception-taxonomy.md) | Error and Exception Taxonomy |
| [0008](discovery/decisions/0008-time-and-unit-handling.md) | Time and Unit Handling |
| [0009](discovery/decisions/0009-public-api-surface.md) | Public API Surface |

## Implementation status

Legend: ✅ done · ◐ partial · ❌ open

### Public API surface (ADR-0009)

| API element | Location | Status |
| --- | --- | --- |
| `SlfClient` (async context manager) | `src/slf_snow/client.py` | ✅ |
| `get_station_measurements(code)` | `src/slf_snow/client.py` | ✅ |
| `list_stations()` | `src/slf_snow/client.py` | ✅ |
| `get_measurements(codes)` (batch) | `src/slf_snow/client.py` | ✅ |
| `Measurement`, `StationReading` models | `src/slf_snow/models.py` | ✅ |
| `Station` model (discovery metadata) | `src/slf_snow/models.py` | ✅ |
| Exception taxonomy | `src/slf_snow/exceptions.py` | ✅ |

### Functional requirements

| FR | Description | Status | Evidence |
| --- | --- | --- | --- |
| FR-1 | Station discovery (list IMIS stations + metadata) | ✅ | `list_stations()` → `list[Station]` from `GET /public/api/imis/stations`. |
| FR-2 | Current measurements (HS, HN24 + weather), each addressable | ✅ | `get_station_measurements` composes `/measurements` + `daily-snow.HN_1D` + precipitation. |
| FR-3 | Multiple stations in one logical request | ✅ | `get_measurements(codes)` fetches `/measurements`, `/measurements-precipitation`, `/daily-snow` once each concurrently, grouped by `station_code` (ADR-0006). |
| FR-4 | Value metadata: unit + UTC timestamp | ✅ | `Measurement.unit` from `_fields.FIELD_UNITS`; `to_utc` normalises. |
| FR-5 | Missing vs. zero | ✅ | `_emit_latest` skips `None`, preserves `0.0`. |
| FR-6 | Unknown station → explicit not found | ✅ | `StationNotFoundError` on 400 `STATION_NOT_FOUND`. |
| FR-7 | Per-station field availability (absent ≠ error) | ✅ | Precipitation 404 → absent via `absent_on_404`; `None` fields omitted. |

### User stories

| US | Description | Traces to | Status |
| --- | --- | --- | --- |
| US-001 | List all stations | FR-1 | ✅ |
| US-002 | Current measurements for a station | FR-2 | ✅ |
| US-003 | Measurements for several stations at once | FR-3 | ✅ |
| US-004 | Trust value units and freshness | FR-4 | ✅ |
| US-005 | Distinguish "no data" from zero | FR-5 | ✅ |
| US-006 | Predictable handling of unknown stations | FR-6 | ✅ |
| US-007 | Stations expose only what they measure | FR-7 | ✅ (single-station path) |

### Non-functional requirements

- **NFR-001 Performance** — ✅ async client with configurable timeout; the
  round-trip-minimising batch path (US-003 / ADR-0006) fetches the three
  all-stations endpoints concurrently, so cost is constant in the number of
  requested codes.
- **NFR-002 Reliability** — ✅ typed errors (`SlfTransportError`,
  `SlfResponseError`), raw `aiohttp` errors never leak.
- **NFR-003 Security** — ✅ HTTPS base URL, no credentials, query params encoded
  by `aiohttp`.
- **NFR-004 Presentation neutrality** — ✅ UTC timestamps, native units, no
  translation.
- **NFR-005 Compatibility/distribution** — ◐ `py.typed` shipped, Python ≥ 3.13
  targeted; PyPI release still pending.
- **NFR-006 Testability** — ✅ tests use `aioresponses` + fixtures, never the
  live API.

### Tests (`tests/test_client.py`)

| Test | Covers |
| --- | --- |
| `test_composes_endpoints_and_reduces_to_latest` | US-002, US-004 |
| `test_missing_field_is_absent_not_zero` | US-005, US-007 |
| `test_unknown_station_raises_not_found` | US-006 |
| `test_list_stations_returns_all_with_metadata` | US-001 |
| `test_list_stations_raises_transport_error_on_bad_status` | NFR-002 |
| `test_get_measurements_returns_reading_per_requested_code` | US-003 |
| `test_get_measurements_raises_not_found_for_unknown_code` | US-006, ADR-0007 |

## What's left for the MVP

- Publish the package to PyPI (NFR-005).
