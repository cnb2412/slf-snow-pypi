# Requirements — slf-snow (MVP)

> Derived from `01_raw_idea.md` (project concept) and
> `02_functional_requirements.md` (functional analysis & decisions). This
> document turns the functional requirements (FR-1…FR-7) and decisions (D1…D8)
> into structured, testable requirements.
>
> **Traceability.** Every user story (US-NNN) and non-functional requirement
> (NFR-NNN) has a stable ID so downstream Architecture Decision Records (ADRs)
> can cite the requirement that drives them. Each story lists the functional
> requirements / decisions it traces back to.
>
> Scope note: this document makes **no technology/architecture decisions** —
> those belong in the ADRs that consume these requirements as drivers.

## 1. Actors

- **Integrator** — a Python developer consuming `slf-snow` in their own code (the
  primary actor for every story below).
- **HA integration** — the planned Home Assistant integration; a specific
  Integrator whose end users watch snow conditions at home.
- **End user** — the person (skier, homeowner) who ultimately reads the values
  via the HA integration; the value recipient, not a direct API user.

## 2. User Stories

### US-001 — List all stations
*As an* integrator, *I want* to retrieve the full list of automated (IMIS)
stations with their identifying metadata, *so that* I can present a station
picker and let users choose which station(s) to monitor.

**Acceptance criteria**
- *Given* the SLF API is reachable, *when* I request the station list, *then* I
  receive every automated (IMIS) station.
- *Given* a station in the result, *when* I inspect it, *then* it exposes station
  code, name/label, canton, elevation, geographic coordinates and station type.
- *Given* a station name as published by the source, *when* it is returned,
  *then* the label is passed through unchanged (no translation).

*Traces to:* FR-1, D2, D3, D7 · Journey A.

### US-002 — Get current measurements for a station
*As an* integrator, *I want* to fetch all current measurements a station reports
for a given station code, *so that* I can display its current conditions (snow
and accompanying weather).

**Acceptance criteria**
- *Given* a valid station code, *when* I request its current measurements,
  *then* I receive the most recent reading for each measurement the station
  reports.
- *Given* a snow-reporting station, *when* I request current measurements,
  *then* snow depth (HS) and new snow 24 h (HN24) are included.
- *Given* any returned measurement, *when* I inspect it, *then* it carries a
  value, a unit and a measurement timestamp.

*Traces to:* FR-2, D1, D4 · Journey B.

### US-003 — Get measurements for several stations at once
*As an* integrator, *I want* to fetch current measurements for multiple station
codes in a single operation, *so that* I can refresh all monitored stations
efficiently.

**Acceptance criteria**
- *Given* several valid station codes, *when* I request current measurements for
  all of them in one call, *then* I receive a result for each requested station.
- *Given* the result set, *when* I look up a specific station, *then* its values
  are addressable by its station code.

*Traces to:* FR-3, D6 · Journey C.

### US-004 — Trust value units and freshness
*As an* integrator, *I want* every measurement to carry its unit and a UTC
measurement timestamp, *so that* I can render values correctly and detect stale
data.

**Acceptance criteria**
- *Given* a returned measurement, *when* I read its metadata, *then* it provides
  the measurement's unit (in the source's native unit, e.g. cm / °C / m·s⁻¹) and
  a timestamp expressed in UTC.
- *Given* the source has not published a newer reading, *when* I re-fetch, *then*
  the timestamp still reflects the original measurement time, so staleness is
  detectable.

*Traces to:* FR-4, D1, D4.

### US-005 — Distinguish "no data" from zero
*As an* integrator, *I want* missing measurements represented as absent (not as
`0`), *so that* I never display a fabricated reading.

**Acceptance criteria**
- *Given* a station does not report a particular measurement, *when* I read that
  field, *then* it is absent / None.
- *Given* a station reports a genuine reading of `0`, *when* I read that field,
  *then* the value is `0` and is distinguishable from absent.

*Traces to:* FR-5, D5.

### US-006 — Predictable handling of unknown stations
*As an* integrator, *I want* an explicit "not found" outcome when I request an
unknown station code, *so that* I can handle the error path deterministically.

**Acceptance criteria**
- *Given* an unknown / invalid station code, *when* I request its measurements,
  *then* I receive an explicit "not found" result rather than a silent empty
  value.

*Traces to:* FR-6.

### US-007 — Stations expose only what they measure
*As an* integrator, *I want* each station to return only the measurements its
sensors provide, with no error for absent fields, *so that* every station
(including non-snow ones) maps cleanly to one sensor per reported measurement.

**Acceptance criteria**
- *Given* a wind-only station (no snow sensors), *when* I request its current
  measurements, *then* I receive its wind values and no snow values, without an
  error.
- *Given* a station with only a subset of sensors, *when* I request measurements,
  *then* only the reported measurements are returned.

*Traces to:* FR-7, D3, D5.

## 3. Non-Functional Requirements (Architecture Constraints)

**NFR-001 — Performance & efficiency.**
- The client is **asynchronous / non-blocking** so consumers (notably the HA
  integration's polling loop) are never blocked.
- Fetching several stations (US-003) minimises round-trips.
- All network calls honour a configurable timeout.

**NFR-002 — Reliability & error handling.**
- Transport/protocol failures (timeouts, connection errors, non-success HTTP
  status, unparseable payloads) surface as explicit, typed errors — distinct
  from the "not found" of US-006 and the "absent value" of US-005.
- The library must not crash the host process on source-side failures.

**NFR-003 — Security.**
- All traffic over **HTTPS** only.
- No credentials or API key are used or stored (the source is public).
- Caller-supplied input (e.g. station codes) is safely encoded when building
  requests — no request/URL injection.
- The client is a good API citizen (sane defaults, no aggressive polling) to
  respect the source's terms.

**NFR-004 — Localisation & presentation neutrality.**
- Values are returned in the source's **native units** (no conversion);
  conversion and locale formatting are the consumer's responsibility.
- Station labels are passed through **as published** (no translation).
- Timestamps are returned in **UTC**; timezone presentation is the consumer's
  responsibility.

**NFR-005 — Compatibility & distribution.**
- Targets **Python ≥ 3.13**.
- Ships as a **typed** package (inline type hints, marked typed) for type-checker
  support in consuming code.
- Distributed as the open-source **`slf-snow`** package on PyPI under MIT.

**NFR-006 — Testability.**
- The design allows the functional behaviour to be tested **without hitting the
  live API** (the HTTP boundary is substitutable), so the acceptance criteria
  above can be verified with deterministic mocked/recorded responses.

## 4. Out of Scope (MVP)

Per `02_functional_requirements.md` §3: no manual (study-plot) stations, no
historical/time-series data or date ranges, no server-side search/filtering
beyond "all" and "by code", no unit conversion or label localisation, no local
persistence/caching/scheduling, and no avalanche bulletins, danger levels or
forecasts.

## 5. Traceability Matrix

| User story | Functional source (02) | Journey | Likely ADR driver |
| --- | --- | --- | --- |
| US-001 | FR-1, D2, D3, D7 | A | station listing & model |
| US-002 | FR-2, D1, D4 | B | measurement model, "current" semantics |
| US-003 | FR-3, D6 | C | batch fetch strategy |
| US-004 | FR-4, D1, D4 | B / C | value+metadata model, time handling |
| US-005 | FR-5, D5 | B | optional / None modelling |
| US-006 | FR-6 | B | error taxonomy |
| US-007 | FR-7, D3, D5 | B | per-station field mapping |

NFR-001…NFR-006 are cross-cutting and apply across all stories as drivers for the
architecture ADRs.
