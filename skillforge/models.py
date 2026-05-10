from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class FailurePacket:
    cell_idx: int
    traceback: str
    cell_source: str
    prior_cells: list[str]
    notebook_path: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class DiagnosisResult:
    diagnosis: str
    fix_code: str
    explanation: str
    confidence: float
    provider: str
    tokens_used: int


@dataclass
class Skill:
    name: str
    description: str
    keywords: list[str]
    cell_hints: list[str]
    fix_template: str
    confidence: float
    file_path: str
