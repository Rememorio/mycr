# Repo-Managed MyCR Skill

## Decision

Use `/Users/guoqizhou/projects/github/mycr` as the canonical home for MyCR:

- canonical skill instructions in `skill/SKILL.md`
- renderer and archive scripts in `scripts/`
- source report JSON in `src/data/reports/`
- public report JSON/HTML in `public/reports/`
- self-evolution records in `data/evolution/`

The installed skill under `~/.codex/skills/mycr` should only bootstrap to this
repository.

## Rationale

The old setup made reports easy to lose because they lived under the target
checkout's local `.vscode` directory. It also made skill improvements hard to
track because the installed skill directory was not managed as a normal GitHub
repo.

Moving the workflow into this repo makes each improvement reviewable, commit
addressable, and deployable to the personal site.

## Follow-Up

Future runs should archive reports through `scripts/archive-report.mjs`, run
`npm run verify`, and push meaningful report history to `main`.
