# Architecture Decision Records — slf-snow (MVP)

This directory records the architecture decisions that resolve the open technical
questions raised by the requirements in
[`../03_requirements.md`](../03_requirements.md) (user stories US-001…US-007,
non-functional requirements NFR-001…NFR-006) and the functional decisions in
[`../02_functional_requirements.md`](../02_functional_requirements.md) (D1…D8).
Each ADR follows the format **Status / Context / Decision / Consequences**, cites
the requirement IDs that drive it, and is `Accepted` for the MVP. Endpoint-related
ADRs are grounded in the live SLF IMIS API
(`https://measurement-api.slf.ch/openapi.json`).

| # | Title | Status | Summary |
| --- | --- | --- | --- |
| [0001](0001-async-http-client-foundation.md) | Async HTTP Client Foundation | Accepted | aiohttp `ClientSession` with optional injected session, `async with` lifecycle, configurable timeout, HTTPS base URL. |
| [0002](0002-domain-data-model-technology.md) | Domain Data Model Technology | Accepted | Frozen stdlib dataclasses, no runtime-validation dependency; ship `py.typed`. |
| [0003](0003-generic-measurement-model.md) | Generic Per-Parameter Measurement Model | Accepted | `Measurement(parameter, value, unit, timestamp)` in a `StationReading` keyed by parameter; only reported parameters present. |
| [0004](0004-missing-vs-zero.md) | Representing Missing vs. Zero | Accepted | `null`/absent ⇒ omitted/`None`; numeric `0.0` ⇒ present measurement; never coerce. |
| [0005](0005-endpoint-composition-and-current-reduction.md) | Endpoint Composition and "Current" Reduction | Accepted | Compose `/measurements` + `daily-snow.HN_1D` + precipitation; reduce each series to the latest `measure_date`. |
| [0006](0006-multi-station-batch-strategy.md) | Multi-Station Batch Strategy | Accepted | Fetch the three all-stations endpoints once each, group by code, reduce to latest; constant round-trips. |
| [0007](0007-error-and-exception-taxonomy.md) | Error and Exception Taxonomy | Accepted | `SlfSnowError` root; `StationNotFoundError` (HTTP 400 / `STATION_NOT_FOUND`); typed transport errors; never leak raw aiohttp. |
| [0008](0008-time-and-unit-handling.md) | Time and Unit Handling | Accepted | Normalise timestamps to UTC; units from a static field-metadata catalog; no conversion or label translation. |
| [0009](0009-public-api-surface.md) | Public API Surface | Accepted | `SlfClient` async context manager: `list_stations`, `get_station_measurements`, `get_measurements`. |

## Traceability

| User story / NFR | Resolved by |
| --- | --- |
| US-001 — list stations | 0002, 0009 |
| US-002 — current measurements | 0003, 0005, 0008, 0009 |
| US-003 — several stations | 0006, 0009 |
| US-004 — units & freshness | 0003, 0008 |
| US-005 — no-data vs zero | 0004 |
| US-006 — unknown station | 0007 |
| US-007 — per-station fields | 0003, 0004, 0005 |
| NFR-001 — performance | 0001, 0006 |
| NFR-002 — reliability | 0007 |
| NFR-003 — security | 0001 |
| NFR-004 — presentation neutrality | 0008 |
| NFR-005 — compatibility/distribution | 0002, 0009 |
| NFR-006 — testability | 0001 |
