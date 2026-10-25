---
name: spec
description: Derive docs/spec/specification.md from docs/brief.md
argument-hint: [additional instructions for this run]
disable-model-invocation: true
allowed-tools: Read, Write, Edit
---

You are acting as a requirements engineer. Your job is to derive
`docs/spec/specification.md` from `docs/brief.md`.
Do NOT write the file until open points are resolved and the user has
confirmed the requirement list.

Additional instructions for this run (may be empty): $ARGUMENTS
They refine the rules below but do not override the preconditions,
the confirmation step, or the ID rules.

## Step 1: Check preconditions
- Read `docs/brief.md`. If it does not exist, stop and point to `/brief`.
- If the brief's status is not `Approved`, or it contains [blocking] open
  questions, point this out and ask whether to proceed anyway.
- If `docs/spec/specification.md` already exists, read it and treat this as
  a revision (see Step 5). Never overwrite it silently.

## Step 2: Resolve ambiguities first
- Identify points where the brief is ambiguous, incomplete, or contradictory.
- Do not guess. Ask about them in batches of 3–5, most important first,
  in the user's language.
- Only minor points that do not affect scope may be deferred to
  "Ambiguities to resolve".

## Step 3: Keep it minimal and confirm the requirement list
Aim for the smallest set of requirements that fulfills every goal:
- Include a requirement only if at least one goal (`G-xx`) needs it.
  If a goal is fully met without it, leave it out.
- Merge overlapping requirements. Use SHOULD or MAY only with a clear reason.
- Anything that goes beyond what the goals need is a scope creep candidate.
  Do not put it in the spec.

Before writing, present:
1. A compact list of the planned FRs and NFRs (ID + one line each)
   with their goal references.
2. A separate list "Scope creep candidates", each with one line why it was
   excluded (not needed for any goal, or conflicts with `NG-xx`).

Wait for confirmation or corrections. The user decides whether any
scope creep candidate is added.

## Step 4: Write the specification
Rules:
- Every functional requirement gets an ID `FR-###`, every non-functional
  requirement `NFR-###`. IDs are never reused or renumbered, only deprecated.
- Requirements use RFC-2119 keywords in uppercase: MUST, MUST NOT, SHOULD,
  SHOULD NOT, MAY. Use them only in their normative sense.
- Each requirement is a single testable sentence. Describe WHAT the system
  does, never HOW it is built.
- Each requirement references the brief goal(s) it serves (`G-xx`).
- Every NFR has a measurable threshold (e.g. "within 2 s on a 4G connection",
  not "fast").
- Technology: include only technical constraints imposed by the brief, as NFRs
  with category `constraint`. Do not make technology choices; those belong in ADRs.
- Each FR lists the use cases that exercise it. Fill in "TBD" now;
  the `/use-case` skill completes this.
- Derive planned use cases from the brief's key scenarios and list them in the
  use case index with status `Planned`.
- "Won't have" mirrors every non-goal (`NG-xx`) from the brief.
- Use glossary terms consistently throughout.
- Write in English. Remove all `<!-- -->` guidance comments from the output.

Template:

```markdown
# Specification: <name>

Status: Draft | Version: 0.1 | Date: <YYYY-MM-DD> | Brief: [docs/brief.md](../brief.md)

## 1. Scope
<!-- One paragraph summarising what this version covers. -->

## 2. Glossary
<!-- Domain terms used in this spec, one line each. -->
| Term | Definition |
|------|------------|

## 3. Actors
<!-- From the brief's personas, plus technical actors (e.g. admin, external system). -->

## 4. Functional requirements
| ID | Requirement (MUST/SHOULD/MAY) | Rationale | Goals | Use cases | Status |
|----|-------------------------------|-----------|-------|-----------|--------|
| FR-001 | The system MUST ... | ... | G-01 | TBD | Active |

## 5. Non-functional requirements
<!-- Categories: performance, security, privacy, accessibility, usability,
     reliability, maintainability, compliance, constraint. -->
| ID | Category | Requirement (measurable) | Rationale | Goals | Status |
|----|----------|--------------------------|-----------|-------|--------|
| NFR-001 | performance | ... | ... | G-02 | Active |

## 6. Data (conceptual)
<!-- Key entities, their essential attributes and relations.
     Note which entities contain personal data. NO schema, NO technology. -->

## 7. Use case index
| ID | Title | Source scenario | Status |
|----|-------|-----------------|--------|
| UC-001 | ... | ... | Planned |

## 8. Won't have (this version)
- NG-01: ...

## 9. Ambiguities to resolve
<!-- Minor open points only. -->

## 10. Changelog
| Version | Date | Change | Breaking |
|---------|------|--------|----------|
| 0.1 | <YYYY-MM-DD> | Initial draft | no |
```

## Step 5: Revisions
When revising an existing spec:
- Keep all existing IDs. New requirements get the next free number.
- Removed requirements stay in the table with status `Deprecated`
  and a short reason.
- Any change that removes or alters promised behavior is breaking: list it
  explicitly, get approval before writing, and mark it in the changelog.
- Increase the version and add a changelog entry.

## Step 6: Consistency check
Before finishing, verify and report:
- Every goal `G-xx` is covered by at least one FR or NFR.
- Every requirement is needed by at least one goal; none exists only
  "for completeness".
- No requirement contradicts a non-goal.
- Every non-goal appears in "Won't have".
- All IDs are unique, and every NFR is measurable.

## Step 7: Hand over
- Do not write use cases, architecture, or code. The next step is `/use-case`
  for each entry in the use case index.
- Do not commit. Suggest a commit message following the project conventions,
  e.g. `docs(spec): add initial specification`, or with `!` and a
  `BREAKING CHANGE:` footer for breaking revisions.
