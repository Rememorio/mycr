# Reviewability Ledger

## Problem

Previous MyCR runs could over-collapse exclusion reasons into broad groups such
as CI state, unresolved review, or stale `Changes Requested`. That made a PR
look blocked even when the author had already fixed the issue or when the real
state was simply "not reached this run".

## Decision

Every run must maintain a reviewability ledger for all open PRs. A non-draft,
non-WIP, non-own PR with green CI or acceptable soft-CI failures, no merge
conflict, and no verified live blocker must be processed or explicitly reported
as `not_reached`.

The final report must make these near-ready PRs visible instead of hiding them
inside broad skip groups. Human review, bot review, and soft-CI blockers must
name the concrete current thread, check, or verification result.

## Expected Effect

The operator can quickly see whether MyCR actually reviewed all reviewable PRs.
If capacity or ordering prevents a PR from being reviewed, the report will say
that directly and future runs can pick it up first.
