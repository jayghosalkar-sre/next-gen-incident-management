#!/usr/bin/env python3
"""
Next-Gen Incident Management
----------------------------
Matches EMR/Spark and Airflow task failure logs against a JSON knowledge base
of previously seen issues and recommends the action that was taken before.

Usage:
    # Analyze all sample logs (EMR + Airflow)
    python main.py

    # Analyze a specific local log file
    python main.py --log sample_logs/airflow_task_timeout.log

    # Use a custom known issues file
    python main.py --known-issues my_issues.json
"""

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.known_issues import KnownIssuesStore
from src.log_reader import read_local_log, list_sample_logs
from src.matcher import analyze_failure

console = Console()


def print_decision(log_name: str, decision: dict) -> None:
    """Pretty print the decision result."""
    status = decision["status"]
    color = "green" if status == "known_issue" else "yellow"

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Field", style="bold cyan")
    table.add_column("Value")

    table.add_row("Status", f"[{color}]{status}[/{color}]")
    table.add_row("Issue ID", str(decision.get("issue_id") or "—"))
    table.add_row("Category", decision.get("category", "—"))
    table.add_row("Specialist Needed", decision.get("specialist_needed", "—"))
    table.add_row("Can Auto Retry", str(decision.get("can_auto_retry", False)))
    table.add_row("Urgency (1-5)", str(decision.get("urgency", "—")))
    table.add_row("Match Score", str(decision.get("match_score", 0.0)))
    table.add_row("Recommended Action", decision.get("action_taken", "—"))

    console.print(Panel(table, title=f"[bold]{log_name}[/bold]", border_style=color))
    console.print()


def main():
    parser = argparse.ArgumentParser(
        description="Next-Gen Incident Management — match failure logs against known issues"
    )
    parser.add_argument(
        "--log",
        type=str,
        help="Path to a specific log file to analyze",
    )
    parser.add_argument(
        "--known-issues",
        type=str,
        default="known_issues.json",
        help="Path to known issues JSON file (default: known_issues.json)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.35,
        help="Minimum match score threshold (default: 0.35)",
    )
    parser.add_argument(
        "--sample-dir",
        type=str,
        default="sample_logs",
        help="Directory containing sample log files",
    )
    args = parser.parse_args()

    console.print(
        Panel.fit(
            "[bold blue]Next-Gen Incident Management[/bold blue]\n"
            "Matches EMR/Spark and Airflow failure logs against known issues",
            border_style="blue",
        )
    )
    console.print()

    # Load knowledge base
    store = KnownIssuesStore(args.known_issues)

    if args.log:
        # Analyze a single log file
        try:
            content = read_local_log(args.log)
            decision = analyze_failure(content, store, threshold=args.threshold)
            print_decision(Path(args.log).name, decision)
        except Exception as e:
            console.print(f"[red]Error reading log: {e}[/red]")
            sys.exit(1)
    else:
        # Analyze all sample logs
        samples = list_sample_logs(args.sample_dir)
        if not samples:
            console.print(
                f"[yellow]No sample logs found in '{args.sample_dir}'. "
                "Use --log to specify a file.[/yellow]"
            )
            sys.exit(0)

        console.print(f"Found {len(samples)} sample log(s). Analyzing...\n")

        for item in samples:
            try:
                content = read_local_log(item["path"])
                decision = analyze_failure(content, store, threshold=args.threshold)
                print_decision(item["name"], decision)
            except Exception as e:
                console.print(f"[red]Error processing {item['name']}: {e}[/red]")


if __name__ == "__main__":
    main()
