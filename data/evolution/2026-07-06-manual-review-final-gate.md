# Manual Review Final Gate

## Observation

Recent runs approved and merged PRs that should have stayed in human-controlled
paths after CI became green, including program-track work, security-boundary
work, and broad verification-contract changes. The existing `manual_review`
rule named part of the right risk class, but it was not enforced as an
unavoidable final-action predicate before `LGTM` and merge.

The same run pattern can affect non-member PRs even when their code review is
otherwise useful: MyCR can review the code, but the repository may still require
a human to perform the final merge.

## Change

- Recheck `manual_review` immediately before approval and merge.
- Treat a MyCR-submitted `LGTM` as insufficient evidence that a maintainer made
  the human selection decision.
- Add `merge_policy` for action-level limits such as `human_required`, keeping
  it separate from blocker kinds and applying it by default to PRs whose authors
  are not owners, members, or collaborators.
- Keep `human_review` focused on unresolved human review comments or threads.

## Expected Effect

Mentorship, contest, security-boundary, broad API, architecture, and competing
candidate PRs can still be audited by MyCR, but MyCR cannot convert a clean code
review into the human decision to accept and merge the PR. PRs that only need a
human final merge can be reported as reviewed or approved while remaining
unmerged.
