# MyCR

MyCR is the repo-managed workflow for reviewing ready
`trpc-group/trpc-agent-go` pull requests and publishing auditable review
reports at `https://www.wineandchord.com/mycr/`.

The canonical skill now lives in this repository at `skill/SKILL.md`. The
installed Codex skill is only a small bootstrap that points back here, so skill
changes, report history, and the website can evolve through normal Git commits.

## Repository Layout

- `skill/SKILL.md`: canonical MyCR skill instructions.
- `scripts/render_mycr_report.py`: renders one structured JSON run summary into
  a self-contained interactive HTML report.
- `scripts/archive-report.mjs`: copies a run JSON into the website archive and
  renders the matching HTML file.
- `scripts/check-reports.mjs`: validates archived JSON/HTML pairs.
- `src/data/reports/`: tracked source JSON for every MyCR run.
- `public/reports/`: public JSON and HTML artifacts served by the site.
- `src/pages/index.astro`: `/mycr` report archive dashboard.
- `data/evolution/`: improvement backlog and decision records for the skill.
- `data/specs/`: living specs for report data and repo behavior.

## Local Commands

```sh
npm install
npm run dev -- --port 4321
npm run verify
```

To archive a newly generated run:

```sh
node scripts/archive-report.mjs /path/to/mycr-YYYYmmdd-HHMMSS.json
```

The archive command writes:

- `src/data/reports/mycr-YYYYmmdd-HHMMSS.json`
- `public/reports/mycr-YYYYmmdd-HHMMSS.json`
- `public/reports/mycr-YYYYmmdd-HHMMSS.html`

## Deployment

GitHub Pages builds this repository on every push to `main`. The Astro site is
configured with `base: "/mycr"`, matching the intended public path:

```text
https://www.wineandchord.com/mycr/
```

## Target Checkout Resolution

MyCR reviews `trpc-group/trpc-agent-go`. The target checkout is resolved in this
order:

1. `MYCR_TARGET_CHECKOUT`
2. `../trpc-agent-go` relative to this repository
3. `/Users/guoqizhou/projects/github/trpc-agent-go`

Keep new scripts and docs repo-relative where possible. Absolute paths are only
documented fallbacks for local bootstrap compatibility.
