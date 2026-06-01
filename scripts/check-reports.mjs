import { constants as fsConstants } from "node:fs";
import { access, readdir, readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const sourceReportDir = path.join(repoRoot, "src", "data", "reports");
const publicReportDir = path.join(repoRoot, "public", "reports");
const jsonExtension = ".json";
const htmlExtension = ".html";
const requiredArrayFields = [
  "approved",
  "commented",
  "skipped_groups",
  "follow_up",
];

async function exists(filePath) {
  try {
    await access(filePath, fsConstants.F_OK);
    return true;
  } catch {
    return false;
  }
}

function requireString(data, field, problems, reportName) {
  if (typeof data[field] !== "string" || data[field].trim() === "") {
    problems.push(`${reportName}: missing non-empty string field "${field}"`);
  }
}

function requireArray(data, field, problems, reportName) {
  if (!Array.isArray(data[field])) {
    problems.push(`${reportName}: missing array field "${field}"`);
  }
}

function inlineCommentHasText(comment) {
  if (typeof comment === "string") {
    return comment.trim() !== "";
  }
  if (!comment || typeof comment !== "object" || Array.isArray(comment)) {
    return false;
  }
  return [comment.body, comment.summary].some(
    (value) => typeof value === "string" && value.trim() !== "",
  );
}

function validateInlineComments(parsed, problems, reportName) {
  const entries = [
    ...asArray(parsed.approved),
    ...asArray(parsed.commented),
    ...asArray(parsed.maintained),
    ...asArray(parsed.blocked),
  ];

  for (const entry of entries) {
    const comments = entry?.inline_comments;
    if (comments === undefined) {
      continue;
    }
    if (!Array.isArray(comments)) {
      problems.push(
        `${reportName}: PR #${entry?.number || "unknown"} inline_comments must be an array`,
      );
      continue;
    }
    comments.forEach((comment, index) => {
      if (!inlineCommentHasText(comment)) {
        problems.push(
          `${reportName}: PR #${entry?.number || "unknown"} inline_comments[${index}] has no body or summary`,
        );
      }
    });
  }
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

async function validateReport(fileName, problems) {
  const sourceJsonPath = path.join(sourceReportDir, fileName);
  const publicJsonPath = path.join(publicReportDir, fileName);
  const publicHtmlPath = path.join(
    publicReportDir,
    fileName.replace(/\.json$/u, htmlExtension),
  );

  let parsed;
  try {
    const raw = await readFile(sourceJsonPath, "utf8");
    parsed = JSON.parse(raw);
  } catch (error) {
    problems.push(`${fileName}: invalid JSON (${error.message})`);
    return;
  }

  requireString(parsed, "title", problems, fileName);
  requireString(parsed, "repo", problems, fileName);
  requireString(parsed, "generated_at", problems, fileName);
  requireString(parsed, "overview", problems, fileName);
  requireArray(parsed, "timeline", problems, fileName);
  for (const field of requiredArrayFields) {
    requireArray(parsed, field, problems, fileName);
  }
  validateInlineComments(parsed, problems, fileName);

  if (!(await exists(publicJsonPath))) {
    problems.push(`${fileName}: missing public JSON copy`);
  }

  if (!(await exists(publicHtmlPath))) {
    problems.push(`${fileName}: missing public HTML report`);
    return;
  }

  const html = await readFile(publicHtmlPath, "utf8");
  if (!html.includes("<html") || !html.includes("MyCR")) {
    problems.push(`${fileName}: public HTML does not look like a MyCR report`);
  }
}

async function main() {
  const entries = await readdir(sourceReportDir);
  const reportFiles = entries
    .filter((entry) => entry.endsWith(jsonExtension))
    .sort();
  const problems = [];

  if (reportFiles.length === 0) {
    problems.push("no report JSON files found");
  }

  for (const fileName of reportFiles) {
    await validateReport(fileName, problems);
  }

  if (problems.length > 0) {
    for (const problem of problems) {
      console.error(problem);
    }
    process.exit(1);
  }

  console.log(`validated ${reportFiles.length} MyCR report(s)`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
