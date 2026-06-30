# Source Problem Evidence Gates

## Context

MyCR previously had strong gates for CI, review-thread state, mergeability, and
diff-level code quality, but it did not make the source problem itself a hard
approval gate. A bugfix could look locally reasonable, have passing tests, and
still be unnecessary or speculative when the linked problem report was stale,
contradicted by current base behavior, or missing the raw evidence needed to
connect the symptom to the edited code path.

There is a related design-review failure mode: the source problem can be real,
but the requested or submitted implementation can still use the wrong control
surface. A linked issue's proposed fix should be treated as input, not as the
contract. Review must distinguish user pain from API/default/configuration/docs
design.

## Decision

Treat source-problem evidence as first-class review input for bugfixes,
behavior fixes, compatibility fixes, and linked-problem PRs. Each such PR should
be classified as:

- `confirmed`
- `plausible_but_unproven`
- `contradicted_or_stale`
- `product_decision_needed`

Only confirmed problems, or explicit design/product changes with a stated
contract, may proceed to approval or merge. Unverified or contradicted premises
must be reported as blockers even when CI is green and the implementation looks
plausible.

When the problem is real but the submitted approach is the wrong abstraction,
report a `solution_fit` blocker or residual risk. Examples include misleading
mode switches, defaults that push complexity onto common users, documentation
that promises stronger behavior than the runtime provides, or options that
encode a narrow workaround as a broad public contract.

## Implementation Notes

- The skill now requires a problem-evidence pass before external candidate
  approval or merge.
- The subagent prompt asks for necessity and implementation-derivation analysis
  before diff-level findings.
- The report schema and renderer expose necessity assessment, evidence checked,
  base reproduction, evidence gaps, implementation derivation, and solution-fit
  assessment.
- New blocker kinds distinguish missing evidence, stale premises, implementation
  scope uncertainty, and poor solution fit from ordinary CI, review, or
  mergeability blockers.
