"""Evaluation engine for validating tool calls, argument schemas, and output assertions."""

from __future__ import annotations

import asyncio
import re
import statistics
import time
from typing import Any, Callable, Dict, List, Optional

from evallite.models import EvalCase, EvalResult, SuiteSummary


class EvalEngine:
    """Executes evaluation cases against an agent runner callable."""

    def __init__(self, suite_name: str = "agent-evaluation-suite"):
        self.suite_name = suite_name

    async def evaluate_case(
        self, case: EvalCase, runner: Callable[[str], Any]
    ) -> EvalResult:
        """Runs a single test case against the runner and evaluates assertions."""
        errors: List[str] = []
        diffs: List[str] = []

        start_time = time.perf_counter()
        try:
            if asyncio.iscoroutinefunction(runner):
                output = await runner(case.prompt)
            else:
                output = runner(case.prompt)
        except Exception as exc:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return EvalResult(
                case_id=case.id,
                passed=False,
                latency_ms=latency_ms,
                errors=[f"Agent execution raised exception: {exc}"],
            )

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        # Extract tool name and arguments from output
        actual_tool: Optional[str] = None
        actual_args: Dict[str, Any] = {}
        actual_text: Optional[str] = None

        if isinstance(output, dict):
            actual_tool = output.get("tool") or output.get("name")
            actual_args = output.get("arguments") or output.get("args") or {}
            actual_text = output.get("output") or output.get("text")
        elif hasattr(output, "tool"):
            actual_tool = getattr(output, "tool")
            actual_args = getattr(output, "arguments", {})
            actual_text = getattr(output, "output", str(output))
        else:
            actual_text = str(output)

        # 1. Check Tool Selection
        if case.expected_tool is not None:
            if actual_tool != case.expected_tool:
                errors.append(
                    f"Tool mismatch: expected '{case.expected_tool}', got '{actual_tool}'"
                )
                diffs.append(f"- tool: {case.expected_tool}\n+ tool: {actual_tool}")

        # 2. Check Expected Arguments
        for key, expected_val in case.expected_args.items():
            if key not in actual_args:
                errors.append(f"Missing required argument: '{key}'")
                diffs.append(f"- {key}: {expected_val}\n+ {key}: <MISSING>")
            elif actual_args[key] != expected_val:
                errors.append(
                    f"Argument value mismatch for '{key}': expected {expected_val!r}, got {actual_args[key]!r}"
                )
                diffs.append(f"- {key}: {expected_val}\n+ {key}: {actual_args[key]}")

        # 3. Check Forbidden / Hallucinated Arguments
        for forbidden in case.forbidden_args:
            if forbidden in actual_args:
                errors.append(f"Hallucinated forbidden argument detected: '{forbidden}'")
                diffs.append(f"+ [HALLUCINATION] {forbidden}: {actual_args[forbidden]}")

        # 4. Check Latency Threshold
        if case.max_latency_ms is not None and latency_ms > case.max_latency_ms:
            errors.append(
                f"Latency SLA exceeded: {latency_ms:.1f}ms > {case.max_latency_ms:.1f}ms"
            )

        # 5. Check Text Assertions
        for assertion in case.assertions:
            if assertion.startswith("contains:"):
                needle = assertion[len("contains:") :].strip()
                if not actual_text or needle not in actual_text:
                    errors.append(f"Assertion failed: output does not contain '{needle}'")
            elif assertion.startswith("regex:"):
                pattern = assertion[len("regex:") :].strip()
                if not actual_text or not re.search(pattern, actual_text):
                    errors.append(f"Assertion failed: output does not match pattern '{pattern}'")

        passed = len(errors) == 0
        return EvalResult(
            case_id=case.id,
            passed=passed,
            actual_tool=actual_tool,
            actual_args=actual_args,
            actual_output=actual_text,
            latency_ms=latency_ms,
            errors=errors,
            diffs=diffs,
        )

    async def run_suite(
        self, cases: List[EvalCase], runner: Callable[[str], Any]
    ) -> SuiteSummary:
        """Evaluates an entire suite of cases."""
        start_wall = time.perf_counter()
        results: List[EvalResult] = []

        for case in cases:
            res = await self.evaluate_case(case, runner)
            results.append(res)

        total_duration = time.perf_counter() - start_wall
        passed_count = sum(1 for r in results if r.passed)
        failed_count = len(results) - passed_count
        accuracy = (passed_count / len(cases) * 100.0) if cases else 0.0

        latencies = [r.latency_ms for r in results]
        p50 = statistics.median(latencies) if latencies else 0.0

        return SuiteSummary(
            suite_name=self.suite_name,
            total_cases=len(cases),
            passed_cases=passed_count,
            failed_cases=failed_count,
            accuracy_pct=accuracy,
            p50_latency_ms=p50,
            total_duration_sec=total_duration,
            results=results,
        )
