from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .models import CaseResult, RunReport, Suite


def build_report(suite: Suite, results: list[CaseResult]) -> RunReport:
    now = datetime.now(timezone.utc).astimezone()
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed
    stamp = now.isoformat(timespec="seconds")
    return RunReport(
        suite=suite.name,
        started_at=stamp,
        finished_at=stamp,
        total=len(results),
        passed=passed,
        failed=failed,
        results=results,
    )


def write_json(report: RunReport, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(asdict(report), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def write_html(report: RunReport, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for r in report.results:
        color = "#0a7" if r.passed else "#c33"
        status = "PASS" if r.passed else "FAIL"
        rows.append(
            f"<tr><td>{r.id}</td><td>{r.name}</td>"
            f"<td style='color:{color};font-weight:600'>{status}</td>"
            f"<td>{r.duration_ms} ms</td><td>{_esc(r.message)}</td></tr>"
        )
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <title>Test Report — { _esc(report.suite) }</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 32px; }}
    h1 {{ margin-bottom: 4px; }}
    .meta {{ color: #666; margin-bottom: 20px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 8px 10px; text-align: left; }}
    th {{ background: #f6f6f6; }}
  </style>
</head>
<body>
  <h1>{_esc(report.suite)}</h1>
  <div class="meta">
    total={report.total} passed={report.passed} failed={report.failed}
    · { _esc(report.finished_at) }
  </div>
  <table>
    <thead><tr><th>ID</th><th>Name</th><th>Result</th><th>Duration</th><th>Message</th></tr></thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")
    return path


def _esc(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )