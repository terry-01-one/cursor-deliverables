from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Expect:
    status: int | None = None
    json_path: dict[str, Any] = field(default_factory=dict)
    contains: list[str] = field(default_factory=list)
    headers: dict[str, str] = field(default_factory=dict)


@dataclass
class Case:
    id: str
    name: str
    method: str = "GET"
    path: str = "/"
    headers: dict[str, str] = field(default_factory=dict)
    query: dict[str, Any] = field(default_factory=dict)
    body: Any = None
    expect: Expect = field(default_factory=Expect)


@dataclass
class Suite:
    name: str
    base_url: str = ""
    timeout: float = 10.0
    headers: dict[str, str] = field(default_factory=dict)
    cases: list[Case] = field(default_factory=list)


@dataclass
class CaseResult:
    id: str
    name: str
    passed: bool
    duration_ms: float
    message: str = ""
    request: dict[str, Any] = field(default_factory=dict)
    response: dict[str, Any] = field(default_factory=dict)


@dataclass
class RunReport:
    suite: str
    started_at: str
    finished_at: str
    total: int
    passed: int
    failed: int
    results: list[CaseResult] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.failed == 0