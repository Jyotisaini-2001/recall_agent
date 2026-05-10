import json
import os
from dataclasses import dataclass, field
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich import box

console = Console()

# Path to the JSON file the web dashboard polls
_STATS_JSON = os.path.join(os.path.dirname(os.path.dirname(__file__)), "stats.json")


@dataclass
class Stats:
    tokens_spent: int = 0
    tokens_saved: int = 0
    fast_count: int = 0
    slow_count: int = 0
    skills_in_library: int = 0
    total_latency_ms: float = 0
    log: list[str] = field(default_factory=list)


_stats = Stats()


def record_fast(skill_name: str, latency_ms: float):
    _stats.fast_count += 1
    _stats.tokens_saved += 2940
    _stats.total_latency_ms += latency_ms
    _stats.log.append(f"[green][FAST][/green] {skill_name} — {latency_ms:.0f}ms  |  ~2,940 tokens saved")
    _render()


def record_slow(provider: str, tokens: int, latency_s: float):
    _stats.slow_count += 1
    _stats.tokens_spent += tokens
    _stats.total_latency_ms += latency_s * 1000
    _stats.log.append(f"[yellow][SLOW][/yellow] {provider} — {latency_s:.1f}s  |  {tokens} tokens used")
    _render()


def record_skill_added(skill_name: str):
    _stats.skills_in_library += 1
    _stats.log.append(f"[cyan][NEW SKILL][/cyan] {skill_name} added to library")
    _render()


def _cache_hit_rate() -> str:
    total = _stats.fast_count + _stats.slow_count
    if total == 0:
        return "—"
    return f"{_stats.fast_count / total:.0%}"


def _cost_saved() -> str:
    # rough estimate: $0.002 per 1K tokens (GPT-3.5 rate)
    saved_usd = (_stats.tokens_saved / 1000) * 0.002
    return f"~${saved_usd:.3f}"


def _write_json():
    """Write current stats to stats.json for the web dashboard to poll."""
    import re
    # Only strip Rich color/style markup — preserve [FAST], [SLOW], [NEW SKILL] markers
    _RICH_TAG = re.compile(
        r'\[/?(?:bold|dim|green|red|yellow|cyan|blue|white|magenta|italic|underline|blink|reverse)[^\]]*\]'
    )
    clean_log = [_RICH_TAG.sub('', entry).strip() for entry in _stats.log]
    data = {
        "errors_processed": _stats.fast_count + _stats.slow_count,
        "fast_count":       _stats.fast_count,
        "slow_count":       _stats.slow_count,
        "tokens_spent":     _stats.tokens_spent,
        "tokens_saved":     _stats.tokens_saved,
        "skills_in_library": _stats.skills_in_library,
        "log":              clean_log,
    }
    try:
        with open(_STATS_JSON, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass  # Never crash the main flow


def _render():
    console.clear()

    total = _stats.fast_count + _stats.slow_count

    # --- metrics table ---
    metrics = Table(box=box.SIMPLE_HEAVY, show_header=False, padding=(0, 2))
    metrics.add_column(style="dim", width=22)
    metrics.add_column(style="bold white", width=16)

    metrics.add_row("errors processed",  str(total))
    metrics.add_row("fast path (cached)", f"[green]{_stats.fast_count}[/green]")
    metrics.add_row("slow path (llm)",    f"[yellow]{_stats.slow_count}[/yellow]")
    metrics.add_row("cache hit rate",     f"[bold green]{_cache_hit_rate()}[/bold green]")
    metrics.add_row("─" * 20,            "─" * 14)
    metrics.add_row("tokens spent",       f"[red]{_stats.tokens_spent:,}[/red]")
    metrics.add_row("tokens saved",       f"[green]{_stats.tokens_saved:,}[/green]")
    metrics.add_row("est. cost saved",    f"[green]{_cost_saved()}[/green]")
    metrics.add_row("─" * 20,            "─" * 14)
    metrics.add_row("skills in library",  f"[cyan]{_stats.skills_in_library}[/cyan]")

    log_text = "\n".join(_stats.log[-8:]) if _stats.log else "[dim]waiting for errors...[/dim]"

    console.print(Panel(
        metrics,
        title="[bold blue]SkillForge — Procedural Memory for AI Agents[/bold blue]",
        border_style="blue",
        padding=(1, 2),
    ))
    console.print(Panel(
        log_text,
        title="[bold]live activity[/bold]",
        border_style="dim",
        padding=(0, 2),
    ))

    # Also export for web dashboard
    _write_json()

