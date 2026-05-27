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

Skipped PR entries must be auditable. A report may group skipped PRs for
scanability, but each item still needs a concrete `skip_reason` and should use
structured `blockers` when the blocker is a discrete fact such as a CI check,
merge conflict, unresolved human thread, or stale `Changes Requested` state.
Never use aggregate GitHub states as the whole explanation when the exact
thread, check, or conflict can be named.

## Report UI Contract

Self-contained HTML reports must be readable in a narrow editor preview as well
as a normal browser:

- The report should feel like a polished review dashboard, not a dumped table.
  Use clear hierarchy, calm status color, generous spacing, rounded surfaces,
  and compact scan rows before exposing long-form detail.
- PR detail cards are collapsed by default. The collapsed row must still show a
  short outcome/problem summary so users can scan without opening every card.
- Expanding a card must not create horizontal overflow. Long PR titles, paths,
  SHA values, commands, and CI strings must wrap inside their cards.
- Dense review facts may be grouped visually, but they should not be placed in a
  sticky side rail that becomes the dominant content in narrow previews.
- Dashboard panels should size to their content. A short status panel must not be
  stretched to match a long timeline panel and leave a large blank white block.
- "Expand all" and "Collapse all" controls must keep each card's visible toggle
  label and `aria-expanded` state in sync.

## Website Contract

The site is a static Astro build with:

- public base path `/mycr`
- report list sorted by `generated_at` descending
- filters for merged, approved, commented, skipped, and follow-up runs
- links to each self-contained HTML report and raw JSON
- no dependency on runtime APIs

The archive page should share the same visual system as generated reports:

- Latest and historical runs should scan as product cards with clear primary
  actions and status counts.
- Navigation, search, filters, and cards must wrap gracefully in narrow editor
  previews without horizontal scrolling.
- Timeline entries should read both `label` and `text` fields so older reports
  do not render blank details.

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
