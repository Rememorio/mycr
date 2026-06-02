# Cache-Efficient MyCR Planning

## Context

The incremental planner reduced repeated review work in principle, but the
workflow could still behave like a full scan in practice. Two details caused
that:

1. The cheap open-PR index was allowed to contain full comments, review bodies,
   thread bodies, and other large fields. That made the "cheap" phase expensive
   in tokens and network payload before the planner even decided what changed.
2. The periodic full-sweep safety net promoted stale unchanged PRs directly to
   `heavy_review`. That protected freshness, but it also made daily runs reread
   old diffs and review threads even when the head SHA, checks, comments, and
   thread fingerprints were unchanged.

## Decision

Keep the full-open-PR index mandatory, but make it a true cache invalidation
index. It should carry stable IDs, timestamps, states, head SHAs, check
conclusions, and compact fingerprints, not full bodies or diffs.

Add a third planner action, `refresh_probe`, between `carry_forward` and
`heavy_review`. A stale unchanged PR now gets a lightweight freshness probe by
default. The probe rechecks cheap fields and reuses cached full metadata when
the `metadata_cache_key` is unchanged. It promotes to `heavy_review` only when a
fingerprint/cache key changes, a required fingerprint is missing, or the user
explicitly asks for a full heavy sweep.

Each planned PR now has a `metadata_cache_key` and `cache_mode`. The cache
manifest maps those keys to reusable full-metadata and report-entry cache paths
so future runs can skip full diff/source/thread-body collection for unchanged
blockers while still reacting immediately to new commits, CI transitions,
comments, or review-thread changes.

## Consequences

- Freshness is preserved because every run still refreshes cheap PR state, and
  any cache-key change promotes the PR to heavy review.
- Token usage drops because unchanged blockers can be reported from cached
  evidence instead of reloading full discussion and diff context.
- The old behavior remains available with `--force-full-sweep-action heavy`
  when metadata is corrupt or a true full re-review is requested.
