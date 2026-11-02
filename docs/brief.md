# Product Brief: slf-snow-pypi

Status: Approved | Version: 1.3 | Date: 2026-11-02

## Problem statement
The Swiss WSL Institute for Snow and Avalanche Research (SLF) publishes snow
measurements (snow height, new snow, water equivalent of new snow) from its
manual study plots and automated IMIS stations through a public REST API
(https://measurement-api.slf.ch/). Anyone who wants to use this data from
Python today, for example in a Home Assistant integration, has to write the
HTTP access, the response parsing and the error handling themselves. Every
consumer repeats this work, and each one discovers the API's quirks
(nullable values, seasonally inactive stations, undocumented limits) on its own.
The owner searched for an existing async Python client or integration for this
API and found none.

## Target users
**Python integration developer.** Builds an application or home-automation
integration (the reference case is a Home Assistant integration developed by the
owner in a separate project) that should show current snow conditions at one or
more SLF stations. They want to call a library, get typed and documented snow
values, and handle a small, well-defined set of errors. They do not want to deal
with HTTP details or the raw response format.

## Value proposition
- One reusable, publicly installable package instead of every consumer writing
  its own HTTP layer.
- Consistent, documented behavior for missing values, unknown stations and API
  outages, so consumers stay stable when the upstream service misbehaves.
- Built for asynchronous consumers such as Home Assistant from the start.
- No existing alternative is known (see Assumptions).

## Key scenarios
- As an integration developer, I want to list all active SLF stations (study
  plots and IMIS) with name, coordinates, elevation and canton, so that my users
  can choose the station they care about.
- As an integration developer, I want to fetch the latest snow height, new snow
  (24h) and new-snow water equivalent of a chosen study-plot station, so that I
  can show current snow conditions.
- As an integration developer, I want to fetch the latest snow height of a
  chosen IMIS station and its modeled daily snow height and new snow, so that I
  can show current conditions for automated stations as well.
- As an integration developer, I want unknown stations, missing values and API
  outages reported in a clear, documented way, so that my application can react
  without crashing.

## Goals
- G-01: Consumers can list the active study-plot and IMIS stations with their
  metadata (code, name, coordinates, elevation, canton).
- G-02: Consumers can fetch the current snow values of a station: snow height,
  new snow (24h) and water equivalent (study plots); snow height (IMIS); and the
  modeled daily snow height and new snow.
- G-03: Consumers need no HTTP code of their own to use SLF snow data.
- G-04: API problems (outage, unknown station, missing or null values) produce
  clearly defined errors or empty values instead of unexpected failures.
- G-05: The package has a stable public release on PyPI.
- G-06: The package meets Home Assistant Core's requirements for integration
  libraries, including the Platinum-tier rules, so that the reference
  integration can be included in Home Assistant Core.

## Non-goals
- NG-01: Measurements other than snow (air and snow temperature, humidity, wind,
  radiation, precipitation).
- NG-02: Time series or history (the API's 1/3/7-day periods); only current
  values are offered.
- NG-03: Functionality beyond what the API provides, e.g. finding the nearest
  station to given coordinates.
- NG-04: The Home Assistant integration itself; it is built in a separate project.
- NG-05: Own data storage, caching across calls, or historical archiving.
- NG-06: The avalanche bulletin and any data source other than the SLF
  Measurement API.
- NG-07: A command-line tool or any user interface.

## Constraints
- The client is written in Python and is asynchronous.
- It is a standalone package, published on PyPI and usable independently of
  Home Assistant.
- Hobby project; no deadline and no budget.
- The SLF data is licensed under CC BY 4.0 (SLF Data Service terms of use,
  https://www.slf.ch/en/services-and-products/slf-data-service). Products that
  display the data must visibly name the source (WSL Institute for Snow and
  Avalanche Research SLF), in digital products as a link to www.slf.ch. This
  obligation lies with the displaying product; the package points it out in
  its documentation.
- Use of the API must not impair or overload the SLF infrastructure.
- The reference integration targets inclusion in Home Assistant Core (decided
  2026-10-31). Home Assistant's requirements for integration libraries
  (https://contributors.home-assistant.io/core/integrations/api-library/,
  https://contributors.home-assistant.io/core/quality-scale/dependency-transparency/)
  apply: published on PyPI with a source distribution; an OSI-approved license
  for the package and its dependencies, stated in its metadata; every PyPI
  version matches a tagged release in a public repository and is built and
  published by a public CI pipeline; a public issue tracker. Platinum-tier rules
  additionally require an asynchronous library that accepts an HTTP session
  supplied by the caller (inject-websession) and is typed with a `py.typed`
  marker (strict-typing).

## Assumptions
- No existing Python client or integration for the SLF Measurement API exists
  (based on the owner's own search, not a systematic review).
- The API stays publicly accessible without authentication.
- Undocumented rate limits are high enough for typical polling by
  integrations, without conflicting with the load clause in the terms of use
  (see Risks).

## Success metrics
- G-01: Station types in scope that can be listed (baseline: 0 of 2; target:
  2 of 2, study plots and IMIS).
- G-02: In-scope snow values available through the package (baseline: 0;
  target: all values listed in G-02).
- G-03: HTTP requests a consumer writes itself for in-scope data (baseline: all;
  target: none).
- G-04: Documented API failure classes (outage, unknown station, invalid
  response, null values) with defined behavior (baseline: none; target: all).
- G-05: Stable release on PyPI (baseline: none; target: one stable release).
- G-06: Home Assistant library requirements and Platinum-tier library rules met
  (baseline: none; target: all listed under Constraints).

## Risks
- **Load / direct-use clause** (likelihood medium, severity high): the terms
  of use state that the interfaces are "not dimensioned to directly serve the
  requests of the customers' information systems". Many installations polling
  the API directly could conflict with this clause or be throttled. Recorded
  as a risk only; SLF is not contacted (decided 2026-10-26).
- **Unannounced API changes** (likelihood medium, severity high): the API makes
  no stability promise and lists no contact; breaking changes would break all
  consumers. Mitigation: the owner registers for SLF's "Live measurement and
  model data" mailing list (data@slf.ch), which announces changes,
  interruptions and new terms of use.
- **Undocumented rate limits** (likelihood low to medium, severity medium):
  frequent polling by many installations could be throttled or blocked.
- **Inconsistent API documentation** (likelihood confirmed, severity low): at
  least one endpoint's description contradicts its parameters, so actual
  behavior has to be confirmed by observation.
- **Seasonal gaps** (likelihood high, severity medium): stations may be
  inactive or return null values outside the winter season, which consumers
  could mistake for errors.
- **Unverified raw data, no liability** (likelihood medium, severity medium):
  SLF accepts no liability for errors, delays or failures, offers no stand-by
  service, and part of the data is raw data that is not regularly checked;
  values can be wrong or missing.
- **Measured vs. modeled values** (likelihood medium, severity medium): mixing
  up measured and modeled snow values could mislead end users.

## Open questions
None. The package license was decided in ADR-006 (MIT, accepted 2026-11-02).
