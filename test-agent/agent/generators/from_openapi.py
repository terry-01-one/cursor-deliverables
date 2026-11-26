from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml


def _load(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("OpenAPI 文件根节点必须是对象")
    return data


def _base_url(spec: dict[str, Any]) -> str:
    servers = spec.get("servers") or []
    if servers and isinstance(servers[0], dict) and servers[0].get("url"):
        return str(servers[0]["url"]).rstrip("/")
    return ""


def generate_suite(openapi_path: str | Path, suite_name: str | None = None) -> dict[str, Any]:
    """从 OpenAPI 生成可编辑的 YAML 套件结构（仅 GET/常见写方法骨架）。"""
    path = Path(openapi_path)
    spec = _load(path)
    paths = spec.get("paths") or {}
    cases: list[dict[str, Any]] = []
    idx = 1
    for api_path, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        for method, op in methods.items():
            m = str(method).upper()
            if m not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
                continue
            if not isinstance(op, dict):
                continue
            op_id = op.get("operationId") or f"{m.lower()}_{idx}"
            name = op.get("summary") or op_id
            expect_status = 200
            responses = op.get("responses") or {}
            for code in ("200", "201", "204"):
                if code in responses:
                    expect_status = int(code)
                    break
            case: dict[str, Any] = {
                "id": str(op_id),
                "name": str(name),
                "method": m,
                "path": str(api_path),
                "expect": {"status": expect_status},
            }
            if m in {"POST", "PUT", "PATCH"}:
                case["headers"] = {"Content-Type": "application/json"}
                case["body"] = {}
            cases.append(case)
            idx += 1

    name = suite_name or path.stem
    base = _base_url(spec)
    # 相对 server 时留给用户补全
    if base and not urlparse(base).scheme:
        base = ""
    return {
        "name": name,
        "base_url": base or "https://example.com",
        "timeout": 10,
        "cases": cases,
    }


def write_suite_yaml(openapi_path: str | Path, out_path: str | Path, suite_name: str | None = None) -> Path:
    suite = generate_suite(openapi_path, suite_name=suite_name)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        yaml.safe_dump(suite, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return out