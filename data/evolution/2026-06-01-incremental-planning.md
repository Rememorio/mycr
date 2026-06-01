# Incremental MyCR Planning

## Context

MyCR had been optimized for auditability by scanning every open
`trpc-group/trpc-agent-go` PR and keeping a run-level reviewability ledger. That
prevented missed review opportunities, but it also made every run repeat
expensive work for PRs whose head SHA, CI, comments, review threads, and
readiness state had not changed.

The goal is to reduce time and token cost without weakening the review bar.
The important distinction is between a cheap full-open-PR index, which every run
must still collect, and the expensive work of diff reading, source inspection,
thread-level auditing, xhigh subagent review, and long-form report writing.

## Decision

Each MyCR run should first build a lightweight index for every open PR, compare
it with the previous successful run's `run_state`, and then promote only the
changed or risky items into the heavy-review queue.

A PR must enter the heavy path when it is new, its head SHA changed, its check
fingerprint changed, its review-thread or comment fingerprint changed, its
readiness markers changed, its base or mergeability changed, it was previously
`not_reached`, it has new activity after the overlapped watermark, or the run is
performing a periodic full sweep.

An unchanged PR may be carried forward only as an unchanged blocker with its
previous evidence and verification time. Carry-forward state is not permission
to approve, merge, submit comments, or push own-PR fixes. Those actions still
require a fresh fetch of head SHA, checks, comments, and review threads.

## Implementation

`scripts/mycr-incremental-plan.mjs` performs the comparison. It accepts a
current lightweight open-PR index and an optional previous report or run-state
file, then emits:

- `heavy_review`: PRs requiring expensive work this run.
- `carry_forward`: PRs whose prior concrete blocker can be reused.
- `closed_or_missing`: PRs present in the previous state but no longer open.
- `run_state`: the next snapshot that should be embedded in the run report.

The script intentionally does not call GitHub or decide review outcomes. It is a
planner only, so the existing MyCR workflow remains responsible for collecting
fresh PR metadata before any user-visible action.

## Quality Guardrails

- Missing, stale, or suspicious planner input must fall back to a conservative
  heavy scan.
- The lightweight full-open-PR ledger remains mandatory every run.
- Periodic full sweeps prevent long-lived metadata drift.
- Report JSON should include `incremental_plan` and `run_state` so future runs
  can explain why a PR was reviewed heavily or carried forward.
