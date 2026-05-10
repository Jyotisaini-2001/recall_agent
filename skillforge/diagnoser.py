from skillforge.models import FailurePacket, DiagnosisResult
from skillforge.llm import call


PROMPT_TEMPLATE = """You are an expert Python data science debugger.

A Jupyter notebook cell failed with the following error:

TRACEBACK:
{traceback}

FAILING CELL SOURCE:
{cell_source}

PRIOR CELLS (context):
{prior_cells}

Your job:
1. Diagnose why this error happened (1-2 sentences)
2. Write a Python code fix that can be inserted as the next cell to resolve the error
3. Give a short explanation of the fix
4. Rate your confidence (0.0 to 1.0)

Respond ONLY with valid JSON in this exact format:
{{
  "diagnosis": "why the error happened",
  "fix_code": "python code to fix the issue",
  "explanation": "short explanation of the fix",
  "confidence": 0.85
}}"""


def diagnose(packet: FailurePacket) -> DiagnosisResult:
    prior = "\n---\n".join(packet.prior_cells) if packet.prior_cells else "none"

    prompt = PROMPT_TEMPLATE.format(
        traceback=packet.traceback,
        cell_source=packet.cell_source,
        prior_cells=prior,
    )

    result, tokens, provider = call(prompt)

    return DiagnosisResult(
        diagnosis=result.get("diagnosis", ""),
        fix_code=result.get("fix_code", ""),
        explanation=result.get("explanation", ""),
        confidence=float(result.get("confidence", 0.0)),
        provider=provider,
        tokens_used=tokens,
    )
