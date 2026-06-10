class SlfSnowError(Exception):
    """Base class for all slf-snow errors."""


class StationNotFoundError(SlfSnowError):
    """Raised when the SLF API reports an unknown station code."""

    def __init__(self, station_code: str) -> None:
        self.station_code = station_code
        super().__init__(f"Unknown station code: {station_code!r}")


class SlfTransportError(SlfSnowError):
    """Raised on transport/protocol failures (timeout, connection, bad status)."""


class SlfResponseError(SlfSnowError):
    """Raised when the API returns an unexpected or unparseable payload."""
