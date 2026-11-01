# ADR-006: License

Status: Proposed | Date: 2026-10-31

## Context
The package needs an OSI-approved license stated in its metadata (NFR-010,
Home Assistant library requirement). After the first release the license is
practically fixed, because published versions keep their license. The only
runtime dependency, aiohttp, is licensed "Apache-2.0 AND MIT"; Home Assistant
Core is licensed Apache-2.0. The package contains no SLF data; the SLF data
itself is licensed CC BY 4.0 (brief constraint, NFR-007).

## Decision drivers
- Constraint NFR-010: OSI-approved license for the package and its runtime
  dependencies, stated in the metadata.
- G-06: usable in Home Assistant Core.
- Brief: a public package for any Python developer.

## Considered options
1. MIT
2. Apache-2.0
3. BSD-3-Clause
4. A copyleft license (LGPL/GPL)

## Decision
We license the package under MIT, because it is the simplest OSI-approved
license with the fewest obligations for consumers, is compatible with aiohttp
and Home Assistant Core (NFR-010, G-06), and is widely used by Home Assistant
libraries.

## Consequences
- **Positive:** Minimal obligations for consumers; no compatibility concerns
  with the dependency or Home Assistant.
- **Negative:** No explicit patent grant, unlike Apache-2.0.
- **Follow-ups:** Add a `LICENSE` file and the SPDX license expression `MIT` to
  the project metadata; test fixtures derived from SLF responses carry a
  separate CC BY 4.0 attribution note (see ADR-004).

## Rejected options
**Apache-2.0:** Equally suitable and identical to Home Assistant Core's license,
with a patent grant, but adds formalities (change notices, NOTICE file) that
bring no benefit for this package.

**BSD-3-Clause:** Practically equivalent to MIT; no reason to prefer it.

**Copyleft:** Conflicts with the goal of broad reuse and inclusion in
Apache-2.0 projects such as Home Assistant.

## Sources
- https://contributors.home-assistant.io/core/integrations/api-library/
- https://pypi.org/project/aiohttp/
