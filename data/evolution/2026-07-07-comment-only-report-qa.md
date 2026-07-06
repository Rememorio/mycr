# Comment-Only Report QA

## Context

The 2026-07-07 comment-only run reviewed all open `trpc-agent-go` pull
requests, posted only inline review comments, and intentionally avoided `LGTM`,
approval, merge, or direct own-PR branch updates.

## Findings

- The first report draft reused process-oriented wording in
  `technical_background` instead of domain background.
- Skipped group headings rendered raw machine reasons such as `pending_ci`.
- Human-review blockers had reviewer names but no review URLs.
- Inline comments preserved the exact GitHub body but did not provide a
  Chinese-first summary for the default report view.
- A copied run-state blocker could make processed PR CI state look internally
  inconsistent.
- Truncated GitHub review text can split Unicode surrogate pairs if collectors
  slice by UTF-16 index.

## Changes

- Updated the report renderer to use localized skipped-group titles and prefer
  Chinese inline-comment summaries in the default view.
- Extended report quality checks to reject process narration in
  `technical_background`, stale CI blockers on processed green entries, and
  empty optional blocker fields.
- Updated the report schema and canonical skill to require valid Unicode text
  and code-point truncation for stored GitHub excerpts.
- Recorded the remaining collector-level work in the backlog.

## Validation

- `node scripts/archive-report.mjs .mycr-cache/mycr-20260707-005404/mycr-20260706-171423.json`
- `npm run verify`
