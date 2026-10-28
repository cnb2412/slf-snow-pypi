# Specification: slf-snow-pypi

Status: Draft | Version: 0.1 | Date: 2026-10-28 | Brief: [docs/brief.md](../brief.md)

## 1. Scope
This version specifies a standalone, asynchronous Python client package for the
snow values of the SLF Measurement API (https://measurement-api.slf.ch/). It
covers listing the active study-plot and IMIS stations, retrieving the current
measured snow values of study plots and IMIS stations, retrieving the current
modeled daily snow values of IMIS stations (per station or for all stations of a
network in one call), and a defined behavior for missing data and API failures.
Everything else that the API offers (other measurements, time series) and all
functionality beyond the API are out of scope (see section 8).

## 2. Glossary
| Term | Definition |
|------|------------|
| SLF | WSL Institute for Snow and Avalanche Research, operator of the SLF Measurement API. |
| SLF Measurement API | The public REST API at https://measurement-api.slf.ch/ (OpenAPI version 1.1.0 at the time of writing). |
| Network | A group of stations served by the API: *study plots* or *IMIS*. |
| Study plot | Manual measuring site; reports snow height, new snow and new-snow water equivalent, typically once per day. |
| IMIS station | Automated measuring station of the IMIS network; has a station type (e.g. `SNOW_FLAT`, `WIND`). |
| Station code | Identifier of a station within the API (e.g. `DAV2`). |
| Snow height (HS) | Total thickness of the snowpack in cm. |
| New snow (HN_1D) | Height of new snow during the last 24 hours in cm. |
| New-snow water equivalent (HNW_1D) | Water equivalent of the new snow during the last 24 hours in mm. |
| Measured value | A value observed at a station (study plot or IMIS measurement). |
| Modeled value | A daily snow height or new-snow value computed by SLF's snowpack model for an IMIS station (API resource `daily-snow`). |
| Record | One entry returned by the API for one station and one timestamp. |
| Current record | The record with the latest timestamp that the API returns for a station, delivered as-is. |
| Empty value | A value that the API delivers as null or that is otherwise absent; represented as `None`. |
| Call | One invocation of a public operation of the package by a consumer. |
| Package error | Any error raised by the package; all error kinds below are package errors. |
| Station not found | Error kind: the API reports that a station code is unknown. |
| Service unavailable | Error kind: the API cannot be reached, answers with an HTTP error, or does not answer within the time limit. |
| Invalid response | Error kind: the API answers, but the response does not match the expected format. |

## 3. Actors
- **Integration developer** (primary): writes a Python application or integration
  (reference: a Home Assistant integration in a separate project) and uses the
  package to obtain SLF snow data.
- **SLF Measurement API** (external system): provides station lists and records.

## 4. Functional requirements
| ID | Requirement (MUST/SHOULD/MAY) | Rationale | Goals | Use cases | Status |
|----|-------------------------------|-----------|-------|-----------|--------|
| FR-001 | The package MUST return the list of active study-plot stations, each with station code, name, latitude and longitude (WGS84), elevation (m a.s.l.), country code and canton code. | Consumers let users choose a study plot. | G-01 | TBD | Active |
| FR-002 | The package MUST return the list of all active IMIS stations, each with the attributes of FR-001 plus the station type as delivered by the API. | Consumers let users choose an IMIS station and filter by type themselves. | G-01 | TBD | Active |
| FR-003 | For a given study-plot station code, the package MUST return the current record with its timestamp, snow height, new snow and new-snow water equivalent. | Core scenario for study plots. | G-02 | TBD | Active |
| FR-004 | For a given IMIS station code, the package MUST return the current measured record with its timestamp and snow height. | Core scenario for IMIS stations. | G-02 | TBD | Active |
| FR-005 | For a given IMIS station code, the package MUST return the current modeled record with its timestamp, snow height and new snow. | Modeled values complement IMIS measurements. | G-02 | TBD | Active |
| FR-006 | The package MUST return, in one call each, the current record of every station for study-plot measurements, IMIS measurements and IMIS modeled values. | Consumers watching several stations need fewer requests, which reduces load on SLF (brief constraint). | G-02 | TBD | Active |
| FR-007 | Modeled records MUST be distinguishable from measured records without inspecting their origin. | Mixing up measured and modeled values could mislead end users (brief risk). | G-02 | TBD | Active |
| FR-008 | Every timestamp returned by the package MUST be timezone-aware and expressed in UTC, including timestamps that the API delivers without a zone designator. | The API delivers timestamps inconsistently (with and without `Z`). | G-02 | TBD | Active |
| FR-009 | An empty value in a record MUST be returned as `None` and MUST NOT cause an error. | Null values are normal, especially outside the winter season. | G-04 | TBD | Active |
| FR-010 | When a station has no current record, the package MUST return "no record" instead of raising an error; for modeled values, a station absent from the API response MUST also be treated as "no record". | Seasonally inactive stations are normal; the modeled-values resource cannot distinguish unknown stations from stations without data within one request (NFR-004). | G-04 | TBD | Active |
| FR-011 | When the API reports an unknown station code, the package MUST raise a *station not found* error. | Consumers must distinguish a wrong code from missing data. | G-04 | TBD | Active |
| FR-012 | When the API cannot be reached, answers with an HTTP error status (other than the one covered by FR-011), or exceeds the time limit of NFR-006, the package MUST raise a *service unavailable* error. | Outages must be reported in a defined way. | G-04 | TBD | Active |
| FR-013 | When the API response does not match the expected format, the package MUST raise an *invalid response* error. | The API makes no stability promise; format changes must not cause undefined failures. | G-04 | TBD | Active |
| FR-014 | Every error raised by the package MUST be catchable as a package error, and the package MUST NOT let any other error escape for the conditions in FR-011 to FR-013. | Consumers handle all API problems with one well-defined set of errors. | G-04 | TBD | Active |

## 5. Non-functional requirements
| ID | Category | Requirement (measurable) | Rationale | Goals | Status |
|----|----------|--------------------------|-----------|-------|--------|
| NFR-001 | constraint | The package MUST be a Python package whose public data operations are all asynchronous (awaitable) and MUST NOT block the caller's event loop while waiting for the API. | Brief constraint: Python, asynchronous. | G-03 | Active |
| NFR-002 | constraint | The package MUST be installable and usable without Home Assistant installed (0 dependencies on Home Assistant packages). | Brief constraint: standalone package. | G-03, G-05 | Active |
| NFR-003 | usability | Every value in scope (FR-001 to FR-006) MUST be obtainable with exactly 1 call, without the consumer building URLs, sending HTTP requests or parsing API responses. | Consumers need no HTTP code of their own. | G-03 | Active |
| NFR-004 | compliance | Each call MUST cause at most 1 HTTP request to the API; the package MUST NOT retry failed requests automatically. | Brief constraint: do not overload SLF infrastructure. | G-04 | Active |
| NFR-005 | compliance | The package MUST NOT send any request to the API except as part of a call by the consumer (0 background requests). | Brief constraint: do not overload SLF infrastructure. | G-03 | Active |
| NFR-006 | reliability | A call for which the API does not answer MUST end with a *service unavailable* error no later than 10 s after the request was sent; the consumer MUST be able to change this limit. | An outage is only detectable with a time limit. | G-04 | Active |
| NFR-007 | compliance | The package documentation MUST state that the SLF data is licensed under CC BY 4.0 and that products displaying it must visibly name the WSL Institute for Snow and Avalanche Research SLF, in digital products as a link to www.slf.ch. | Brief constraint: attribution is the displaying product's obligation; the package points it out. | G-05 | Active |
| NFR-008 | constraint | The package MUST be published on PyPI and installable from there with the standard Python package installer. | Brief goal: public release on PyPI. | G-05 | Active |

## 6. Data (conceptual)
- **Station**: station code, name, latitude, longitude (WGS84), elevation
  (m a.s.l.), country code, canton code, network (study plot or IMIS).
  IMIS stations additionally have a station type.
- **Study-plot record** (measured): station code, timestamp (UTC), snow height
  (cm), new snow (cm), new-snow water equivalent (mm); each value may be empty.
- **IMIS record** (measured): station code, timestamp (UTC), snow height (cm);
  the value may be empty.
- **Modeled daily snow record** (modeled): station code, timestamp (UTC), snow
  height (cm), new snow (cm); each value may be empty.
- Relations: a station has zero or one current record per kind; records refer to
  stations by station code within the same network.
- No entity contains personal data.

## 7. Use case index
| ID | Title | Source scenario | Status |
|----|-------|-----------------|--------|
| UC-001 | List stations | Brief scenario 1 (list active stations) | Planned |
| UC-002 | Get current study-plot snow values | Brief scenario 2 (study-plot values); includes the all-stations variant of FR-006 | Planned |
| UC-003 | Get current IMIS snow values (measured and modeled) | Brief scenario 3 (IMIS values); includes the all-stations variant of FR-006 | Planned |
| UC-004 | Handle missing data and API failures | Brief scenario 4 (defined errors) | Planned |

## 8. Won't have (this version)
- NG-01: Measurements other than snow (air and snow temperature, humidity, wind,
  radiation, precipitation).
- NG-02: Time series or history (the API's 1/3/7-day periods); only current
  values are offered.
- NG-03: Functionality beyond what the API provides, e.g. finding the nearest
  station to given coordinates, or filtering stations by type or canton.
- NG-04: The Home Assistant integration itself.
- NG-05: Own data storage, caching across calls, or historical archiving.
- NG-06: The avalanche bulletin and any data source other than the SLF
  Measurement API.
- NG-07: A command-line tool or any user interface.

Also excluded in this version (decided 2026-10-28): automatic retries or
backoff (conflicts with NFR-004), a maximum age for current records, client-side
rate limiting, a recommended polling interval, an identifying User-Agent, a
consumer-supplied HTTP session, a synchronous interface, distinguishing unknown
stations from stations without data for modeled values (would need a second
request), a semantic-versioning promise, and shipping the attribution text as a
value in the package.

## 9. Ambiguities to resolve
- "Current record" is chosen by the latest timestamp among the records the API
  returns for the default period (1 day); whether the API ever returns records
  out of order is not documented.
- Timestamps of modeled records come without a zone designator; FR-008 treats
  them as UTC because the API documentation states that all timestamps are UTC.
  Not confirmed by SLF.
- How the package classifies an HTTP 422 (validation error) is open: it should
  not occur for valid calls; FR-012 currently treats it as *service
  unavailable*.
- It is not documented whether `STATION_NOT_FOUND` is also returned for a valid
  code of the other network (e.g. an IMIS code queried as a study plot).
- Values of IMIS records that are outside scope (NG-01) are ignored; whether
  their absence or change in a future API version counts as an *invalid
  response* (FR-013) is not yet decided.

## 10. Changelog
| Version | Date | Change | Breaking |
|---------|------|--------|----------|
| 0.1 | 2026-10-28 | Initial draft | no |
