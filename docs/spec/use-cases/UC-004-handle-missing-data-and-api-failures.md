# UC-004: Handle missing data and API failures

Status: Draft | Date: 2026-10-31 | Spec version: 0.3

**Primary actor:** Integration developer
**Goals:** G-04
**Covered requirements:** FR-009, FR-010, FR-011, FR-014, FR-015, FR-016,
FR-017
**Related NFRs:** NFR-004, NFR-006

**Preconditions:** The package is installed; the integration developer uses any
data operation of UC-001, UC-002 or UC-003.
**Trigger:** The SLF Measurement API fails, answers unexpectedly, or delivers
incomplete data during a call.

## Main success scenario
1. The integration developer makes a call to any data operation and is prepared
   to catch package errors.
2. The package sends one request to the SLF Measurement API.
3. The SLF Measurement API cannot be reached.
4. The package raises a *service unavailable* error without retrying the
   request.
5. The integration developer catches the error as a package error and recognizes
   it as *service unavailable*, i.e. a transient failure.

## Alternative flows
- **A1 (from step 1):** The integration developer has set a time limit of their
  own. If the SLF Measurement API does not answer, the call ends with a *service
  unavailable* error no later than that limit instead of the default 10 s.
  Continues with step 5.
- **A2 (from step 3):** The SLF Measurement API answers with records in which
  values or station attributes are null. The package returns them as `None`
  without an error. The use case ends.
- **A3 (from step 3):** The SLF Measurement API returns no record for a station,
  or omits the station from the modeled values. The package returns "no record"
  without an error. The use case ends.
- **A4 (from step 3):** The SLF Measurement API answers with fields that are not
  in scope having changed, been added or been removed. The package ignores them
  and returns the in-scope data without an error. The use case ends.

## Error flows
- **E1 (from step 3):** The SLF Measurement API does not answer within the time
  limit (default 10 s). The package raises a *service unavailable* error.
- **E2 (from step 3):** The SLF Measurement API answers with HTTP 5xx. The package
  raises a *service unavailable* error.
- **E3 (from step 3):** The SLF Measurement API answers with HTTP 429. The package
  raises a *service unavailable* error.
- **E4 (from step 3):** The response cannot be read. The package raises an
  *invalid response* error.
- **E5 (from step 3):** The response does not have the expected basic form (a list
  of entries). The package raises an *invalid response* error.
- **E6 (from step 3):** An entry lacks an in-scope field or has an in-scope field
  of the wrong type. The package raises an *invalid response* error.
- **E7 (from step 3):** The SLF Measurement API answers with an HTTP 4xx response
  other than `STATION_NOT_FOUND` and HTTP 429 (e.g. HTTP 422). The package raises
  an *invalid response* error, i.e. a persistent failure.
- **E8 (from step 3):** The SLF Measurement API reports the station code as
  unknown. The package raises a *station not found* error.
- **E9 (from step 1):** The station code is empty. The package raises a *station
  not found* error without sending a request (step 2 is skipped).

In every error flow, the integration developer catches the error as a package
error, as in step 5.

## Postconditions
- **Success:** The integration developer can tell transient failures (*service
  unavailable*), persistent failures (*invalid response*) and wrong station codes
  (*station not found*) apart, and missing data never appears as an error.
- **Minimal guarantees:** The call caused at most one request and no retry; no
  error other than a package error escapes for the conditions of E1 to E9; the
  call ends no later than the time limit.

## Acceptance criteria
- **UC-004-AC1 (main):** Given the API cannot be reached, when the integration
  developer makes any data call, then a *service unavailable* error is raised
  that is catchable as a package error, and exactly one connection attempt was
  made.
- **UC-004-AC2 (A1):** Given the integration developer set a time limit of 2 s
  and the API does not answer, when they make a data call, then a *service
  unavailable* error is raised no later than 2 s after the request was sent.
- **UC-004-AC3 (A2):** Given the API returns a record with all values null, when
  the integration developer requests it, then all values are `None` and no error
  is raised.
- **UC-004-AC4 (A3):** Given the API returns no record for a known station, when
  the integration developer requests its current record, then "no record" is
  returned and no error is raised.
- **UC-004-AC5 (A4):** Given the API response contains an additional unknown
  field and lacks an out-of-scope field such as `TA_30MIN_MEAN`, when the
  integration developer requests a current IMIS record, then the in-scope data is
  returned and no error is raised.
- **UC-004-AC6 (E1):** Given the API does not answer and no time limit was set,
  when the integration developer makes a data call, then a *service unavailable*
  error is raised no later than 10 s after the request was sent.
- **UC-004-AC7 (E2):** Given the API answers with HTTP 500, when the integration
  developer makes a data call, then a *service unavailable* error is raised and
  no second request is sent.
- **UC-004-AC8 (E3):** Given the API answers with HTTP 429, when the integration
  developer makes a data call, then a *service unavailable* error is raised and
  no second request is sent.
- **UC-004-AC9 (E4):** Given the API answers with a body that is not readable as
  data, when the integration developer makes a data call, then an *invalid
  response* error is raised.
- **UC-004-AC10 (E5):** Given the API answers with a single object instead of a
  list, when the integration developer requests a station list, then an *invalid
  response* error is raised.
- **UC-004-AC11 (E6):** Given an entry lacks the in-scope field `HS`, when the
  integration developer requests a current record, then an *invalid response*
  error is raised.
- **UC-004-AC12 (E7):** Given the API answers with HTTP 422, when the integration
  developer makes a data call, then an *invalid response* error is raised.
- **UC-004-AC13 (E8):** Given the API answers `STATION_NOT_FOUND`, when the
  integration developer requests a current record, then a *station not found*
  error is raised.
- **UC-004-AC14 (E9):** Given an empty station code, when the integration
  developer requests a current record, then a *station not found* error is raised
  and no request is sent.
