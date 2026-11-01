# Specification: slf-snow-pypi

Status: Approved | Version: 2.0 | Date: 2026-11-01 | Brief: [docs/brief.md](../brief.md)

## 1. Scope
This version specifies a standalone, asynchronous Python client package for the
snow values of the SLF Measurement API (https://measurement-api.slf.ch/). It
covers listing the active study-plot and IMIS stations (per network or as one
combined list), retrieving the current measured snow values of a study plot or
IMIS station with one operation for both networks, retrieving the current
modeled daily snow values of IMIS stations (per station or for all stations of a
network in one call), and a defined behavior for missing data and API failures.
Everything else that the API offers (other measurements, time series) and all
functionality beyond the API are out of scope (see section 8).

## 2. Glossary
| Term | Definition |
|------|------------|
| SLF | WSL Institute for Snow and Avalanche Research, operator of the SLF Measurement API. |
| SLF Measurement API | The public REST API at https://measurement-api.slf.ch/ (OpenAPI version 1.1.0 at the time of writing). |
| Network | A group of stations served by the API: *study plots* or *IMIS*; identified in the package as `study_plot` or `imis`. |
| Study plot | Manual measuring site; reports snow height, new snow and new-snow water equivalent, typically once per day. |
| IMIS station | Automated measuring station of the IMIS network; has a station type (e.g. `SNOW_FLAT`, `WIND`). |
| Station code | Identifier of a station within the API (e.g. `DAV2`). |
| Snow height (HS) | Total thickness of the snowpack in cm. |
| New snow (HN_1D) | Height of new snow during the last 24 hours in cm. |
| New-snow water equivalent (HNW_1D) | Water equivalent of the new snow during the last 24 hours in mm. |
| Measured value | A value observed at a station (study plot or IMIS measurement). |
| Modeled value | A daily snow height or new-snow value computed by SLF's snowpack model for an IMIS station (API resource `daily-snow`). |
| Record | One entry returned by the API for one station and one timestamp. |
| Current record | The record with the latest timestamp among the records the API returns for a station, independent of the order in which the API delivers them; if several records share the latest timestamp, the first one delivered. Its values are delivered as-is. |
| Empty value | A value that the API delivers as null or that is otherwise absent; represented as `None`. |
| Call | One invocation of a public operation of the package by a consumer. |
| Package error | Any error raised by the package; all error kinds below are package errors. |
| Station not found | Error kind: the API reports that a station code is unknown. |
| Service unavailable | Error kind for transient failures: the API cannot be reached, does not answer within the time limit, or answers with HTTP 5xx or HTTP 429 (FR-015). |
| Invalid response | Error kind for persistent failures: the API answers, but not as expected, i.e. the response does not match the in-scope fields or is an unexpected HTTP 4xx response (FR-016). |
| In-scope field | A field of an API response that the package delivers: for stations `code`, `label`, `lat`, `lon`, `elevation`, `country_code`, `canton_code` (IMIS additionally `type`); for study-plot records `station_code`, `measure_date`, `HS`, `HN_1D`, `HNW_1D`; for IMIS records `station_code`, `measure_date`, `HS`; for modeled records `station_code`, `measure_date`, `HS`, `HN_1D`. All other fields are out of scope. |

## 3. Actors
- **Integration developer** (primary): writes a Python application or integration
  (reference: a Home Assistant integration in a separate project) and uses the
  package to obtain SLF snow data.
- **SLF Measurement API** (external system): provides station lists and records.

## 4. Functional requirements
| ID | Requirement (MUST/SHOULD/MAY) | Rationale | Goals | Use cases | Status |
|----|-------------------------------|-----------|-------|-----------|--------|
| FR-001 | The package MUST return the list of active study-plot stations, each with station code, name, latitude and longitude (WGS84), elevation (m a.s.l.), country code and canton code. | Consumers let users choose a study plot. | G-01 | UC-001 | Active |
| FR-002 | The package MUST return the list of all active IMIS stations, each with the attributes of FR-001 plus the station type as delivered by the API. | Consumers let users choose an IMIS station and filter by type themselves. | G-01 | UC-001 | Active |
| FR-003 | For a given study-plot station code, the package MUST return the current record with its timestamp, snow height, new snow and new-snow water equivalent. | Core scenario for study plots. | G-02 | — | Deprecated (replaced by FR-021, v2.0) |
| FR-004 | For a given IMIS station code, the package MUST return the current measured record with its timestamp and snow height. | Core scenario for IMIS stations. | G-02 | — | Deprecated (replaced by FR-021, v2.0) |
| FR-005 | For a given IMIS station code, the package MUST return the current modeled record with its timestamp, snow height and new snow. | Modeled values complement IMIS measurements. | G-02 | UC-003 | Active |
| FR-006 | The package MUST return, in one call each, the current record of every station for study-plot measurements, IMIS measurements and IMIS modeled values. | Consumers watching several stations need fewer requests, which reduces load on SLF (brief constraint). | G-02 | — | Deprecated (replaced by FR-018, v0.3) |
| FR-007 | Modeled records MUST be distinguishable from measured records without inspecting their origin. | Mixing up measured and modeled values could mislead end users (brief risk). | G-02 | UC-003 | Active |
| FR-008 | Every timestamp returned by the package MUST be timezone-aware and expressed in UTC, including timestamps that the API delivers without a zone designator. | The API delivers timestamps inconsistently (with and without `Z`). Timestamps without zone designator are treated as UTC because the API documentation states that all timestamps are UTC (decided 2026-10-28); observed 2026-10-28: period boundaries start at Swiss local midnight; not confirmed by SLF. | G-02 | UC-002, UC-003 | Active |
| FR-009 | An empty value in a record or in a station's attributes MUST be returned as `None` and MUST NOT cause an error. | Null values are normal, especially outside the winter season. | G-04 | UC-001, UC-002, UC-003, UC-004 | Active |
| FR-010 | When a station has no current record, the package MUST return "no record" instead of raising an error; for modeled values, a station absent from the API response MUST also be treated as "no record". | Seasonally inactive stations are normal; the modeled-values resource cannot distinguish unknown stations from stations without data within one request (NFR-004). | G-04 | UC-002, UC-003, UC-004 | Active |
| FR-011 | When the API reports an unknown station code, including a valid code of the other network, the package MUST raise a *station not found* error. | Consumers must distinguish a wrong code from missing data; observed 2026-10-28: the API reports codes of the other network as `STATION_NOT_FOUND` in both directions. | G-04 | UC-002, UC-004 | Active |
| FR-012 | When the API cannot be reached, answers with an HTTP error status (other than the one covered by FR-011), or exceeds the time limit of NFR-006, the package MUST raise a *service unavailable* error. | Outages must be reported in a defined way. | G-04 | — | Deprecated (replaced by FR-015, v0.2) |
| FR-013 | When the API response does not match the expected format, the package MUST raise an *invalid response* error. | The API makes no stability promise; format changes must not cause undefined failures. | G-04 | — | Deprecated (replaced by FR-016, v0.2) |
| FR-014 | Every error raised by the package MUST be catchable as a package error, and the package MUST NOT let any other error escape for the conditions in FR-011, FR-015, FR-016 and FR-017. | Consumers handle all API problems with one well-defined set of errors. | G-04 | UC-001, UC-002, UC-003, UC-004 | Active |
| FR-015 | When the API cannot be reached, exceeds the time limit of NFR-006, or answers with HTTP 5xx or HTTP 429, the package MUST raise a *service unavailable* error. | These failures are transient; consumers may try again later. | G-04 | UC-001, UC-002, UC-003, UC-004 | Active |
| FR-016 | When the API response cannot be read, does not have the expected basic form (a list of entries), lacks an in-scope field or has an in-scope field of the wrong type, or is an HTTP 4xx response not covered by FR-011 or FR-015, the package MUST raise an *invalid response* error; fields that are not in scope MUST NOT cause an error, and an in-scope value that is null is an empty value (FR-009). | These failures are persistent and need a package update; changes to out-of-scope fields (NG-01) must not break consumers. | G-04 | UC-001, UC-002, UC-003, UC-004 | Active |
| FR-017 | A station code given by the consumer MUST be transmitted to the API only as a station identifier, so that no code can address any other API resource; an empty station code MUST raise a *station not found* error without sending a request. | A code such as `../imis` must not make the package read another resource as snow data; an empty code is a caller mistake, not an API failure. | G-04 | UC-002, UC-003, UC-004 | Active |
| FR-018 | The package MUST return, in one call each, the current record of every station contained in the API response for study-plot measurements, IMIS measurements and IMIS modeled values; stations without a current record are not included. | Consumers watching several stations need fewer requests (brief load constraint); within one request (NFR-004) the package cannot know stations that the API omits. | G-02 | UC-002, UC-003 | Active |
| FR-019 | The package MUST return, in one call, the combined list of all active study-plot and IMIS stations, each with the attributes of FR-001, its network, and for IMIS stations the station type (FR-002). If any request of the call fails, the package MUST raise the package error of FR-015 or FR-016 for a failed request and MUST NOT return a partial list. | Consumers let users choose from all stations at once; the API has no combined resource. A partial list could hide stations without the consumer noticing (decided 2026-11-01). | G-01 | UC-001 | Active |
| FR-020 | Every station and every measured record returned by the package (FR-001, FR-002, FR-018, FR-019, FR-021) MUST state its network as `study_plot` or `imis`. | Stations of a combined list and records of the generic operation must be distinguishable; the IMIS station type is a different attribute. | G-01, G-02 | UC-001, UC-002 | Active |
| FR-021 | For a given station, identified by its network and station code, the package MUST return the current measured record of that station: for a study plot with its timestamp, snow height, new snow and new-snow water equivalent; for an IMIS station with its timestamp and snow height. | One operation for both networks (decided 2026-11-01); the network comes from the station list (FR-020) because station codes are not documented to reveal their network (observed 2026-11-01: disjoint code patterns in both networks, not relied upon). | G-02 | UC-002 | Active |

## 5. Non-functional requirements
| ID | Category | Requirement (measurable) | Rationale | Goals | Status |
|----|----------|--------------------------|-----------|-------|--------|
| NFR-001 | constraint | The package MUST be a Python package whose public data operations are all asynchronous (awaitable) and MUST NOT block the caller's event loop while waiting for the API. | Brief constraint: Python, asynchronous. | G-03 | Active |
| NFR-002 | constraint | The package MUST be installable and usable without Home Assistant installed (0 dependencies on Home Assistant packages). | Brief constraint: standalone package. | G-03, G-05 | Active |
| NFR-003 | usability | Every value in scope (FR-001, FR-002, FR-005, FR-018, FR-019 and FR-021) MUST be obtainable with exactly 1 call, without the consumer building URLs, sending HTTP requests or parsing API responses. | Consumers need no HTTP code of their own. | G-03 | Active |
| NFR-004 | compliance | Each call MUST cause at most 1 HTTP request to the API per network it covers (at most 2 for FR-019); the package MUST NOT retry failed requests automatically. | Brief constraint: do not overload SLF infrastructure. | G-04 | Active |
| NFR-005 | compliance | The package MUST NOT send any request to the API except as part of a call by the consumer (0 background requests). | Brief constraint: do not overload SLF infrastructure. | G-03 | Active |
| NFR-006 | reliability | A call for which the API does not answer MUST end with a *service unavailable* error no later than 10 s after the request was sent (for FR-019: after the call's first request was sent); the consumer MUST be able to change this limit. | An outage is only detectable with a time limit. | G-04 | Active |
| NFR-007 | compliance | The package documentation MUST state that the SLF data is licensed under CC BY 4.0 and that products displaying it must visibly name the WSL Institute for Snow and Avalanche Research SLF, in digital products as a link to www.slf.ch. | Brief constraint: attribution is the displaying product's obligation; the package points it out. | G-05 | Active |
| NFR-008 | constraint | The package MUST be published on PyPI and installable from there with the standard Python package installer. | Brief goal: public release on PyPI. | G-05 | Active |
| NFR-009 | constraint | The consumer MUST be able to supply an HTTP session of their own; if supplied, the package MUST send all requests through it and MUST NOT close it (0 requests through any other session). | Home Assistant Platinum rule inject-websession: integrations pass Home Assistant's shared session. | G-06 | Active |
| NFR-010 | constraint | The package and every runtime dependency MUST be under an OSI-approved open-source license, and the package's license MUST be stated in its package metadata. | Home Assistant library requirement. | G-06 | Active |
| NFR-011 | constraint | Every version published on PyPI MUST include a source distribution, MUST be built and published by a public CI pipeline, and MUST match a tagged release in the public repository; the repository MUST have a public issue tracker. | Home Assistant library requirements (dependency-transparency). | G-05, G-06 | Active |
| NFR-012 | constraint | Every public operation, data type and error of the package MUST carry complete type annotations (0 errors from a strict static type check of the public interface), and the package MUST mark itself as typed (`py.typed`, PEP 561). | Home Assistant Platinum rule strict-typing. | G-06 | Active |

## 6. Data (conceptual)
- **Station**: station code, name, latitude, longitude (WGS84), elevation
  (m a.s.l.), country code, canton code, network (study plot or IMIS).
  IMIS stations additionally have a station type.
- **Study-plot record** (measured): station code, network, timestamp (UTC), snow
  height (cm), new snow (cm), new-snow water equivalent (mm); each value may be
  empty.
- **IMIS record** (measured): station code, network, timestamp (UTC), snow height
  (cm); the value may be empty.
- **Modeled daily snow record** (modeled): station code, timestamp (UTC), snow
  height (cm), new snow (cm); each value may be empty.
- Relations: a station has zero or one current record per kind; records refer to
  stations by station code within the same network.
- The attributes above correspond to the in-scope fields (see glossary); all
  other fields of API responses are out of scope.
- No entity contains personal data.

## 7. Use case index
| ID | Title | Source scenario | Status |
|----|-------|-----------------|--------|
| UC-001 | List stations | Brief scenario 1 (list active stations) | Written |
| UC-002 | Get current measured snow values of a station | Brief scenarios 2 and 3 (study-plot and IMIS measured values); includes the all-stations variants of FR-018 | Written |
| UC-003 | Get current modeled IMIS snow values | Brief scenario 3 (IMIS modeled values); includes the all-stations variant of FR-018 | Written |
| UC-004 | Handle missing data and API failures | Brief scenario 4 (defined errors) | Written |

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
synchronous interface, distinguishing unknown
stations from stations without data for modeled values (would need a second
request), a semantic-versioning promise, and shipping the attribution text as a
value in the package.

Also excluded (decided 2026-10-31): defined behavior for a time limit of zero
or less set by the consumer (a caller mistake, not an API problem covered by
G-04).

Also excluded (decided 2026-11-01): detecting a station's network from its
station code, and defined behavior for a network value other than `study_plot`
or `imis` (a caller mistake, prevented by the typed interface).

## 9. Ambiguities to resolve
None.

## 10. Changelog
| Version | Date | Change | Breaking |
|---------|------|--------|----------|
| 0.1 | 2026-10-28 | Initial draft | no |
| 0.2 | 2026-10-28 | Resolved all ambiguities of v0.1: (A1) only in-scope fields define the expected format, added glossary term "In-scope field"; (A2) FR-012 and FR-013 deprecated and replaced by FR-015 (service unavailable: unreachable, timeout, HTTP 5xx, HTTP 429) and FR-016 (invalid response: unreadable or non-conforming in-scope fields, other unexpected HTTP 4xx), FR-014 references updated; (A3) FR-011 clarified for codes of the other network (observed 2026-10-28); (A4) "Current record" selected by latest timestamp independent of API order, first delivered on a tie; (A5) timestamps without zone designator remain UTC per API documentation, observation added to FR-008 rationale. | yes (FR-012, FR-013) |
| 0.3 | 2026-10-31 | Gaps found while writing UC-001..UC-004: FR-009 extended to station attributes; FR-006 deprecated and replaced by FR-018 (only stations contained in the API response are returned); FR-017 added (station code transmitted only as identifier, empty code raises station not found without request); FR-014 references FR-017; time limit of zero or less excluded; use case traceability filled in. | yes (FR-006) |
| 1.0 | 2026-10-31 | Brief v1.2 sets Home Assistant Core as target (G-06): added NFR-009 (consumer-supplied HTTP session, removed from "Also excluded"), NFR-010 (OSI license), NFR-011 (sdist, public CI, tags, issue tracker), NFR-012 (typed, `py.typed`); NFR-003 reference corrected from FR-006 to FR-018; status set to Approved. | no |
| 1.1 | 2026-11-01 | Combined station list: added FR-019 (study-plot and IMIS stations in one call, no partial list on failure) and FR-020 (every station states its network, `study_plot` or `imis`); NFR-004 allows one request per network covered by a call; NFR-006 bounds the combined call from its first request; NFR-003 references FR-019; glossary "Network" and scope updated. | no |
| 2.0 | 2026-11-01 | Generic measured-value query: FR-003 and FR-004 deprecated and replaced by FR-021 (current measured record of a station identified by network and station code); FR-020 extended to measured records; NFR-003 references updated; UC-002 now covers measured values of both networks, UC-003 only modeled IMIS values; network detection from codes excluded. | yes (FR-003, FR-004) |
