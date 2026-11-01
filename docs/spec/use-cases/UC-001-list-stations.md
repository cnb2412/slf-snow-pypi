# UC-001: List stations

Status: Draft | Date: 2026-11-01 | Spec version: 1.1

**Primary actor:** Integration developer
**Goals:** G-01, G-03, G-04
**Covered requirements:** FR-001, FR-002, FR-009, FR-014, FR-015, FR-016, FR-019, FR-020
**Related NFRs:** NFR-001, NFR-003, NFR-004, NFR-005, NFR-006

**Preconditions:** The package is installed in the integration developer's
application.
**Trigger:** The integration developer needs the stations of one network or of
both networks, e.g. to let end users choose a station.

## Main success scenario
1. The integration developer requests the list of study-plot stations with one
   call.
2. The package sends one request to the SLF Measurement API.
3. The SLF Measurement API returns the active study-plot stations.
4. The package returns every active study-plot station with station code, name,
   latitude and longitude (WGS84), elevation (m a.s.l.), country code, canton
   code and its network `study_plot`.

## Alternative flows
- **A1 (from step 1):** The integration developer requests the list of IMIS
  stations instead. The package returns every active IMIS station with the
  attributes of step 4, its network `imis` and its station type, for all station
  types delivered by the API. The use case ends.
- **A2 (from step 3):** The SLF Measurement API returns no stations. The package
  returns an empty list without an error. The use case ends.
- **A3 (from step 3):** An in-scope attribute of a station is null. The package
  returns that attribute as `None` without an error and continues with step 4.
- **A4 (from step 1):** The integration developer requests the combined list of
  all stations with one call. The package sends one request per network and
  returns all active stations of both networks in one list, each with the
  attributes of step 4 and its network (`study_plot` or `imis`), IMIS stations
  additionally with their station type. If one network returns no stations, only
  the stations of the other network are returned (see A2). The use case ends.

## Error flows
- **E1 (from step 2):** The SLF Measurement API cannot be reached, does not answer
  within the time limit, or answers with HTTP 5xx or HTTP 429. The package raises
  a *service unavailable* error (see UC-004). No list is returned.
- **E2 (from step 3):** The response cannot be read, does not have the expected
  basic form, lacks an in-scope field or has an in-scope field of the wrong type,
  or is any other unexpected HTTP 4xx response. The package raises an *invalid
  response* error (see UC-004). No list is returned.
- **E3 (from A4):** One or both requests of the combined list fail as in E1 or
  E2. The package raises the *service unavailable* or *invalid response* error of
  a failed request (see UC-004). No list, not even a partial one, is returned.

## Postconditions
- **Success:** The integration developer has the complete list of active
  stations of the requested network, or of both networks, as delivered by the
  API.
- **Minimal guarantees:** The call caused at most one request per network it
  covers and no retry; any failure is reported as a package error.

## Acceptance criteria
- **UC-001-AC1 (main):** Given the API returns active study-plot stations, when
  the integration developer requests the study-plot station list, then every
  station is returned with station code, name, latitude, longitude, elevation,
  country code, canton code and network `study_plot`, and exactly one request
  was sent.
- **UC-001-AC2 (A1):** Given the API returns IMIS stations of several station
  types, when the integration developer requests the IMIS station list, then
  every station of every type is returned with the attributes of AC1, network
  `imis` and its station type.
- **UC-001-AC3 (A2):** Given the API returns no stations, when the integration
  developer requests a station list, then an empty list is returned and no error
  is raised.
- **UC-001-AC4 (A3):** Given a station's canton code is null in the API response,
  when the integration developer requests the station list, then that station is
  returned with canton code `None` and no error is raised.
- **UC-001-AC5 (E1):** Given the API answers with HTTP 503, when the integration
  developer requests a station list, then a *service unavailable* error is raised
  that is catchable as a package error, and no second request is sent.
- **UC-001-AC6 (E2):** Given a station in the API response lacks its station
  code, when the integration developer requests a station list, then an *invalid
  response* error is raised that is catchable as a package error.
- **UC-001-AC7 (A4):** Given both networks return active stations, when the
  integration developer requests the combined station list, then all stations of
  both networks are returned in one list, each with its network (`study_plot` or
  `imis`), IMIS stations with their station type, exactly two requests were sent,
  and the call ends within the time limit counted from its first request.
- **UC-001-AC8 (E3):** Given the study-plot request succeeds and the IMIS request
  is answered with HTTP 503, when the integration developer requests the combined
  station list, then a *service unavailable* error is raised that is catchable as
  a package error, no list is returned, and no retry is sent.
