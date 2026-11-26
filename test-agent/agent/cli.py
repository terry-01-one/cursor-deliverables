from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .generators.from_openapi import write_suite_yaml
from .loaders import load_suite
from .report import build_report, write_html, write_json
from .runners.http_runner import run_suite

console = Console()


def cmd_run(args: argparse.Namespace) -> int:
    suite = load_suite(args.suite)
    if not suite.cases:
        console.print("[yellow]套件里没有用例[/yellow]")
        return 1
    results = run_suite(suite)
    report = build_report(suite, results)

    table = Table(title=f"Suite: {suite.name}")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Result")
    table.add_column("ms")
    table.add_column("Message")
    for r in results:
        mark = "[green]PASS[/green]" if r.passed else "[red]FAIL[/red]"
        table.add_row(r.id, r.name, mark, str(r.duration_ms), r.message)
    console.print(table)
    console.print(
        f"total={report.total} passed={report.passed} failed={report.failed}"
    )

    out_dir = Path(args.out)
    stamp = suite.name.replace(" ", "_")
    json_path = write_json(report, out_dir / f"{stamp}.json")
    html_path = write_html(report, out_dir / f"{stamp}.html")
    console.print(f"JSON: {json_path}")
    console.print(f"HTML: {html_path}")
    return 0 if report.ok else 1


def cmd_gen(args: argparse.Namespace) -> int:
    out = write_suite_yaml(args.openapi, args.out, suite_name=args.name)
    console.print(f"已生成套件: {out}")
    console.print("请先核对 base_url / 鉴权 / body，再执行 run")
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    target = Path(args.path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not args.force:
        console.print(f"[red]已存在: {target}（加 --force 覆盖）[/red]")
        return 1
    sample = Path(__file__).resolve().parents[1] / "examples" / "sample_suite.yaml"
    target.write_text(sample.read_text(encoding="utf-8"), encoding="utf-8")
    console.print(f"已写入示例套件: {target}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="test-agent",
        description="通用测试 Agent：YAML 套件执行 + OpenAPI 生成 + HTML/JSON 报告",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="执行测试套件")
    p_run.add_argument("suite", help="YAML 套件路径")
    p_run.add_argument(
        "--out",
        default="reports",
        help="报告输出目录（默认 reports）",
    )
    p_run.set_defaults(func=cmd_run)

    p_gen = sub.add_parser("gen", help="从 OpenAPI 生成套件骨架")
    p_gen.add_argument("openapi", help="openapi.json / openapi.yaml")
    p_gen.add_argument(
        "-o",
        "--out",
        default="examples/generated_suite.yaml",
        help="输出 YAML 路径",
    )
    p_gen.add_argument("--name", default=None, help="套件名称")
    p_gen.set_defaults(func=cmd_gen)

    p_init = sub.add_parser("init", help="生成一份示例套件")
    p_init.add_argument(
        "path",
        nargs="?",
        default="examples/my_suite.yaml",
        help="输出路径",
    )
    p_init.add_argument("--force", action="store_true")
    p_init.set_defaults(func=cmd_init)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())