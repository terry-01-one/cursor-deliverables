from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import Case, Expect, Suite


def _expect_from(raw: dict[str, Any] | None) -> Expect:
    raw = raw or {}
    return Expect(
        status=raw.get("status"),
        json_path=dict(raw.get("json_path") or {}),
        contains=list(raw.get("contains") or []),
        headers=dict(raw.get("headers") or {}),
    )


def load_suite(path: str | Path) -> Suite:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"套件文件格式错误: {path}")

    cases: list[Case] = []
    for i, item in enumerate(data.get("cases") or []):
        if not isinstance(item, dict):
            raise ValueError(f"cases[{i}] 必须是对象")
        case_id = str(item.get("id") or f"case_{i+1}")
        cases.append(
            Case(
                id=case_id,
                name=str(item.get("name") or case_id),
                method=str(item.get("method") or "GET").upper(),
                path=str(item.get("path") or "/"),
                headers=dict(item.get("headers") or {}),
                query=dict(item.get("query") or {}),
                body=item.get("body"),
                expect=_expect_from(item.get("expect")),
            )
        )

    return Suite(
        name=str(data.get("name") or Path(path).stem),
        base_url=str(data.get("base_url") or "").rstrip("/"),
        timeout=float(data.get("timeout") or 10),
        headers=dict(data.get("headers") or {}),
        cases=cases,
    )