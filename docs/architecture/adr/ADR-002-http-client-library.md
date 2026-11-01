# ADR-002: HTTP client library

Status: Proposed | Date: 2026-10-31

## Context
The package needs an asynchronous HTTP client to call the SLF Measurement API.
Because the consumer can supply an HTTP session of their own (NFR-009), the
session type of the chosen client becomes part of the public interface;
changing it later would be a breaking change. Home Assistant's library guide
says "Use `aiohttp` and let the caller pass in the `ClientSession`"; the
Platinum rule `inject-websession` accepts aiohttp or HTTPX sessions. Current
versions: aiohttp 3.14.5 (Apache-2.0 AND MIT), httpx 0.28.1 (BSD-3-Clause);
Home Assistant Core pins exactly these versions.

## Decision drivers
- Constraint NFR-001: asynchronous, non-blocking interface.
- Constraint NFR-009: consumer-supplied HTTP session, never closed by the package.
- Constraint NFR-010: OSI-approved licenses for runtime dependencies.
- NFR-004: at most one request per network covered by a call, no automatic
  retries.
- NFR-006: time limit of 10 s (configurable), also with a supplied session and
  across the two concurrent requests of FR-019.
- FR-015: connection failures and timeouts must be recognizable.

## Considered options
1. aiohttp
2. httpx
3. Own transport abstraction with adapters for aiohttp and httpx
4. Standard library only (asyncio streams, own HTTP handling)

## Decision
We use aiohttp, because it is the client Home Assistant recommends for
libraries and the type of Home Assistant's shared session (NFR-009, G-06), it
supports a per-request time limit independent of who created the session
(NFR-006), and its license is OSI-approved (NFR-010). The consumer may pass an
aiohttp client session; if none is passed, the package creates its own session
and closes it when the consumer closes the client. The package configures no
retry behavior (NFR-004).

## Consequences
- **Positive:** Directly fits Home Assistant's shared session; single runtime
  dependency; Home Assistant keeps the version current.
- **Negative:** The aiohttp session type is part of the public interface;
  switching clients later is a breaking change. Consumers outside Home Assistant
  must use aiohttp sessions if they want to share one.
- **Follow-ups:** Declare aiohttp with a lower bound only (no exact pin) so it
  stays compatible with Home Assistant's pin; map aiohttp connection errors and
  timeouts to *service unavailable* (FR-015); build request URLs so that station
  codes are encoded as one path segment (FR-017).

## Rejected options
**httpx:** Also accepted by Home Assistant, but not the client its library guide
recommends, and the project has stayed on 0.28.x for a long time.

**Own abstraction for both clients:** No goal requires supporting both; doubles
the test effort and goes beyond the goals.

**Standard library only:** Violates NFR-009, because a Home Assistant session
cannot be accepted; would also require implementing TLS and HTTP handling.

## Sources
- https://contributors.home-assistant.io/core/integrations/api-library/
- https://contributors.home-assistant.io/core/quality-scale/inject-websession/
- https://github.com/home-assistant/core/blob/dev/homeassistant/package_constraints.txt
- https://pypi.org/project/aiohttp/
- https://pypi.org/project/httpx/
