import os
import re
from datetime import date

from skillforge.models import FailurePacket, DiagnosisResult
from skillforge.llm import call


PROMPT_TEMPLATE = """You are an expert at distilling Python debugging fixes into reusable skill templates.

A notebook error was fixed. Here are the details:

ORIGINAL ERROR TRACEBACK:
{traceback}

FAILING CELL SOURCE:
{cell_source}

FIX THAT WORKED:
{fix_code}

DIAGNOSIS:
{diagnosis}

Your job: distill this into a reusable skill that can fix the same CLASS of error in future notebooks.

Respond ONLY with valid JSON in this exact format:
{{
  "name": "kebab-case-skill-name",
  "description": "one line description of what this skill fixes",
  "keywords": ["keyword1", "keyword2"],
  "fix_template": "the generalized fix code with {{PLACEHOLDER}} for variable parts",
  "diagnosis": "why this class of error happens (1-2 sentences)",
  "verification": "how to verify the fix worked"
}}"""


def _slugify(name: str) -> str:
    name = name.lower().strip()
    name = re.sub(r"[^a-z0-9-]", "-", name)
    name = re.sub(r"-+", "-", name)
    return name.strip("-")


def distill(packet: FailurePacket, result: DiagnosisResult, skills_dir: str = "./skills") -> str:
    prompt = PROMPT_TEMPLATE.format(
        traceback=packet.traceback,
        cell_source=packet.cell_source,
        fix_code=result.fix_code,
        diagnosis=result.diagnosis,
    )

    data, _, _ = call(prompt)

    # Use exact exception class name as primary keyword — most reliable for matching
    exc_match = re.search(r"(\w+Error|\w+Exception|\w+Warning)", packet.traceback)
    exact_keywords = [exc_match.group(1)] if exc_match else []
    llm_keywords = data.get("keywords", [])
    all_keywords = list(dict.fromkeys(exact_keywords + llm_keywords))  # deduplicate, exact first

    slug = _slugify(data.get("name", "unknown-skill"))
    os.makedirs(skills_dir, exist_ok=True)
    file_path = os.path.join(skills_dir, f"{slug}.md")

    content = f"""---
name: {slug}
description: {data.get('description', '')}
keywords: {all_keywords}
confidence: {result.confidence}
times_used: 0
created_at: {date.today().isoformat()}
---

# Diagnosis
{data.get('diagnosis', '')}

# Fix template
```python
{data.get('fix_template', result.fix_code)}
```

# Verification
{data.get('verification', 'Re-run the failing cell and confirm no error.')}
"""

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return file_path
