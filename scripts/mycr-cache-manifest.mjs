import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const schemaVersion = 1;
const jsonIndent = 2;
const defaultCacheDir = ".mycr-cache/full-metadata";
const actionHeavyReview = "heavy_review";
const actionRefreshProbe = "refresh_probe";
const cacheModeRefreshFullMetadata = "refresh_full_metadata";
const cacheModeRefreshProbe = "refresh_lightweight_probe";
const cacheModeReusePreviousResult = "reuse_previous_result";
const unknownCacheKey = "unknown";

function usage() {
  console.error(
    [
      "usage: node scripts/mycr-cache-manifest.mjs --plan <plan.json> [--output <manifest.json>]",
      "",
      "Options:",
      `  --cache-dir <dir>  Directory for reusable full-metadata cache entries. Default: ${defaultCacheDir}`,
    ].join("\n"),
  );
}

function parseArgs(argv) {
  const parsed = {
    planPath: "",
    outputPath: "",
    cacheDir: defaultCacheDir,
  };

  const args = [...argv];
  while (args.length > 0) {
    const arg = args.shift();
    if (arg === "--plan") {
      parsed.planPath = args.shift() || "";
      continue;
    }
    if (arg === "--output") {
      parsed.outputPath = args.shift() || "";
      continue;
    }
    if (arg === "--cache-dir") {
      parsed.cacheDir = args.shift() || "";
      continue;
    }
    throw new Error(`unexpected argument: ${arg}`);
  }

  if (!parsed.planPath) {
    throw new Error("missing --plan path");
  }
  if (!parsed.cacheDir) {
    throw new Error("missing --cache-dir value");
  }

  return parsed;
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

function cacheModeForAction(action) {
  if (action === actionHeavyReview) {
    return cacheModeRefreshFullMetadata;
  }
  if (action === actionRefreshProbe) {
    return cacheModeRefreshProbe;
  }
  return cacheModeReusePreviousResult;
}

function safeCacheKey(value) {
  return asString(value) || unknownCacheKey;
}

function cachePath(cacheDir, number, cacheKey, suffix) {
  return path.posix.join(
    cacheDir,
    `pr-${number}`,
    `${safeCacheKey(cacheKey)}.${suffix}.json`,
  );
}

function makeCacheManifest(plan, options = {}) {
  const cacheDir = asString(options.cacheDir) || defaultCacheDir;
  const entries = asArray(plan.queue).map((item) => {
    const number = asNumber(item.number);
    const action = asString(item.action);
    const cacheMode = asString(item.cache_mode) || cacheModeForAction(action);
    const cacheKey = safeCacheKey(item.metadata_cache_key);
    const previousCacheKey = safeCacheKey(item.previous_metadata_cache_key);
    const fullMetadataReusable =
      action !== actionHeavyReview &&
      cacheKey !== unknownCacheKey &&
      cacheKey === previousCacheKey;

    return {
      number,
      title: asString(item.title),
      url: asString(item.url),
      author: asString(item.author),
      action,
      cache_mode: cacheMode,
      reasons: asArray(item.reasons),
      metadata_cache_key: cacheKey,
      previous_metadata_cache_key: previousCacheKey,
      full_metadata_path: cachePath(cacheDir, number, cacheKey, "full"),
      report_entry_path: cachePath(cacheDir, number, cacheKey, "report"),
      can_reuse_full_metadata: fullMetadataReusable,
      should_fetch_full_metadata: action === actionHeavyReview,
      should_refresh_lightweight_probe: action === actionRefreshProbe,
      should_write_full_metadata_cache: action === actionHeavyReview,
    };
  });

  return {
    schema_version: schemaVersion,
    generated_at: asString(plan.generated_at),
    repo: asString(plan.repo),
    cache_dir: cacheDir,
    totals: {
      open: entries.length,
      full_metadata_fetches: entries.filter(
        (entry) => entry.should_fetch_full_metadata,
      ).length,
      lightweight_probes: entries.filter(
        (entry) => entry.should_refresh_lightweight_probe,
      ).length,
      reusable_full_metadata: entries.filter((entry) => entry.can_reuse_full_metadata)
        .length,
    },
    entries,
  };
}

async function readJson(filePath) {
  const raw = await readFile(filePath, "utf8");
  return JSON.parse(raw);
}

async function main() {
  let args;
  try {
    args = parseArgs(process.argv.slice(2));
  } catch (error) {
    usage();
    throw error;
  }

  const plan = await readJson(path.resolve(args.planPath));
  const manifest = makeCacheManifest(plan, { cacheDir: args.cacheDir });
  const output = `${JSON.stringify(manifest, null, jsonIndent)}\n`;
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

export { makeCacheManifest };
