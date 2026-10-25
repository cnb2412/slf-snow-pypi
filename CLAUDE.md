# Project: slf-snow-pypi

## Process: Spec-Driven Development
- The spec is the source of truth. Code must implement `docs/spec/specification.md`.
- Technology decisions are recorded in ADRs; technical constraints are NFRs
  in the spec. Do not introduce frameworks, libraries or services that no
  accepted ADR covers; propose a new ADR instead.
- Commands (install, dev, build, test, lint, typecheck) and code locations are in
  `docs/architecture/architecture.md`, section "Development & tooling".
  Read them before running commands; do not guess.
- Requirements are numbered (FR-xxx, NFR-xxx); use cases are numbered (UC-xxx);
  architecture decisions are recorded as ADRs in `docs/architecture/adr/`.
- Reference requirement/use-case IDs in commit messages and code comments
  for non-obvious logic (e.g. `// FR-012: reject expired tokens`).

### Scope of the spec rule
- Never implement behavior that is not covered by a requirement or use case.
- Needs a spec change: anything user-visible, API contracts, data model,
  new features, changes to promised behavior.
- Does NOT need a spec change: refactoring, tests, tooling, and internal
  technical details required to fulfil an existing requirement.
- If a task requires unspecified behavior: STOP, propose the spec change,
  and WAIT for explicit approval before editing the spec or implementing.

## Artifact locations
- Product brief: docs/brief.md
- Specification: docs/spec/specification.md
- Use cases: docs/spec/use-cases/UC-###-<slug>.md
- Architecture: docs/architecture/architecture.md
- ADRs: docs/architecture/adr/ADR-###-<slug>.md
- Implementation plan: docs/plan/implementation-plan.md

## Artifact flow
- Order: brief → spec → use cases → architecture/ADRs → plan → code.
  Skills: `/brief`, `/spec`, `/use-case`, `/architecture`, `/plan`, `/implement`.
- Code is written one plan step at a time via `/implement`. Do not start
  a step that is not in the plan; add new work to "Discovered work" instead.
- When an upstream artifact changes, check and update affected downstream artifacts.
- IDs are never reused or renumbered; removed requirements are marked `Deprecated`.
- Write an ADR for any decision that is hard to reverse
  (e.g. framework, hosting, data storage, authentication).
- ADR status: `Proposed` → `Accepted` → `Superseded by ADR-###`.
  Accepted ADRs are immutable; change a decision by writing a new ADR.
- Follow accepted ADRs. If a task conflicts with one, STOP and propose
  a superseding ADR instead of working around it.
- Architecture describes the result and links to ADRs; ADRs hold the reasoning.
  When an ADR changes, update `architecture.md` to match.

## Definition of done
- All tests pass; lint and typecheck are clean.
- Each implemented FR/UC has at least one test referencing its ID.
- Completed steps are checked off in `docs/plan/implementation-plan.md`.

## Conventions
- Documentation, code comments and commit messages are written in English.
- Commit messages follow Conventional Commits 1.0.0
  (https://www.conventionalcommits.org/en/v1.0.0/):
  `<type>[optional scope]: <description>` + optional body + optional footers.
  - Types: `docs` for brief/spec/use-cases/architecture/ADRs/plan,
    `chore` for tooling & skills, `feat`/`fix`/`test`/`refactor` for code,
    `build`, `ci`, `perf`, `style` where applicable.
  - Scopes: `spec`, `arch`, `plan`, or the code area (`api`, `ui`, `db`, ...).
  - Reference FR/NFR/UC/ADR IDs in the body or a `Refs:` footer.
  - Spec changes that remove or change promised behavior are breaking:
    use `!` and a `BREAKING CHANGE:` footer.
