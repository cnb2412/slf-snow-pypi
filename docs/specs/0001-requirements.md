# Technical Spec 0001 — Client Surface

> Implementation spec for the `slf_snow` client. Realises the user stories in
> [`../discovery/03_requirements.md`](../discovery/03_requirements.md) per the
> ADRs in [`../discovery/decisions/`](../discovery/decisions/README.md). Endpoint
> shapes are grounded in `https://measurement-api.slf.ch/openapi.json`.

## Client

`SlfClient` is an async context manager owning an `aiohttp.ClientSession` (or an
injected one), with a fixed HTTPS base URL and a configurable timeout
(ADR-0001). All requests go through `_fetch_rows`, which returns the JSON list
payload and maps failures to typed errors:

- non-200 (other than the cases below) → `SlfTransportError`
- transport/timeout (`aiohttp.ClientError`, `TimeoutError`) → `SlfTransportError`
- payload that is not a JSON list → `SlfResponseError`
- HTTP 400 with body `{"code": "STATION_NOT_FOUND"}` → `StationNotFoundError`
  (only when a `station_code` context is supplied)

## `list_stations()` — US-001 / FR-1

`async def list_stations(self) -> list[Station]`

- **Endpoint:** `GET /public/api/imis/stations` — **no query parameters**.
- Returns every automated (IMIS) station, including non-snow ones (D3); the
  station label is passed through unchanged (D7).
- Each row is mapped to a frozen `Station` dataclass (ADR-0002, ADR-0009):

  | `Station` field | Source field | Type |
  | --- | --- | --- |
  | `code` | `code` | str |
  | `label` | `label` | str |
  | `canton` | `canton_code` | str |
  | `country` | `country_code` | str |
  | `elevation` | `elevation` | float |
  | `latitude` | `lat` | float |
  | `longitude` | `lon` | float |
  | `type` | `type` | str (e.g. `SNOW_FLAT`, `WIND`) |

*Traces to:* FR-1, D2, D3, D7 · ADR-0002, ADR-0009 · Journey A.

## `get_station_measurements(code)` — US-002, US-004…US-007

`async def get_station_measurements(self, code: str) -> StationReading`

Composes one current `StationReading` from three time-series endpoints, each
queried with `period_in_days=1` and reduced to the most recent row by
`measure_date` (ADR-0005):

- `GET /public/api/imis/station/{code}/measurements` — `HS` plus weather values.
- `GET /public/api/imis/daily-snow` — `HN_1D` (HN24); has no per-station path and
  is filtered by `station_code` client-side.
- `GET /public/api/imis/station/{code}/measurements-precipitation` —
  `RR_10MIN_SUM`; a 404 means the station has no precipitation sensor and yields
  absence, not an error (US-007).

Each `Measurement` carries `value`, `unit` (from the static field catalog in
`_fields.FIELD_UNITS`) and a UTC `timestamp` (US-004). A `null`/absent source
value is omitted; a genuine `0.0` is kept (US-005). An unknown code raises
`StationNotFoundError` (US-006).

*Traces to:* FR-2, FR-4…FR-7, D1, D4, D5 · ADR-0003…ADR-0008.

## `get_measurements(codes)` — US-003 / FR-3

`async def get_measurements(self, codes: Iterable[str]) -> dict[str, StationReading]`

Fetches the three **all-stations** endpoints once each, concurrently
(`asyncio.gather`), so batch cost is constant (3 requests) regardless of how many
codes are requested (ADR-0006):

- `GET /public/api/imis/measurements` — **no query params** (last 24 h).
- `GET /public/api/imis/measurements-precipitation` — **no query params**.
- `GET /public/api/imis/daily-snow` — with `period_in_days=1`.

Each endpoint returns rows for every station, carrying a `station_code`. Rows are
grouped by code (keeping only the requested codes), and each group is reduced to
its latest row and merged into a `StationReading` exactly as the single-station
path does. The result is a `dict[str, StationReading]` addressable by code.

A requested code absent from **all three** datasets raises
`StationNotFoundError(code)` — never a silent empty reading (ADR-0007). Duplicate
input codes are de-duplicated; input order is preserved.

*Traces to:* FR-3, D6 · ADR-0006, ADR-0007 · Journey C.
