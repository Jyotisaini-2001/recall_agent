#!/usr/bin/env python3
"""
SkillForge Baseline Measurement
Runs the LLM on every error WITHOUT using the skill cache.
This gives a real, measured token cost to compare against SkillForge.

Usage:
    python3 baseline_run.py error_notebook.ipynb

Output:
    Writes baseline_tokens_spent and baseline_log to stats.json
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from skillforge import notebook, diagnoser, watcher


STATS_FILE = os.path.join(os.path.dirname(__file__), "stats.json")


def run_baseline(notebook_path: str):
    print(f"\n📊 SkillForge Baseline Measurement")
    print(f"   Notebook : {notebook_path}")
    print(f"   Mode     : NO skill cache — LLM called for every error\n")
    print("─" * 58)

    packets = watcher.run_and_capture(notebook_path)

    if not packets:
        print("No errors found in notebook.")
        return

    print(f"Found {len(packets)} error(s). Calling LLM for each...\n")

    total_tokens = 0
    baseline_log = []

    for i, packet in enumerate(packets, 1):
        error_line = packet.traceback.splitlines()[0] if packet.traceback else "Unknown"
        print(f"[{i}/{len(packets)}] {error_line}")

        result = diagnoser.diagnose(packet)
        total_tokens += result.tokens_used

        entry = (
            f"[BASELINE] {error_line[:50]} "
            f"— {result.tokens_used} tokens used  |  provider: {result.provider}"
        )
        baseline_log.append(entry)
        print(f"           ✓ {result.tokens_used} tokens  (confidence: {result.confidence:.0%})")

    print("\n" + "─" * 58)
    print(f"✅ Baseline complete")
    print(f"   Total tokens (no cache): {total_tokens:,}")
    print(f"   Errors measured        : {len(packets)}")
    print(f"   Avg per error          : {total_tokens // len(packets):,}")

    # Load existing stats and merge baseline data
    try:
        with open(STATS_FILE) as f:
            stats = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        stats = {}

    stats["baseline_tokens_spent"] = total_tokens
    stats["baseline_errors_count"] = len(packets)
    stats["baseline_avg_per_error"] = total_tokens // len(packets) if packets else 0
    stats["baseline_log"] = baseline_log

    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)

    print(f"\n   Saved to stats.json → dashboard will update automatically")
    print(f"\n💡 Now run SkillForge to see the comparison:")
    print(f"   python3 -m skillforge run {notebook_path}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 baseline_run.py <notebook.ipynb>")
        sys.exit(1)
    run_baseline(sys.argv[1])
