from datetime import UTC, datetime
from typing import Any

import pytest
from aioresponses import aioresponses

from slf_snow import SlfClient, StationNotFoundError
from slf_snow.const import BASE_URL

STATION = "WFJ2"
MEAS_URL = f"{BASE_URL}/public/api/imis/station/{STATION}/measurements?period_in_days=1"
PRECIP_URL = (
    f"{BASE_URL}/public/api/imis/station/{STATION}"
    "/measurements-precipitation?period_in_days=1"
)
DAILY_URL = f"{BASE_URL}/public/api/imis/daily-snow?period_in_days=1"


def _mock_wfj2(
    mocked: aioresponses,
    measurements: list[dict[str, Any]],
    daily_snow: list[dict[str, Any]],
) -> None:
    mocked.get(MEAS_URL, payload=measurements)
    mocked.get(PRECIP_URL, status=404)  # WFJ2 has no precipitation sensor
    mocked.get(DAILY_URL, payload=daily_snow)


async def test_composes_endpoints_and_reduces_to_latest(
    imis_measurements: list[dict[str, Any]],
    imis_daily_snow: list[dict[str, Any]],
) -> None:
    with aioresponses() as mocked:
        _mock_wfj2(mocked, imis_measurements, imis_daily_snow)
        async with SlfClient() as client:
            reading = await client.get_station_measurements(STATION)

    # HS comes from the sub-daily measurements series, reduced to the latest row.
    assert reading["HS"].unit == "cm"
    assert reading["HS"].timestamp == datetime(2026, 6, 9, 21, 0, tzinfo=UTC)
    # A weather value carries its native unit (US-004).
    assert reading["TA_30MIN_MEAN"].unit == "°C"
    # HN24 is sourced from daily-snow's HN_1D field (ADR-0005).
    assert "HN_1D" in reading
    assert reading["HN_1D"].unit == "cm"
    assert reading["HN_1D"].timestamp.tzinfo is UTC


async def test_missing_field_is_absent_not_zero(
    imis_measurements: list[dict[str, Any]],
    imis_daily_snow: list[dict[str, Any]],
) -> None:
    with aioresponses() as mocked:
        _mock_wfj2(mocked, imis_measurements, imis_daily_snow)
        async with SlfClient() as client:
            reading = await client.get_station_measurements(STATION)

    # A genuine 0.0 reading is present and distinguishable from absent (US-005).
    assert reading["HS"].value == 0.0
    # The latest row has DW_30MIN_SD == null -> absent, not coerced to 0.
    assert "DW_30MIN_SD" not in reading
    # WFJ2 reports no precipitation (endpoint 404) -> absent, no error (US-007).
    assert "RR_10MIN_SUM" not in reading


async def test_unknown_station_raises_not_found() -> None:
    with aioresponses() as mocked:
        mocked.get(
            f"{BASE_URL}/public/api/imis/station/NOPE/measurements?period_in_days=1",
            status=400,
            payload={
                "code": "STATION_NOT_FOUND",
                "title": "Bad Request",
                "status": 400,
            },
        )
        async with SlfClient() as client:
            with pytest.raises(StationNotFoundError):
                await client.get_station_measurements("NOPE")
