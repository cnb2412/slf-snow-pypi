---
name: plan
description: Derive docs/plan/implementation-plan.md from the spec, use cases, and architecture
argument-hint: [additional instructions for this run]
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob
---
You are acting as a technical lead. Your job is to break the specification,
use cases, and architecture into small, ordered, testable implementation steps
in `docs/plan/implementation-plan.md`. You plan; you do not write code.

Additional instructions for this run (may be empty): $ARGUMENTS
They refine the rules below but do not override the preconditions,
the confirmation step, or the coverage rules.

## Step 1: Check preconditions
- Read `docs/spec/specification.md`, all use cases in `docs/spec/use-cases/`,
  `docs/architecture/architecture.md`, and all ADRs.
  If the architecture does not exist, stop and point to `/architecture`.
- Point out, and ask whether to proceed anyway, if:
  - any ADR is still `Proposed`,
  - section "Development & tooling" in `architecture.md` is incomplete,
  - use cases in the index are still `Planned`.
- If the plan already exists, read it and treat this as a revision
  (see Step 5). Never overwrite it silently.

## Step 2: Draft the steps
Rules for slicing:
- **Step 1 is always a walking skeleton:** project setup according to the
  ADRs, the commands from "Development & tooling" working, one trivial test,
  lint and typecheck running, and, if the architecture defines one, a
  deployment of an empty page to the target environment. This proves the
  toolchain end to end before any feature work.
- **Slice vertically:** each later step delivers observable behavior end to end
  (usually one use case or one flow of it), not a technical layer such as
  "all database tables" or "all components".
- **Keep steps small:** one step fits one working session and one reviewable
  commit. Split a use case into several steps (main scenario first, then
  alternative and error flows) if needed.
- **Every step is verifiable:** it names the acceptance criteria (`UC-###-AC#`)
  whose tests must pass when it is done. Steps without ACs (setup,
  crosscutting NFRs) name a concrete check instead.
- **Order:** dependencies first, then the riskiest or most uncertain items,
  then the most valuable. Crosscutting NFRs (accessibility, performance
  budgets, security headers) are verified as early as their component exists,
  not collected at the end.
- Plan only what the spec covers and only with technology the accepted ADRs
  allow. If a step would need anything else, STOP and propose a spec change
  or a new ADR.
- Optionally group steps into milestones, each ending in a releasable state.

## Step 3: Confirm
Before writing, present:
1. The step list: ID, title, covered IDs, dependencies (one line each).
2. A coverage summary: FRs, ACs, and NFRs not yet covered by any step,
   with a reason if this is intentional.
Wait for confirmation or corrections.

## Step 4: Write the plan
Write `docs/plan/implementation-plan.md` in English. Remove all `<!-- -->`
guidance comments from the output.

```markdown
# Implementation Plan: <name>

Status: Draft | Version: 0.1 | Date: <YYYY-MM-DD>
Based on: Spec <x.y>, Architecture <x.y>

Legend: [ ] open · [~] in progress · [x] done · [-] dropped

## Milestone 1: <name>
<!-- Optional. What is releasable at the end of this milestone. -->

### [ ] STEP-01: Walking skeleton
- **Goal:** <one sentence>
- **Covers:** <ADR-…, NFR-…>
- **Depends on:** —
- **Done when:** <concrete checks, e.g. `pnpm test` passes with one test;
  empty page deployed to …>
- **Notes:** <!-- Risks, hints, open points. Omit if none. -->

### [ ] STEP-02: <UC-001 main scenario: …>
- **Goal:** …
- **Covers:** UC-001 (main), FR-…, NFR-…
- **Depends on:** STEP-01
- **Done when:** tests for UC-001-AC1 pass; DoD from CLAUDE.md met.

## Coverage
| ID | Step(s) |
|----|---------|
| FR-001 | STEP-02 |
| UC-001-AC1 | STEP-02 |
| NFR-001 | STEP-01, STEP-04 |

## Discovered work
<!-- Items found during implementation that are not yet planned. Each needs
     approval and, if it adds behavior, a spec change before it becomes a step. -->

## Changelog
| Version | Date | Change |
|---------|------|--------|
| 0.1 | <YYYY-MM-DD> | Initial plan |
```

## Step 5: Revisions
- Step IDs are never reused or renumbered. New steps get the next free number,
  even if they are inserted earlier in the order.
- Steps that are no longer needed are marked `[-]` with a reason, not deleted.
- Done steps (`[x]`) are not changed. If done work must change, add a new step.
- When the spec or an ADR changes, list the affected steps, update them,
  bump the version, and add a changelog entry.

## Step 6: Coverage check
Before finishing, verify and report:
- Every active FR and every acceptance criterion is covered by at least one step.
- Every architecturally significant NFR is verified by at least one step.
- Every dependency points to an existing, earlier step; there are no cycles.
- No step covers behavior outside the spec or technology outside the ADRs.

## Step 7: Hand over
- Do not write code. The next step is `/implement STEP-01`.
- Do not commit. Suggest a Conventional Commits message, e.g.
  `docs(plan): add initial implementation plan`.
