# Thread-Level Review Gates

## Problem

The MyCR run for `2026-05-26 11:09` grouped several PRs under
"unresolved human review or Changes Requested". A follow-up audit showed that
some of those PRs had no live human-review blocker. The clearest example was
PR #1731: GitHub still reported `reviewDecision=CHANGES_REQUESTED`, but the
concrete WineChord threads had author `done` replies and were resolved. The
remaining `go-apidiff` failure was a soft review gate that required inspection,
not an automatic skip.

## Decision

MyCR must never skip a PR only because the aggregate GitHub review decision is
`CHANGES_REQUESTED`. That state is only a signal to audit the underlying review
threads.

A human-review blocker is valid only when the report can name the exact current
thread or comment, reviewer, file and line when available, latest author
response, and why the current diff still fails to address the request.

If all concrete threads are resolved, outdated, or verified fixed, the PR
remains reviewable when CI is green or only acceptable soft-CI failures remain.
If it is not reviewed because of candidate ordering or time, the report must say
"not reached this run" rather than implying a human-review blocker.

## Report Impact

Skipped PR entries now support structured `blockers` and `readiness_audit`.
The HTML report renders those blockers under each skipped PR so users can see
which exact check, conflict, thread, or soft gate prevented review.
