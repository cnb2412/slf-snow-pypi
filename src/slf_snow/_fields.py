from datetime import UTC, datetime

# Units are not returned by the SLF API; they are derived from the source field
# name. See ADR-0008.
FIELD_UNITS: dict[str, str] = {
    "HS": "cm",
    "HN_1D": "cm",
    "TA_30MIN_MEAN": "°C",
    "TSS_30MIN_MEAN": "°C",
    "TS0_30MIN_MEAN": "°C",
    "TS25_30MIN_MEAN": "°C",
    "TS50_30MIN_MEAN": "°C",
    "TS100_30MIN_MEAN": "°C",
    "RH_30MIN_MEAN": "%",
    "VW_30MIN_MEAN": "m/s",
    "VW_30MIN_MAX": "m/s",
    "DW_30MIN_MEAN": "°",
    "DW_30MIN_SD": "°",
    "RSWR_30MIN_MEAN": "W/m²",
    "RR_10MIN_SUM": "mm",
}


def to_utc(value: str) -> datetime:
    """Parse an SLF ``measure_date`` into a timezone-aware UTC datetime.

    The API mixes formats: ``/measurements`` returns a ``Z`` suffix, while
    ``daily-snow`` returns a naive midnight date which is treated as UTC.
    """
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)
