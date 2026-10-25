---
name: implement
description: Implement exactly one step of docs/plan/implementation-plan.md, test-first
argument-hint: <STEP-## or "next">
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---
You are acting as a software engineer. Implement exactly one step of
`docs/plan/implementation-plan.md`: $ARGUMENTS

## Step 1: Select and check the step
- Read the plan. If no step was given or "next" was given, pick the first
  open step (`[ ]`) whose dependencies are all done (`[x]`), and name it.
- Stop and explain if the step is already done or dropped, or if a dependency
  is not done.
- If another step is `[~]` in progress, point it out and ask whether to
  continue that one first.
- Check `git status`. If there are uncommitted changes, point them out
  and ask how to proceed.

## Step 2: Load context
Read only what this step needs:
- the step itself, and every FR, NFR, use case, and acceptance criterion it covers,
- the ADRs that apply to the affected components,
- `docs/architecture/architecture.md`, especially "Development & tooling"
  for the commands to use,
- the existing code in the affected area.

## Step 3: Propose and confirm
Present a short implementation outline:
- files to create or change,
- tests to write, each mapped to an acceptance criterion (`UC-###-AC#`)
  or to the step's "Done when" check,
- any new dependency, and the ADR that covers it.
Ask about anything unclear, and wait for confirmation.
Then mark the step `[~]` in the plan.

## Step 4: Implement test-first
1. Write the tests first. Name or annotate each test with the ID it verifies
   (e.g. `it("UC-001-AC2: rejects an empty message", …)`).
2. Run them and confirm they fail for the expected reason.
3. Implement the smallest change that makes them pass.
4. Refactor while the tests stay green.

Rules:
- Stay inside this step. Do not implement behavior from later steps,
  and do not "improve" unrelated code.
- Implement only specified behavior. If the step needs behavior that no
  requirement covers, or a decision that contradicts an accepted ADR,
  STOP and propose a spec change or a new ADR. Do not work around it.
- Add a dependency only if an accepted ADR covers it, or the outline that
  the user confirmed listed it.
- Reference FR/UC IDs in code comments only for non-obvious logic.
- Use only the commands from "Development & tooling". Do not guess commands.
- Never weaken, skip, or delete a test to get to green. If a test seems wrong,
  explain why and ask.

## Step 5: Verify the definition of done
Run the test, lint, and typecheck commands from "Development & tooling"
and show the results. The step is done only if:
- all tests pass, including those from earlier steps,
- lint and typecheck are clean,
- every acceptance criterion and "Done when" check of the step is verified.
If something fails and cannot be fixed within the step, report it and
leave the step `[~]`.

## Step 6: Update the plan
- Mark the step `[x]`.
- Add anything found along the way that belongs to no step (bugs, missing
  edge cases, spec gaps, technical debt) to "Discovered work", one line each.
  Do not implement it.
- If the "Development & tooling" commands changed (e.g. in the walking
  skeleton), update that section of `architecture.md`.

## Step 7: Report and hand over
Report briefly:
- what was implemented, with the covered IDs,
- the tests added and the verification results,
- any deviations from the outline, and new entries in "Discovered work".

Do not commit unless asked. Suggest a Conventional Commits message, e.g.
`feat(ui): add contact form submission (STEP-02)` with a `Refs:` footer
listing the covered FR/UC IDs.
Then name the next open step.
