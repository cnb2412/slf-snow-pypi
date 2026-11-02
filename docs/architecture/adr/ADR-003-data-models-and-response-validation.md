# ADR-003: Data models and response validation

Status: Accepted | Date: 2026-10-31

## Context
The package turns API responses into typed objects (station, study-plot record,
IMIS record, modeled record). It must check only the in-scope fields for
presence and type and ignore all others (FR-016), return null values as `None`
(FR-009), return timezone-aware UTC timestamps (FR-008), and keep measured and
modeled records distinguishable (FR-007). Home Assistant's library guide
recommends mirroring the API's names and doing minimal processing. Every
runtime dependency must be compatible with Home Assistant's pins (e.g.
`pydantic==2.14.1`, `mashumaro>=3.17.0`).

## Decision drivers
- FR-016, FR-009, FR-008: validation of in-scope fields, empty values, UTC.
- FR-007: measured and modeled records are distinguishable.
- FR-014: validation failures surface as package errors.
- Constraint NFR-010: OSI-approved runtime dependencies.
- Constraint NFR-012: fully typed public data types.

## Considered options
1. Immutable standard-library dataclasses with own validation of in-scope fields
2. pydantic v2 models
3. mashumaro dataclasses
4. Raw dictionaries typed as `TypedDict`, without validation

## Decision
We use immutable standard-library dataclasses, one type per record kind, with
own validation of the in-scope fields, because only four small types with a
fixed list of fields are needed (FR-016), it adds no runtime dependency that
could conflict with Home Assistant's pins (NFR-010, G-06), and the types are
fully annotated (NFR-012). Field names mirror the API's meaning; units are not
converted.

## Consequences
- **Positive:** aiohttp remains the only runtime dependency; public types are
  plain, typed and immutable; validation errors are mapped to *invalid response*
  in one place.
- **Negative:** Validation and timestamp parsing are written and tested by hand;
  if the data model grows significantly, this becomes more effort than a
  library.
- **Follow-ups:** One parsing function per resource that checks in-scope fields
  and raises *invalid response*; separate types for measured and modeled
  records (FR-007); tests per in-scope field for missing, null and wrong type.

## Rejected options
**pydantic v2:** Convenient validation, but a large dependency with a compiled
core that Home Assistant pins exactly; pydantic types would leak into the public
interface.

**mashumaro:** Lighter and common in Home Assistant libraries, but not needed
for four small types; worth reconsidering if the data model grows.

**TypedDict without validation:** Violates FR-016 (no type check) and FR-007
(measured and modeled records are not distinguishable at runtime).

## Sources
- https://contributors.home-assistant.io/core/integrations/api-library/
- https://github.com/home-assistant/core/blob/dev/homeassistant/package_constraints.txt
