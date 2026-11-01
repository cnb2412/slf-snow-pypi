# UC-003: Get current modeled IMIS snow values

Status: Draft | Date: 2026-11-01 | Spec version: 2.0

**Primary actor:** Integration developer
**Goals:** G-02, G-03, G-04
**Covered requirements:** FR-005, FR-007, FR-008, FR-009, FR-010, FR-014,
FR-015, FR-016, FR-017, FR-018
**Related NFRs:** NFR-001, NFR-003, NFR-004, NFR-005, NFR-006

**Preconditions:** The package is installed; the integration developer knows the
station code of an IMIS station (e.g. from UC-001).
**Trigger:** The integration developer needs the modeled daily snow values of an
IMIS station. Measured values of IMIS stations are covered by UC-002 (since spec
2.0).

## Main success scenario
1. The integration developer requests the current modeled record of an IMIS
   station by its station code with one call.
2. The package sends one request for the modeled values to the SLF Measurement
   API.
3. The SLF Measurement API returns the modeled records.
4. The package selects the current record of that station (latest timestamp,
   independent of the order delivered by the API).
5. The package returns the current modeled record with its timestamp as
   timezone-aware UTC (also when the API delivers it without zone designator),
   snow height (cm) and new snow (cm). The record is recognizable as modeled
   without inspecting its origin.

## Alternative flows
- **A1 (from step 3):** The station is absent from the API response for modeled
  values. The package returns "no record" without an error, also if the station
  code is unknown (the modeled values cannot distinguish these cases). The use
  case ends.
- **A2 (from step 1):** The integration developer requests the current modeled
  records of all IMIS stations with one call. The package sends one request and
  returns the current modeled record of every station contained in the API
  response, each as in step 5. The use case ends.
- **A3 (from step 4):** One or more values of the current modeled record are
  null. The package returns them as `None` without an error and continues with
  step 5.

## Error flows
- **E1 (from step 1):** The station code is empty. The package raises a *station
  not found* error without sending a request.
- **E2 (from step 2 or A2):** The SLF Measurement API cannot be reached, does not
  answer within the time limit, or answers with HTTP 5xx or HTTP 429. The package
  raises a *service unavailable* error (see UC-004).
- **E3 (from step 3 or A2):** The response cannot be read, does not have the
  expected basic form, lacks an in-scope field or has an in-scope field of the
  wrong type, or is any other unexpected HTTP 4xx response. The package raises an
  *invalid response* error (see UC-004).

## Postconditions
- **Success:** The integration developer has the current modeled record of the
  IMIS station (or of all IMIS stations contained in the API response), or knows
  that there is no current record.
- **Minimal guarantees:** The call caused at most one request and no retry;
  modeled records cannot be confused with measured records; any failure is
  reported as a package error.

## Acceptance criteria
- **UC-003-AC1:** Moved to UC-002-AC11 (spec 2.0).
- **UC-003-AC2 (main):** Given the API returns two modeled records for `DAV2` in
  descending order with timestamps without zone designator, when the integration
  developer requests its current modeled record, then the newer record is
  returned with a timezone-aware UTC timestamp, snow height and new snow, and it
  is recognizable as modeled.
- **UC-003-AC3:** Moved to UC-002-AC12 (spec 2.0).
- **UC-003-AC4:** Moved to UC-002-AC13 (spec 2.0).
- **UC-003-AC5 (A1):** Given station `XXXX` is absent from the modeled values,
  when the integration developer requests its current modeled record, then "no
  record" is returned, no error is raised, and exactly one request was sent.
- **UC-003-AC6:** Moved to UC-002-AC14 (spec 2.0).
- **UC-003-AC7 (A2):** Given the API returns two modeled records each for 2
  stations, when the integration developer requests the current modeled records
  of all IMIS stations, then exactly 2 records are returned, each the newer one of
  its station and each recognizable as modeled.
- **UC-003-AC8:** Moved to UC-002-AC15 (spec 2.0).
- **UC-003-AC9 (E1):** Given an empty station code, when the integration
  developer requests a current modeled record, then a *station not found* error
  is raised and no request is sent.
- **UC-003-AC10 (E2):** Given the API answers with HTTP 429, when the integration
  developer requests the current modeled records of all IMIS stations, then a
  *service unavailable* error is raised.
- **UC-003-AC11 (E3):** Given a modeled record has snow height of type text, when
  the integration developer requests a current modeled record, then an *invalid
  response* error is raised.
- **UC-003-AC12 (A3):** Given the current modeled record of a station has new
  snow null, when the integration developer requests it, then new snow is `None`,
  snow height is returned, and no error is raised.
