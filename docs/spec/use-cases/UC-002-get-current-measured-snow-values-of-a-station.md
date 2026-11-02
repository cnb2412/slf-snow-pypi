# UC-002: Get current measured snow values of a station

Status: Draft | Date: 2026-11-02 | Spec version: 2.1

**Primary actor:** Integration developer
**Goals:** G-02, G-03, G-04
**Covered requirements:** FR-008, FR-009, FR-010, FR-011, FR-014, FR-015,
FR-016, FR-017, FR-018, FR-020, FR-021
**Related NFRs:** NFR-001, NFR-003, NFR-004, NFR-005, NFR-006

**Preconditions:** The package is installed; the integration developer knows the
network and station code of a station (e.g. a station from UC-001).
**Trigger:** The integration developer needs the current measured snow values of
a study plot or IMIS station, e.g. to update a sensor.

## Main success scenario
1. The integration developer requests the current measured record of a station,
   identified by its network and station code, with one call.
2. The package sends one request for the measured records of that network to the
   SLF Measurement API, transmitting the station code only as a station
   identifier.
3. The SLF Measurement API returns the records of that station.
4. The package selects the current record (latest timestamp, independent of the
   order delivered by the API).
5. The package returns the current record with its network, its timestamp as
   timezone-aware UTC and the measured values of its network: for a study plot
   snow height (cm), new snow (cm) and new-snow water equivalent (mm); for an
   IMIS station snow height (cm).

## Alternative flows
- **A1 (from step 4):** One or more values of the current record are null (e.g.
  the snow height at an IMIS wind station). The package returns them as `None`
  without an error and continues with step 5.
- **A2 (from step 3):** The SLF Measurement API returns no record for the station
  or reports that it has no data for the station (e.g. outside the winter season
  or when a study plot skipped a reading). The package returns "no record" without an
  error. The use case ends.
- **A3 (from step 1):** The integration developer requests the current records of
  all study plots with one call. The package sends one request and returns the
  current record of every station contained in the API response, each as in
  step 5 with network `study_plot`; stations without a current record are not
  included. The use case ends.
- **A4 (from step 1):** The integration developer requests the current measured
  records of all IMIS stations with one call. The package sends one request and
  returns the current record of every station contained in the API response, each
  as in step 5 with network `imis`; stations without a current record are not
  included. The use case ends.

## Error flows
- **E1 (from step 3):** The SLF Measurement API reports the station code as
  unknown in the given network, including a valid code of the other network. The
  package raises a *station not found* error. No record is returned.
- **E2 (from step 1):** The station code is empty. The package raises a *station
  not found* error without sending a request.
- **E3 (from step 2, A3 or A4):** The SLF Measurement API cannot be reached, does
  not answer within the time limit, or answers with HTTP 5xx or HTTP 429. The
  package raises a *service unavailable* error (see UC-004).
- **E4 (from step 3, A3 or A4):** The response cannot be read, does not have the
  expected basic form, lacks an in-scope field or has an in-scope field of the
  wrong type, or is any other unexpected HTTP 4xx response. The package raises an
  *invalid response* error (see UC-004).

## Postconditions
- **Success:** The integration developer has the current measured record of the
  station (or of all stations of a network contained in the API response), or
  knows that the station has no current record.
- **Minimal guarantees:** The call caused at most one request and no retry; no
  station code addressed any API resource other than the station's records; any
  failure is reported as a package error.

## Acceptance criteria
- **UC-002-AC1 (main):** Given the API returns several records for study plot
  `4EG0` in ascending order, when the integration developer requests the current
  measured record of `4EG0` in network `study_plot`, then the record with the
  latest timestamp is returned with network `study_plot`, a timezone-aware UTC
  timestamp, snow height, new snow and new-snow water equivalent, and exactly one
  request was sent.
- **UC-002-AC2 (main):** Given the API returns the same records in descending
  order, when the integration developer requests the current record, then the
  same record as in AC1 is returned.
- **UC-002-AC3 (A1):** Given the current study-plot record has new snow null,
  when the integration developer requests it, then new snow is `None`, the other
  values are returned, and no error is raised.
- **UC-002-AC4 (A2):** Given the API returns no record for a known study plot,
  when the integration developer requests its current record, then "no record"
  is returned and no error is raised.
- **UC-002-AC5 (A3):** Given the API returns records for 5 study plots, when the
  integration developer requests the current records of all study plots, then
  exactly 5 current records are returned, one per station, each with network
  `study_plot`, and exactly one request was sent.
- **UC-002-AC6 (E1):** Given the API answers `STATION_NOT_FOUND` for code `DAV2`,
  when the integration developer requests the current measured record of `DAV2`
  in network `study_plot`, then a *station not found* error is raised.
- **UC-002-AC7 (E2):** Given an empty station code, when the integration
  developer requests a current record, then a *station not found* error is raised
  and no request is sent.
- **UC-002-AC8 (main):** Given the station code `../imis/stations`, when the
  integration developer requests a current record, then the request addresses
  only the records of a station with that code and no other API resource.
- **UC-002-AC9 (E3):** Given the API does not answer within the time limit, when
  the integration developer requests a current record, then a *service
  unavailable* error is raised.
- **UC-002-AC10 (E4):** Given a record in the API response lacks `measure_date`,
  when the integration developer requests a current record, then an *invalid
  response* error is raised.
- **UC-002-AC11 (main):** Given the API returns 336 measured records for `DAV2` in
  ascending order, when the integration developer requests the current measured
  record of `DAV2` in network `imis`, then the record with the latest timestamp
  is returned with network `imis`, a timezone-aware UTC timestamp and snow
  height, and exactly one request was sent.
- **UC-002-AC12 (A1):** Given the current measured record of an IMIS wind station
  has snow height null, when the integration developer requests it, then snow
  height is `None` and no error is raised.
- **UC-002-AC13 (A2):** Given the API returns no measured record for a known IMIS
  station, when the integration developer requests its current measured record,
  then "no record" is returned and no error is raised.
- **UC-002-AC14 (A4):** Given the API returns measured records for 3 IMIS
  stations, when the integration developer requests the current measured records
  of all IMIS stations, then exactly 3 current records are returned, one per
  station, each with network `imis`.
- **UC-002-AC15 (E1):** Given the API answers `STATION_NOT_FOUND` for code `4AO0`,
  when the integration developer requests the current measured record of `4AO0`
  in network `imis`, then a *station not found* error is raised.
- **UC-002-AC16 (A2):** Given the API answers HTTP 404 with code `NO_DATA` for
  study plot `4UL0`, when the integration developer requests its current measured
  record, then "no record" is returned and no error is raised.
