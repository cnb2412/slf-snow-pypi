# Product Brief: slf-snow-pypi

Status: Draft | Version: 0.1 | Date: 2026-10-25

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

## Assumptions
- No existing Python client or integration for the SLF Measurement API exists
  (based on the owner's own search, not a systematic review).
- The API stays publicly accessible without authentication.
- Undocumented rate limits are high enough for typical polling by integrations.
- The SLF terms of use permit using and redistributing access to the data
  through a public library (not yet verified; see Open questions).

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

## Risks
- **Terms of use not checked** (likelihood unknown, severity high): attribution
  or redistribution rules could restrict a public package or require changes.
- **Unannounced API changes** (likelihood medium, severity high): the API makes
  no stability promise and lists no contact; breaking changes would break all
  consumers.
- **Undocumented rate limits** (likelihood low to medium, severity medium):
  frequent polling by many installations could be throttled or blocked.
- **Inconsistent API documentation** (likelihood confirmed, severity low): at
  least one endpoint's description contradicts its parameters, so actual
  behavior has to be confirmed by observation.
- **Seasonal gaps** (likelihood high, severity medium): stations may be
  inactive or return null values outside the winter season, which consumers
  could mistake for errors.
- **Measured vs. modeled values** (likelihood medium, severity medium): mixing
  up measured and modeled snow values could mislead end users.

## Open questions
- [blocking] What do the SLF Data Service Terms of Use require (attribution,
  redistribution, commercial use), and do they allow a public client library?
- [deferred] Will the Home Assistant integration target inclusion in Home
  Assistant Core? If so, Core's requirements for libraries become constraints
  for this package.
- [deferred] Which open-source license will the package use?
- [deferred] Should SLF be contacted about API stability and rate limits?
