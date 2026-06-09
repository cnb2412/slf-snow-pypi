# ADR-0009: Public API Surface

## Status: Accepted

## Context
US-001 (list stations), US-002 (one station's current measurements) and US-003
(several stations at once) define the operations the library must expose, and
NFR-005 requires a typed, ergonomic public surface. Open question: what is the
concrete shape of the client and its methods / return types?

## Decision
Expose a single async-context-manager client, `SlfClient`
([ADR-0001](0001-async-http-client-foundation.md)), with three coroutine methods:

- `list_stations() -> list[Station]` — full IMIS station list with code, label,
  canton, elevation, coordinates and type (US-001).
- `get_station_measurements(code: str) -> StationReading` — one station's current
  reading; raises `StationNotFoundError` on an unknown code (US-002, US-006).
- `get_measurements(codes: Iterable[str]) -> dict[str, StationReading]` — batch
  result keyed by station code and addressable by code (US-003), implemented per
  [ADR-0006](0006-multi-station-batch-strategy.md).

`Station`, `StationReading` and `Measurement`
([ADR-0002](0002-domain-data-model-technology.md),
[ADR-0003](0003-generic-measurement-model.md)) and the exception types
([ADR-0007](0007-error-and-exception-taxonomy.md)) are exported via a curated
`slf_snow.__all__`.

Rationale: three methods map one-to-one onto the three user stories; returning a
dict keyed by code makes US-003 results directly addressable; a curated `__all__`
gives consumers a clear, typed entry point (NFR-005).

## Consequences
**Positive:** Minimal, story-aligned surface that is easy to type-check and
document; a clear single import point.

**Negative:** A small public surface may not anticipate every future need (e.g.
server-side filtering); deliberately deferred to keep MVP scope minimal.

**Effort to change later:** Low for additive methods; renaming or changing return
types would be breaking, so the model and return shapes above are the commitment
point.
