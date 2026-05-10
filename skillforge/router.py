import os
import re
from typing import Optional

from skillforge.models import FailurePacket, Skill


SKILLS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "skills")


def _parse_frontmatter(text: str) -> dict:
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    fm = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip()
    return fm


def _parse_list(raw: str) -> list[str]:
    return [s.strip().strip('"').strip("'") for s in raw.strip("[]").split(",") if s.strip()]


def _extract_fix_template(text: str) -> str:
    match = re.search(r"# Fix template\s*```python\n(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else ""


def load_skills(skills_dir: str = SKILLS_DIR) -> list[Skill]:
    skills = []
    if not os.path.isdir(skills_dir):
        return skills
    for fname in os.listdir(skills_dir):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(skills_dir, fname)
        with open(path, encoding="utf-8") as f:
            content = f.read()
        fm = _parse_frontmatter(content)
        if not fm:
            continue
        skills.append(Skill(
            name=fm.get("name", fname.replace(".md", "")),
            description=fm.get("description", ""),
            keywords=_parse_list(fm.get("keywords", "[]")),
            cell_hints=_parse_list(fm.get("cell_hints", "[]")),
            fix_template=_extract_fix_template(content),
            confidence=float(fm.get("confidence", 0.8)),
            file_path=path,
        ))
    return skills


def match(packet: FailurePacket) -> Optional[Skill]:
    skills = load_skills()
    traceback_lower = packet.traceback.lower()
    source_lower = packet.cell_source.lower()

    for skill in skills:
        # Match if ANY keyword found in traceback (first keyword is always exact exception type)
        keywords_match = any(kw.lower() in traceback_lower for kw in skill.keywords)
        if not keywords_match:
            continue

        if skill.cell_hints:
            hints_match = any(hint.lower() in source_lower for hint in skill.cell_hints)
            if not hints_match:
                continue

        return skill

    return None
