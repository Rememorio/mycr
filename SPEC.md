# MyCR Repository Spec

## Goals

MyCR must be easy to run, audit, and improve:

- The skill instructions are versioned in Git.
- Every run can publish structured JSON and a self-contained HTML report.
- The `/mycr` site shows all historical runs without needing local files.
- Improvements discovered during real runs are captured and can become tracked
  skill, script, or UI changes.

## Non-Goals

- This repo does not vendor `trpc-agent-go`.
- This repo does not replace GitHub PR review state. It summarizes and links to
  the source PRs.
- This repo does not store private credentials.

## Report Artifact Contract

Each run uses a timestamped basename:

```text
mycr-YYYYmmdd-HHMMSS
```

Required tracked files:

- `src/data/reports/<basename>.json`
- `public/reports/<basename>.json`
- `public/reports/<basename>.html`

The source JSON is the durable data model for the archive page. The public JSON
and HTML files are served as direct artifacts for inspection and sharing.

## Website Contract

The site is a static Astro build with:

- public base path `/mycr`
- report list sorted by `generated_at` descending
- filters for merged, approved, commented, skipped, and follow-up runs
- links to each self-contained HTML report and raw JSON
- no dependency on runtime APIs

## Skill Contract

`skill/SKILL.md` is the canonical instruction file. The installed Codex skill
must read this file first and follow it.

The skill must use repo-relative paths wherever possible. Absolute local paths
are allowed only as documented fallbacks for bootstrap compatibility.

## Evolution Contract

Self-evolution is deliberate and auditable:

1. Capture improvement candidates in `data/evolution/backlog.md`.
2. Promote stable decisions into dated files under `data/evolution/`.
3. Update `skill/SKILL.md`, scripts, specs, or the site in this repo.
4. Run `npm run verify`.
5. Commit and push to `main`.
