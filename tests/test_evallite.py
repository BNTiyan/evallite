"""Unit and integration tests for EVALLITE engine and CLI."""

import asyncio
import subprocess
import sys
import pytest

from evallite.demo import get_demo_cases, mock_agent_runner
from evallite.engine import EvalEngine
from evallite.models import EvalCase, SuiteSummary


@pytest.mark.asyncio
async def test_engine_evaluates_demo_cases_successfully():
    cases = get_demo_cases()
    engine = EvalEngine(suite_name="test-suite")
    summary = await engine.run_suite(cases, mock_agent_runner)

    assert isinstance(summary, SuiteSummary)
    assert summary.total_cases == len(cases)
    assert summary.passed_cases == len(cases)
    assert summary.failed_cases == 0
    assert summary.accuracy_pct == 100.0
    assert summary.p50_latency_ms >= 0.0


@pytest.mark.asyncio
async def test_engine_detects_tool_mismatch():
    case = EvalCase(
        id="mismatch-case",
        prompt="Calculate 2 + 2",
        expected_tool="non_existent_tool",
    )
    engine = EvalEngine()
    result = await engine.evaluate_case(case, mock_agent_runner)

    assert result.passed is False
    assert any("Tool mismatch" in err for err in result.errors)


@pytest.mark.asyncio
async def test_engine_detects_hallucinated_arguments():
    def agent_with_hallucination(prompt: str):
        return {
            "tool": "get_weather",
            "arguments": {"city": "Paris", "stolen_token": "secret_123"},
        }

    case = EvalCase(
        id="hallucination-case",
        prompt="Weather in Paris",
        expected_tool="get_weather",
        expected_args={"city": "Paris"},
        forbidden_args=["stolen_token"],
    )
    engine = EvalEngine()
    result = await engine.evaluate_case(case, agent_with_hallucination)

    assert result.passed is False
    assert any("Hallucinated forbidden argument" in err for err in result.errors)


def test_cli_version():
    res = subprocess.run([sys.executable, "-m", "evallite.cli", "--version"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "evallite" in res.stdout


def test_cli_demo_execution():
    res = subprocess.run([sys.executable, "-m", "evallite.cli", "demo", "--ci"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "EVALLITE" in res.stdout
    assert "Accuracy Score" in res.stdout
