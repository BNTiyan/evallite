"""Data models for local-first agent evaluations, assertions, and test suites."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class EvalCase:
    """A single evaluation scenario for an agent or tool-calling pipeline."""

    id: str
    prompt: str
    expected_tool: Optional[str] = None
    expected_args: Dict[str, Any] = field(default_factory=dict)
    forbidden_args: List[str] = field(default_factory=list)
    assertions: List[str] = field(default_factory=list)
    max_latency_ms: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvalResult:
    """Outcome of evaluating one test case."""

    case_id: str
    passed: bool
    actual_tool: Optional[str] = None
    actual_args: Dict[str, Any] = field(default_factory=dict)
    actual_output: Optional[str] = None
    latency_ms: float = 0.0
    errors: List[str] = field(default_factory=list)
    diffs: List[str] = field(default_factory=list)


@dataclass
class SuiteSummary:
    """Aggregated metrics across an entire evaluation run."""

    suite_name: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    accuracy_pct: float
    p50_latency_ms: float
    total_duration_sec: float
    results: List[EvalResult] = field(default_factory=list)
