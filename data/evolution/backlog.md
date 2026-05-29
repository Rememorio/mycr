# MyCR Evolution Backlog

This file is the working queue for improvements discovered while running MyCR.
Keep entries concrete enough that a later agent can implement or reject them.

## Active Candidates

| Date | Area | Observation | Proposed Change | Status |
| --- | --- | --- | --- | --- |
| 2026-05-26 | Repo layout | Reports and skill logic were split between the installed skill directory and `trpc-agent-go/.vscode`. | Make `/Users/guoqizhou/projects/github/mycr` the canonical home for skill, scripts, report history, and website deployment. | Done |
| 2026-05-26 | Reports | Old reports were only local HTML/JSON files and could not be browsed from the personal site. | Archive JSON/HTML under this repo and expose them through the `/mycr` Astro site. | Done |
| 2026-05-26 | Paths | The skill used `../../github/trpc-agent-go` and `.vscode/mycr-reports` as hardcoded defaults. | Resolve the target checkout through `MYCR_TARGET_CHECKOUT`, repo-relative fallback, and one documented absolute fallback; write reports to this repo. | Done |
| 2026-05-26 | Report UI | Expanded PR details were rendered as many vertically stacked field boxes, which made long reports hard to scan. | Group PR details into narrative sections, keep review outcome/risk/CI in a compact side rail, and keep inline comments as a distinct evidence block. | Done |
| 2026-05-26 | Report UI | PR cards still had similar visual weight, making it hard to know which PRs deserved careful reading. | Add reading recommendations, priority colors, and inline keyword highlights to full HTML reports. | Done |
| 2026-05-26 | Review gates | MyCR could skip PRs because GitHub still showed `CHANGES_REQUESTED` even after the author fixed and resolved the concrete threads. | Require thread-level blocker audits, forbid aggregate `CHANGES_REQUESTED` as a standalone skip reason, and display structured concrete blockers in reports. | Done |
| 2026-05-26 | Review coverage | Reviewable PRs could be hidden by candidate ordering, broad skip groups, or ambiguous soft-gate reasoning. | Maintain a run-level reviewability ledger and require every reviewable PR to be processed or explicitly reported as `not_reached` with a concrete reason. | Done |
| 2026-05-27 | Own PR handling | MyCR previously skipped the authenticated user's PRs, which hid issues in the maintainer's own changes and encouraged self-review comments if treated like external PRs. | Add an own-PR maintenance path that checks out pushable own PR branches in separate worktrees, fixes valid findings directly, reports them as `maintained`, and never self-approves, self-merges, or posts self-review comments. | Done |
| 2026-05-26 | GitHub review posting | The GitHub connector requires a non-empty review body for `COMMENT` reviews, which risks creating top-level review text when MyCR should submit inline-only comments. | Add a small MyCR helper that submits inline-only reviews through `gh api`, validates created review/comment URLs, and falls back to the connector only when an inline-only API path is unavailable. | Open |
| 2026-05-27 | GitHub review posting | `POST /pulls/{number}/reviews` returned a COMMENTED review for #1859 but did not create a visible inline comment, requiring a second direct `/pulls/{number}/comments` call and manual URL validation. | Implement a report-time and post-time invariant that every submitted inline comment has a matching `pulls/comments` URL; retry through the direct review-comment endpoint when the review wrapper produces no comments. | Open |
| 2026-05-27 | Review gates | A PR skipped for pending CI (#1874) turned green during the same run and needed to be promoted back into the candidate queue manually. | Add a late pre-report requeue pass that refreshes every non-draft external PR with prior pending/missing checks and automatically reviews any item that became green. | Open |
| 2026-05-27 | Comment blockers | #1400 had a concrete changed-line compatibility blocker, but GitHub returned `Issue is locked`, leaving the finding only in the report. | Represent comment-delivery failures as first-class blocked outcomes with the attempted payload, API error, and recommended maintainer escalation path. | Open |
| 2026-05-29 | Run orchestration | The full run required repeated manual `gh`/GraphQL refreshes for PR metadata, checks, threads, merge state, and own-PR CI after each action, and the report had to be assembled from many temporary JSON files. | Add a run-state collector that stores one normalized ledger per PR, refreshes processed PRs before reporting, and emits the report JSON skeleton directly from that ledger. | Open |

## Parking Lot

| Date | Area | Observation | Proposed Change | Status |
| --- | --- | --- | --- | --- |
| 2026-05-26 | Report quality | The archive index currently summarizes run-level data and links to full HTML. | Add a generated per-PR search index if the number of reports grows enough that cross-run PR lookup becomes slow. | Open |
| 2026-05-26 | CI visibility | GitHub Pages deploy status is separate from the local run report. | Add latest deploy/check status to README or the dashboard if it becomes useful. | Open |
