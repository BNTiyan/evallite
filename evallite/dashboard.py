"""Rich Terminal UI Dashboard for visualizing agent evaluation runs and argument diffs."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from evallite.models import SuiteSummary

console = Console()


def render_dashboard(summary: SuiteSummary) -> Panel:
    """Renders the full evaluation summary leaderboard and test result matrix."""
    title = Text("🎯 EVALLITE — Local-First Agent Evaluation Dashboard", style="bold cyan")

    # Metrics table
    score_color = "bold green" if summary.accuracy_pct >= 90 else "bold yellow" if summary.accuracy_pct >= 75 else "bold red"
    meta_table = Table(show_header=False, box=None, expand=True)
    meta_table.add_column("Key", style="bold white", width=22)
    meta_table.add_column("Value", style="bold cyan")

    meta_table.add_row("Suite Name", summary.suite_name)
    meta_table.add_row(
        "Accuracy Score",
        f"[{score_color}]{summary.passed_cases}/{summary.total_cases} ({summary.accuracy_pct:.1f}%)[/{score_color}]",
    )
    meta_table.add_row("Median Latency (p50)", f"[green]{summary.p50_latency_ms:.2f} ms[/green]")
    meta_table.add_row("Total Wall Time", f"{summary.total_duration_sec:.2f} sec")
    meta_table.add_row("Inference Cost", "[bold green]$0.00 (Zero-Cloud Local Execution)[/bold green]")

    # Detailed results table
    res_table = Table(
        title="🧪 Evaluation Case Matrix",
        header_style="bold blue",
        border_style="blue",
        expand=True,
    )
    res_table.add_column("Case ID", style="bold white", width=20)
    res_table.add_column("Status", width=12)
    res_table.add_column("Tool Invoked", style="bold cyan", width=20)
    res_table.add_column("Latency", justify="right", width=12)
    res_table.add_column("Diagnostic / Diff Summary", style="dim white")

    for res in summary.results:
        status_text = "[bold green]✓ PASS[/bold green]" if res.passed else "[bold red]✗ FAIL[/bold red]"
        tool_str = res.actual_tool or "[dim]none[/dim]"
        lat_str = f"{res.latency_ms:.1f}ms"

        if res.passed:
            diag = "[green]All assertions and schemas satisfied[/green]"
        else:
            diag = "; ".join(res.errors[:2])

        res_table.add_row(res.case_id, status_text, tool_str, lat_str, diag)

    # Combine into a single dashboard panel
    from rich.layout import Layout

    layout = Layout()
    layout.split_column(
        Layout(Panel(meta_table, title="[bold]Suite Scorecard[/bold]", border_style="cyan")),
        Layout(res_table),
    )

    border_color = "bright_green" if summary.accuracy_pct == 100 else "bright_yellow" if summary.accuracy_pct >= 80 else "red"
    return Panel(layout, title=title, border_style=border_color, padding=(1, 2))
