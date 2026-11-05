# ADR-007: Query period for single-station measurements

Status: Accepted | Date: 2026-11-02

## Context
FR-021 returns the current measured record of one station. The API's
per-station resources (`/study-plot/station/{code}/measurements`,
`/imis/station/{code}/measurements`) require a query period
`period_in_days` of 1, 3 or 7; other values are rejected with HTTP 422. The
period decides how old a record may be and still be returned, because the
current record is selected only among the records the API returns (glossary
"Current record"); a maximum age is excluded by the spec. Observed 2026-11-02:
the periods are rolling windows ending now (IMIS `DAV2`, 1 day: 47 records
every 30 minutes); a known study plot without a record in the period
(`4UL0`, last reading the day before) is answered with HTTP 404 `NO_DATA`,
which FR-010 treats as "no record"; the all-stations resources of FR-018 offer
no period and return the last 24 hours.

## Decision drivers
- FR-021, FR-010: current record or "no record" for a single station.
- FR-018: the all-stations variant covers 24 hours.
- Brief constraint and NFR-004: do not load the SLF infrastructure.

## Considered options
1. 1 day
2. 3 days
3. 7 days

## Decision
We request single-station measurements with a period of 1 day, because it is
the same window as the all-stations variant (FR-018), so a station has a
current record in both or in neither, and it transfers the least data (brief
load constraint).

## Consequences
- **Positive:** Single-station and all-stations queries agree; smallest
  responses (IMIS about 48 records instead of about 336 for 7 days).
- **Negative:** A study plot that skipped its daily reading returns "no record",
  although an older value would be available with a longer period.
- **Follow-ups:** The period is a fixed internal constant, not configurable;
  revisit if consumers need older values (would need a spec change for a
  maximum age).

## Rejected options
**3 days:** Tolerates a skipped study-plot reading, but the single-station query
would return records that the all-stations query omits, and IMIS responses are
three times as large.

**7 days:** As 3 days, with about 336 IMIS records per call.

## Sources
- https://measurement-api.slf.ch/ (OpenAPI 1.1.0; observations 2026-11-02)
