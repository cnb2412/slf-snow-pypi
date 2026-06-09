# ADR-0006: Multi-Station Batch Strategy

## Status: Accepted

## Context
US-003 / D6 require fetching current measurements for several station codes in
one logical operation, and NFR-001 requires minimising round-trips. The live API
offers all-stations variants of the three IMIS measurement endpoints
(`/measurements`, `/measurements-precipitation`, `/daily-snow`), each returning
data for every station in a single response. Open question: how does the batch
operation map onto these endpoints?

## Decision
For a multi-station request, fetch the **three all-stations endpoints once each**
(three requests total, independent of how many station codes were requested),
group the rows by `station_code`, reduce each group to its latest row per
[ADR-0005](0005-endpoint-composition-and-current-reduction.md), and return a
`dict[str, StationReading]` containing only the requested codes. The three
independent endpoint calls run concurrently via `asyncio.gather`. The
single-station path ([ADR-0009](0009-public-api-surface.md)) instead uses the
per-station endpoints, whose payloads are far smaller.

Rationale: the all-stations endpoints make batch cost **constant** (3 requests)
rather than proportional to the number of stations (3×N), directly serving
NFR-001; `asyncio.gather` overlaps the three independent fetches.

## Consequences
**Positive:** Constant, minimal round-trips for any batch size (NFR-001);
naturally efficient for the HA polling loop tracking a handful of stations.

**Negative:** Each all-stations response is large (~10k rows) even when few
stations are requested, trading bandwidth/parse cost for fewer requests; a
requested code absent from the all-stations data must be reconciled with the
not-found contract ([ADR-0007](0007-error-and-exception-taxonomy.md)).

**Effort to change later:** Low. A threshold could later switch small batches to
per-station fan-out without changing the public signature.
