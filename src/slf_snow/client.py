from collections.abc import Iterable
from typing import Any, Self

import aiohttp

from ._fields import FIELD_UNITS, to_utc
from .const import BASE_URL, DEFAULT_PERIOD_DAYS
from .exceptions import SlfResponseError, SlfTransportError, StationNotFoundError
from .models import Measurement, StationReading

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

    async def get_station_measurements(self, code: str) -> StationReading:
        # The measurements endpoint is the authority on whether the station
        # exists (unknown code -> 400 STATION_NOT_FOUND), so it is fetched first.
        measurement_rows = await self._fetch_rows(
            f"/public/api/imis/station/{code}/measurements",
            station_code=code,
        )
        # A station without a precipitation sensor returns 404 here; that is
        # absence, not an error (US-007).
        precipitation_rows = await self._fetch_rows(
            f"/public/api/imis/station/{code}/measurements-precipitation",
            station_code=code,
            absent_on_404=True,
        )
        # daily-snow has no per-station path; fetch all and filter by code.
        daily_rows = await self._fetch_rows(
            "/public/api/imis/daily-snow",
            station_code=code,
        )
        daily_rows = [row for row in daily_rows if row.get("station_code") == code]

        measurements: dict[str, Measurement] = {}
        self._emit_latest(measurements, measurement_rows)
        self._emit_latest(measurements, precipitation_rows, only={"RR_10MIN_SUM"})
        self._emit_latest(measurements, daily_rows, only={"HN_1D"})
        return StationReading(station_code=code, measurements=measurements)

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
        station_code: str,
        absent_on_404: bool = False,
    ) -> list[dict[str, Any]]:
        if self._session is None:
            raise RuntimeError("SlfClient must be used as an async context manager")
        url = BASE_URL + path
        params = {"period_in_days": str(DEFAULT_PERIOD_DAYS)}
        try:
            async with self._session.get(url, params=params) as resp:
                if resp.status == 400:
                    body = await self._safe_json(resp)
                    if (
                        isinstance(body, dict)
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
