"""Built-in demonstration suite and mock agents for EVALLITE."""

from __future__ import annotations

import re
from typing import Any, Dict, List

from evallite.models import EvalCase


def get_demo_cases() -> List[EvalCase]:
    """Returns sample evaluation cases covering tool calls, arguments, and assertions."""
    return [
        EvalCase(
            id="sql-query-gen",
            prompt="Find all active users in California with more than 10 purchases",
            expected_tool="execute_sql",
            expected_args={"table": "users", "status": "active"},
            assertions=["contains:SELECT", "regex:WHERE.*status"],
            max_latency_ms=250.0,
        ),
        EvalCase(
            id="weather-lookup",
            prompt="What is the forecast for Tokyo in Celsius?",
            expected_tool="get_weather",
            expected_args={"city": "Tokyo", "units": "celsius"},
            forbidden_args=["api_key", "password"],
        ),
        EvalCase(
            id="flight-booker",
            prompt="Book a one-way flight from SFO to JFK on December 15th",
            expected_tool="book_flight",
            expected_args={"origin": "SFO", "destination": "JFK", "one_way": True},
            forbidden_args=["credit_card_cvv"],
        ),
        EvalCase(
            id="calculator-eval",
            prompt="Calculate 144 / 12 + 8",
            expected_tool="calculate",
            expected_args={"expression": "144 / 12 + 8"},
            assertions=["contains:20"],
        ),
    ]


def mock_agent_runner(prompt: str) -> Dict[str, Any]:
    """A deterministic mock agent responding to prompts with tool calls."""
    lower = prompt.lower()
    if "california" in lower or "active users" in lower:
        return {
            "tool": "execute_sql",
            "arguments": {"table": "users", "status": "active", "limit": 100},
            "output": "SELECT * FROM users WHERE status = 'active' AND purchases > 10",
        }
    elif "tokyo" in lower:
        return {
            "tool": "get_weather",
            "arguments": {"city": "Tokyo", "units": "celsius"},
            "output": "Tokyo weather: 18C, Clear skies",
        }
    elif "sfo to jfk" in lower:
        return {
            "tool": "book_flight",
            "arguments": {"origin": "SFO", "destination": "JFK", "one_way": True},
            "output": "Flight SFO->JFK confirmed for Dec 15",
        }
    elif "calculate" in lower or "/" in lower:
        return {
            "tool": "calculate",
            "arguments": {"expression": "144 / 12 + 8"},
            "output": "Calculated value: 20",
        }
    return {"tool": None, "arguments": {}, "output": "I am not sure how to assist with that."}
