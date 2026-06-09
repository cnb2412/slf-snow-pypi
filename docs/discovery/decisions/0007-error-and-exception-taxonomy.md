# ADR-0007: Error and Exception Taxonomy

## Status: Accepted

## Context
US-006 requires an explicit, predictable "not found" outcome for an unknown
station code, and NFR-002 requires that transport/protocol failures (timeouts,
connection errors, non-success status, unparseable payloads) surface as explicit,
typed errors that are distinct from US-006's "not found" and from US-005's
"absent value", without crashing the host process. The live API returns HTTP
`400` with body `{"code":"STATION_NOT_FOUND","status":400}` for an unknown
station, and documents `422` validation responses on per-station endpoints. Open
question: what exception hierarchy expresses these outcomes?

## Decision
Define a typed exception hierarchy rooted at `SlfSnowError`:

- `StationNotFoundError(SlfSnowError)` — raised on HTTP `400` carrying
  `STATION_NOT_FOUND` (carries the offending code). This is the US-006 outcome.
- `SlfTransportError(SlfSnowError)` and subtypes for failure modes: timeout,
  connection failure, and unexpected non-2xx status. Unparseable / schema-invalid
  payloads surface as a distinct `SlfResponseError`. These wrap the underlying
  `aiohttp` exception as `__cause__`.

Raw `aiohttp` exceptions never escape the public API. "Not found" is always a
raised `StationNotFoundError`, never a silent empty value; an **absent
measurement** is never an exception but `None` / omission
([ADR-0004](0004-missing-vs-zero.md)). In the batch path
([ADR-0006](0006-multi-station-batch-strategy.md)), a requested code missing from
the all-stations data is reported per the same not-found contract.

Rationale: a single rooted hierarchy lets consumers `except SlfSnowError` broadly
or target specific failures; wrapping keeps the library's surface stable
regardless of the HTTP backend (NFR-002) and guarantees the host process is never
crashed by a leaked transport error.

## Consequences
**Positive:** Deterministic, catchable error paths (US-006); clear separation of
not-found vs transport vs absent (NFR-002); backend-agnostic public errors.

**Negative:** Requires mapping HTTP statuses/bodies to types and disciplined
wrapping at every call site.

**Effort to change later:** Low. New failure categories slot under the existing
root without breaking `except SlfSnowError` consumers.
