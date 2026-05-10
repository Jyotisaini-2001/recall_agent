import nbformat

from skillforge.models import FailurePacket, DiagnosisResult, Skill
from skillforge import notebook


def _adapt_template(template: str, cell_source: str, traceback: str) -> str:
    """Ask Claude to fill in correct variable names from the cell source."""
    from skillforge.llm import call

    prompt = f"""You are adapting a generic fix template to match specific code.

FAILING CELL SOURCE:
{cell_source}

ERROR:
{traceback}

GENERIC FIX TEMPLATE:
{template}

Your job:
1. Rewrite the fix template replacing any placeholder variable names
   (like new_row, X, df, y) with the actual variable names from the failing cell source.
2. IMPORTANT: The fix cell will be inserted directly after the failing cell in a
   Jupyter notebook. If the failing cell raised an exception, its variable assignments
   may NOT be in scope. Therefore, if the fix code references variables that are
   defined only inside the failing cell, you MUST re-initialize those variables
   at the top of the fix cell (copy-paste the minimal setup lines needed).
3. Keep the fix logic the same — only update variable names and add necessary setup.

Respond ONLY with valid JSON:
{{"fix_code": "the adapted fix code here"}}"""

    try:
        result, _, _ = call(prompt)
        return result.get("fix_code", template)
    except Exception:
        return template


def _ask_user(fix_code: str, explanation: str, confidence: float) -> bool:
    print("\n" + "="*60)
    print(f"SkillForge proposed fix  (confidence: {confidence:.0%})")
    print("="*60)
    print(explanation)
    print("\nFix code:")
    print("-"*40)
    print(fix_code)
    print("-"*40)
    answer = input("Apply this fix? [Y/n]: ").strip().lower()
    return answer in ("", "y", "yes")


def apply_from_skill(packet: FailurePacket, skill: Skill) -> bool:
    """FAST PATH — match skill, adapt template to actual variable names, apply."""
    print(f"\n[FAST] Skill match: {skill.name}  (confidence: {skill.confidence:.0%})")

    # Adapt generic template to actual variable names in this cell
    fix_code = _adapt_template(skill.fix_template, packet.cell_source, packet.traceback)

    if skill.confidence >= 0.95:
        approved = True
    else:
        approved = _ask_user(fix_code, skill.description, skill.confidence)

    if not approved:
        print("[FAST] Skipped by user.")
        return False

    nb = notebook.read(packet.notebook_path)
    notebook.insert_fix_cell(nb, packet.cell_idx, fix_code, skill_name=skill.name)
    notebook.write(nb, packet.notebook_path)

    print(f"[FAST] Fix inserted at cell {packet.cell_idx + 1}")
    return True


def apply_from_diagnosis(packet: FailurePacket, result: DiagnosisResult) -> bool:
    """SLOW PATH — apply an LLM-generated fix."""
    print(f"\n[SLOW] LLM diagnosis via {result.provider}  (confidence: {result.confidence:.0%}, tokens: {result.tokens_used})")

    if result.confidence < 0.70:
        print("[SLOW] Confidence too low — skipping auto-fix.")
        print(f"Diagnosis: {result.diagnosis}")
        return False

    if result.confidence >= 0.95:
        approved = True
    else:
        approved = _ask_user(result.fix_code, result.explanation, result.confidence)

    if not approved:
        print("[SLOW] Skipped by user.")
        return False

    nb = notebook.read(packet.notebook_path)
    notebook.insert_fix_cell(nb, packet.cell_idx, result.fix_code)
    notebook.write(nb, packet.notebook_path)

    print(f"[SLOW] Fix inserted at cell {packet.cell_idx + 1}")
    return True
