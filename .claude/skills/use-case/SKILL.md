---
name: use-case
description: Write or revise numbered use case files under docs/spec/use-cases/
argument-hint: <UC IDs or titles, e.g. UC-001 UC-003, or "all planned">
disable-model-invocation: true
allowed-tools: Read, Write, Edit
---

You are acting as a requirements engineer. Use cases to write: $ARGUMENTS

## Step 1: Check preconditions
- Read `docs/spec/specification.md`. If it does not exist, stop and point to `/spec`.
- If no use cases were named, list the `Planned` entries of the use case index
  and ask which to write.
- Resolve each named use case against the use case index:
  - Listed in the index: use its ID and title.
  - Not listed: it may be scope creep. Explain which goals and FRs it would
    serve and ask for approval before adding it to the index with the next
    free number.
- If a use case file already exists, read it and treat this as a revision:
  keep existing flow and acceptance criterion IDs, and never overwrite silently.

## Step 2: Outline and confirm
For each use case, present a short outline: primary actor, covered FRs and
NFRs, main scenario in one line, and the planned alternative and error flows
(one line each). Ask about edge cases you are unsure of. Wait for confirmation.

## Step 3: Detect spec gaps
Every step and flow must be backed by a requirement. If a flow needs behavior
that no FR or NFR covers (common in error flows), do NOT write it into the use
case as if it were specified. Instead, collect it as a proposed spec change:
the proposed requirement text and the goal (`G-xx`) it serves.
Present all proposals together and wait for approval. Approved proposals are
added to the spec following its revision rules (next free ID, version bump,
changelog entry) before the use case is written.

## Step 4: Write the use case
Create `docs/spec/use-cases/UC-###-<slug>.md` (slug: lowercase, hyphenated).

Rules:
- Every step is observable behavior. No implementation detail, no technology.
- Use glossary terms from the spec consistently.
- Error flows are mandatory. If you can't think of any, you haven't thought hard
  enough: ask about edge cases instead of skipping them.
- Acceptance criteria cover the main scenario, every alternative flow, and every
  error flow. Each criterion has an ID (`UC-###-AC#`) that tests can reference.
- Write in English. Remove all `<!-- -->` guidance comments from the output.

Template:

```markdown
# UC-###: <Title>

Status: Draft | Date: <YYYY-MM-DD> | Spec version: <x.y>

**Primary actor:** …
**Goals:** G-…
**Covered requirements:** FR-…, FR-…
**Related NFRs:** NFR-… <!-- e.g. response time, accessibility; omit if none -->

**Preconditions:** …
**Trigger:** …

## Main success scenario
<!-- Numbered steps, alternating actor/system. -->
1. <Actor> …
2. System …

## Alternative flows
<!-- A1, A2, … each branching from a numbered step and stating where it rejoins
     or ends. -->
- **A1 (from step 2):** …

## Error flows
<!-- E1, E2, … validation failures, conflicts, unavailable resources, timeouts.
     Each branches from a numbered step and states the outcome. -->
- **E1 (from step 2):** …

## Postconditions
- **Success:** …
- **Minimal guarantees:** <!-- What always holds, even on failure. -->

## Acceptance criteria
- **UC-###-AC1 (main):** Given …, when …, then …
- **UC-###-AC2 (A1):** Given …, when …, then …
- **UC-###-AC3 (E1):** Given …, when …, then …
```

## Step 5: Update the specification
- In the FR table, replace "TBD" in the "Use cases" column of each covered
  requirement (or append the UC ID if others are already listed).
- In the use case index, set the status to `Written`.
- Traceability-only updates do not change behavior: no version bump needed.
  Spec changes from Step 3 follow the revision rules.

## Step 6: Consistency check
Before finishing, verify and report:
- Every covered FR is actually exercised by at least one step or flow.
- Every flow (main, A#, E#) has at least one acceptance criterion.
- No step describes behavior outside the covered requirements.
- FRs still marked "TBD" and use cases still `Planned` in the index.

## Step 7: Hand over
- Do not write architecture or code. Remaining `Planned` use cases come next;
  once all are written, the next step is the architecture.
- Do not commit. Suggest a Conventional Commits message, e.g.
  `docs(spec): add UC-001 submit contact form`, with `Refs:` listing the
  covered FR IDs. Use `!` and `BREAKING CHANGE:` if Step 3 changed promised behavior.
