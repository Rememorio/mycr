# Manual Review Merge Gate

## Context

MyCR already blocks approval and merge for concrete code, CI, source-problem,
solution-fit, and unresolved-review issues. That was not enough for PRs where
the code can be reviewed but the merge decision belongs to a human maintainer or
program owner. A Rhino Bird mentorship issue is one example: multiple students
may submit competing PRs for the same task, and the final accepted candidate may
depend on program rules, mentor selection, timing, or ownership decisions that
are not represented by CI or diff quality.

The same failure mode applies outside mentorship programs. Security-boundary
changes, broad public API additions, architecture shifts, and product/roadmap
decisions can look technically clean while still needing explicit owner
approval before merge.

## Decision

Add a `manual_review` blocker kind. MyCR may still inspect the PR, run code
review, and post concrete findings, but it must not submit `LGTM` or merge while
the blocker is present.

Use `manual_review` when issue labels, issue body, PR discussion, maintainer
comments, requested code owners, active competing PRs, or the change scope show
that a human maintainer, mentor, code owner, product owner, or architecture
owner must choose the accepted merge candidate.

The blocker is cleared only by an explicit human statement that the exact PR is
accepted and ready for the normal merge gate. Green CI, resolved code comments,
or a clean subagent review are not enough by themselves.

## Implementation Notes

- `skill/SKILL.md` now treats manual-review-only merge policy as a first-class
  approval and merge gate.
- `data/specs/report-schema.md` documents the `manual_review` blocker.
- `scripts/render_mycr_report.py` renders `manual_review` with localized labels.
