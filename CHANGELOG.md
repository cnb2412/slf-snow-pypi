# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `Station` model and `SlfClient.list_stations()` — full IMIS station discovery
  with code, label, canton, country, elevation, coordinates and type
  (US-001 / FR-1).
- `SlfClient.get_measurements(codes)` — batch readings for several stations from
  the three all-stations endpoints fetched concurrently (`asyncio.gather`), so
  cost stays constant regardless of how many codes are requested. Rows are
  grouped by `station_code` and reduced to the latest per series; a code absent
  from all datasets raises `StationNotFoundError` (US-003 / FR-3, ADR-0006/0007).
