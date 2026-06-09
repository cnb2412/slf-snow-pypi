# ADR-0004: Representing Missing vs. Zero

## Status: Accepted

## Context
FR-5 / US-005 / D5 require that a missing measurement be distinct from a genuine
reading of `0`. The live payloads make this concrete: a single station record
contains both real zeros (`HS: 0.0`) and explicit nulls (`TS100_30MIN_MEAN:
null`), and a station may omit whole parameters (e.g. no precipitation sensor).
Open question: how is "absent" represented so it can never be confused with a
real `0`?

## Decision
A source field that is `null` or absent yields **no `Measurement`** in the
`StationReading` collection ([ADR-0003](0003-generic-measurement-model.md));
looking it up returns absent / `None`. A numeric value — including `0.0` — yields
a present `Measurement` whose `value` is that number. The decoder never coerces
`null`/absent to `0`, and never drops a genuine `0`. "Not found" for an unknown
station is a separate concern handled as a typed error
([ADR-0007](0007-error-and-exception-taxonomy.md)), not as an absent value.

Rationale: conflating "no measurement" with "0 cm" would fabricate readings and
mislead end users (FR-5). Omitting absent parameters from the collection makes
absence unrepresentable-as-zero by construction.

## Consequences
**Positive:** Absent and zero are structurally distinct (US-005); no fabricated
readings; aligns with one-sensor-per-reported-measurement (absent ⇒ no sensor).

**Negative:** Consumers must handle the absent case explicitly (membership check
or `None`) rather than reading a default.

**Effort to change later:** Low. The rule lives entirely in the JSON decoder.
