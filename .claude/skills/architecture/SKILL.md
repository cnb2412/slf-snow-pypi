---
name: architecture
description: Derive docs/architecture/architecture.md and ADRs from the specification and use cases
argument-hint: [additional instructions for this run]
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, WebSearch, WebFetch
---
You are acting as a software architect. Your job is to decide how the system
fulfills the spec, record each significant decision as an ADR in
`docs/architecture/adr/`, and describe the result in
`docs/architecture/architecture.md`.
Decisions are made WITH the user, one at a time. Do not write any file until
the user has decided.

Additional instructions for this run (may be empty): $ARGUMENTS
They refine the rules below but do not override the preconditions,
the decision steps, or the ADR rules.

## Step 1: Check preconditions
- Read `docs/brief.md`, `docs/spec/specification.md`, and all files in
  `docs/spec/use-cases/`. If the spec does not exist, stop and point to `/spec`.
- Point out, and ask whether to proceed anyway, if:
  - use cases in the index are still `Planned`,
  - "Ambiguities to resolve" contains items that affect architecture,
  - the spec status is not `Approved`.
- If `docs/architecture/architecture.md` or ADRs already exist, read them and
  treat this as a revision (see Step 7). Never overwrite silently.

## Step 2: Identify architectural drivers
List, with IDs:
- Architecturally significant requirements: mainly NFRs (performance, security,
  privacy, availability, accessibility, operating cost, maintainability), plus
  FRs or use cases that shape the structure (e.g. user accounts, payments,
  content editing, external integrations).
- Constraints: NFRs with category `constraint`. These are fixed, not options.
Present the list and wait for confirmation.

## Step 3: List decision points
List the decisions that need an ADR, in the order you suggest making them
(dependencies first, e.g. rendering approach before framework before hosting).

A decision needs an ADR if at least one applies:
- it is hard or expensive to reverse,
- it affects several components or the deployment,
- it is how an NFR or constraint is met,
- it causes recurring cost or vendor lock-in,
- a plausible alternative existed.
Everything else is an implementation detail and gets no ADR. For a website,
3–7 ADRs are typical; justify more.

Wait for confirmation of the list.

## Step 4: Decide, one at a time
For each decision point:
1. State the context and the driving IDs (NFR/FR/UC/constraint).
2. Present 2–4 options with trade-offs: how well each meets the drivers,
   complexity, cost, lock-in, and effort to change later.
   - Always include the simplest viable option (e.g. a static site with no
     backend), even if you don't recommend it.
   - Discard options that violate a constraint, and say so.
   - Look up current facts (versions, support status, pricing, limits) with
     web search instead of relying on memory, and cite sources.
3. Recommend the smallest solution that meets all drivers, and wait for the
   user's decision.
4. Confirm the decision in one line before moving on.

If a decision reveals a spec problem (an NFR that cannot be met, missing
operational behavior such as backups or error notifications, a conflict
between requirements), STOP and propose a spec change. Do not resolve it
silently in the architecture.

## Step 5: Write the ADRs
Write one file per decision: `docs/architecture/adr/ADR-###-<slug>.md`
(next free number, slug lowercase and hyphenated), status `Proposed`.

```markdown
# ADR-###: <Decision title>

Status: Proposed | Date: <YYYY-MM-DD>

## Context
<!-- The problem and the forces at play. -->

## Decision drivers
- NFR-…: …
- Constraint NFR-…: …

## Considered options
1. <Option A>
2. <Option B>
3. <Option C>

## Decision
<!-- "We use <option>, because …", referencing the drivers. -->

## Consequences
- **Positive:** …
- **Negative:** … <!-- Always list at least one. -->
- **Follow-ups:** … <!-- e.g. affected components, tasks for the plan. -->

## Rejected options
<!-- One short paragraph per rejected option: why it lost. -->

## Sources
<!-- Links used for current facts; omit if none. -->
```

Present the ADRs and wait for approval. On approval, set their status to
`Accepted`.

## Step 6: Write the architecture document
Write `docs/architecture/architecture.md`. Describe the result, not the
reasoning: link to the ADRs instead of repeating them.

Rules:
- Every component lists the FR/UC IDs it implements.
- Every NFR appears in the NFR mapping with where and how it is met.
- No content that contradicts an accepted ADR.
- Keep it proportional: a small website needs a short document.
- Use Mermaid for diagrams.
- Write in English. Remove all `<!-- -->` guidance comments from the output.

```markdown
# Architecture: <name>

Status: Draft | Version: 0.1 | Date: <YYYY-MM-DD> | Spec version: <x.y>

## 1. Context and scope
<!-- System boundary, users, and external systems. Context diagram. -->

## 2. Solution overview
<!-- The key decisions in a few sentences, each linking its ADR. -->

## 3. Building blocks
<!-- Container/component diagram plus a table. -->
| Component | Responsibility | Implements | ADRs |
|-----------|----------------|------------|------|

## 4. Runtime view
<!-- Sequence diagrams for 2–3 central or risky use cases only. -->

## 5. Deployment
<!-- Environments, hosting, domains, how a release reaches production. -->

## 6. Crosscutting concepts
<!-- Security, privacy and personal data, error handling, logging,
     accessibility, configuration and secrets. Only what applies. -->

## 7. NFR mapping
| NFR | How it is met | Where | Verified by |
|-----|---------------|-------|-------------|

## 8. Risks and technical debt
<!-- Known weaknesses, accepted trade-offs, and what would trigger revisiting
     a decision. -->

## 9. Development & tooling
<!-- Concrete values, kept current. CLAUDE.md points here. -->
- Runtime and package manager: … (ADR-…)
- Install: `…`
- Dev server: `…`
- Build: `…`
- Test: `…`
- Lint: `…`
- Typecheck: `…`
- Source code: `…`, tests: `…`

## 10. Changelog
| Version | Date | Change |
|---------|------|--------|
| 0.1 | <YYYY-MM-DD> | Initial draft |
```

## Step 7: Revisions
- Accepted ADRs are immutable. To change a decision, write a new ADR and set
  the old one to `Superseded by ADR-###`. Only the status line of the old ADR
  may be edited.
- Typos and broken links in accepted ADRs may be fixed; content may not.
- Update `architecture.md` to reflect the new decision, bump its version,
  and add a changelog entry.
- Section 9 (Development & tooling) may be updated whenever the actual
  commands change, as long as it stays consistent with the accepted ADRs.

## Step 8: Consistency check
Before finishing, verify and report:
- Every architecturally significant NFR appears in the NFR mapping.
- Every FR is implemented by at least one component.
- No accepted ADR violates a constraint, and no two ADRs contradict each other.
- Every ADR lists at least one driver and one negative consequence.
- Section 9 is complete enough for code work to start.

## Step 9: Hand over
- Do not write the implementation plan or code. The next step is the
  implementation plan in `docs/plan/implementation-plan.md`.
- Do not commit. Suggest a Conventional Commits message, e.g.
  `docs(arch): add architecture and ADR-001..ADR-004`, with a `Refs:` footer
  listing the driving NFR IDs.
