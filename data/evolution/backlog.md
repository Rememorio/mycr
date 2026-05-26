# MyCR Evolution Backlog

This file is the working queue for improvements discovered while running MyCR.
Keep entries concrete enough that a later agent can implement or reject them.

## Active Candidates

| Date | Area | Observation | Proposed Change | Status |
| --- | --- | --- | --- | --- |
| 2026-05-26 | Repo layout | Reports and skill logic were split between the installed skill directory and `trpc-agent-go/.vscode`. | Make `/Users/guoqizhou/projects/github/mycr` the canonical home for skill, scripts, report history, and website deployment. | Done |
| 2026-05-26 | Reports | Old reports were only local HTML/JSON files and could not be browsed from the personal site. | Archive JSON/HTML under this repo and expose them through the `/mycr` Astro site. | Done |
| 2026-05-26 | Paths | The skill used `../../github/trpc-agent-go` and `.vscode/mycr-reports` as hardcoded defaults. | Resolve the target checkout through `MYCR_TARGET_CHECKOUT`, repo-relative fallback, and one documented absolute fallback; write reports to this repo. | Done |

## Parking Lot

| Date | Area | Observation | Proposed Change | Status |
| --- | --- | --- | --- | --- |
| 2026-05-26 | Report quality | The archive index currently summarizes run-level data and links to full HTML. | Add a generated per-PR search index if the number of reports grows enough that cross-run PR lookup becomes slow. | Open |
| 2026-05-26 | CI visibility | GitHub Pages deploy status is separate from the local run report. | Add latest deploy/check status to README or the dashboard if it becomes useful. | Open |
