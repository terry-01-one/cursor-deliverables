from __future__ import annotations

import time
from typing import Any

import requests

from ..models import Case, CaseResult, Expect, Suite


def _dig(data: Any, dotted: str) -> Any:
    cur = data
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            raise KeyError(dotted)
    return cur


def _check(expect: Expect, response: requests.Response) -> None:
    if expect.status is not None and response.status_code != expect.status:
        raise AssertionError(
            f"status 期望 {expect.status}，实际 {response.status_code}"
        )

    for key, want in expect.headers.items():
        got = response.headers.get(key)
        if got != want:
            raise AssertionError(f"header {key} 期望 {want!r}，实际 {got!r}")

    text = response.text or ""
    for needle in expect.contains:
        if needle not in text:
            raise AssertionError(f"响应文本未包含: {needle!r}")

    if expect.json_path:
        try:
            payload = response.json()
        except Exception as exc:  # noqa: BLE001
            raise AssertionError(f"响应不是合法 JSON: {exc}") from exc
        for path, want in expect.json_path.items():
            got = _dig(payload, path)
            if got != want:
                raise AssertionError(
                    f"json_path {path} 期望 {want!r}，实际 {got!r}"
                )


def run_case(suite: Suite, case: Case) -> CaseResult:
    url = case.path if case.path.startswith("http") else f"{suite.base_url}{case.path}"
    headers = {**suite.headers, **case.headers}
    started = time.perf_counter()
    req_meta = {
        "method": case.method,
        "url": url,
        "headers": headers,
        "query": case.query,
        "body": case.body,
    }
    try:
        response = requests.request(
            method=case.method,
            url=url,
            headers=headers,
            params=case.query or None,
            json=case.body if isinstance(case.body, (dict, list)) else None,
            data=None if isinstance(case.body, (dict, list, type(None))) else case.body,
            timeout=suite.timeout,
        )
        _check(case.expect, response)
        duration = (time.perf_counter() - started) * 1000
        body_preview = response.text[:500]
        return CaseResult(
            id=case.id,
            name=case.name,
            passed=True,
            duration_ms=round(duration, 2),
            message="OK",
            request=req_meta,
            response={
                "status": response.status_code,
                "headers": dict(response.headers),
                "body_preview": body_preview,
            },
        )
    except Exception as exc:  # noqa: BLE001
        duration = (time.perf_counter() - started) * 1000
        return CaseResult(
            id=case.id,
            name=case.name,
            passed=False,
            duration_ms=round(duration, 2),
            message=str(exc),
            request=req_meta,
            response={},
        )


def run_suite(suite: Suite) -> list[CaseResult]:
    return [run_case(suite, case) for case in suite.cases]