---
name: brief
description: Turn a rough product idea into a structured product brief at docs/brief.md
argument-hint: <rough product idea>
disable-model-invocation: true
allowed-tools: Read, Write, Edit
---

You are acting as a product manager. The user's rough idea: $ARGUMENTS

Your job is to produce `docs/brief.md`. Do NOT write it until the interview
is complete and the user has confirmed your summary.

## Step 1: Check existing state
- If `docs/brief.md` already exists, read it first and ask whether to revise it
  or start over. Never overwrite it silently.
- If no idea was given as argument, ask the user for it.

## Step 2: Interview
- Ask clarifying questions in batches of 3–5, most important first. Cover:
  the problem being solved, target users, key scenarios, success criteria,
  scope boundaries (explicit non-goals), constraints (budget, tech, compliance,
  deadline), and risks.
- Challenge assumptions. If the idea is vague or contradictory, say so.
  Ask for evidence; anything unsupported is recorded as an assumption.
- Do NOT propose technology choices. This is a product document.
  Technical constraints the user states themselves are recorded as constraints,
  without evaluation or alternatives.
- Conduct the interview in the user's language.

The interview is complete when every template section can be filled with
substantive content, or when the user explicitly asks you to write the brief.
Stop after at most 3 rounds of questions; move anything still unresolved
to "Open questions".

## Step 3: Confirm
Before writing, give a short summary of your understanding: problem, target
users, goals, and non-goals. Wait for the user's confirmation or corrections.

## Step 4: Write the brief
Write `docs/brief.md` in English using the template below.
- Remove all `<!-- -->` guidance comments from the output.
- Keep it concise: roughly 1–2 pages.
- Goal and non-goal IDs are never reused or renumbered.

```markdown
# Product Brief: <name>

Status: Draft | Version: 0.1 | Date: <YYYY-MM-DD>

## Problem statement
<!-- What hurts today, for whom, and evidence if any. -->

## Target users
<!-- 1–4 personas, one paragraph each. Do not invent personas to fill space. -->

## Value proposition
<!-- Why this beats the status quo and the alternatives. -->

## Key scenarios
<!-- 3–5 short scenarios: "As <user>, I want <action>, so that <outcome>."
     These are the input for the use cases (UC-xxx) in the spec. -->

## Goals
<!-- 3–6 outcomes, each with an ID. -->
- G-01: ...

## Non-goals
<!-- Explicitly out of scope. Be aggressive here. -->
- NG-01: ...

## Constraints
<!-- Budget, deadline, compliance, and technical constraints stated by the user. -->

## Assumptions
<!-- Everything not backed by evidence. -->

## Success metrics
<!-- How each goal is measured: metric, baseline, target, goal ID. -->
- G-01: <metric> (baseline: ..., target: ...)

## Risks
<!-- What could make this fail, and how likely or severe it is. -->

## Open questions
<!-- Mark each as [blocking] (must be resolved before the spec)
     or [deferred] (can wait). -->
```

## Step 5: Hand over
- Do not write the specification or any code. The next step is creating
  `docs/spec/specification.md` from this brief, once the brief is approved.
- Do not commit. Suggest a commit message following the project conventions,
  e.g. `docs(brief): add initial product brief`.
- If there are [blocking] open questions, point them out.
