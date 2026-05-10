import sys
import time

from skillforge import watcher, router, diagnoser, applier, distiller, dashboard, notebook


def run(notebook_path: str):
    print(f"\nSkillForge — watching {notebook_path}\n")

    nb = notebook.read(notebook_path)
    removed = notebook.strip_fix_cells(nb)
    if removed:
        notebook.write(nb, notebook_path)
        print(f"Cleaned {removed} previous fix cell(s) from notebook.\n")

    packets = watcher.run_and_capture(notebook_path)

    if not packets:
        print("No errors found. Notebook ran clean.")
        return

    print(f"Found {len(packets)} error(s). Processing...\n")

    for packet in packets:
        print(f"--- Cell {packet.cell_idx} ---")
        print(f"Error: {packet.traceback.splitlines()[0]}\n")

        skill = router.match(packet)

        if skill:
            start = time.time()
            applied = applier.apply_from_skill(packet, skill)
            latency_ms = (time.time() - start) * 1000

            if applied:
                dashboard.record_fast(skill.name, latency_ms)
        else:
            print("[SLOW] No skill match — calling LLM...")
            start = time.time()
            result = diagnoser.diagnose(packet)
            latency_s = time.time() - start

            applied = applier.apply_from_diagnosis(packet, result)
            dashboard.record_slow(result.provider, result.tokens_used, latency_s)

            if applied:
                skill_path = distiller.distill(packet, result)
                print(f"[DISTILL] New skill saved: {skill_path}")
                dashboard.record_skill_added(skill_path.split("/")[-1].replace(".md", ""))

    print("\nDone. Reopen the notebook to see inserted fix cells.")


def main():
    if len(sys.argv) < 3 or sys.argv[1] != "run":
        print("Usage: python -m skillforge run <notebook.ipynb>")
        sys.exit(1)

    run(sys.argv[2])


if __name__ == "__main__":
    main()
