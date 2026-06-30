import asyncio
from collections.abc import Iterable
from typing import Any, Self

import aiohttp

from ._fields import FIELD_UNITS, to_utc
from .const import BASE_URL, DEFAULT_PERIOD_DAYS
from .exceptions import SlfResponseError, SlfTransportError, StationNotFoundError
from .models import Measurement, Station, StationReading

_META_FIELDS = frozenset({"station_code", "measure_date"})


class SlfClient:
    def __init__(
        self,
        *,
        session: aiohttp.ClientSession | None = None,
        timeout: aiohttp.ClientTimeout | None = None,
    ) -> None:
        self._external_session = session
        self._session = session
        self._timeout = timeout or aiohttp.ClientTimeout(total=30)

    async def __aenter__(self) -> Self:
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=self._timeout)
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        if self._external_session is None and self._session is not None:
            await self._session.close()
            self._session = None

    async def list_stations(self) -> list[Station]:
        rows = await self._fetch_rows("/public/api/imis/stations")
        return [self._to_station(row) for row in rows]

    async def get_station_measurements(self, code: str) -> StationReading:
        period = {"period_in_days": str(DEFAULT_PERIOD_DAYS)}
        # The measurements endpoint is the authority on whether the station
        # exists (unknown code -> 400 STATION_NOT_FOUND), so it is fetched first.
        measurement_rows = await self._fetch_rows(
            f"/public/api/imis/station/{code}/measurements",
            params=period,
            station_code=code,
        )
        # A station without a precipitation sensor returns 404 here; that is
        # absence, not an error (US-007).
        precipitation_rows = await self._fetch_rows(
            f"/public/api/imis/station/{code}/measurements-precipitation",
            params=period,
            station_code=code,
            absent_on_404=True,
        )
        # daily-snow has no per-station path; fetch all and filter by code.
        daily_rows = await self._fetch_rows(
            "/public/api/imis/daily-snow",
            params=period,
            station_code=code,
        )
        daily_rows = [row for row in daily_rows if row.get("station_code") == code]

        measurements: dict[str, Measurement] = {}
        self._emit_latest(measurements, measurement_rows)
        self._emit_latest(measurements, precipitation_rows, only={"RR_10MIN_SUM"})
        self._emit_latest(measurements, daily_rows, only={"HN_1D"})
        return StationReading(station_code=code, measurements=measurements)

    async def get_measurements(self, codes: Iterable[str]) -> dict[str, StationReading]:
        requested = list(dict.fromkeys(codes))
        wanted = set(requested)
        # The all-stations measurements/precipitation endpoints take no
        # period_in_days (they return the last 24 h); only daily-snow does.
        # The three independent fetches run concurrently (ADR-0006).
        meas_rows, precip_rows, daily_rows = await asyncio.gather(
            self._fetch_rows("/public/api/imis/measurements"),
            self._fetch_rows("/public/api/imis/measurements-precipitation"),
            self._fetch_rows(
                "/public/api/imis/daily-snow",
                params={"period_in_days": str(DEFAULT_PERIOD_DAYS)},
            ),
        )
        meas_by = self._group_by_code(meas_rows, wanted)
        precip_by = self._group_by_code(precip_rows, wanted)
        daily_by = self._group_by_code(daily_rows, wanted)
        present = set(meas_by) | set(precip_by) | set(daily_by)

        result: dict[str, StationReading] = {}
        for code in requested:
            # A requested code absent from every dataset is not-found (ADR-0007),
            # never a silent empty reading.
            if code not in present:
                raise StationNotFoundError(code)
            measurements: dict[str, Measurement] = {}
            self._emit_latest(measurements, meas_by.get(code, []))
            self._emit_latest(
                measurements, precip_by.get(code, []), only={"RR_10MIN_SUM"}
            )
            self._emit_latest(measurements, daily_by.get(code, []), only={"HN_1D"})
            result[code] = StationReading(station_code=code, measurements=measurements)
        return result

    @staticmethod
    def _group_by_code(
        rows: list[dict[str, Any]], wanted: set[str]
    ) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            code = row.get("station_code")
            if code in wanted:
                grouped.setdefault(code, []).append(row)
        return grouped

    @staticmethod
    def _to_station(row: dict[str, Any]) -> Station:
        return Station(
            code=row["code"],
            label=row["label"],
            canton=row["canton_code"],
            country=row["country_code"],
            elevation=float(row["elevation"]),
            latitude=float(row["lat"]),
            longitude=float(row["lon"]),
            type=row["type"],
        )

    @staticmethod
    def _emit_latest(
        target: dict[str, Measurement],
        rows: list[dict[str, Any]],
        *,
        only: Iterable[str] | None = None,
    ) -> None:
        if not rows:
            return
        allowed = frozenset(only) if only is not None else None
        latest = max(rows, key=lambda row: to_utc(row["measure_date"]))
        timestamp = to_utc(latest["measure_date"])
        for key, value in latest.items():
            if key in _META_FIELDS:
                continue
            if allowed is not None and key not in allowed:
                continue
            if value is None:
                continue
            target[key] = Measurement(
                parameter=key,
                value=float(value),
                unit=FIELD_UNITS.get(key),
                timestamp=timestamp,
            )

    async def _fetch_rows(
        self,
        path: str,
        *,
        params: dict[str, str] | None = None,
        station_code: str | None = None,
        absent_on_404: bool = False,
    ) -> list[dict[str, Any]]:
        if self._session is None:
            raise RuntimeError("SlfClient must be used as an async context manager")
        url = BASE_URL + path
        try:
            async with self._session.get(url, params=params or {}) as resp:
                if resp.status == 400:
                    body = await self._safe_json(resp)
                    if (
                        station_code is not None
                        and isinstance(body, dict)
                        and body.get("code") == "STATION_NOT_FOUND"
                    ):
                        raise StationNotFoundError(station_code)
                    raise SlfTransportError(f"Bad request for {url}")
                if resp.status == 404 and absent_on_404:
                    return []
                if resp.status != 200:
                    raise SlfTransportError(
                        f"Unexpected status {resp.status} for {url}"
                    )
                data = await resp.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError) as exc:
            raise SlfTransportError(f"Request to {url} failed: {exc}") from exc
        if not isinstance(data, list):
            raise SlfResponseError(f"Expected a list payload from {url}")
        return data

    @staticmethod
    async def _safe_json(resp: aiohttp.ClientResponse) -> Any:
        try:
            return await resp.json(content_type=None)
        except (aiohttp.ClientError, ValueError):
            return None
