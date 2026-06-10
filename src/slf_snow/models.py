from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Measurement:
    parameter: str
    value: float
    unit: str | None
    timestamp: datetime


@dataclass(frozen=True, slots=True)
class StationReading(Mapping[str, Measurement]):
    station_code: str
    measurements: Mapping[str, Measurement]

    def __getitem__(self, key: str) -> Measurement:
        return self.measurements[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.measurements)

    def __len__(self) -> int:
        return len(self.measurements)
