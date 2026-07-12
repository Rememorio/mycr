import { spawnSync } from "node:child_process";
import { copyFile, mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const sourceReportDir = path.join(repoRoot, "src", "data", "reports");
const publicReportDir = path.join(repoRoot, "public", "reports");
const rendererPath = path.join(repoRoot, "scripts", "render_mycr_report.py");
const qualityPath = path.join(repoRoot, "scripts", "report-quality.mjs");
const jsonExtension = ".json";
const htmlExtension = ".html";
const htmlFlag = "--html";
const privateTopLevelFields = [
  "run_state",
  "incremental_plan",
  "metadata_cache",
  "metadata_cache_key",
  "reviewability_ledger",
];
const privateNestedFields = new Set([
  "comment_only",
  "target_checkout_dirty_preserved",
  "target_worktree_dirty_preserved",
]);
const publicTextReplacements = [
  [/\bsubagent\b/giu, "agent"],
  [/按最新心跳重新执行/gu, "重新执行全量检查"],
  [/按照用户明确要求/gu, "本轮采用 comment-only 策略"],
  [/本轮用户要求只发 comments/gu, "本轮采用 comment-only 策略"],
  [/本轮用户只允许 comments/gu, "本轮运行策略只允许提交 comments"],
  [/本轮运行策略只允许提交 comments/gu, "本轮未执行审批或合入"],
  [/这次按用户限制/gu, "本轮按 comment-only 策略"],
  [/用户限制/gu, "运行策略"],
  [/previous_reviewed_clean_comment_only/giu, "previously_reviewed_no_action"],
  [/上轮已复核 clean/gu, "上轮已复核"],
  [/本轮保持 deferred/gu, "本轮暂不审批"],
  [/clean[-_ ]deferred/giu, "已复核但暂不审批"],
  [/comment-only run/giu, "comment-only 模式"],
  [/\bcomment-only\b/giu, "仅评论"],
  [/lightweight state/giu, "状态复用"],
  [/\bnot_reached_status_refresh\b/giu, "status_refreshed_waiting_trigger"],
  [/增量计划/gu, "复核计划"],
  [/历史状态字段/gu, "历史报告状态"],
  [/轻量索引/gu, "状态索引"],
  [/持久化状态字段/gu, "可复用状态"],
  [/\bcheap-index\b/giu, "状态索引"],
  [/\brenderer\b/giu, "报告展示"],
  [/reviewed_clean_deferred\s*\/\s*reviewed_manual_deferred/giu, "已复核但暂不审批 / 需人工选择后再处理"],
  [/MyCR 已 fast-forward 检查/gu, "已完成仓库同步检查"],
  [/fast-forward pull/giu, "同步"],
  [/\bfast-forward\b/giu, "同步"],
  [/刷新 origin\/wine\/june refs/giu, "刷新远端分支状态"],
  [/origin\/wine\/june refs/giu, "远端分支状态"],
  [/REST fallback/giu, "最新状态刷新"],
  [/GitHub App 代发标识/giu, "可见代发标识"],
  [/源 JSON\/质量检查/gu, "报告质量校验"],
  [/源 JSON/gu, "报告数据"],
  [/质量检查/gu, "质量校验"],
  [/源报告保留下一轮所需状态，公共报告剥离内部运行字段/gu, "报告已完成归档，公共页面只保留面向维护者的审计事实"],
  [/计划器/gu, "复核流程"],
  [/状态复用/gu, "已知状态沿用"],
  [/深审/gu, "深入复核"],
  [/未进入本轮深度复核队列/gu, "当前未发现新增高优先级触发信号"],
  [/未进入深度复核队列/gu, "当前未发现新增高优先级触发信号"],
  [/\bmetadata\b/giu, "状态信息"],
  [/\bpublic JSON\/HTML\b/giu, "公共报告"],
  [/内部运行词/gu, "内部诊断词"],
  [/\blatest report\b/giu, "最新报告"],
  [/\bRun-state\b/giu, "报告状态"],
  [/\brun-state\b/giu, "报告状态"],
  [/\brun state\b/giu, "报告状态"],
  [/\bcollector\b/giu, "状态采集器"],
  [/\bnot_collected\b/giu, "未采集"],
  [/\bprocessed\+skipped\b/giu, "已处理和暂缓处理"],
  [/\bopen_prs\b/giu, "open PR 总数"],
  [/\breview thread\b/giu, "review 线程"],
  [/\blocked reason\b/giu, "锁定说明"],
  [/\bmerge simulation\b/giu, "冲突预检查"],
  [/指纹/gu, "状态摘要"],
  [/公共报告 是否包含内部诊断词/gu, "维护者报告是否存在不应展示的诊断信息"],
];

function usage() {
  console.error(
    "usage: node scripts/archive-report.mjs <summary.json> [--html <report.html>]",
  );
}

function parseArgs(argv) {
  const args = [...argv];
  const parsed = {
    summaryPath: "",
    htmlPath: "",
  };

  while (args.length > 0) {
    const arg = args.shift();
    if (arg === htmlFlag) {
      parsed.htmlPath = args.shift() || "";
      continue;
    }
    if (!parsed.summaryPath) {
      parsed.summaryPath = arg || "";
      continue;
    }
    throw new Error(`unexpected argument: ${arg}`);
  }

  if (!parsed.summaryPath) {
    throw new Error("missing summary JSON path");
  }
  if (!parsed.summaryPath.endsWith(jsonExtension)) {
    throw new Error("summary path must end with .json");
  }
  if (parsed.htmlPath && !parsed.htmlPath.endsWith(htmlExtension)) {
    throw new Error("HTML path must end with .html");
  }

  return parsed;
}

async function readJson(filePath) {
  const raw = await readFile(filePath, "utf8");
  return JSON.parse(raw);
}

function publicReportFrom(report) {
  const publicReport = JSON.parse(JSON.stringify(report));
  for (const field of privateTopLevelFields) {
    delete publicReport[field];
  }
  stripPrivateNestedFields(publicReport);
  rewritePublicText(publicReport);
  return publicReport;
}

function stripPrivateNestedFields(value) {
  if (Array.isArray(value)) {
    for (const item of value) {
      stripPrivateNestedFields(item);
    }
    return;
  }
  if (!value || typeof value !== "object") {
    return;
  }
  for (const key of Object.keys(value)) {
    if (privateNestedFields.has(key)) {
      delete value[key];
      continue;
    }
    stripPrivateNestedFields(value[key]);
  }
}

function rewritePublicText(value) {
  if (Array.isArray(value)) {
    for (const item of value) {
      rewritePublicText(item);
    }
    return;
  }
  if (!value || typeof value !== "object") {
    return;
  }
  for (const [key, child] of Object.entries(value)) {
    if (typeof child === "string") {
      value[key] = publicTextReplacements.reduce(
        (current, [pattern, replacement]) => current.replace(pattern, replacement),
        child,
      );
      continue;
    }
    rewritePublicText(child);
  }
}

async function main() {
  let args;
  try {
    args = parseArgs(process.argv.slice(2));
  } catch (error) {
    usage();
    throw error;
  }

  const summaryPath = path.resolve(args.summaryPath);
  const reportName = path.basename(summaryPath);
  const htmlName = reportName.replace(/\.json$/u, htmlExtension);
  const sourceJsonPath = path.join(sourceReportDir, reportName);
  const publicJsonPath = path.join(publicReportDir, reportName);
  const publicHtmlPath = path.join(publicReportDir, htmlName);

  await mkdir(sourceReportDir, { recursive: true });
  await mkdir(publicReportDir, { recursive: true });
  await copyFile(summaryPath, sourceJsonPath);

  const quality = spawnSync(
    "node",
    [qualityPath, "--file", sourceJsonPath, "--write", "--check"],
    { stdio: "inherit" },
  );
  if (quality.status !== 0) {
    throw new Error(`report quality check exited with status ${quality.status}`);
  }

  const publicReport = publicReportFrom(await readJson(sourceJsonPath));
  await writeFile(publicJsonPath, `${JSON.stringify(publicReport, null, 2)}\n`, "utf8");

  if (args.htmlPath) {
    console.warn(
      "ignoring --html after report normalization; rendering HTML from JSON",
    );
  }
  const result = spawnSync(
    "python3",
    [rendererPath, publicJsonPath, "--output", publicHtmlPath],
    { stdio: "inherit" },
  );
  if (result.status !== 0) {
    throw new Error(`renderer exited with status ${result.status}`);
  }

  console.log(`archived ${reportName}`);
  console.log(sourceJsonPath);
  console.log(publicJsonPath);
  console.log(publicHtmlPath);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
