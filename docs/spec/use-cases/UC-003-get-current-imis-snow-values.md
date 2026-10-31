# UC-003: Get current IMIS snow values (measured and modeled)

Status: Draft | Date: 2026-10-31 | Spec version: 0.3

**Primary actor:** Integration developer
**Goals:** G-02, G-03, G-04
**Covered requirements:** FR-004, FR-005, FR-007, FR-008, FR-009, FR-010,
FR-011, FR-014, FR-015, FR-016, FR-017, FR-018
**Related NFRs:** NFR-001, NFR-003, NFR-004, NFR-005, NFR-006

**Preconditions:** The package is installed; the integration developer knows the
station code of an IMIS station (e.g. from UC-001).
**Trigger:** The integration developer needs the current snow height or the
modeled daily snow values of an IMIS station.

## Main success scenario
1. The integration developer requests the current measured record of an IMIS
   station by its station code with one call.
2. The package sends one request to the SLF Measurement API, transmitting the
   station code only as a station identifier.
3. The SLF Measurement API returns the measured records of that station.
4. The package selects the current record (latest timestamp, independent of the
   order delivered by the API).
5. The package returns the current measured record with its timestamp as
   timezone-aware UTC and snow height (cm).

## Alternative flows
- **A1 (from step 1):** The integration developer requests the current modeled
  record of an IMIS station instead. The package sends one request for the
  modeled values, selects the current record of that station as in step 4, and
  returns it with its timestamp as timezone-aware UTC (also when the API delivers
  it without zone designator), snow height (cm) and new snow (cm). The record is
  recognizable as modeled without inspecting its origin. The use case ends.
- **A2 (from step 4):** The snow height of the current record is null (e.g. at a
  wind station). The package returns it as `None` without an error and continues
  with step 5.
- **A3 (from step 3):** The SLF Measurement API returns no measured record for the
  station. The package returns "no record" without an error. The use case ends.
- **A4 (from A1):** The station is absent from the API response for modeled
  values. The package returns "no record" without an error, also if the station
  code is unknown (the modeled values cannot distinguish these cases). The use
  case ends.
- **A5 (from step 1):** The integration developer requests the current measured
  records of all IMIS stations with one call. The package sends one request and
  returns the current record of every station contained in the API response, each
  as in step 5; stations without a current record are not included. The use case
  ends.
- **A6 (from step 1):** The integration developer requests the current modeled
  records of all IMIS stations with one call. The package sends one request and
  returns the current modeled record of every station contained in the API
  response, each as in A1. The use case ends.

## Error flows
- **E1 (from step 3):** The SLF Measurement API reports the station code as
  unknown, including a valid study-plot code. The package raises a *station not
  found* error. No record is returned.
- **E2 (from step 1 or A1):** The station code is empty. The package raises a
  *station not found* error without sending a request.
- **E3 (from step 2, A1, A5 or A6):** The SLF Measurement API cannot be reached,
  does not answer within the time limit, or answers with HTTP 5xx or HTTP 429.
  The package raises a *service unavailable* error (see UC-004).
- **E4 (from step 3, A1, A5 or A6):** The response cannot be read, does not have
  the expected basic form, lacks an in-scope field or has an in-scope field of the
  wrong type, or is any other unexpected HTTP 4xx response. The package raises an
  *invalid response* error (see UC-004).

## Postconditions
- **Success:** The integration developer has the current measured or modeled
  record of the IMIS station (or of all IMIS stations contained in the API
  response), or knows that there is no current record.
- **Minimal guarantees:** The call caused at most one request and no retry;
  measured and modeled records cannot be confused; any failure is reported as a
  package error.

## Acceptance criteria
- **UC-003-AC1 (main):** Given the API returns 336 measured records for `DAV2` in
  ascending order, when the integration developer requests its current measured
  record, then the record with the latest timestamp is returned with a
  timezone-aware UTC timestamp and snow height, and exactly one request was sent.
- **UC-003-AC2 (A1):** Given the API returns two modeled records for `DAV2` in
  descending order with timestamps without zone designator, when the integration
  developer requests its current modeled record, then the newer record is
  returned with a timezone-aware UTC timestamp, snow height and new snow, and it
  is recognizable as modeled.
- **UC-003-AC3 (A2):** Given the current measured record of a wind station has
  snow height null, when the integration developer requests it, then snow height
  is `None` and no error is raised.
- **UC-003-AC4 (A3):** Given the API returns no measured record for a known IMIS
  station, when the integration developer requests its current measured record,
  then "no record" is returned and no error is raised.
- **UC-003-AC5 (A4):** Given station `XXXX` is absent from the modeled values,
  when the integration developer requests its current modeled record, then "no
  record" is returned, no error is raised, and exactly one request was sent.
- **UC-003-AC6 (A5):** Given the API returns measured records for 3 IMIS stations,
  when the integration developer requests the current measured records of all
  IMIS stations, then exactly 3 current records are returned, one per station.
- **UC-003-AC7 (A6):** Given the API returns two modeled records each for 2
  stations, when the integration developer requests the current modeled records
  of all IMIS stations, then exactly 2 records are returned, each the newer one of
  its station and each recognizable as modeled.
- **UC-003-AC8 (E1):** Given the API answers `STATION_NOT_FOUND` for code `4AO0`,
  when the integration developer requests the current measured IMIS record of
  `4AO0`, then a *station not found* error is raised.
- **UC-003-AC9 (E2):** Given an empty station code, when the integration
  developer requests a current measured or modeled record, then a *station not
  found* error is raised and no request is sent.
- **UC-003-AC10 (E3):** Given the API answers with HTTP 429, when the integration
  developer requests the current modeled records of all IMIS stations, then a
  *service unavailable* error is raised.
- **UC-003-AC11 (E4):** Given a modeled record has snow height of type text, when
  the integration developer requests a current modeled record, then an *invalid
  response* error is raised.
