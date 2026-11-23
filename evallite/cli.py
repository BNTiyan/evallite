"""Command-line interface for EVALLITE — Local-First Agent Evaluation Engine."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from typing import List

from rich.console import Console

from evallite.dashboard import render_dashboard
from evallite.demo import get_demo_cases, mock_agent_runner
from evallite.engine import EvalEngine
from evallite.models import EvalCase

console = Console()
__version__ = "1.0.0"


def load_cases_from_file(path: str) -> List[EvalCase]:
    """Loads evaluation cases from a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    cases_raw = data if isinstance(data, list) else data.get("cases", [])
    return [
        EvalCase(
            id=c.get("id", f"case-{i}"),
            prompt=c.get("prompt", ""),
            expected_tool=c.get("expected_tool"),
            expected_args=c.get("expected_args", {}),
            forbidden_args=c.get("forbidden_args", []),
            assertions=c.get("assertions", []),
            max_latency_ms=c.get("max_latency_ms"),
            metadata=c.get("metadata", {}),
        )
        for i, c in enumerate(cases_raw)
    ]


async def run_suite_cli(cases: List[EvalCase], suite_name: str, min_accuracy: float = 100.0, ci_mode: bool = False) -> None:
    """Executes the evaluation suite and displays the Rich dashboard."""
    with console.status(f"[bold cyan]Running evaluation suite: [green]{suite_name}[/green]..."):
        engine = EvalEngine(suite_name=suite_name)
        summary = await engine.run_suite(cases, mock_agent_runner)

    console.clear()
    console.print(render_dashboard(summary))

    if ci_mode and summary.accuracy_pct < min_accuracy:
        console.print(
            f"\n[bold red]CI GATE FAILED: Accuracy {summary.accuracy_pct:.1f}% below required threshold of {min_accuracy:.1f}%[/bold red]"
        )
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="evallite",
        description="🎯 EVALLITE — Lightning-Fast, Local-First Agent & Tool-Call Evaluation Engine",
    )
    parser.add_argument("--version", action="version", version=f"evallite {__version__}")
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # Demo
    demo_parser = subparsers.add_parser("demo", help="Run interactive demonstration on built-in mock agents")
    demo_parser.add_argument("--ci", action="store_true", help="Run in CI mode with exit code checking")

    # Run
    run_parser = subparsers.add_parser("run", help="Run evaluation cases from a JSON file")
    run_parser.add_argument("file", help="Path to evaluation suite JSON file")
    run_parser.add_argument("--name", default="local-eval-suite", help="Suite name")
    run_parser.add_argument("--min-accuracy", type=float, default=100.0, help="Minimum accuracy percentage required in CI")
    run_parser.add_argument("--ci", action="store_true", help="Fail with exit code 1 if accuracy drops below threshold")

    args = parser.parse_args()

    if not args.subcommand or args.subcommand == "demo":
        cases = get_demo_cases()
        asyncio.run(run_suite_cli(cases, suite_name="demo-agent-suite", ci_mode=getattr(args, "ci", False)))
    elif args.subcommand == "run":
        cases = load_cases_from_file(args.file)
        asyncio.run(
            run_suite_cli(
                cases,
                suite_name=args.name,
                min_accuracy=args.min_accuracy,
                ci_mode=args.ci,
            )
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
