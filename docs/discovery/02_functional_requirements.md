# Functional Requirements — slf-snow (MVP)

> Scope of this document: **functional analysis only**. It defines *what* the
> library must do from a domain perspective. It deliberately makes **no
> technology decisions** (architecture, data structures, frameworks); those are
> handled in a later technical spec.
>
> Source: derived from `01_raw_idea.md` and the public SLF measurement API
> domain (`https://measurement-api.slf.ch`).

## 1. Domain Glossary

- **SLF / WSL** — Swiss research institute operating the snow / avalanche
  measurement network.
- **IMIS station** — an **automated** measurement station (synonymous with
  "automated station" in `01_raw_idea.md`).
- **Study-plot station** — a **manually** observed station. Out of scope for MVP.
- **Station code** — stable, unique identifier of a station.
- **HS** — snow depth: total height of the snowpack, in centimetres.
- **HN24** — new snow over the last 24 hours, in centimetres.
- **Measurement timestamp** — the UTC time a value was measured / is valid for.

## 2. Functional Requirements

- **FR-1 — Station discovery.** Return the full list of automated (IMIS)
  stations. Each station includes enough metadata to identify and locate it for
  an end user: station code, human-readable name/label, canton, elevation,
  geographic coordinates and station type.
- **FR-2 — Current measurements.** For a given station (by code), return **all
  current measurements the station reports** — snow depth (HS) and new snow over
  the last 24 h (HN24) as the primary values, plus any accompanying weather
  readings the station provides (e.g. air temperature, wind, humidity). Each
  measurement is an individual, separately addressable value.
- **FR-3 — Multiple stations.** A consumer can obtain current measurements for
  several stations in one logical request.
- **FR-4 — Value metadata.** Every returned measurement carries its **unit**
  (e.g. cm, °C, m/s) and its **measurement timestamp** (UTC), so consumers can
  render values correctly and judge their freshness.
- **FR-5 — Missing vs. zero.** A missing/unavailable measurement is represented
  as *absent* (no value), clearly distinct from a real reading of `0 cm`.
- **FR-6 — Unknown station.** Requesting an unknown/invalid station code yields
  an explicit, predictable "not found" outcome — not a silent empty value.
- **FR-7 — Per-station field availability.** A station yields only the
  measurements its sensors provide; no measurement type is mandatory. Fields a
  station does not report are simply absent (per FR-5) — e.g. a wind-only station
  yields wind values and no snow values, which is not an error. (In Home
  Assistant this maps to one sensor per reported measurement; absent fields
  produce no sensor.)

## 3. MVP Functional Boundaries

### In scope
- Automated **IMIS** stations only.
- **All measurements a station reports** — snow values (HS, HN24) are the
  primary use case; accompanying weather readings (temperature, wind, humidity,
  radiation, precipitation) come along for free.
- **Current / latest** values only.
- Station listing (all) + value retrieval by station code.

### Out of scope (MVP)
- Manual **study-plot** stations.
- Historical data / time ranges / time series.
- Server-side search or filtering beyond "all stations" and "by code".
- Unit conversion (values stay in the source's native units) and localisation
  of names.
- Local persistence, caching, or scheduling of refreshes.
- Avalanche bulletins, danger levels, warnings, forecasts.

## 4. Key User Journeys

### Journey A — Pick my local station (discovery)
1. A developer (or, via the future HA integration, an end user) requests the
   list of automated stations.
2. They receive each station's code, name, canton, elevation and coordinates.
3. They identify the station code(s) closest to where they live or ski.

*Outcome:* the consumer knows which station code(s) to monitor.

### Journey B — Check current conditions (core)
1. With one or more known station codes, the consumer requests current
   measurements.
2. For each station they receive all reported measurements — snow depth and new
   snow plus any weather readings — each with its unit and a measurement
   timestamp.
3. The values are shown to the end user (e.g. one Home Assistant sensor per
   measurement).

*Outcome:* the end user sees current conditions at their station(s) — primarily
how much snow lies and how much fell in the last 24 h, alongside any weather
values the station reports.

### Journey C — Keep values up to date (refresh) *(secondary)*
1. The HA integration re-runs Journey B on a regular interval.
2. Each refresh returns the latest values and timestamps; stale or missing
   readings are recognisable via FR-4 / FR-5.

*Outcome:* sensors reflect the latest published measurements. No history is kept —
a refresh only replaces the current value.

## 5. Functional Decisions

> These functional questions were raised during discovery and have all been
> **accepted** as the MVP approach. Each is stated as a decision with its
> rationale.

**D1 — Meaning of a "current" value.**
- *Decision:* return the **most recent available reading** per station for each
  reported measurement, together with its timestamp.
- *Rationale:* consumers want present conditions; history is an explicit
  non-goal, and a timestamp lets them detect staleness themselves.

**D2 — Station metadata exposed by discovery.**
- *Decision:* code, name/label, canton, elevation, coordinates and station type.
- *Rationale:* the HA integration needs a human-readable, locatable picker; the
  code alone is not user-friendly, and elevation / coordinates / type help users
  choose and group stations.

**D3 — List all IMIS stations (including non-snow ones).**
- *Decision:* list **all** IMIS stations and return whatever measurements each
  one reports; expose the station type so consumers can group or filter.
- *Rationale:* with one sensor per measurement, a non-snow station simply
  produces non-snow sensors — no special-casing needed, and no data is hidden.

**D4 — Units.**
- *Decision:* keep each measurement in the source's **native unit** (cm for snow,
  °C for temperature, m/s for wind, % for humidity, …) and label it explicitly;
  do not convert.
- *Rationale:* conversion is lossy and is a presentation concern best left to the
  consumer (Home Assistant localises / converts per its own settings).

**D5 — Missing data.**
- *Decision:* return the value as **absent / None** with no error; reserve errors
  for genuine failures (unknown station, transport failure).
- *Rationale:* "no measurement" and a real `0` reading are functionally
  different; conflating them misleads users (FR-5).

**D6 — Querying several stations at once.**
- *Decision:* support current measurements for a **set of station codes** in one
  logical operation.
- *Rationale:* HA users typically track a few favourite stations; one operation
  is simpler and lighter than many.

**D7 — Station name language.**
- *Decision:* use the station **label as provided**; no translation in MVP.
- *Rationale:* localisation adds scope with little MVP value; names are mostly
  place-based.

**D8 — Time range / amount of data.**
- *Decision:* expose **only the current value**; no date ranges or series.
- *Rationale:* history is an explicit non-goal and keeps the surface minimal.

## 6. Items to Confirm Later (not blocking MVP)

- **Update frequency** of the source data is undocumented; choose a conservative
  refresh cadence for the HA integration once observed.
- The exact mapping of each measurement to source endpoints/fields (HS and the
  weather readings from `/measurements`, HN24 from `/daily-snow`, precipitation
  from the precipitation endpoint) is an implementation detail for the technical
  spec, intentionally left out of this functional doc.
