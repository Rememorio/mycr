# MyCR Agent Notes

## Purpose

This repository is the canonical home for the `mycr` Codex skill, its report
renderer, its historical run archive, and the public `/mycr` dashboard.

## Canonical Paths

- Repo root: `/Users/guoqizhou/projects/github/mycr`
- Canonical skill: `skill/SKILL.md`
- Report source JSON: `src/data/reports/`
- Public report artifacts: `public/reports/`
- Evolution records: `data/evolution/`

The installed skill under `~/.codex/skills/mycr` is a bootstrap only. Do not
copy long-lived logic back into that directory.

## Report Workflow

When a MyCR run produces `mycr-YYYYmmdd-HHMMSS.json`, archive it with:

```sh
node scripts/archive-report.mjs /path/to/mycr-YYYYmmdd-HHMMSS.json
```

Then run:

```sh
npm run verify
```

If the run is meaningful and the user did not ask to keep it local, commit and
push the archived report artifacts so `https://www.wineandchord.com/mycr/`
stays complete.

## Self-Evolution Workflow

After each real run, record concrete friction or improvement ideas in
`data/evolution/backlog.md`. Examples include repeated manual checks, missing
report fields, unclear skip reasons, brittle path assumptions, and UI gaps in
the dashboard.

When the improvement is safe and local to this repo, update the canonical skill,
scripts, specs, or frontend here; run `npm run verify`; then commit and push the
change. Keep the change auditable and avoid unrelated edits.

## Target Repository

MyCR reviews `trpc-group/trpc-agent-go`. Resolve the local target checkout in
this order:

1. `MYCR_TARGET_CHECKOUT`
2. `../trpc-agent-go` relative to this repo
3. `/Users/guoqizhou/projects/github/trpc-agent-go`

Use `gh` for GitHub PR operations when authenticated.
