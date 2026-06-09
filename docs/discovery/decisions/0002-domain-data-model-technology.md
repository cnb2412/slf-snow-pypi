# ADR-0002: Domain Data Model Technology

## Status: Accepted

## Context
US-001/US-002/US-004 require typed, inspectable objects for stations and
measurements, and the package must ship as a **typed** distribution (`py.typed`)
so consumers get type-checker support (NFR-005). Open question: which technology
backs the domain models — a runtime-validation library such as pydantic, or
stdlib constructs (dataclasses / `TypedDict` / `attrs`)?

## Decision
Model the domain with **frozen stdlib dataclasses**
(`@dataclass(frozen=True, slots=True)`) and explicit type hints; do **not** add a
runtime-validation dependency. The only runtime dependency stays `aiohttp`.
Decoding the JSON payload into models — including null handling per
[ADR-0004](0004-missing-vs-zero.md) and timestamp/unit derivation per
[ADR-0008](0008-time-and-unit-handling.md) — is hand-written at the response
boundary.

Rationale: the payloads are small and well understood (see the verified field
set in `../03_requirements.md` traceability and ADR-0005), so a validation
framework adds dependency weight and version coupling for little benefit. Frozen
dataclasses are immutable (safe to share across an async polling loop), hashable,
fully typed, and free of third-party runtime constraints — the leanest option
that satisfies NFR-005. `TypedDict` was rejected because it offers no instance
behaviour or immutability; pydantic was rejected to keep the dependency surface
minimal for a library a Home Assistant integration will embed.

## Consequences
**Positive:** Minimal dependency surface (good for an embedded HA integration);
immutable, hashable, fully typed models; no third-party version coupling.

**Negative:** Parsing/validation is hand-rolled and must be unit-tested rather
than delegated to a framework.

**Effort to change later:** Moderate. Internals could move to pydantic/attrs, but
because the dataclasses are public return types, changing them is a breaking API
change for consumers.
