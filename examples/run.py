"""Manual smoke test against the live SLF API. Not run in CI.

Usage: uv run python examples/run.py [STATION_CODE]
"""

import asyncio
import sys

from slf_snow import SlfClient


async def main(code: str) -> None:
    async with SlfClient() as client:
        reading = await client.get_station_measurements(code)
    print(f"Station {code}: {len(reading)} measurements")
    for parameter, measurement in sorted(reading.items(), key=lambda item: item[0]):
        unit = measurement.unit or ""
        print(
            f"  {parameter:<18} {measurement.value:>10} {unit:<5}"
            f" @ {measurement.timestamp.isoformat()}"
        )


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "WFJ2"))
