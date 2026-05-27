#!/usr/bin/env python3
"""Render a self-contained interactive HTML report for mycr runs."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
from pathlib import Path
from typing import Any


DEFAULT_REPORT_DIR = Path("public") / "reports"
STATUS_APPROVED = "approved"
STATUS_COMMENTED = "commented"
STATUS_MAINTAINED = "maintained"
STATUS_MERGED = "merged"
STATUS_SKIPPED = "skipped"
STATUS_BLOCKED = "blocked"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render an interactive HTML report for a mycr run.",
    )
    parser.add_argument(
        "summary_json",
        type=Path,
        help="Path to a UTF-8 JSON summary produced by the mycr workflow.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="HTML output path. Defaults to <cwd>/public/reports/.",
    )
    return parser.parse_args()


def read_summary(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError("summary_json must contain a JSON object")
    return data


def default_output_path() -> Path:
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    return Path.cwd() / DEFAULT_REPORT_DIR / f"mycr-{timestamp}.html"


def dump_json_for_script(data: dict[str, Any]) -> str:
    payload = json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return payload.replace("</", "<\\/")


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_html(data: dict[str, Any]) -> str:
    title = data.get("title") or "MyCR Review Report"
    generated_at = data.get("generated_at") or dt.datetime.now().isoformat()
    payload = dump_json_for_script(data)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<style>
:root {{
  color-scheme: light;
  --bg: #f7f8fb;
  --panel: #ffffff;
  --ink: #19202a;
  --muted: #667085;
  --line: #d8dee8;
  --accent: #116466;
  --accent-2: #d17a22;
  --ok: #188038;
  --warn: #b45309;
  --bad: #b42318;
  --info: #1d4ed8;
  --shadow: 0 12px 32px rgba(15, 23, 42, 0.08);
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background:
    linear-gradient(180deg, rgba(17, 100, 102, 0.08), transparent 340px),
    var(--bg);
  color: var(--ink);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
    "Segoe UI", sans-serif;
  line-height: 1.5;
}}
a {{ color: var(--accent); text-decoration-thickness: 1px; }}
.shell {{ max-width: 1180px; margin: 0 auto; padding: 28px 18px 56px; }}
.topbar {{
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 20px;
}}
h1 {{ margin: 0 0 8px; font-size: clamp(28px, 4vw, 46px); line-height: 1.08; }}
.subtitle {{ color: var(--muted); max-width: 760px; margin: 0; }}
.toggle {{
  display: inline-flex;
  border: 1px solid var(--line);
  background: var(--panel);
  border-radius: 999px;
  padding: 3px;
  box-shadow: var(--shadow);
  flex: none;
}}
.toggle button {{
  border: 0;
  background: transparent;
  color: var(--muted);
  border-radius: 999px;
  padding: 8px 13px;
  cursor: pointer;
  font-weight: 700;
}}
.toggle button.active {{ background: var(--accent); color: white; }}
.metrics {{
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
  margin: 18px 0;
}}
.metric {{
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 16px;
  box-shadow: var(--shadow);
}}
.metric .value {{ font-size: 32px; line-height: 1; font-weight: 800; }}
.metric .label {{ color: var(--muted); margin-top: 7px; font-size: 13px; }}
.dashboard {{
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 16px;
  align-items: stretch;
}}
.panel {{
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  box-shadow: var(--shadow);
  padding: 16px;
}}
.panel h2 {{ margin: 0 0 12px; font-size: 18px; }}
.bars {{ display: grid; gap: 12px; }}
.bar-row {{
  display: grid;
  grid-template-columns: 122px 1fr 36px;
  gap: 10px;
  align-items: center;
}}
.bar-label {{ color: var(--muted); font-size: 13px; }}
.bar-track {{
  height: 12px;
  background: #eef2f7;
  border-radius: 999px;
  overflow: hidden;
}}
.bar-fill {{ height: 100%; border-radius: 999px; background: var(--accent); }}
.bar-fill.approved, .bar-fill.merged {{ background: var(--ok); }}
.bar-fill.commented {{ background: var(--accent-2); }}
.bar-fill.maintained {{ background: var(--accent); }}
.bar-fill.skipped {{ background: var(--info); }}
.bar-fill.blocked {{ background: var(--bad); }}
.timeline {{ display: grid; gap: 10px; }}
.timeline-item {{
  display: grid;
  grid-template-columns: 96px 1fr;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid #edf0f5;
}}
.timeline-item:last-child {{ border-bottom: 0; }}
.time {{ color: var(--muted); font-size: 13px; }}
.controls {{
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  margin: 18px 0 12px;
}}
.search {{
  flex: 1 1 280px;
  min-width: 0;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 10px 12px;
  font: inherit;
  background: white;
}}
.chips {{ display: flex; flex-wrap: wrap; gap: 8px; }}
.chip {{
  border: 1px solid var(--line);
  background: white;
  color: var(--ink);
  border-radius: 999px;
  padding: 8px 11px;
  cursor: pointer;
  font-weight: 700;
}}
.chip.active {{ background: var(--ink); color: white; border-color: var(--ink); }}
.cards {{ display: grid; gap: 12px; }}
.section-heading {{
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 14px;
  margin: 22px 0 12px;
}}
.section-heading h2 {{ margin: 0; font-size: 20px; }}
.section-heading .hint {{ color: var(--muted); font-size: 13px; }}
.card {{
  min-width: 0;
  background: var(--panel);
  border: 1px solid var(--line);
  border-left: 5px solid var(--accent);
  border-radius: 8px;
  box-shadow: var(--shadow);
  overflow: hidden;
}}
.card[data-status="approved"],
.card[data-status="merged"] {{ border-left-color: var(--ok); }}
.card[data-status="commented"] {{ border-left-color: var(--accent-2); }}
.card[data-status="maintained"] {{ border-left-color: var(--accent); }}
.card[data-status="skipped"] {{ border-left-color: var(--info); }}
.card[data-status="blocked"] {{ border-left-color: var(--bad); }}
.card-head {{
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 16px;
  padding: 16px;
  cursor: pointer;
}}
.card-title {{ margin: 0; font-size: 17px; overflow-wrap: anywhere; }}
.card-title a {{ overflow-wrap: anywhere; }}
.meta {{
  color: var(--muted);
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
  font-size: 13px;
  margin-top: 5px;
  min-width: 0;
}}
.card-summary {{
  color: #42526a;
  display: -webkit-box;
  font-size: 13px;
  line-height: 1.5;
  margin-top: 8px;
  overflow: hidden;
  overflow-wrap: anywhere;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}}
.card-actions {{
  align-items: flex-end;
  display: flex;
  flex-direction: column;
  gap: 8px;
}}
.card-toggle {{
  border: 1px solid #d8e1ec;
  background: #fff;
  border-radius: 999px;
  color: var(--muted);
  cursor: pointer;
  font: inherit;
  font-size: 12px;
  font-weight: 800;
  padding: 6px 10px;
  white-space: nowrap;
}}
.card-toggle:hover {{ border-color: #9aa8bb; color: var(--ink); }}
.badge {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 88px;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  background: #eef2f7;
}}
.badge.approved, .badge.merged {{ color: var(--ok); background: #e7f5ec; }}
.badge.commented {{ color: var(--warn); background: #fff4e5; }}
.badge.maintained {{ color: var(--accent); background: #e6fffb; }}
.badge.skipped {{ color: var(--info); background: #eaf1ff; }}
.badge.blocked {{ color: var(--bad); background: #fff0ee; }}
.read-pill {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid transparent;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 12px;
  font-weight: 900;
  white-space: nowrap;
}}
.read-pill.critical {{
  color: #9f1239;
  background: #fff1f2;
  border-color: #fecdd3;
}}
.read-pill.focus {{
  color: #92400e;
  background: #fffbeb;
  border-color: #fde68a;
}}
.read-pill.skim {{
  color: #166534;
  background: #ecfdf3;
  border-color: #bbf7d0;
}}
.read-pill.follow {{
  color: #1d4ed8;
  background: #eff6ff;
  border-color: #bfdbfe;
}}
.headline-row {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}}
.advice-reason {{
  color: var(--muted);
  font-size: 12px;
  font-style: italic;
}}
.reading-guide {{
  margin-top: 16px;
}}
.guide-head {{
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 12px;
}}
.guide-head h2 {{ margin: 0; }}
.guide-head span {{
  color: var(--muted);
  font-size: 13px;
}}
.guide-grid {{
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}}
.guide-card {{
  display: grid;
  gap: 8px;
  min-width: 0;
  border: 1px solid #e5edf5;
  border-left: 4px solid var(--accent);
  border-radius: 8px;
  padding: 12px;
  background: linear-gradient(180deg, #fff, #fbfcfe);
}}
.guide-card.critical {{ border-left-color: #e11d48; }}
.guide-card.focus {{ border-left-color: #d97706; }}
.guide-card.skim {{ border-left-color: #16a34a; }}
.guide-card.follow {{ border-left-color: #2563eb; }}
.guide-card a {{
  color: var(--ink);
  font-weight: 900;
  text-decoration: none;
}}
.guide-card a:hover {{ color: var(--accent); }}
.guide-meta {{
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}}
.guide-reason {{
  color: var(--muted);
  font-size: 12px;
  line-height: 1.45;
}}
.card-body {{
  display: none;
  border-top: 1px solid #edf0f5;
  padding: 0 16px 16px;
}}
.card.open .card-body {{ display: block; }}
.grid {{
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-top: 14px;
}}
.field {{
  border: 1px solid #edf0f5;
  background: #fbfcfe;
  border-radius: 8px;
  padding: 12px;
}}
.field strong {{
  display: block;
  color: var(--muted);
  font-size: 12px;
  margin-bottom: 5px;
}}
.field-body {{
  overflow-wrap: anywhere;
  white-space: pre-wrap;
}}
.overview-content {{
  overflow-wrap: anywhere;
  white-space: pre-wrap;
  color: var(--ink);
}}
.comment {{
  border-left: 3px solid var(--accent-2);
  padding: 10px 12px;
  background: #fffaf2;
  border-radius: 6px;
  margin-top: 10px;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
}}
.pr-readout {{
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 18px;
  align-items: start;
  padding-top: 18px;
}}
.pr-story {{
  display: grid;
  gap: 16px;
  min-width: 0;
}}
.story-block {{
  border-top: 1px solid #e7edf4;
  padding-top: 14px;
}}
.story-block:first-child {{
  border-top: 0;
  padding-top: 0;
}}
.story-block.hero-block {{
  border: 1px solid #dce9e7;
  border-left: 4px solid var(--accent);
  border-radius: 8px;
  padding: 15px 16px;
  background: linear-gradient(180deg, #fbfffe, #f8fbfd);
}}
.story-block h4,
.review-rail h4,
.comments-panel h4 {{
  margin: 0 0 9px;
  color: #17202a;
  font-size: 14px;
  letter-spacing: 0;
}}
.story-line {{
  display: grid;
  grid-template-columns: 108px minmax(0, 1fr);
  gap: 12px;
  margin: 0;
  padding: 9px 0;
  border-top: 1px solid #edf2f7;
  color: #1f2937;
  line-height: 1.68;
}}
.story-line:first-of-type {{
  border-top: 0;
  padding-top: 0;
}}
.story-label {{
  color: #536175;
  font-size: 12px;
  font-weight: 850;
}}
.story-text {{
  min-width: 0;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
}}
.review-rail {{
  position: static;
  display: grid;
  gap: 14px;
  align-self: start;
}}
.reading-callout {{
  display: grid;
  gap: 6px;
  border: 1px solid #e5edf5;
  border-left: 4px solid var(--accent);
  border-radius: 8px;
  padding: 12px;
  background: #fff;
}}
.reading-callout.critical {{
  border-left-color: #e11d48;
  background: linear-gradient(180deg, #fff7f8, #fff);
}}
.reading-callout.focus {{
  border-left-color: #d97706;
  background: linear-gradient(180deg, #fffbeb, #fff);
}}
.reading-callout.skim {{
  border-left-color: #16a34a;
  background: linear-gradient(180deg, #f0fdf4, #fff);
}}
.reading-callout.follow {{
  border-left-color: #2563eb;
  background: linear-gradient(180deg, #eff6ff, #fff);
}}
.reading-callout strong {{
  font-size: 13px;
}}
.reading-callout span {{
  color: var(--muted);
  font-size: 12px;
  font-style: italic;
  line-height: 1.5;
}}
.story-text mark,
.fact dd mark,
.field-body mark,
.card-summary mark,
.overview-content mark,
.comment mark,
.skip-detail mark {{
  border-radius: 5px;
  padding: 0 4px;
  font-weight: 850;
}}
.mark-good {{
  color: #166534;
  background: #dcfce7;
}}
.mark-warn {{
  color: #92400e;
  background: #fef3c7;
}}
.mark-bad {{
  color: #9f1239;
  background: #ffe4e6;
}}
.mark-info {{
  color: #1d4ed8;
  background: #dbeafe;
}}
.fact-list {{
  display: grid;
  gap: 10px;
  margin: 0;
  padding: 0;
}}
.fact {{
  border-top: 1px solid #e7edf4;
  padding-top: 10px;
}}
.fact:first-child {{
  border-top: 0;
  padding-top: 0;
}}
.fact dt {{
  margin: 0 0 4px;
  color: #536175;
  font-size: 11px;
  font-weight: 850;
  letter-spacing: 0;
  text-transform: uppercase;
}}
.fact dd {{
  margin: 0;
  color: #1f2937;
  line-height: 1.55;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
}}
.comments-panel {{
  border-top: 1px solid #e7edf4;
  padding-top: 14px;
}}
.comment-list {{
  display: grid;
  gap: 10px;
}}
.skip-groups {{ display: grid; gap: 14px; margin-top: 12px; }}
.skip-group {{
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  box-shadow: var(--shadow);
  overflow: hidden;
}}
.skip-group-head {{
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 14px;
  padding: 15px 16px;
  cursor: pointer;
  background: #fbfcfe;
}}
.skip-group-title {{ margin: 0; font-size: 16px; }}
.skip-group-count {{
  color: var(--info);
  background: #eaf1ff;
  border-radius: 999px;
  padding: 5px 10px;
  font-weight: 800;
  font-size: 12px;
}}
.skip-group-body {{ display: none; border-top: 1px solid #edf0f5; }}
.skip-group.open .skip-group-body {{ display: block; }}
.skip-row {{
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(170px, 0.7fr);
  gap: 12px;
  padding: 13px 16px;
  border-bottom: 1px solid #edf0f5;
}}
.skip-row:last-child {{ border-bottom: 0; }}
.skip-title {{ font-weight: 750; }}
.skip-detail {{ color: var(--muted); font-size: 13px; margin-top: 4px; }}
.blocker-list {{
  display: grid;
  gap: 8px;
  margin: 8px 0 0;
  padding: 0;
  list-style: none;
}}
.blocker-item {{
  border: 1px solid #e5edf5;
  border-left: 3px solid var(--warn);
  border-radius: 8px;
  padding: 9px 10px;
  background: #fff;
}}
.blocker-item a {{
  color: var(--accent);
  font-weight: 800;
}}
.blocker-meta {{
  color: var(--muted);
  font-size: 12px;
  line-height: 1.45;
  margin-top: 4px;
}}
.empty {{
  border: 1px dashed var(--line);
  border-radius: 8px;
  padding: 22px;
  color: var(--muted);
  text-align: center;
  background: rgba(255, 255, 255, 0.68);
}}
.footer {{
  color: var(--muted);
  font-size: 12px;
  margin-top: 22px;
}}
:root {{
  --bg: #f4f6f8;
  --panel: #ffffff;
  --ink: #111827;
  --muted: #657386;
  --line: #dce3ec;
  --accent: #0f766e;
  --accent-2: #b45309;
  --ok: #167a3a;
  --warn: #a16207;
  --bad: #b42318;
  --info: #2563eb;
  --soft: #f8fafc;
  --shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
  --shadow-lg: 0 18px 48px rgba(15, 23, 42, 0.10);
}}
body {{
  background:
    linear-gradient(180deg, rgba(15, 118, 110, 0.10), rgba(244, 246, 248, 0) 300px),
    var(--bg);
  font-size: 14px;
}}
a:hover {{ color: #0a5d57; }}
.shell {{ max-width: 1280px; padding: 24px 20px 64px; }}
.topbar {{
  align-items: center;
  background:
    linear-gradient(135deg, rgba(15, 118, 110, 0.06), rgba(37, 99, 235, 0.04)),
    var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 22px 24px;
  box-shadow: var(--shadow-lg);
}}
h1 {{
  font-size: clamp(30px, 4vw, 48px);
  letter-spacing: 0;
}}
.subtitle {{ max-width: 860px; font-size: 14px; }}
.toggle {{ box-shadow: none; }}
.toggle button {{ padding: 7px 12px; }}
.metrics {{
  grid-template-columns: repeat(5, minmax(140px, 1fr));
  gap: 10px;
  margin: 16px 0;
}}
.metric {{
  position: relative;
  overflow: hidden;
  padding: 14px 16px;
  box-shadow: var(--shadow);
}}
.metric::before {{
  content: "";
  position: absolute;
  inset: 0 auto 0 0;
  width: 4px;
  background: var(--accent);
}}
.metric .value {{ font-size: 30px; }}
.metric .label {{
  margin-top: 6px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
}}
.dashboard {{
  grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
}}
.panel {{
  box-shadow: var(--shadow);
  padding: 18px;
}}
.panel h2 {{
  font-size: 15px;
  letter-spacing: 0;
}}
.bar-row {{
  grid-template-columns: 112px 1fr 32px;
  padding: 4px 0;
}}
.bar-label {{ font-weight: 700; }}
.bar-track {{ height: 9px; background: #edf2f7; }}
.timeline-item {{
  grid-template-columns: 74px 1fr;
  padding: 9px 0;
}}
.time {{
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 12px;
}}
.overview-content {{
  background: var(--soft);
  border: 1px solid #e7edf4;
  border-radius: 8px;
  padding: 14px;
}}
.controls {{
  position: sticky;
  top: 0;
  z-index: 20;
  background: rgba(244, 246, 248, 0.88);
  backdrop-filter: blur(14px);
  border: 1px solid rgba(220, 227, 236, 0.86);
  border-radius: 8px;
  padding: 10px;
  margin: 18px 0 14px;
  box-shadow: var(--shadow);
}}
.search {{
  min-height: 40px;
  border-color: #cfd8e3;
  box-shadow: inset 0 1px 0 rgba(15, 23, 42, 0.02);
}}
.search:focus {{
  outline: 2px solid rgba(15, 118, 110, 0.22);
  border-color: var(--accent);
}}
.chips {{ align-items: center; }}
.chip, .utility-button {{
  min-height: 34px;
  border: 1px solid #cfd8e3;
  background: #fff;
  border-radius: 999px;
  color: var(--ink);
  cursor: pointer;
  font: inherit;
  font-weight: 750;
  padding: 7px 11px;
}}
.chip:hover, .utility-button:hover {{ border-color: #9aa8bb; }}
.chip.active {{
  background: #15202b;
  border-color: #15202b;
  color: #fff;
}}
.utilities {{
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-left: auto;
}}
.utility-button {{
  color: var(--muted);
  font-size: 12px;
}}
.section-heading {{
  margin: 24px 0 12px;
  padding-top: 2px;
}}
.section-heading h2 {{ font-size: 18px; }}
.cards {{ gap: 14px; }}
.card {{
  border-left: 0;
  box-shadow: var(--shadow);
  transition: box-shadow 160ms ease, transform 160ms ease, border-color 160ms ease;
}}
.card:hover {{
  border-color: #c8d2df;
  box-shadow: var(--shadow-lg);
}}
.card-head {{
  align-items: center;
  background: linear-gradient(180deg, #fff, #fbfcfe);
  border-left: 4px solid var(--accent);
}}
.card[data-status="approved"] .card-head,
.card[data-status="merged"] .card-head {{ border-left-color: var(--ok); }}
.card[data-status="commented"] .card-head {{ border-left-color: var(--accent-2); }}
.card[data-status="maintained"] .card-head {{ border-left-color: var(--accent); }}
.card[data-status="skipped"] .card-head {{ border-left-color: var(--info); }}
.card[data-status="blocked"] .card-head {{ border-left-color: var(--bad); }}
.card.priority-critical .card-head {{
  background: linear-gradient(180deg, #fff7f8, #fff);
}}
.card.priority-focus .card-head {{
  background: linear-gradient(180deg, #fffbeb, #fff);
}}
.card.priority-follow .card-head {{
  background: linear-gradient(180deg, #eff6ff, #fff);
}}
.card-title {{
  font-size: 16px;
  line-height: 1.42;
}}
.meta {{
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 7px;
}}
.badge {{
  gap: 7px;
  min-width: 0;
  padding: 6px 11px;
  text-transform: none;
  white-space: nowrap;
}}
.card-summary {{
  color: #526173;
  margin-top: 9px;
}}
.badge::before {{
  content: "";
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}}
.card-body {{
  background: #fff;
  padding: 0 18px 18px;
}}
.grid {{
  grid-template-columns: 1fr;
  gap: 10px;
}}
.field {{
  background: #fbfcfe;
  border-color: #e6ecf3;
  padding: 13px 14px;
}}
.field strong {{
  color: #536175;
  font-size: 11px;
  letter-spacing: 0;
  text-transform: uppercase;
}}
.field-body {{
  color: #1f2937;
  line-height: 1.62;
}}
.comment {{
  background: #fff8ed;
  border-left-color: var(--accent-2);
  color: #1f2937;
}}
.pr-readout {{
  grid-template-columns: minmax(0, 1fr);
  gap: 18px;
}}
.story-block {{
  border-top-color: #e2e8f0;
}}
.story-block.hero-block {{
  background: linear-gradient(180deg, #fbfffe, #f7fbfa);
  border-color: #d5e7e4;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.72);
}}
.story-block h4,
.review-rail h4,
.comments-panel h4 {{
  font-size: 13px;
  font-weight: 900;
}}
.story-line {{
  grid-template-columns: 116px minmax(0, 1fr);
  border-top-color: #e9eef5;
}}
.story-label {{
  color: #607086;
}}
.review-rail {{
  border: 1px solid #e3eaf2;
  border-radius: 8px;
  padding: 14px;
  background: #fbfcfe;
}}
.review-rail .fact-list {{
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}}
.fact {{
  border-top-color: #e8eef5;
}}
.comments-panel {{
  border-top-color: #e2e8f0;
}}
.comment-list {{
  gap: 12px;
}}
.skip-group {{
  box-shadow: var(--shadow);
}}
.skip-group-head {{
  align-items: center;
  background: linear-gradient(180deg, #fff, #fbfcfe);
}}
.skip-row {{
  grid-template-columns: minmax(0, 1.15fr) minmax(220px, 0.85fr);
}}
.blocker-item {{
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.75);
}}
.empty {{
  background: #fff;
  box-shadow: var(--shadow);
}}
@media (max-width: 840px) {{
  .topbar, .card-head {{ grid-template-columns: 1fr; display: grid; }}
  .card-actions {{ align-items: flex-start; flex-direction: row; flex-wrap: wrap; }}
  .dashboard, .grid, .metrics {{ grid-template-columns: 1fr; }}
  .guide-grid {{ grid-template-columns: 1fr; }}
  .headline-row {{ align-items: flex-start; flex-direction: column; }}
  .pr-readout {{ grid-template-columns: 1fr; }}
  .review-rail {{ position: static; }}
  .story-line {{ grid-template-columns: 1fr; gap: 4px; }}
  .timeline-item {{ grid-template-columns: 1fr; }}
  .controls {{ position: static; }}
  .utilities {{ width: 100%; margin-left: 0; }}
  .utility-button {{ flex: 1 1 auto; }}
  .skip-row {{ grid-template-columns: 1fr; }}
}}
</style>
</head>
<body>
<div class="shell">
  <div class="topbar">
    <div>
      <h1 data-i18n="title">MyCR 审核报告</h1>
      <p class="subtitle" id="subtitle"></p>
    </div>
    <div class="toggle" aria-label="Language">
      <button type="button" data-lang-button="zh" class="active">中文</button>
      <button type="button" data-lang-button="en">EN</button>
    </div>
  </div>
  <section class="metrics" id="metrics"></section>
  <section class="dashboard">
    <div class="panel">
      <h2 data-i18n="statusDistribution">状态分布</h2>
      <div class="bars" id="bars"></div>
    </div>
    <div class="panel">
      <h2 data-i18n="timeline">执行时间线</h2>
      <div class="timeline" id="timeline"></div>
    </div>
  </section>
  <section class="panel" id="overviewPanel" style="display: none; margin-top: 16px;">
    <h2 data-i18n="overviewSection">整体摘要</h2>
    <div class="overview-content" id="overviewContent"></div>
  </section>
  <section class="panel reading-guide" id="readingGuidePanel" style="display: none;">
    <div class="guide-head">
      <h2 data-i18n="readingGuide">阅读建议</h2>
      <span data-i18n="readingGuideHint">先看高风险和高影响 PR</span>
    </div>
    <div class="guide-grid" id="readingGuide"></div>
  </section>
  <section class="controls">
    <input class="search" id="search" type="search">
    <div class="chips" id="chips"></div>
    <div class="utilities">
      <button type="button" class="utility-button" id="openAll"></button>
      <button type="button" class="utility-button" id="closeAll"></button>
    </div>
  </section>
  <section class="section-heading">
    <h2 data-i18n="reviewedSection">已处理 PR</h2>
    <div class="hint" data-i18n="reviewedHint">点击卡片查看细节</div>
  </section>
  <main class="cards" id="cards"></main>
  <section class="section-heading" id="skippedHeading">
    <h2 data-i18n="skippedGroups">未审核 PR 分类</h2>
    <div class="hint" data-i18n="skippedHint">按排除原因分组</div>
  </section>
  <section class="skip-groups" id="skipGroups"></section>
  <section class="section-heading" id="followUpHeading">
    <h2 data-i18n="followUpSection">后续关注</h2>
    <div class="hint" data-i18n="followUpHint">接近可处理但仍有阻塞</div>
  </section>
  <section class="cards" id="followUpCards"></section>
  <div class="footer" id="footer"></div>
</div>
<script>
const reportData = {payload};
const labels = {{
  zh: {{
    title: "MyCR 审核报告",
    subtitle: "仓库 {{repo}}，生成时间 {{time}}。默认展示中文，可切换英文。",
    statusDistribution: "状态分布",
    timeline: "执行时间线",
    all: "全部",
    approved: "已批准",
    commented: "已评论",
    maintained: "已维护",
    merged: "已合并",
    skipped: "未审核",
    blocked: "阻塞",
    total: "总 PR",
    reviewed: "已审核",
    comments: "评论",
    followups: "需关注",
    search: "搜索 PR、作者、标题、原因",
    author: "作者",
    technicalBackground: "技术背景",
    problem: "解决的问题",
    problemFraming: "问题本质与视角",
    rootCause: "根因判断",
    approach: "实现方式",
    alternativeDesigns: "可选设计方案",
    tradeoffs: "设计取舍",
    designAssessment: "设计评估",
    outcome: "审核结果",
    risk: "剩余风险",
    ci: "CI / 线程状态",
    backgroundAndProblem: "背景与问题",
    solutionAndTradeoffs: "方案与取舍",
    impactAndEvidence: "影响与证据",
    reviewSummary: "审查结论",
    overviewSection: "整体摘要",
    readingGuide: "阅读建议",
    readingGuideHint: "先看高风险和高影响 PR",
    readingAdvice: "阅读建议",
    modules: "涉及模块",
    apiSurface: "导出 API 变化",
    changeInventory: "具体变更清单",
    semanticChanges: "语义变化",
    moduleImpact: "模块影响",
    crossModuleImpact: "模块交叉影响",
    behaviorImpact: "行为与兼容性影响",
    testsDocs: "测试与文档",
    attentionPoints: "需要注意",
    directFixes: "直接修复",
    selfReviewPolicy: "自审策略",
    reason: "跳过原因",
    reviewedSection: "已处理 PR",
    reviewedHint: "点击卡片查看细节",
    skippedGroups: "未审核 PR 分类",
    skippedHint: "按排除原因分组",
    followUpSection: "后续关注",
    followUpHint: "接近可处理但仍有阻塞",
    items: "项",
    blocker: "阻塞点",
    blockerDetails: "具体阻塞点",
    readinessAudit: "就绪性审计",
    blockerKinds: {{
      ci: "CI",
      human_review: "人类评审",
      bot_review: "机器人评审",
      merge_conflict: "合并冲突",
      draft_wip: "Draft/WIP",
      own_pr: "自己发起",
      soft_ci: "软门禁",
      not_reached: "本轮未处理",
      other: "其他"
    }},
    inlineComments: "内联评论",
    focus: "审核重点",
    severity: "严重级别",
    expandAll: "展开全部",
    collapseAll: "收起全部",
    expandDetails: "展开详情",
    collapseDetails: "收起详情",
    summaryFallback: "展开查看完整审查结论、风险和证据。",
    empty: "当前筛选条件下没有 PR。",
    footer: "报告文件为自包含 HTML，默认保存在 public/reports 并由 /mycr 站点归档。"
  }},
  en: {{
    title: "MyCR Review Report",
    subtitle: "Repository {{repo}}, generated at {{time}}. Chinese is the default view; English is available here.",
    statusDistribution: "Status Distribution",
    timeline: "Run Timeline",
    all: "All",
    approved: "Approved",
    commented: "Commented",
    maintained: "Maintained",
    merged: "Merged",
    skipped: "Not Reviewed",
    blocked: "Blocked",
    total: "Total PRs",
    reviewed: "Reviewed",
    comments: "Comments",
    followups: "Follow-ups",
    search: "Search PR, author, title, or reason",
    author: "Author",
    technicalBackground: "Technical Background",
    problem: "Problem",
    problemFraming: "Problem Framing",
    rootCause: "Root Cause",
    approach: "Implementation",
    alternativeDesigns: "Alternative Designs",
    tradeoffs: "Tradeoffs",
    designAssessment: "Design Assessment",
    outcome: "Outcome",
    risk: "Remaining Risk",
    ci: "CI / Thread State",
    backgroundAndProblem: "Background and Problem",
    solutionAndTradeoffs: "Solution and Tradeoffs",
    impactAndEvidence: "Impact and Evidence",
    reviewSummary: "Review Summary",
    overviewSection: "Overview",
    readingGuide: "Reading Guide",
    readingGuideHint: "Start with high-risk or high-impact PRs",
    readingAdvice: "Reading Advice",
    modules: "Touched Modules",
    apiSurface: "Exported API Changes",
    changeInventory: "Concrete Change Inventory",
    semanticChanges: "Semantic Changes",
    moduleImpact: "Module Impact",
    crossModuleImpact: "Cross-module Impact",
    behaviorImpact: "Behavior and Compatibility Impact",
    testsDocs: "Tests and Docs",
    attentionPoints: "Attention Points",
    directFixes: "Direct Fixes",
    selfReviewPolicy: "Self-review Policy",
    reason: "Skip Reason",
    reviewedSection: "Processed PRs",
    reviewedHint: "Click a card for details",
    skippedGroups: "Not Reviewed by Reason",
    skippedHint: "Grouped by exclusion reason",
    followUpSection: "Follow-up Attention",
    followUpHint: "Close to ready but still blocked",
    items: "items",
    blocker: "Blocker",
    blockerDetails: "Concrete Blockers",
    readinessAudit: "Readiness Audit",
    blockerKinds: {{
      ci: "CI",
      human_review: "Human Review",
      bot_review: "Bot Review",
      merge_conflict: "Merge Conflict",
      draft_wip: "Draft/WIP",
      own_pr: "Own PR",
      soft_ci: "Soft CI",
      not_reached: "Not Reached",
      other: "Other"
    }},
    inlineComments: "Inline Comments",
    focus: "Review Focus",
    severity: "Severity",
    expandAll: "Expand all",
    collapseAll: "Collapse all",
    expandDetails: "Expand details",
    collapseDetails: "Collapse details",
    summaryFallback: "Expand for the full review outcome, risk, and evidence.",
    empty: "No PRs match the current filters.",
    footer: "This self-contained HTML report is saved under public/reports by default and archived by the /mycr site."
  }}
}};

let lang = "zh";
let filter = "all";
const statusOrder = ["approved", "commented", "maintained", "merged", "skipped", "blocked"];

function text(value, fallback = "") {{
  if (value === undefined || value === null || value === "") return fallback;
  if (typeof value === "object" && !Array.isArray(value)) {{
    return value[lang] || value.zh || value.en || fallback;
  }}
  return String(value);
}}

function escapeHtml(value) {{
  return text(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}}

function formatRich(value) {{
  let html = escapeHtml(value);
  const replacements = [
    [
      /(P[0-2]|codecov\\/patch=FAILURE|go-apidiff=FAILURE|go-apidiff|FAILURE|失败|阻塞|不能合入|不能 merge|未合并|破坏性|breaking|unbounded|无界|绕过|丢失|重复|不稳定|风险)/gi,
      "mark-bad"
    ],
    [
      /(LGTM|已合并|已批准|squash merge|merged|approved|CI 全绿|全绿|修复有效|\\bresolved\\b|\\bresolve\\b)/gi,
      "mark-good"
    ],
    [
      /(pending|soft[- ]?CI|软门禁|follow-up|后续|关注|CodeRabbit|reviewability ledger|not_reached)/gi,
      "mark-info"
    ],
    [
      /(导出 API|\\bAPI\\b|兼容性|\\bsession\\b|\\brunner\\b|\\bmemory\\b|GraphRAG|workspace_exec|OpenAPI|\\bpolicy\\b|security|安全)/gi,
      "mark-warn"
    ]
  ];
  for (const [pattern, className] of replacements) {{
    html = html.replace(pattern, `<mark class="${{className}}">$1</mark>`);
  }}
  return html;
}}

function prs() {{
  const groups = reportData.skipped_groups || [];
  const skipped = groups.flatMap(group =>
    (group.items || []).map(item => ({{
      ...item,
      status: item.status || "skipped",
      skip_reason: item.skip_reason || group.reason
    }}))
  );
  return [
    ...(reportData.approved || []),
    ...(reportData.commented || []),
    ...(reportData.maintained || []),
    ...(reportData.blocked || []),
    ...skipped
  ];
}}

function skippedGroups() {{
  return reportData.skipped_groups || [];
}}

function counts(items) {{
  const result = Object.fromEntries(statusOrder.map(status => [status, 0]));
  for (const item of items) {{
    const status = item.status || "skipped";
    result[status] = (result[status] || 0) + 1;
  }}
  return result;
}}

function setLanguage(nextLang) {{
  lang = nextLang;
  document.documentElement.lang = nextLang === "zh" ? "zh-CN" : "en";
  document.querySelectorAll("[data-lang-button]").forEach(button => {{
    button.classList.toggle("active", button.dataset.langButton === nextLang);
  }});
  render();
}}

function renderStatic() {{
  document.querySelectorAll("[data-i18n]").forEach(node => {{
    node.textContent = labels[lang][node.dataset.i18n];
  }});
  const repo = reportData.repo || "trpc-group/trpc-agent-go";
  const generated = reportData.generated_at || "{esc(generated_at)}";
  document.getElementById("subtitle").textContent = labels[lang].subtitle
    .replace("{{repo}}", repo)
    .replace("{{time}}", generated);
  document.getElementById("search").placeholder = labels[lang].search;
  document.getElementById("openAll").textContent = labels[lang].expandAll;
  document.getElementById("closeAll").textContent = labels[lang].collapseAll;
  document.getElementById("footer").textContent = labels[lang].footer;
}}

function renderMetrics(items) {{
  const totalComments = items.reduce((sum, item) =>
    sum + ((item.inline_comments || []).length || item.comment_count || 0), 0);
  const followups = (reportData.follow_up || []).length;
  const reviewed = items.filter(item =>
    ["approved", "commented", "maintained", "merged", "blocked"].includes(item.status)
  ).length;
  const metricRows = [
    [labels[lang].total, items.length],
    [labels[lang].reviewed, reviewed],
    [labels[lang].approved, items.filter(item =>
      ["approved", "merged"].includes(item.status)).length],
    [labels[lang].comments, totalComments],
    [labels[lang].followups, followups]
  ];
  document.getElementById("metrics").innerHTML = metricRows.map(([label, value]) => `
    <div class="metric">
      <div class="value">${{value}}</div>
      <div class="label">${{escapeHtml(label)}}</div>
    </div>
  `).join("");
}}

function renderBars(items) {{
  const byStatus = counts(items);
  const maxCount = Math.max(1, ...Object.values(byStatus));
  document.getElementById("bars").innerHTML = statusOrder.map(status => {{
    const value = byStatus[status] || 0;
    const width = Math.max(3, Math.round((value / maxCount) * 100));
    return `
      <div class="bar-row">
        <div class="bar-label">${{labels[lang][status]}}</div>
        <div class="bar-track"><div class="bar-fill ${{status}}" style="width:${{width}}%"></div></div>
        <strong>${{value}}</strong>
      </div>
    `;
  }}).join("");
}}

function renderTimeline() {{
  const events = reportData.timeline || [];
  const container = document.getElementById("timeline");
  if (!events.length) {{
    container.innerHTML = `<div class="empty">${{labels[lang].empty}}</div>`;
    return;
  }}
  container.innerHTML = events.map(event => `
    <div class="timeline-item">
      <div class="time">${{escapeHtml(event.time || "")}}</div>
      <div>${{escapeHtml(text(event.label || event.text || event))}}</div>
    </div>
  `).join("");
}}

function renderOverview() {{
  const panel = document.getElementById("overviewPanel");
  const content = document.getElementById("overviewContent");
  const overview = reportData.overview || reportData.summary;
  const body = text(overview);
  if (!body) {{
    panel.style.display = "none";
    content.textContent = "";
    return;
  }}
  panel.style.display = "block";
  content.innerHTML = formatRich(body);
}}

function renderChips() {{
  const chipRows = ["all", ...statusOrder];
  document.getElementById("chips").innerHTML = chipRows.map(status => `
    <button type="button" class="chip ${{filter === status ? "active" : ""}}"
      data-filter="${{status}}">${{labels[lang][status]}}</button>
  `).join("");
  document.querySelectorAll("[data-filter]").forEach(button => {{
    button.addEventListener("click", () => {{
      filter = button.dataset.filter;
      renderCards();
      renderSkipGroups();
      renderFollowUp();
      renderChips();
    }});
  }});
}}

function matchesSearch(item, query) {{
  if (!query) return true;
  const haystack = [
    item.number,
    text(item.title),
    item.author,
    text(item.problem),
    text(item.approach),
    text(item.outcome),
    text(item.skip_reason),
    text(item.group_reason),
    text(item.readiness_audit),
    blockersSearchText(item.blockers),
    text(item.risk),
    text(item.ci_state)
  ].join(" ").toLowerCase();
  return haystack.includes(query.toLowerCase());
}}

function blockersSearchText(blockers) {{
  if (!Array.isArray(blockers)) return "";
  return blockers.map(blocker => {{
    if (typeof blocker !== "object" || blocker === null) return text(blocker);
    return [
      blocker.kind,
      blocker.summary,
      blocker.reviewer,
      blocker.path,
      blocker.line,
      blocker.latest_response,
      blocker.verification,
      blocker.url
    ].map(value => text(value)).join(" ");
  }}).join(" ");
}}

function field(label, value) {{
  const body = text(value);
  if (!body) return "";
  return `<div class="field"><strong>${{label}}</strong><div class="field-body">${{formatRich(body)}}</div></div>`;
}}

function renderBlockers(item) {{
  const blockers = Array.isArray(item.blockers) ? item.blockers : [];
  if (!blockers.length) return "";
  const rendered = blockers.map(blocker => {{
    const data = typeof blocker === "object" && blocker !== null
      ? blocker
      : {{ summary: blocker }};
    const location = [data.path, data.line ? `:${{data.line}}` : ""].filter(Boolean).join("");
    const meta = [
      data.kind ? blockerKindLabel(data.kind) : "",
      data.reviewer ? `reviewer: ${{text(data.reviewer)}}` : "",
      location,
      data.latest_response ? `latest: ${{text(data.latest_response)}}` : "",
      data.verification ? text(data.verification) : ""
    ].filter(Boolean).join(" · ");
    const summary = formatRich(data.summary || blocker);
    const link = data.url
      ? ` <a href="${{escapeHtml(data.url)}}">link</a>`
      : "";
    return `<li class="blocker-item"><div>${{summary}}${{link}}</div>${{meta ? `<div class="blocker-meta">${{escapeHtml(meta)}}</div>` : ""}}</li>`;
  }}).join("");
  return `<div class="skip-detail"><strong>${{labels[lang].blockerDetails}}:</strong></div><ul class="blocker-list">${{rendered}}</ul>`;
}}

function blockerKindLabel(kind) {{
  return (labels[lang].blockerKinds || {{}})[kind] || text(kind);
}}

function allPrText(item) {{
  const comments = (item.inline_comments || []).map(comment => [
    comment.severity,
    comment.focus,
    comment.body,
    comment.path
  ].map(value => text(value)).join(" ")).join(" ");
  const blockers = blockersSearchText(item.blockers);
  return [
    item.status,
    item.number,
    item.title,
    item.author,
    item.problem,
    item.approach,
    item.outcome,
    item.risk,
    item.ci_state,
    item.skip_reason,
    item.readiness_audit,
    item.modules,
    item.api_surface,
    comments,
    blockers
  ].map(value => text(value)).join(" ").toLowerCase();
}}

function readingAdvice(item) {{
  const status = item.status || "skipped";
  const comments = item.inline_comments || [];
  const blockers = item.blockers || [];
  const body = allPrText(item);
  const hasP1 = comments.some(comment =>
    /\\bP[01]\\b/i.test(text(comment.severity)) ||
    /\\bP[01]\\b/i.test(text(comment.body))
  );
  const hasCriticalRisk = hasP1 ||
    /(security|安全|bypass|绕过|breaking|破坏性|unbounded|无界|丢失|重复|不稳定|兼容|api|go-apidiff|failure|失败|不能 merge|不能合入|race|并发)/i.test(body);
  const highImpactFeature =
    /(add|new|新增|support|支持|agent|runner|session|memory|graphrag|knowledge|openapi|workspace_exec|policy|extension|tool|graph|api)/i.test(body);

  const copy = {{
    critical: {{
      icon: "🔥",
      zh: "重点精读",
      en: "Deep Read",
      reasonZh: comments.length
        ? `有 ${{comments.length}} 条行级评论，且包含 P1/兼容/正确性/安全类风险。`
        : "包含高风险兼容性或正确性信号，需要重点复核。",
      reasonEn: comments.length
        ? `${{comments.length}} inline comment(s), including P1, compatibility, correctness, or security risk.`
        : "High-risk compatibility or correctness signal; review carefully."
    }},
    focus: {{
      icon: "🔎",
      zh: "建议细看",
      en: "Read Carefully",
      reasonZh: comments.length
        ? `有 ${{comments.length}} 条评论或重要设计取舍，建议看完整结论。`
        : "涉及核心模块、导出 API 或较大功能，建议细看。",
      reasonEn: comments.length
        ? `${{comments.length}} comment(s) or important design tradeoffs; read the full conclusion.`
        : "Core module, exported API, or larger feature; read carefully."
    }},
    skim: {{
      icon: "✅",
      zh: "快速略看",
      en: "Quick Skim",
      reasonZh: "风险低或改动较直接，扫结论和 CI 状态即可。",
      reasonEn: "Low risk or straightforward change; skim outcome and CI state."
    }},
    follow: {{
      icon: "⏳",
      zh: "只看阻塞",
      en: "Blocker Only",
      reasonZh: blockers.length
        ? `主要看 ${{blockers.length}} 个具体阻塞点，暂不需要读完整实现。`
        : "当前不是可合并状态，先看阻塞和后续动作。",
      reasonEn: blockers.length
        ? `Focus on ${{blockers.length}} concrete blocker(s); no need to read the full implementation yet.`
        : "Not merge-ready; focus on blockers and next action."
    }}
  }};

  let level = "skim";
  if (status === "blocked") {{
    level = "follow";
  }} else if (status === "commented") {{
    level = hasCriticalRisk ? "critical" : "focus";
  }} else if (status === "maintained") {{
    level = hasCriticalRisk || highImpactFeature ? "focus" : "skim";
  }} else if (status === "approved") {{
    level = hasCriticalRisk || highImpactFeature ? "focus" : "skim";
  }} else if (status === "merged") {{
    level = highImpactFeature || hasCriticalRisk ? "focus" : "skim";
  }} else if (status === "skipped") {{
    level = blockers.length || /(conflict|ci|failure|失败|未回应|review)/i.test(body)
      ? "follow"
      : "skim";
  }}

  const selected = copy[level];
  return {{
    level,
    icon: selected.icon,
    label: lang === "zh" ? selected.zh : selected.en,
    reason: lang === "zh" ? selected.reasonZh : selected.reasonEn
  }};
}}

function priorityRank(level) {{
  return {{ critical: 4, focus: 3, follow: 2, skim: 1 }}[level] || 0;
}}

function renderReadingGuide(items) {{
  const panel = document.getElementById("readingGuidePanel");
  const container = document.getElementById("readingGuide");
  const candidates = [
    ...items.filter(item => (item.status || "skipped") !== "skipped"),
    ...(reportData.follow_up || []).map(item => ({{ ...item, status: item.status || "blocked" }}))
  ].map(item => ({{ item, advice: readingAdvice(item) }}))
    .filter(entry => entry.advice.level !== "skim")
    .sort((left, right) => priorityRank(right.advice.level) - priorityRank(left.advice.level));

  if (!candidates.length) {{
    panel.style.display = "none";
    container.innerHTML = "";
    return;
  }}

  panel.style.display = "block";
  container.innerHTML = candidates.slice(0, 9).map(entry => {{
    const item = entry.item;
    const advice = entry.advice;
    const prText = item.number ? `#${{item.number}}` : "PR";
    const prLink = item.url
      ? `<a href="${{escapeHtml(item.url)}}">${{prText}} · ${{escapeHtml(text(item.title))}}</a>`
      : `<span>${{prText}} · ${{escapeHtml(text(item.title))}}</span>`;
    return `
      <article class="guide-card ${{advice.level}}">
        <div class="guide-meta">
          <span class="read-pill ${{advice.level}}">${{advice.icon}} ${{escapeHtml(advice.label)}}</span>
          <span class="badge ${{item.status || "skipped"}}">${{labels[lang][item.status] || item.status || labels[lang].skipped}}</span>
        </div>
        <div>${{prLink}}</div>
        <div class="guide-reason">${{escapeHtml(advice.reason)}}</div>
      </article>
    `;
  }}).join("");
}}

function storyLine(label, value) {{
  const body = text(value);
  if (!body) return "";
  return `
    <p class="story-line">
      <span class="story-label">${{escapeHtml(label)}}</span>
      <span class="story-text">${{formatRich(body)}}</span>
    </p>
  `;
}}

function storyBlock(title, rows, className = "") {{
  const body = rows.filter(Boolean).join("");
  if (!body) return "";
  const classes = ["story-block", className].filter(Boolean).join(" ");
  return `<section class="${{classes}}"><h4>${{escapeHtml(title)}}</h4>${{body}}</section>`;
}}

function compactSummary(item) {{
  const candidates = [
    item.outcome,
    item.skip_reason,
    item.reason,
    item.problem,
    item.design_assessment,
    item.risk
  ].map(value => text(value).trim()).filter(Boolean);
  return candidates[0] || labels[lang].summaryFallback;
}}

function updateCardToggle(card) {{
  const button = card.querySelector(".card-toggle");
  if (!button) return;
  const open = card.classList.contains("open");
  button.textContent = open ? labels[lang].collapseDetails : labels[lang].expandDetails;
  button.setAttribute("aria-expanded", open ? "true" : "false");
}}

function setCardOpen(card, open) {{
  card.classList.toggle("open", open);
  updateCardToggle(card);
}}

function factItem(label, value) {{
  const body = text(value);
  if (!body) return "";
  return `
    <div class="fact">
      <dt>${{escapeHtml(label)}}</dt>
      <dd>${{formatRich(body)}}</dd>
    </div>
  `;
}}

function directFixesText(fixes) {{
  if (!Array.isArray(fixes) || !fixes.length) return "";
  return fixes.map(fix => {{
    if (typeof fix !== "object" || fix === null) return text(fix);
    return [
      fix.branch ? `branch: ${{text(fix.branch)}}` : "",
      fix.commit ? `commit: ${{text(fix.commit)}}` : "",
      fix.message ? `message: ${{text(fix.message)}}` : "",
      fix.files ? `files: ${{Array.isArray(fix.files) ? fix.files.map(file => text(file)).join(", ") : text(fix.files)}}` : "",
      fix.tests ? `tests: ${{Array.isArray(fix.tests) ? fix.tests.map(test => text(test)).join(", ") : text(fix.tests)}}` : "",
      fix.push_state ? `push: ${{text(fix.push_state)}}` : "",
      fix.ci_state ? `CI: ${{text(fix.ci_state)}}` : ""
    ].filter(Boolean).join(" · ");
  }}).join("\\n");
}}

function renderReviewRail(item) {{
  const advice = readingAdvice(item);
  const callout = `
    <div class="reading-callout ${{advice.level}}">
      <strong>${{advice.icon}} ${{escapeHtml(advice.label)}}</strong>
      <span>${{escapeHtml(advice.reason)}}</span>
    </div>
  `;
  const facts = [
    factItem(labels[lang].outcome, item.outcome),
    factItem(labels[lang].risk, item.risk),
    factItem(labels[lang].ci, item.ci_state),
    factItem(labels[lang].attentionPoints, item.attention_points),
    factItem(labels[lang].directFixes, directFixesText(item.direct_fixes)),
    factItem(labels[lang].selfReviewPolicy, item.self_review_policy),
    factItem(labels[lang].testsDocs, item.tests_docs),
    factItem(labels[lang].modules, item.modules),
    factItem(labels[lang].apiSurface, item.api_surface),
    factItem(labels[lang].reason, item.skip_reason)
  ].filter(Boolean).join("");
  if (!facts) return `<aside class="review-rail">${{callout}}</aside>`;
  return `<aside class="review-rail">${{callout}}<h4>${{labels[lang].reviewSummary}}</h4><dl class="fact-list">${{facts}}</dl></aside>`;
}}

function renderComments(item) {{
  const comments = item.inline_comments || [];
  if (!comments.length) return "";
  const rendered = comments.map(comment => `
    <div class="comment">
      <strong>${{escapeHtml(comment.path || "")}}${{comment.line ? ":" + escapeHtml(comment.line) : ""}}</strong>
      <div>${{formatRich(text(comment.body || comment))}}</div>
      ${{comment.focus ? `<div><strong>${{labels[lang].focus}}:</strong> ${{escapeHtml(text(comment.focus))}}</div>` : ""}}
      ${{comment.severity ? `<div><strong>${{labels[lang].severity}}:</strong> ${{escapeHtml(text(comment.severity))}}</div>` : ""}}
    </div>
  `).join("");
  return `<section class="comments-panel">
    <h4>${{labels[lang].inlineComments}}</h4>
    <div class="comment-list">${{rendered}}</div>
  </section>`;
}}

function renderPrReadout(item) {{
  const story = [
    storyBlock(labels[lang].backgroundAndProblem, [
      storyLine(labels[lang].technicalBackground, item.technical_background),
      storyLine(labels[lang].problem, item.problem),
      storyLine(labels[lang].problemFraming, item.problem_framing),
      storyLine(labels[lang].rootCause, item.root_cause)
    ], "hero-block"),
    storyBlock(labels[lang].solutionAndTradeoffs, [
      storyLine(labels[lang].approach, item.approach),
      storyLine(labels[lang].alternativeDesigns, item.alternative_designs),
      storyLine(labels[lang].tradeoffs, item.tradeoffs),
      storyLine(labels[lang].designAssessment, item.design_assessment)
    ]),
    storyBlock(labels[lang].impactAndEvidence, [
      storyLine(labels[lang].changeInventory, item.change_inventory),
      storyLine(labels[lang].semanticChanges, item.semantic_changes),
      storyLine(labels[lang].behaviorImpact, item.behavior_impact),
      storyLine(labels[lang].moduleImpact, item.module_impact),
      storyLine(labels[lang].crossModuleImpact, item.cross_module_impact)
    ]),
    renderComments(item)
  ].filter(Boolean).join("");
  return `<div class="pr-readout"><div class="pr-story">${{story}}</div>${{renderReviewRail(item)}}</div>`;
}}

function renderCards() {{
  const query = document.getElementById("search").value.trim();
  const visible = prs().filter(item => (item.status || "skipped") !== "skipped")
    .filter(item => {{
    const status = item.status || "skipped";
    return (filter === "all" || status === filter) && matchesSearch(item, query);
  }});
  const container = document.getElementById("cards");
  if (!visible.length) {{
    container.innerHTML = `<div class="empty">${{labels[lang].empty}}</div>`;
    return;
  }}
  container.innerHTML = visible.map(item => {{
    const status = item.status || "skipped";
    const advice = readingAdvice(item);
    const summary = compactSummary(item);
    const prText = item.number ? `#${{item.number}}` : "PR";
    const prLink = item.url
      ? `<a href="${{escapeHtml(item.url)}}">${{prText}}</a>`
      : prText;
    return `
      <article class="card priority-${{advice.level}}" data-status="${{status}}">
        <div class="card-head">
          <div>
            <div class="headline-row">
              <h3 class="card-title">${{prLink}} · ${{escapeHtml(text(item.title))}}</h3>
              <span class="read-pill ${{advice.level}}">${{advice.icon}} ${{escapeHtml(advice.label)}}</span>
            </div>
            <div class="meta">
              <span>${{labels[lang].author}}: ${{escapeHtml(item.author || "")}}</span>
              <span class="advice-reason">${{escapeHtml(advice.reason)}}</span>
            </div>
            <div class="card-summary">${{formatRich(summary)}}</div>
          </div>
          <div class="card-actions">
            <span class="badge ${{status}}">${{labels[lang][status] || status}}</span>
            <button class="card-toggle" type="button" aria-expanded="false">${{labels[lang].expandDetails}}</button>
          </div>
        </div>
        <div class="card-body">
          ${{renderPrReadout(item)}}
        </div>
      </article>
    `;
  }}).join("");
  document.querySelectorAll(".card-head").forEach(head => {{
    head.addEventListener("click", event => {{
      if (event.target.closest("a")) return;
      const card = head.closest(".card");
      setCardOpen(card, !card.classList.contains("open"));
    }});
  }});
  document.querySelectorAll(".card").forEach(card => updateCardToggle(card));
}}

function renderSkipGroups() {{
  const heading = document.getElementById("skippedHeading");
  const container = document.getElementById("skipGroups");
  if (!["all", "skipped"].includes(filter)) {{
    heading.style.display = "none";
    container.style.display = "none";
    return;
  }}
  heading.style.display = "flex";
  container.style.display = "grid";
  const query = document.getElementById("search").value.trim();
  const groups = skippedGroups().map(group => {{
    const reason = group.reason || "";
    const items = (group.items || []).map(item => ({{
      ...item,
      status: item.status || "skipped",
      group_reason: reason,
      skip_reason: item.skip_reason || reason
    }})).filter(item => matchesSearch(item, query));
    return {{ reason, items }};
  }}).filter(group => group.items.length > 0);
  if (!groups.length) {{
    container.innerHTML = `<div class="empty">${{labels[lang].empty}}</div>`;
    return;
  }}
  container.innerHTML = groups.map((group, index) => `
    <article class="skip-group open">
      <div class="skip-group-head" data-skip-group="${{index}}">
        <h3 class="skip-group-title">${{escapeHtml(text(group.reason))}}</h3>
        <span class="skip-group-count">${{group.items.length}} ${{labels[lang].items}}</span>
      </div>
      <div class="skip-group-body">
        ${{group.items.map(item => {{
          const prText = item.number ? `#${{item.number}}` : "PR";
          const prLink = item.url
            ? `<a href="${{escapeHtml(item.url)}}">${{prText}}</a>`
            : prText;
          return `
            <div class="skip-row">
              <div>
                <div class="skip-title">${{prLink}} · ${{escapeHtml(text(item.title))}}</div>
                <div class="skip-detail">${{labels[lang].author}}: ${{escapeHtml(item.author || "")}}</div>
              </div>
              <div>
                <div><strong>${{labels[lang].blocker}}:</strong> ${{formatRich(text(item.skip_reason))}}</div>
                ${{item.readiness_audit ? `<div class="skip-detail"><strong>${{labels[lang].readinessAudit}}:</strong> ${{formatRich(text(item.readiness_audit))}}</div>` : ""}}
                ${{renderBlockers(item)}}
                ${{item.ci_state ? `<div class="skip-detail">${{formatRich(text(item.ci_state))}}</div>` : ""}}
                ${{item.risk ? `<div class="skip-detail">${{formatRich(text(item.risk))}}</div>` : ""}}
              </div>
            </div>
          `;
        }}).join("")}}
      </div>
    </article>
  `).join("");
  document.querySelectorAll("[data-skip-group]").forEach(head => {{
    head.addEventListener("click", () => {{
      head.closest(".skip-group").classList.toggle("open");
    }});
  }});
}}

function renderFollowUp() {{
  const heading = document.getElementById("followUpHeading");
  const container = document.getElementById("followUpCards");
  if (!["all", "skipped", "blocked"].includes(filter)) {{
    heading.style.display = "none";
    container.style.display = "none";
    return;
  }}
  const query = document.getElementById("search").value.trim().toLowerCase();
  const items = (reportData.follow_up || []).filter(item => {{
    if (!query) return true;
    return [
      item.number,
      item.author,
      text(item.title),
      text(item.reason),
      text(item.next)
    ].join(" ").toLowerCase().includes(query);
  }});
  if (!items.length) {{
    heading.style.display = "none";
    container.style.display = "none";
    return;
  }}
  heading.style.display = "flex";
  container.style.display = "grid";
  container.innerHTML = items.map(item => {{
    const prText = item.number ? `#${{item.number}}` : "PR";
    const prLink = item.url
      ? `<a href="${{escapeHtml(item.url)}}">${{prText}}</a>`
      : prText;
    return `
      <article class="card open" data-status="blocked">
        <div class="card-head">
          <div>
            <h3 class="card-title">${{prLink}} · ${{escapeHtml(text(item.title))}}</h3>
            <div class="meta">${{labels[lang].author}}: ${{escapeHtml(item.author || "")}}</div>
          </div>
          <span class="badge blocked">${{labels[lang].followups}}</span>
        </div>
        <div class="card-body">
          <div class="grid">
            ${{field(labels[lang].reason, item.reason)}}
            ${{field(labels[lang].outcome, item.next)}}
          </div>
        </div>
      </article>
    `;
  }}).join("");
}}

function render() {{
  const items = prs();
  renderStatic();
  renderMetrics(items);
  renderBars(items);
  renderTimeline();
  renderOverview();
  renderReadingGuide(items);
  renderChips();
  renderCards();
  renderSkipGroups();
  renderFollowUp();
}}

document.querySelectorAll("[data-lang-button]").forEach(button => {{
  button.addEventListener("click", () => setLanguage(button.dataset.langButton));
}});
document.getElementById("search").addEventListener("input", () => {{
  renderCards();
  renderSkipGroups();
  renderFollowUp();
}});
document.getElementById("openAll").addEventListener("click", () => {{
  document.querySelectorAll(".card").forEach(card => setCardOpen(card, true));
  document.querySelectorAll(".skip-group").forEach(node => node.classList.add("open"));
}});
document.getElementById("closeAll").addEventListener("click", () => {{
  document.querySelectorAll(".card").forEach(card => setCardOpen(card, false));
  document.querySelectorAll(".skip-group").forEach(node => node.classList.remove("open"));
}});
render();
</script>
</body>
</html>
"""


def main() -> None:
    args = parse_args()
    data = read_summary(args.summary_json)
    output = args.output or default_output_path()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_html(data), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
