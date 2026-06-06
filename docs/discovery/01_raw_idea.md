# SLF Snow — Project Concept

## Vision & Problem Statement

`slf-snow` is an asynchronous Python client for the Swiss Avalanche Service
(SLF / WSL) snow measurement API. It provides developers with convenient,
typed access to current measurement data (snow depth, new snow, and the
accompanying weather readings) from Switzerland's automated measurement
stations.

The primary driver is a future Home Assistant integration, which will be built
on top of this library. Keeping the API client as a standalone, reusable
package lets that integration — and any other Python project — consume SLF data
without re-implementing the HTTP layer.

## Target Audience

- Python developers who need programmatic access to SLF snow data.
- Primary consumer: the planned Home Assistant integration (built later, on top
  of this library).
- Distributed as an open-source package on PyPI (`slf-snow`).

## Goals & Core Features (Phase 1)

- List all available automated (IMIS) measurement stations.
- Retrieve **all current measurements** a station reports for selected stations —
  snow depth (HS) and new snow over the last 24 h (HN24) as the primary values,
  plus accompanying weather readings (e.g. temperature, wind).
- Select stations by their **station code / ID**.
- Provide a clean **asynchronous** API (built on `aiohttp`).
- Scope is limited to automated stations:
  https://measurement-api.slf.ch/#tag/IMIS

## Non-Goals (Out of Scope)

- No avalanche bulletins, danger levels, or warnings — measurement data only.
- No weather forecasts — only current / measured values.
- No local data storage, persistence, or time-series history — live queries only.
- Manual (study-plot) stations are deferred to a later phase.

## Tech Stack & Constraints

- Language: **Python ≥ 3.13**.
- Asynchronous HTTP via **`aiohttp`**.
- Data source: the SLF measurement API — https://measurement-api.slf.ch
  (public, **no API key required**).
- License: **MIT**.
- Distribution: published to **PyPI** as `slf-snow`.

## Success Criteria — Definition of Done (Phase 1)

- The library can list stations and fetch the current measurements (including HS
  and HN24) for selected stations.
- Functionality is covered by automated tests.
- The package is published as a release on PyPI.

## Future Features / Roadmap

- Home Assistant integration built on top of this library.
- Support for manual (study-plot) stations:
  https://measurement-api.slf.ch/#tag/study-plot
