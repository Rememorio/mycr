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

## Parking Lot

| Date | Area | Observation | Proposed Change | Status |
| --- | --- | --- | --- | --- |
| 2026-05-26 | Report quality | The archive index currently summarizes run-level data and links to full HTML. | Add a generated per-PR search index if the number of reports grows enough that cross-run PR lookup becomes slow. | Open |
| 2026-05-26 | CI visibility | GitHub Pages deploy status is separate from the local run report. | Add latest deploy/check status to README or the dashboard if it becomes useful. | Open |
