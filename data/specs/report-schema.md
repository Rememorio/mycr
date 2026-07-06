# MyCR Report Schema

The archive page accepts the JSON shape produced by `mycr` reports.

## Top-Level Fields

- `title`: display title.
- `repo`: reviewed GitHub repository, normally `trpc-group/trpc-agent-go`.
- `generated_at`: ISO-like timestamp for the run.
- `overview`: Chinese-first narrative summary.
- `timeline`: ordered run events.
- `approved`: PRs approved or merged by the run.
- `commented`: PRs that received inline comments.
- `maintained`: own PRs that were audited directly and either fixed on their
  branch or confirmed as needing no self-review comment.
- `blocked`: PRs blocked after candidate processing.
- `skipped_groups`: skipped PRs grouped by reason.
- `follow_up`: PRs requiring later attention.
- `incremental_plan`: optional machine-readable plan produced before the heavy
  review pass.
- `run_state`: optional machine-readable snapshot for the next incremental run.

## PR Entry Fields

Reviewed entries should include:

- `number`, `title`, `url`, `author`, `status`
- `technical_background`
- `problem`
- `necessity_assessment`: for bugfixes or linked problem reports, whether the
  source problem is `confirmed`, `plausible_but_unproven`,
  `contradicted_or_stale`, or `product_decision_needed`, with a short human
  explanation.
- `evidence_checked`: source problem reports, PR discussion, logs, raw payloads,
  reproduction steps, current-base behavior, tests, docs, or maintainer
  statements checked before judging the premise.
- `reproduction_on_base`: whether the problem was reproduced or otherwise
  verified against the current target base, and why direct reproduction was not
  practical if it was skipped.
- `issue_evidence_gaps`: missing evidence that prevents a confident approval,
  such as raw provider payloads, a minimal current-base reproduction, or an
  explicit contract decision.
- `problem_framing`
- `root_cause`
- `approach`
- `implementation_derivation`: why the edited code path and patch scope follow
  from the confirmed problem evidence, or what part of that chain remains
  uncertain.
- `solution_fit_assessment`: whether the chosen code behavior, public API,
  option, default, documentation, example, or migration path is the right
  control surface for the underlying user pain, not merely the literal proposed
  fix.
- `alternative_designs`
- `tradeoffs`
- `design_assessment`
- `modules`
- `api_surface`
- `change_inventory`
- `semantic_changes`
- `module_impact`
- `cross_module_impact`
- `behavior_impact`
- `tests_docs`
- `attention_points`
- `outcome`
- `risk`
- `ci_state`
- `merge_policy`: optional action policy when MyCR may review or approve a PR
  but must not perform the final merge. Prefer an object with:
  - `mode`: normally `human_required`.
  - `reason`: the policy source, such as `external_contributor`,
    `repo_policy`, or `user_policy`.
  - `required_evidence`: what human action or evidence clears the policy.
  - `current_evidence`: what the run checked, such as author association,
    approvals, maintainer comments, or merge actor.
  - `summary`: a short human-readable explanation for renderers.
- `inline_comments`
- `direct_fixes`: optional array for own PRs with direct branch maintenance
  details. Each object should include the branch, commit SHA or message when
  available, files touched, tests run, and push/CI state.
- `self_review_policy`: optional text for own PRs confirming that no review
  comments, `LGTM` approval, or merge were submitted by the same account.

Skipped entries should also include:

- `skip_reason`: the concrete reason this PR was not reviewed in the run.
- `blockers`: optional array of discrete blocker facts. Prefer this over a
  broad paragraph when a PR is excluded. Each object may include:
  - `kind`: `ci`, `human_review`, `bot_review`, `merge_conflict`,
    `draft_wip`, `own_pr`, `soft_ci`, `necessity`,
    `insufficient_evidence`, `stale_issue`, `implementation_scope`,
    `solution_fit`, `manual_review`,
    `not_reached`, or `other`.
  - `summary`: the exact blocker, such as a check name, conflict state, or
    unresolved review request.
  - `reviewer`: reviewer login for human or bot review blockers.
  - `url`: thread, comment, check, or PR URL.
  - `path` and `line`: changed file location when relevant.
  - `latest_response`: latest author response when review state matters.
  - `verification`: why the blocker is still valid, stale, resolved, or only
    a soft gate.
- `readiness_audit`: optional plain-language audit of why a broad GitHub state
  such as `CHANGES_REQUESTED` does or does not block review.

Use `manual_review` when the PR may still be code-reviewed, but MyCR must not
decide acceptance or submit approval/merge actions. Typical evidence includes
mentorship/contest issue labels, issue text that reserves the task for program
participants, multiple active PRs competing for one issue, explicit maintainer
selection requirements, security-boundary changes, broad public API or
architecture decisions, broad test or verification contracts that set
expectations for multiple backends, or roadmap/product ownership decisions. A
MyCR-submitted `LGTM` is not evidence that the human decision happened.

Use `merge_policy` separately when the PR may pass code review, but the final
merge action must be performed by a human. This is not a blocker kind: blockers
explain why the PR is not ready for automated approval, while `merge_policy`
explains why MyCR cannot perform a specific action.

The report archive page only requires a subset, but richer fields make the
self-contained HTML report useful without opening GitHub.

## Incremental Plan Fields

`incremental_plan` may mirror the output from
`scripts/mycr-incremental-plan.mjs`:

- `schema_version`: planner schema version.
- `generated_at`: when the lightweight index was evaluated.
- `previous_generated_at`: previous run-state timestamp when available.
- `overlap_watermark`: previous run start minus the configured overlap window.
- `force_full_sweep`: whether every open PR was intentionally promoted to the
  heavy path.
- `totals`: counts for open PRs, heavy-review PRs, carried-forward PRs, and
  PRs that disappeared since the previous state.
- `queue`: one item per open PR with `number`, `action`, `reasons`, head SHA,
  previous head SHA, and latest activity time.
- `heavy_review`: queue subset that needs expensive diff, source, CI, thread,
  subagent, or report-writing work.
- `carry_forward`: queue subset whose concrete blocker can be carried forward
  because the lightweight fingerprints did not change.

Planner reasons should be discrete strings such as `new_pr`,
`head_sha_changed`, `checks_changed`, `review_threads_changed`,
`comments_changed`, `readiness_changed`, `previous_not_reached`,
`updated_after_watermark`, `missing_required_fingerprint`, or
`force_full_sweep`.

## Run State Snapshot

`run_state` is hidden workflow memory for the next run. It should be compact,
stable, and safe to publish. Store only GitHub metadata and review-state facts,
not local paths, private tokens, temporary files, or raw model prompts.
Any stored excerpt from GitHub comments, reviews, checks, or issue text must be
valid Unicode. Collectors should sanitize lone surrogate characters and
truncate text by Unicode code point rather than UTF-16 index so serialized JSON
remains parseable by standard tools.

Recommended fields:

- `schema_version`
- `generated_at`
- `run_started_at`
- `repo`
- `overlap_watermark`
- `pull_requests`: object keyed by PR number. Each item should include the
  lightweight index fields used for change detection: title, author, labels,
  draft/WIP state, base ref, head ref, head SHA, update/activity timestamps,
  mergeability, review decision, check fingerprint, review-thread fingerprint,
  comment/review fingerprint, ledger bucket, last action, last heavy-reviewed
  head SHA, last verification time, planning reasons, and carried-forward
  blockers when applicable.

Do not let `run_state` replace final-action checks. A MyCR run must still fresh
fetch head SHA, checks, comments, and review threads before posting comments,
approving, merging, or pushing own-PR fixes.
