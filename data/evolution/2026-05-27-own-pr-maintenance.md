# Own PR Maintenance Path

## Context

MyCR originally treated pull requests authored by the authenticated reviewer as
`own_pr` skip cases. That avoided self-approval, but it also meant the
maintainer's own changes were not pushed toward the same review quality bar as
external pull requests.

For the repository owner's workflow, own PRs should still be audited. The
difference is the action taken after the audit: a valid finding should become a
direct branch fix, not a GitHub review comment from the same account.

## Decision

Own PRs now enter a separate maintenance path:

- Include own PRs in the run-level reviewability ledger instead of hiding them
  under a skip bucket.
- Use the same readiness and quality checks as external PRs where practical.
- Prefer a dedicated `git worktree` for checkout and fixes so existing target
  checkout changes are preserved.
- Push direct fixes to the PR branch when the authenticated account can write to
  it.
- Never submit self-review comments, self-approval, `LGTM`, self-merge, or
  third-party-style thread resolution for own PRs.
- Report successful own-PR handling as `maintained`, with direct fixes, tests,
  CI state, and any remaining external-review expectations.

## Reporting Impact

The report schema and dashboard support a `maintained` status. This keeps own
PR work visible without mixing it with approvals, comments, merges, or skipped
PRs.
