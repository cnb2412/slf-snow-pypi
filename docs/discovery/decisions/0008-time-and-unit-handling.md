# ADR-0008: Time and Unit Handling

## Status: Accepted

## Context
US-004 / D4 / NFR-004 require every measurement to carry its unit in the source's
**native** unit and a **UTC** timestamp, with no conversion and no label
translation. The live API complicates both: timestamps are inconsistent —
`/measurements` returns UTC with a `Z` suffix (`2026-06-09T19:00:00Z`) while
`daily-snow` returns a naive midnight datetime with no offset
(`2026-06-08T00:00:00`) — and **no endpoint returns units at all**; units are
only implied by field-name conventions. Open question: how does the library
deliver UTC timestamps and native units from this?

## Decision
Normalise every `measure_date` to a timezone-aware UTC `datetime`: parse the `Z`
form as UTC, and interpret the naive `daily-snow` date as a UTC date-at-midnight
(the reporting day). Supply units and human labels from a **static
field-metadata catalog** maintained in the library, keyed by source parameter id:

| Parameter(s) | Unit |
| --- | --- |
| `HS`, `HN_1D` | cm |
| `TA_30MIN_MEAN`, `TSS_30MIN_MEAN`, `TS0/25/50/100_30MIN_MEAN` | °C |
| `RH_30MIN_MEAN` | % |
| `VW_30MIN_MEAN`, `VW_30MIN_MAX` | m/s |
| `DW_30MIN_MEAN`, `DW_30MIN_SD` | ° |
| `RSWR_30MIN_MEAN` | W/m² |
| `RR_10MIN_SUM` | mm |

No unit conversion and no station-label translation are performed (NFR-004, D7);
each `Measurement` carries the native unit string and its UTC `timestamp`.

Rationale: consumers (Home Assistant) localise and convert per their own
settings, so the library's job is faithful, labelled passthrough. Because the API
omits units, a maintained catalog is the only source; centralising it keeps
[ADR-0003](0003-generic-measurement-model.md)'s generic model unit-aware without
hard-coding units at call sites.

## Consequences
**Positive:** Correct, comparable UTC timestamps despite mixed source formats;
every value labelled with its native unit (US-004); presentation-neutral
(NFR-004).

**Negative:** The unit catalog is hand-maintained and must track new/renamed
source parameters; a parameter missing from the catalog needs a defined fallback
(e.g. unit `None`).

**Effort to change later:** Low. The catalog and the timestamp normaliser are
isolated tables/functions.
