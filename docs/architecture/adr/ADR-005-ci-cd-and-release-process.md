# ADR-005: CI/CD and release process

Status: Proposed | Date: 2026-10-31

## Context
Every PyPI version must be built and published by a public CI pipeline, include
a source distribution, and match a tagged release in the public repository
(NFR-011). The repository is hosted on GitHub. The owner's working rules apply:
changes are proven on staging before production, and only the owner approves a
production release. For a library, TestPyPI is the staging environment and PyPI
is production; a PyPI release cannot be undone because a version number can
never be reused. PyPI supports Trusted Publishing via OIDC from GitHub Actions
(short-lived tokens, no stored secrets); a pending publisher allows the first
release; a GitHub environment is strongly recommended. The Python Packaging
guide recommends separate build and publish jobs, environments `testpypi` and
`pypi`, tag-only PyPI publishing and required manual approval for `pypi`;
`pypa/gh-action-pypi-publish` (current v1.14.3) creates PEP 740 attestations by
default.

## Decision drivers
- Constraint NFR-008: published on PyPI.
- Constraint NFR-011: source distribution, public CI, version matches a tag.
- Definition of done: tests, lint and typecheck run for every change.
- Owner rules: staging before production; only the owner approves production.

## Considered options
1. GitHub Actions with Trusted Publishing; tag → build → TestPyPI → owner approval → PyPI
2. As option 1, plus TestPyPI uploads of development versions on every push to `main`
3. As option 1, but with API tokens stored as GitHub secrets
4. Manual publishing from a developer machine

## Decision
We use GitHub Actions with PyPI Trusted Publishing. A CI workflow runs lint,
format check, typecheck and tests on Python 3.14 and 3.15 for every pull request
and push. A release workflow runs on tags `vX.Y.Z`: it builds the source
distribution and wheel once, fails if the tag does not match the version in the
project metadata, publishes to TestPyPI, verifies installation from TestPyPI,
and then waits in the `pypi` environment for the owner's approval before
publishing to PyPI. The version is set statically in the project metadata.
Only the owner approves the `pypi` environment; Claude never does.

## Consequences
- **Positive:** Meets NFR-011 with no stored secrets; every release is proven on
  TestPyPI first; production requires a deliberate human approval; releases get
  attestations.
- **Negative:** Bound to GitHub Actions; each release needs a version bump
  commit before tagging; one-time manual setup on PyPI, TestPyPI and GitHub.
- **Follow-ups:** Owner registers pending trusted publishers on PyPI and
  TestPyPI and creates the GitHub environments `testpypi` and `pypi` (with the
  owner as required reviewer); enable the public issue tracker (NFR-011); add
  workflows `ci` and `release` in the plan.

## Rejected options
**TestPyPI on every push to `main`:** Requires deriving development versions
from Git and floods TestPyPI with versions; staging on tags is enough.

**API tokens as secrets:** Long-lived credentials that must be rotated; not
recommended by the Packaging guide.

**Manual publishing:** Violates NFR-011 (public CI pipeline).

## Sources
- https://docs.pypi.org/trusted-publishers/
- https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/
- https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/
- https://github.com/pypa/gh-action-pypi-publish/releases
- https://contributors.home-assistant.io/core/quality-scale/dependency-transparency/
