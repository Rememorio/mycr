# Report Quality and Self-Evolution Gate

Date: 2026-07-04

## Trigger

The latest full MyCR run produced a valid HTML file, but the report was not a
complete engineering brief. Many PR cards had empty detail fields, some
`approach` values described reviewer actions instead of the PR implementation,
`skipped_groups` lacked per-PR item details, and string `follow_up` entries were
rendered as empty follow-up cards.

## Decision

Publishing a report is no longer sufficient evidence that a MyCR run finished
cleanly. A meaningful run must pass a post-report quality gate before final
commit and push:

- normalize skipped groups into renderable per-PR items when the lightweight
  run state has enough metadata;
- reject empty rendered detail placeholders for processed PRs;
- reject non-canonical display statuses that break filtering and counts;
- reject `approach` text that describes review actions instead of the PR's own
  implementation;
- verify `follow_up` entries can render as either structured objects or
  non-empty plain strings;
- require `skill_evolution` entries for concrete process friction discovered
  during the run.

The first implementation is `scripts/report-quality.mjs`, called by both
`scripts/archive-report.mjs` and `npm run verify`.

## Subagent QA Policy

When the user explicitly asks for an independent reviewer, or when the active
Codex tool policy otherwise permits subagent work, spawn a fresh xhigh reviewer
after the report exists. The reviewer should inspect the latest JSON/HTML and
the MyCR flow as read-only input, then return concrete defects and evolution
suggestions. The main agent remains responsible for validating the feedback,
implementing local fixes, running `npm run verify`, and committing/pushing the
result.

If subagent tools are unavailable or the active policy does not permit spawning,
record that limitation in the run report and perform the same QA checklist
locally.

## Follow-Up

This gate is intentionally strict only for the latest report so historical
archives do not block unrelated maintenance. The long-term finalizer should
generate a canonical primary bucket per open PR, keep secondary blockers as
metadata, and add fixture/DOM smoke tests for every report section.
