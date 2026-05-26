# Reading Priority Visuals

## Problem

The detailed HTML report had better structure than the original stacked field
layout, but all PR cards still had similar visual weight. Important review
findings, large features, and low-risk merges were not easy to distinguish at a
glance.

## Decision

The full-report renderer now computes a reading recommendation for every PR:
`Deep Read`, `Read Carefully`, `Quick Skim`, or `Blocker Only`. Cards show the
recommendation in the header and the side rail repeats the reason. A compact
reading guide near the top lists the PRs that deserve attention first.

Important words such as `P1`, `FAILURE`, `LGTM`, `merged`, API changes,
compatibility risk, and blockers are highlighted inline with restrained colors.

## Expected Effect

The reader can scan a report quickly, identify the PRs that need careful review,
and avoid spending time on low-risk or currently blocked entries.
