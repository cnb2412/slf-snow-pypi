# UC-002: Get current study-plot snow values

Status: Draft | Date: 2026-10-31 | Spec version: 0.3

**Primary actor:** Integration developer
**Goals:** G-02, G-03, G-04
**Covered requirements:** FR-003, FR-008, FR-009, FR-010, FR-011, FR-014,
FR-015, FR-016, FR-017, FR-018
**Related NFRs:** NFR-001, NFR-003, NFR-004, NFR-005, NFR-006

**Preconditions:** The package is installed; the integration developer knows the
station code of a study plot (e.g. from UC-001).
**Trigger:** The integration developer needs the current snow values of a study
plot, e.g. to update a sensor.

## Main success scenario
1. The integration developer requests the current record of a study-plot station
   by its station code with one call.
2. The package sends one request to the SLF Measurement API, transmitting the
   station code only as a station identifier.
3. The SLF Measurement API returns the records of that station.
4. The package selects the current record (latest timestamp, independent of the
   order delivered by the API).
5. The package returns the current record with its timestamp as timezone-aware
   UTC, snow height (cm), new snow (cm) and new-snow water equivalent (mm).

## Alternative flows
- **A1 (from step 4):** One or more values of the current record are null. The
  package returns them as `None` without an error and continues with step 5.
- **A2 (from step 3):** The SLF Measurement API returns no record for the station
  (e.g. outside the winter season). The package returns "no record" without an
  error. The use case ends.
- **A3 (from step 1):** The integration developer requests the current records of
  all study plots with one call. The package sends one request and returns the
  current record of every station contained in the API response, each as in
  step 5; stations without a current record are not included. The use case ends.

## Error flows
- **E1 (from step 3):** The SLF Measurement API reports the station code as
  unknown, including a valid IMIS code. The package raises a *station not found*
  error. No record is returned.
- **E2 (from step 1):** The station code is empty. The package raises a *station
  not found* error without sending a request.
- **E3 (from step 2):** The SLF Measurement API cannot be reached, does not answer
  within the time limit, or answers with HTTP 5xx or HTTP 429. The package raises
  a *service unavailable* error (see UC-004).
- **E4 (from step 3):** The response cannot be read, does not have the expected
  basic form, lacks an in-scope field or has an in-scope field of the wrong type,
  or is any other unexpected HTTP 4xx response. The package raises an *invalid
  response* error (see UC-004).

## Postconditions
- **Success:** The integration developer has the current record of the study
  plot (or of all study plots contained in the API response), or knows that the
  station has no current record.
- **Minimal guarantees:** The call caused at most one request and no retry; no
  station code addressed any API resource other than the station's records; any
  failure is reported as a package error.

## Acceptance criteria
- **UC-002-AC1 (main):** Given the API returns several records for study plot
  `4EG0` in ascending order, when the integration developer requests its current
  record, then the record with the latest timestamp is returned with a
  timezone-aware UTC timestamp, snow height, new snow and new-snow water
  equivalent, and exactly one request was sent.
- **UC-002-AC2 (main):** Given the API returns the same records in descending
  order, when the integration developer requests the current record, then the
  same record as in AC1 is returned.
- **UC-002-AC3 (A1):** Given the current record has new snow null, when the
  integration developer requests it, then new snow is `None`, the other values
  are returned, and no error is raised.
- **UC-002-AC4 (A2):** Given the API returns no record for a known study plot,
  when the integration developer requests its current record, then "no record"
  is returned and no error is raised.
- **UC-002-AC5 (A3):** Given the API returns records for 5 study plots, when the
  integration developer requests the current records of all study plots, then
  exactly 5 current records are returned, one per station, and exactly one
  request was sent.
- **UC-002-AC6 (E1):** Given the API answers `STATION_NOT_FOUND` for code `DAV2`,
  when the integration developer requests the current study-plot record of
  `DAV2`, then a *station not found* error is raised.
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
