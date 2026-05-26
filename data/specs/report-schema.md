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

The report archive page only requires a subset, but richer fields make the
self-contained HTML report useful without opening GitHub.
