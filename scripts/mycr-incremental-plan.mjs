import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const schemaVersion = 1;
const defaultOverlapMinutes = 10;
const defaultForceFullSweepHours = 24;
const jsonIndent = 2;
const minuteInMilliseconds = 60 * 1000;
const hourInMilliseconds = 60 * minuteInMilliseconds;

const actionHeavyReview = "heavy_review";
const actionCarryForward = "carry_forward";

const reasonNoPreviousState = "no_previous_state";
const reasonNewPr = "new_pr";
const reasonForceFullSweep = "force_full_sweep";
const reasonHeadChanged = "head_sha_changed";
const reasonChecksChanged = "checks_changed";
const reasonThreadsChanged = "review_threads_changed";
const reasonCommentsChanged = "comments_changed";
const reasonReviewDecisionChanged = "review_decision_changed";
const reasonMergeabilityChanged = "mergeability_changed";
const reasonReadinessChanged = "readiness_changed";
const reasonBaseChanged = "base_ref_changed";
const reasonUpdatedAfterWatermark = "updated_after_watermark";
const reasonPreviousNotReached = "previous_not_reached";
const reasonMissingFingerprint = "missing_required_fingerprint";
const reasonUnchanged = "unchanged_since_last_run";

const wipLabelPattern = /\bwip\b/iu;
const wipTitlePattern = /(?:^|\W)wip(?:\W|$)/iu;

function usage() {
  console.error(
    [
      "usage: node scripts/mycr-incremental-plan.mjs --current <snapshot.json> [--previous <state-or-report.json>] [--output <plan.json>]",
      "",
      "Options:",
      "  --overlap-minutes <n>          Re-scan activity newer than previous start minus this overlap. Default: 10",
      "  --force-full-sweep-hours <n>   Re-scan every open PR when the previous state is older than this. Default: 24",
    ].join("\n"),
  );
}

function parseArgs(argv) {
  const parsed = {
    currentPath: "",
    previousPath: "",
    outputPath: "",
    overlapMinutes: defaultOverlapMinutes,
    forceFullSweepHours: defaultForceFullSweepHours,
  };

  const args = [...argv];
  while (args.length > 0) {
    const arg = args.shift();
    if (arg === "--current") {
      parsed.currentPath = args.shift() || "";
      continue;
    }
    if (arg === "--previous") {
      parsed.previousPath = args.shift() || "";
      continue;
    }
    if (arg === "--output") {
      parsed.outputPath = args.shift() || "";
      continue;
    }
    if (arg === "--overlap-minutes") {
      parsed.overlapMinutes = parseNonNegativeNumber(
        args.shift(),
        "--overlap-minutes",
      );
      continue;
    }
    if (arg === "--force-full-sweep-hours") {
      parsed.forceFullSweepHours = parseNonNegativeNumber(
        args.shift(),
        "--force-full-sweep-hours",
      );
      continue;
    }
    throw new Error(`unexpected argument: ${arg}`);
  }

  if (!parsed.currentPath) {
    throw new Error("missing --current snapshot path");
  }

  return parsed;
}

function parseNonNegativeNumber(value, flagName) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed < 0) {
    throw new Error(`${flagName} must be a non-negative number`);
  }
  return parsed;
}

async function readJson(filePath) {
  const raw = await readFile(filePath, "utf8");
  return JSON.parse(raw);
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function asString(value) {
  return typeof value === "string" ? value : "";
}

function asNumber(value) {
  return Number.isFinite(value) ? value : 0;
}

function normalizeDate(value) {
  const text = asString(value);
  if (!text) {
    return "";
  }
  const timestamp = Date.parse(text);
  if (Number.isNaN(timestamp)) {
    return text;
  }
  return new Date(timestamp).toISOString();
}

function dateValue(value) {
  const timestamp = Date.parse(asString(value));
  return Number.isNaN(timestamp) ? 0 : timestamp;
}

function stableStringify(value) {
  if (Array.isArray(value)) {
    return `[${value.map((item) => stableStringify(item)).join(",")}]`;
  }
  if (value && typeof value === "object") {
    const keys = Object.keys(value).sort();
    const fields = keys.map(
      (key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`,
    );
    return `{${fields.join(",")}}`;
  }
  return JSON.stringify(value);
}

function normalizeLabels(pr) {
  return asArray(pr.labels)
    .map((label) => {
      if (typeof label === "string") {
        return label;
      }
      return asString(label?.name);
    })
    .filter(Boolean)
    .sort((left, right) => left.localeCompare(right));
}

function hasWipMarker(title, labels) {
  return (
    wipTitlePattern.test(asString(title)) ||
    labels.some((label) => wipLabelPattern.test(label))
  );
}

function normalizeFingerprint(pr, explicitField, fallbackFields) {
  if (typeof pr[explicitField] === "string" && pr[explicitField]) {
    return pr[explicitField];
  }

  for (const field of fallbackFields) {
    if (pr[field] !== undefined) {
      return stableStringify(pr[field]);
    }
  }

  return "";
}

function normalizePullRequest(pr) {
  const labels = normalizeLabels(pr);
  const title = asString(pr.title);
  const isDraft = Boolean(pr.is_draft ?? pr.isDraft);
  const headSha = asString(pr.head_sha ?? pr.headSha);
  const baseRef = asString(pr.base_ref ?? pr.baseRefName ?? pr.baseRef);
  const updatedAt = normalizeDate(pr.updated_at ?? pr.updatedAt);
  const latestActivityAt = normalizeDate(
    pr.latest_activity_at ?? pr.latestActivityAt ?? pr.updated_at ?? pr.updatedAt,
  );

  return {
    number: asNumber(pr.number),
    title,
    url: asString(pr.url),
    author: asString(pr.author ?? pr.author_login ?? pr.authorLogin),
    state: asString(pr.state || "OPEN").toUpperCase(),
    is_draft: isDraft,
    is_wip: Boolean(pr.is_wip ?? pr.isWip ?? hasWipMarker(title, labels)),
    labels,
    base_ref: baseRef,
    head_ref: asString(pr.head_ref ?? pr.headRefName ?? pr.headRef),
    head_sha: headSha,
    updated_at: updatedAt,
    latest_activity_at: latestActivityAt,
    mergeable: asString(pr.mergeable),
    review_decision: asString(pr.review_decision ?? pr.reviewDecision),
    checks_fingerprint: normalizeFingerprint(pr, "checks_fingerprint", [
      "checks",
      "status_checks",
      "statusChecks",
      "workflow_runs",
      "workflowRuns",
    ]),
    review_threads_fingerprint: normalizeFingerprint(
      pr,
      "review_threads_fingerprint",
      ["review_threads", "reviewThreads"],
    ),
    comments_fingerprint: normalizeFingerprint(pr, "comments_fingerprint", [
      "comments",
      "reviews",
    ]),
  };
}

function normalizePullRequests(value) {
  const source = value?.pull_requests ?? value?.pullRequests ?? value;
  if (Array.isArray(source)) {
    return source.map(normalizePullRequest).filter((pr) => pr.number > 0);
  }
  if (source && typeof source === "object") {
    return Object.values(source)
      .map(normalizePullRequest)
      .filter((pr) => pr.number > 0);
  }
  return [];
}

function extractRunState(value) {
  if (!value) {
    return {
      generated_at: "",
      run_started_at: "",
      pull_requests: {},
    };
  }

  const state = value.run_state ?? value.runState ?? value;
  const pullRequests = {};
  for (const pr of normalizePullRequests(state)) {
    pullRequests[String(pr.number)] = {
      ...pr,
      ledger_bucket: asString(pr.ledger_bucket ?? pr.ledgerBucket),
      last_action: asString(pr.last_action ?? pr.lastAction),
      last_heavy_reviewed_head_sha: asString(
        pr.last_heavy_reviewed_head_sha ?? pr.lastHeavyReviewedHeadSha,
      ),
      last_verified_at: normalizeDate(pr.last_verified_at ?? pr.lastVerifiedAt),
      blockers: asArray(pr.blockers),
    };
  }

  return {
    generated_at: normalizeDate(
      state.generated_at ?? state.generatedAt ?? value.generated_at,
    ),
    run_started_at: normalizeDate(
      state.run_started_at ?? state.runStartedAt ?? state.started_at ?? state.startedAt,
    ),
    pull_requests: pullRequests,
  };
}

function readinessFingerprint(pr) {
  return stableStringify({
    state: pr.state,
    is_draft: pr.is_draft,
    is_wip: pr.is_wip,
    labels: pr.labels,
  });
}

function reasonIfChanged(reasons, current, previous, field, reason) {
  if (current[field] !== previous[field]) {
    reasons.push(reason);
  }
}

function hasMissingRequiredFingerprint(current, previous) {
  const requiredFields = [
    "checks_fingerprint",
    "review_threads_fingerprint",
    "comments_fingerprint",
  ];
  return requiredFields.some((field) => !current[field] || !previous[field]);
}

function isPreviouslyNotReached(previous) {
  return (
    previous.ledger_bucket === "not_reached" ||
    previous.last_action === "not_reached"
  );
}

function shouldForceFullSweep(previousState, generatedAt, forceFullSweepHours) {
  const previousTime = dateValue(
    previousState.run_started_at || previousState.generated_at,
  );
  const currentTime = dateValue(generatedAt);
  if (previousTime === 0 || currentTime === 0) {
    return false;
  }
  const maxAge = forceFullSweepHours * hourInMilliseconds;
  return maxAge > 0 && currentTime - previousTime >= maxAge;
}

function makeWatermark(previousState, overlapMinutes) {
  const baseTime = dateValue(
    previousState.run_started_at || previousState.generated_at,
  );
  if (baseTime === 0) {
    return "";
  }
  return new Date(baseTime - overlapMinutes * minuteInMilliseconds).toISOString();
}

function updatedAfterWatermark(pr, watermark) {
  const watermarkTime = dateValue(watermark);
  const activityTime = dateValue(pr.latest_activity_at || pr.updated_at);
  return watermarkTime > 0 && activityTime > watermarkTime;
}

function planPullRequest(current, previous, options) {
  const reasons = [];

  if (!previous) {
    reasons.push(options.hasPreviousState ? reasonNewPr : reasonNoPreviousState);
    return {
      action: actionHeavyReview,
      reasons,
    };
  }

  if (options.forceFullSweep) {
    reasons.push(reasonForceFullSweep);
  }

  if (hasMissingRequiredFingerprint(current, previous)) {
    reasons.push(reasonMissingFingerprint);
  }

  reasonIfChanged(reasons, current, previous, "head_sha", reasonHeadChanged);
  reasonIfChanged(reasons, current, previous, "checks_fingerprint", reasonChecksChanged);
  reasonIfChanged(
    reasons,
    current,
    previous,
    "review_threads_fingerprint",
    reasonThreadsChanged,
  );
  reasonIfChanged(reasons, current, previous, "comments_fingerprint", reasonCommentsChanged);
  reasonIfChanged(reasons, current, previous, "review_decision", reasonReviewDecisionChanged);
  reasonIfChanged(reasons, current, previous, "mergeable", reasonMergeabilityChanged);
  reasonIfChanged(reasons, current, previous, "base_ref", reasonBaseChanged);

  if (readinessFingerprint(current) !== readinessFingerprint(previous)) {
    reasons.push(reasonReadinessChanged);
  }

  if (isPreviouslyNotReached(previous)) {
    reasons.push(reasonPreviousNotReached);
  }

  if (
    current.latest_activity_at !== previous.latest_activity_at &&
    updatedAfterWatermark(current, options.watermark)
  ) {
    reasons.push(reasonUpdatedAfterWatermark);
  }

  const uniqueReasons = [...new Set(reasons)];
  if (uniqueReasons.length > 0) {
    return {
      action: actionHeavyReview,
      reasons: uniqueReasons,
    };
  }

  return {
    action: actionCarryForward,
    reasons: [reasonUnchanged],
  };
}

function makePlan(currentSnapshot, previousSnapshot, options = {}) {
  const generatedAt = normalizeDate(
    currentSnapshot.generated_at ?? currentSnapshot.generatedAt ?? new Date().toISOString(),
  );
  const previousState = extractRunState(previousSnapshot);
  const hasPreviousState = Object.keys(previousState.pull_requests).length > 0;
  const overlapMinutes = options.overlapMinutes ?? defaultOverlapMinutes;
  const forceFullSweepHours =
    options.forceFullSweepHours ?? defaultForceFullSweepHours;
  const watermark = makeWatermark(previousState, overlapMinutes);
  const forceFullSweep = shouldForceFullSweep(
    previousState,
    generatedAt,
    forceFullSweepHours,
  );

  const queue = normalizePullRequests(currentSnapshot).map((current) => {
    const previous = previousState.pull_requests[String(current.number)];
    const planned = planPullRequest(current, previous, {
      forceFullSweep,
      hasPreviousState,
      watermark,
    });
    return {
      number: current.number,
      title: current.title,
      url: current.url,
      author: current.author,
      action: planned.action,
      reasons: planned.reasons,
      head_sha: current.head_sha,
      previous_head_sha: previous?.head_sha || "",
      previous_bucket: previous?.ledger_bucket || "",
      previous_last_action: previous?.last_action || "",
      latest_activity_at: current.latest_activity_at,
    };
  });

  const heavyReview = queue.filter((item) => item.action === actionHeavyReview);
  const carryForward = queue.filter((item) => item.action === actionCarryForward);
  const currentByNumber = new Set(queue.map((item) => String(item.number)));
  const closedOrMissing = Object.values(previousState.pull_requests)
    .filter((previous) => !currentByNumber.has(String(previous.number)))
    .map((previous) => ({
      number: previous.number,
      title: previous.title,
      url: previous.url,
      author: previous.author,
      previous_bucket: previous.ledger_bucket || "",
      previous_last_action: previous.last_action || "",
    }));

  const runStatePullRequests = {};
  for (const current of normalizePullRequests(currentSnapshot)) {
    const queueItem = queue.find((item) => item.number === current.number);
    const previous = previousState.pull_requests[String(current.number)];
    runStatePullRequests[String(current.number)] = {
      ...current,
      ledger_bucket:
        queueItem.action === actionHeavyReview
          ? "eligible_candidate"
          : "carried_forward",
      last_action: queueItem.action,
      last_heavy_reviewed_head_sha:
        queueItem.action === actionHeavyReview
          ? current.head_sha
          : previous?.last_heavy_reviewed_head_sha || previous?.head_sha || "",
      last_verified_at: generatedAt,
      planning_reasons: queueItem.reasons,
      blockers: previous?.blockers || [],
    };
  }

  return {
    schema_version: schemaVersion,
    generated_at: generatedAt,
    repo: asString(currentSnapshot.repo),
    previous_generated_at: previousState.generated_at,
    overlap_watermark: watermark,
    force_full_sweep: forceFullSweep,
    totals: {
      open: queue.length,
      heavy_review: heavyReview.length,
      carry_forward: carryForward.length,
      closed_or_missing: closedOrMissing.length,
    },
    queue,
    heavy_review: heavyReview,
    carry_forward: carryForward,
    closed_or_missing: closedOrMissing,
    run_state: {
      schema_version: schemaVersion,
      generated_at: generatedAt,
      run_started_at: generatedAt,
      repo: asString(currentSnapshot.repo),
      overlap_watermark: watermark,
      pull_requests: runStatePullRequests,
    },
  };
}

async function main() {
  let args;
  try {
    args = parseArgs(process.argv.slice(2));
  } catch (error) {
    usage();
    throw error;
  }

  const currentSnapshot = await readJson(path.resolve(args.currentPath));
  const previousSnapshot = args.previousPath
    ? await readJson(path.resolve(args.previousPath))
    : undefined;
  const plan = makePlan(currentSnapshot, previousSnapshot, {
    overlapMinutes: args.overlapMinutes,
    forceFullSweepHours: args.forceFullSweepHours,
  });
  const output = `${JSON.stringify(plan, null, jsonIndent)}\n`;

  if (args.outputPath) {
    await writeFile(path.resolve(args.outputPath), output, "utf8");
  } else {
    process.stdout.write(output);
  }
}

const currentFileUrl = pathToFileURL(fileURLToPath(import.meta.url)).href;
if (
  process.argv[1] &&
  pathToFileURL(path.resolve(process.argv[1])).href === currentFileUrl
) {
  main().catch((error) => {
    console.error(error);
    process.exit(1);
  });
}

export {
  actionCarryForward,
  actionHeavyReview,
  makePlan,
  normalizePullRequest,
  reasonChecksChanged,
  reasonForceFullSweep,
  reasonHeadChanged,
  reasonNewPr,
  reasonNoPreviousState,
  reasonMissingFingerprint,
  reasonUnchanged,
  reasonUpdatedAfterWatermark,
};
