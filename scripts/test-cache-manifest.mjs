import assert from "node:assert/strict";

import { makeCacheManifest } from "./mycr-cache-manifest.mjs";

const plan = {
  generated_at: "2026-06-02T05:00:00.000Z",
  repo: "trpc-group/trpc-agent-go",
  queue: [
    {
      number: 1,
      title: "agent: changed",
      url: "https://github.com/trpc-group/trpc-agent-go/pull/1",
      author: "alice",
      action: "heavy_review",
      cache_mode: "refresh_full_metadata",
      reasons: ["head_sha_changed"],
      metadata_cache_key: "new-key",
      previous_metadata_cache_key: "old-key",
    },
    {
      number: 2,
      title: "session: stale",
      url: "https://github.com/trpc-group/trpc-agent-go/pull/2",
      author: "bob",
      action: "refresh_probe",
      cache_mode: "refresh_lightweight_probe",
      reasons: ["force_full_sweep"],
      metadata_cache_key: "same-key",
      previous_metadata_cache_key: "same-key",
    },
    {
      number: 3,
      title: "tool: unchanged",
      url: "https://github.com/trpc-group/trpc-agent-go/pull/3",
      author: "carol",
      action: "carry_forward",
      cache_mode: "reuse_previous_result",
      reasons: ["unchanged_since_last_run"],
      metadata_cache_key: "carry-key",
      previous_metadata_cache_key: "carry-key",
    },
  ],
};

const manifest = makeCacheManifest(plan, {
  cacheDir: ".cache/mycr",
});

assert.equal(manifest.totals.open, 3);
assert.equal(manifest.totals.full_metadata_fetches, 1);
assert.equal(manifest.totals.lightweight_probes, 1);
assert.equal(manifest.totals.reusable_full_metadata, 2);

assert.equal(manifest.entries[0].should_fetch_full_metadata, true);
assert.equal(manifest.entries[0].can_reuse_full_metadata, false);
assert.equal(
  manifest.entries[0].full_metadata_path,
  ".cache/mycr/pr-1/new-key.full.json",
);

assert.equal(manifest.entries[1].should_refresh_lightweight_probe, true);
assert.equal(manifest.entries[1].can_reuse_full_metadata, true);
assert.equal(manifest.entries[2].should_fetch_full_metadata, false);
assert.equal(manifest.entries[2].can_reuse_full_metadata, true);

console.log("validated cache manifest behavior");
