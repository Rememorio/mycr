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

## PR Entry Fields

Reviewed entries should include:

- `number`, `title`, `url`, `author`, `status`
- `technical_background`
- `problem`
- `problem_framing`
- `root_cause`
- `approach`
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
    `draft_wip`, `own_pr`, `soft_ci`, `not_reached`, or `other`.
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

The report archive page only requires a subset, but richer fields make the
self-contained HTML report useful without opening GitHub.
