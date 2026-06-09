# ADR-0005: Endpoint Composition and "Current" Reduction

## Status: Accepted

## Context
US-002 asks for "all current measurements a station reports", and D1/D8 define
"current" as the most recent value with no history. The live IMIS API offers no
single current-snapshot endpoint; instead a station's data is split across three
endpoints, each returning a **time series**:

- `GET /public/api/imis/station/{code}/measurements` — `HS` plus weather
  (`TA_30MIN_MEAN`, `RH_30MIN_MEAN`, `TSS_30MIN_MEAN`, `TS0/25/50/100_30MIN_MEAN`,
  `RSWR_30MIN_MEAN`, `VW_30MIN_MEAN`, `VW_30MIN_MAX`, `DW_30MIN_MEAN`,
  `DW_30MIN_SD`) at 30-minute resolution.
- `GET /public/api/imis/daily-snow` — `HN_1D` (= HN24) and a daily `HS`; **no
  per-station path**, so it is filtered by `station_code` client-side.
- `GET /public/api/imis/station/{code}/measurements-precipitation` —
  `RR_10MIN_SUM`.

All accept `period_in_days ∈ {1, 3, 7}` (default 1). Open question (the §6 "Items
to Confirm Later"): how does the library assemble one current reading per station
from these series?

## Decision
Compose the three endpoints into a single `StationReading`. Source the primary
and weather values from `/measurements`, HN24 from `daily-snow.HN_1D`, and
precipitation from `measurements-precipitation.RR_10MIN_SUM`. For each series,
reduce to the **single most recent row by `measure_date`** (D1); merge the
resulting parameters into one `StationReading`, each `Measurement` keeping its own
source `measure_date` ([ADR-0008](0008-time-and-unit-handling.md)). Request
`period_in_days=1` for the MVP — the smallest window that reliably contains the
latest reading. HS is taken from the sub-daily `/measurements` series (fresher);
the daily-snow `HS` is used only alongside `HN_1D` where needed.

Rationale: this is the only way to deliver "all current measurements" given the
API's split, series-based shape, while honouring the history non-goal (D8) by
discarding all but the latest row of each series.

## Consequences
**Positive:** Delivers a complete per-station current reading (US-002, US-007)
from the real API; keeps the "current-only" contract (D1/D8).

**Negative:** Up to three requests per single station; daily-snow must be fetched
whole and filtered by code; HN24 freshness is bounded by the daily cadence.

**Effort to change later:** Low–moderate. If SLF later adds a snapshot or
per-station daily endpoint, only the composition/reduction layer changes; the
returned model is unaffected. Batch efficiency is addressed in
[ADR-0006](0006-multi-station-batch-strategy.md).
