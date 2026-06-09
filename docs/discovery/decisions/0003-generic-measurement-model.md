# ADR-0003: Generic Per-Parameter Measurement Model

## Status: Accepted

## Context
FR-7 / US-007 require that a station expose only the measurements its sensors
provide, with no error for absent fields, and D3 lists all IMIS stations
regardless of which sensors they carry. The live API confirms this is real: the
precipitation series reports only ~92 of 207 stations, and individual fields can
be `null`. US-002/US-004 require each measurement to carry a value, a unit and a
timestamp. Open question: model a station reading as a **fixed struct** of named
fields (HS, HN24, temperature, …) or as a **generic collection** of measurements
keyed by parameter?

## Decision
Use a generic value object `Measurement(parameter, value, unit, timestamp)` and
aggregate a station's current readings in a `StationReading` that maps a
parameter identifier → `Measurement`. Only parameters the station actually
reports are present (see [ADR-0004](0004-missing-vs-zero.md)); there are no
mandatory fields. Parameter identifiers follow the source field names (e.g. `HS`,
`HN_1D`, `TA_30MIN_MEAN`, `RR_10MIN_SUM`); their units and human labels come from
the field-metadata catalog in
[ADR-0008](0008-time-and-unit-handling.md). Convenience accessors for the primary
snow values (HS, HN24) may be layered on top without changing the underlying
generic shape.

Rationale: a fixed struct would force every station into one shape and require
special-casing wind-only or precipitation-only stations; a keyed collection maps
one-to-one onto "one Home Assistant sensor per reported measurement" (FR-7) and
absorbs new source parameters without a model change.

## Consequences
**Positive:** Cleanly supports heterogeneous stations (US-007); maps directly to
per-measurement HA sensors; tolerant of new/removed source parameters.

**Negative:** Less compile-time discoverability than named attributes — consumers
look up by parameter id; primary values (HS/HN24) need convenience accessors to
stay ergonomic.

**Effort to change later:** Moderate. Adding typed convenience accessors is
additive; replacing the generic collection with a fixed struct would be a
breaking change.
