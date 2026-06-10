import json
from pathlib import Path
from typing import Any

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> Any:
    return json.loads((FIXTURES / name).read_text())


@pytest.fixture
def imis_measurements() -> list[dict[str, Any]]:
    data: list[dict[str, Any]] = _load("imis_wfj2_measurements.json")
    return data


@pytest.fixture
def imis_daily_snow() -> list[dict[str, Any]]:
    data: list[dict[str, Any]] = _load("imis_daily_snow.json")
    return data
