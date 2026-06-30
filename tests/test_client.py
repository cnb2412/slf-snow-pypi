from datetime import UTC, datetime
from typing import Any

import pytest
from aioresponses import aioresponses

from slf_snow import SlfClient, SlfTransportError, StationNotFoundError
from slf_snow.const import BASE_URL

STATION = "WFJ2"
MEAS_URL = f"{BASE_URL}/public/api/imis/station/{STATION}/measurements?period_in_days=1"
PRECIP_URL = (
    f"{BASE_URL}/public/api/imis/station/{STATION}"
    "/measurements-precipitation?period_in_days=1"
)
DAILY_URL = f"{BASE_URL}/public/api/imis/daily-snow?period_in_days=1"
STATIONS_URL = f"{BASE_URL}/public/api/imis/stations"
ALL_MEAS_URL = f"{BASE_URL}/public/api/imis/measurements"
ALL_PRECIP_URL = f"{BASE_URL}/public/api/imis/measurements-precipitation"


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


async def test_list_stations_returns_all_with_metadata(
    imis_stations: list[dict[str, Any]],
) -> None:
    with aioresponses() as mocked:
        mocked.get(STATIONS_URL, payload=imis_stations)
        async with SlfClient() as client:
            stations = await client.list_stations()

    # Every IMIS station is returned (US-001), including non-snow ones (D3).
    assert len(stations) == len(imis_stations)
    types = {station.type for station in stations}
    assert {"SNOW_FLAT", "WIND"} <= types

    by_code = {station.code: station for station in stations}
    wfj2 = by_code["WFJ2"]
    # Identifying metadata is exposed and mapped from the source field names.
    assert wfj2.label == "Weissfluhjoch"
    assert wfj2.canton == "GR"
    assert wfj2.country == "CH"
    assert wfj2.elevation == 2536.0
    assert wfj2.latitude == 46.829
    assert wfj2.longitude == 9.809
    assert wfj2.type == "SNOW_FLAT"


async def test_list_stations_raises_transport_error_on_bad_status() -> None:
    with aioresponses() as mocked:
        mocked.get(STATIONS_URL, status=500)
        async with SlfClient() as client:
            with pytest.raises(SlfTransportError):
                await client.list_stations()


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


def _mock_all_stations(
    mocked: aioresponses,
    measurements: list[dict[str, Any]],
    precipitation: list[dict[str, Any]],
    daily_snow: list[dict[str, Any]],
) -> None:
    mocked.get(ALL_MEAS_URL, payload=measurements)
    mocked.get(ALL_PRECIP_URL, payload=precipitation)
    mocked.get(DAILY_URL, payload=daily_snow)


async def test_get_measurements_returns_reading_per_requested_code(
    imis_all_measurements: list[dict[str, Any]],
    imis_all_precipitation: list[dict[str, Any]],
    imis_all_daily_snow: list[dict[str, Any]],
) -> None:
    with aioresponses() as mocked:
        _mock_all_stations(
            mocked, imis_all_measurements, imis_all_precipitation, imis_all_daily_snow
        )
        async with SlfClient() as client:
            readings = await client.get_measurements(["WFJ2", "KLO2"])

    # Each requested station is addressable by its code (US-003).
    assert set(readings) == {"WFJ2", "KLO2"}
    assert readings["KLO2"].station_code == "KLO2"

    # Each series is reduced to its latest row (ADR-0005).
    assert readings["KLO2"]["HS"].value == 120.0
    assert readings["WFJ2"]["HS"].value == 0.0
    # HN24 comes from daily-snow's latest row.
    assert readings["KLO2"]["HN_1D"].value == 5.0
    # Precipitation is present only for the station that reports it (US-007).
    assert "RR_10MIN_SUM" in readings["KLO2"]
    assert readings["KLO2"]["RR_10MIN_SUM"].value == 1.2
    assert "RR_10MIN_SUM" not in readings["WFJ2"]


async def test_get_measurements_raises_not_found_for_unknown_code(
    imis_all_measurements: list[dict[str, Any]],
    imis_all_precipitation: list[dict[str, Any]],
    imis_all_daily_snow: list[dict[str, Any]],
) -> None:
    with aioresponses() as mocked:
        _mock_all_stations(
            mocked, imis_all_measurements, imis_all_precipitation, imis_all_daily_snow
        )
        async with SlfClient() as client:
            with pytest.raises(StationNotFoundError):
                await client.get_measurements(["WFJ2", "NOPE"])
