# ADR-0001: Async HTTP Client Foundation

## Status: Accepted

## Context
The library must provide a non-blocking client for the public SLF measurement
API so that consumers — notably the planned Home Assistant integration's polling
loop — are never blocked (NFR-001). All traffic must be HTTPS-only with no
credentials, and caller-supplied station codes must be encoded safely to avoid
request/URL injection (NFR-003). The behaviour must also be testable without
hitting the live API (NFR-006). Open question: how is the HTTP layer
structured — who owns the connection/session, how are timeouts configured, and
how is the boundary made substitutable for tests?

## Decision
Build on a single `aiohttp.ClientSession`. `SlfClient` is an async context
manager (`async with SlfClient() as client: ...`) that lazily creates and owns a
session and closes it on exit. The constructor accepts an **optional**
externally supplied `session: aiohttp.ClientSession` (dependency injection); when
provided, the caller owns its lifecycle and the client does not close it. The
base URL is fixed to `https://measurement-api.slf.ch` (HTTPS only). A
configurable `aiohttp.ClientTimeout` (default total 30 s) is applied to every
request. Station codes and query parameters are passed through aiohttp's `params`
/ URL building (yarl) rather than f-string interpolation, so encoding is handled
by the HTTP layer.

Rationale: aiohttp is the chosen dependency (`01_raw_idea.md`); an injectable
session is the standard, dependency-free way to make the network boundary
substitutable for deterministic tests (NFR-006) and to let consumers share a
session/connector. A fixed HTTPS base and library-side parameter encoding satisfy
NFR-003 by construction.

## Consequences
**Positive:** Non-blocking by design (NFR-001); HTTPS-only and injection-safe
(NFR-003); test seams for mocked/recorded responses without monkeypatching
(NFR-006); consumers can reuse their own session/connector.

**Negative:** Callers must use the context manager (or explicitly close) to avoid
unclosed-session warnings; two ownership modes (owned vs injected) add a small
amount of lifecycle logic.

**Effort to change later:** Low. Swapping the HTTP backend or timeout policy is
contained behind the client; method signatures and the injected-session seam stay
stable.
