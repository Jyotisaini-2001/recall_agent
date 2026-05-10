# BUILD_PLAN.md — SkillForge Development Plan

Focused only on what to build, in what order, and how the system works.
Demo and pitch live in README/PITCH. This is the engineering doc.

---

## What we are building (scoped, final)

A Python notebook self-healing agent that:
1. Watches a `.ipynb` notebook run
2. Catches cell errors
3. Matches the error against a pre-baked skill library (keyword match — FAST)
4. Falls back to an LLM for unknown errors (SLOW), then saves that as a new skill
5. Inserts the fix as the next cell and reruns it

**Scope:** Python notebooks. Data science errors only. No generalization.

**Not building:** web UI, multi-language support, cloud sync, API server (MCP is stretch only).

---

## Where the "agentic" part lives (30–40%)

This is NOT a fully autonomous system. Here is exactly what the agent decides vs what is hardcoded:

| Component | Agentic? | What it does |
|---|---|---|
| Watcher | No | Deterministic — catches error, builds FailurePacket |
| Router | Partial | Keyword match score decides FAST vs SLOW vs GIVE UP |
| Diagnoser | YES | LLM reasons about the fix. Produces `{fix_code, explanation, confidence}` |
| Approval gate | Partial | Agent decides auto-apply (conf > 0.9) or ask user (0.7–0.9) or decline (< 0.7) |
| Distiller | YES | LLM converts the successful fix into a reusable skill file |
| Applier | No | Deterministic — inserts cell, reruns it |

The LLM is only called when keyword match fails. Everything else is logic.
The agent never auto-applies below confidence 0.7 — human is always the last gate on low-confidence fixes.

---

## The 5 pre-baked skills (write these before hackathon day)

These cover ~80% of what a data scientist hits in a notebook session.

### Skill 1: pandas-keyerror
```
Triggers:  "KeyError" in traceback AND ("DataFrame" OR "pandas" OR "df[" in cell source)
Fix:       print df.columns.tolist() + rename or correct column access
```

### Skill 2: pandas-append-deprecated
```
Triggers:  "has no attribute 'append'" in traceback
Fix:       replace df.append(...) with pd.concat([df, new_row], ignore_index=True)
```

### Skill 3: sklearn-string-to-float
```
Triggers:  "could not convert string to float" in traceback
Fix:       identify non-numeric columns, apply LabelEncoder or pd.to_numeric(errors='coerce')
```

### Skill 4: nameError-import-missing
```
Triggers:  "NameError: name" in traceback
Fix:       extract the missing name, map to known import (pd→pandas, np→numpy, plt→matplotlib, etc.)
```

### Skill 5: sklearn-nan-input
```
Triggers:  "Input contains NaN" in traceback OR "Input X contains NaN" in traceback
Fix:       add SimpleImputer before the model, or df.dropna() before train/test split
```

Each skill file schema:
```yaml
---
name: pandas-keyerror
description: one line
triggers:
  keywords: ["KeyError"]          # must ALL appear in traceback
  cell_hints: ["df[", "pandas"]   # at least ONE must appear in cell source
confidence: 0.9                   # pre-set for pre-baked skills
times_used: 0
---

# Why this happens
...

# Fix template
```python
# {placeholders} replaced by regex extraction from traceback
```

# Verification
...
```

---

## System flow (exact)

```
notebook cell errors
        ↓
   Watcher fires
   builds FailurePacket {traceback, cell_source, prior_cells, cell_idx}
        ↓
   Router: keyword scan all 5 skills
        ↓
   ┌── MATCH found (all keywords hit) ──────────────────────────────┐
   │   confidence = skill.confidence (pre-set, e.g. 0.9)            │
   │   fill template placeholders via regex from traceback           │
   │   → Applier                                                     │
   └─────────────────────────────────────────────────────────────────┘
        ↓ no match
   Diagnoser: call LLM with FailurePacket
   returns {fix_code, explanation, confidence: 0.0–1.0}
        ↓
   ┌── confidence > 0.9 ─→ auto-apply (log "AUTO-APPLIED")          │
   │   confidence 0.7–0.9 → show fix + ask user Y/n                 │
   │   confidence < 0.7   → print "I don't know" + raw traceback    │
   └─────────────────────────────────────────────────────────────────┘
        ↓ (on successful fix)
   Distiller: call LLM to write a new skill file → skills/{slug}.md
        ↓
   Applier: insert fix as next cell, re-run it
        ↓
   Dashboard: update counters
```

---

## Phase 1 — Hackathon build (6 hours)

Keyword match only. No embeddings. LLM fallback for unknowns. Distiller writes new skills.

### File build order (strict — each file depends on the one above)

```
Hour 0–1   skillforge/notebook.py
           skillforge/watcher.py (capture only, no fix yet)

Hour 1–2   skills/*.md  (write all 5 pre-baked skill files)
           skillforge/router.py (keyword matcher)

Hour 2–3   skillforge/llm.py (provider wrapper: Minimax → Gemini → Anthropic)
           skillforge/diagnoser.py (LLM call + JSON parse)

Hour 3–4   skillforge/distiller.py (new skill from fix)
           skillforge/applier.py (cell insert + rerun)
           Wire everything into skillforge/__main__.py

Hour 4–5   skillforge/dashboard.py (rich terminal panel)
           demo.ipynb (4 cells with staged bugs)
           End-to-end test: run demo.ipynb, confirm FAST + SLOW paths both work

Hour 5–6   Edge cases, approval gate, error handling
           Screencast + submission
```

---

## Phase 2 — Post-hackathon upgrade (semantic search)

After hackathon, upgrade Router with embedding-based matching:
- Use `sentence-transformers` (`all-MiniLM-L6-v2`, 80MB local)
- Embed each skill's keywords + description at load time → `.npy` sidecar
- On error: embed traceback → cosine similarity vs all skills
- Threshold: > 0.85 → FAST, 0.70–0.85 → LLM-validate then apply, < 0.70 → SLOW
- This unlocks: matching errors the keyword scanner would miss (paraphrased tracebacks, stack depth variations)

Router becomes: `keyword match` → `embedding match` → `LLM`

No other changes needed. The skill file schema is already compatible.

---

## Module contracts (what each file must expose)

```python
# notebook.py
read(path: str) -> NotebookNode
find_error_cells(nb: NotebookNode) -> list[tuple[int, dict]]  # (idx, cell)
insert_cell(nb: NotebookNode, after_idx: int, code: str) -> int
write(nb: NotebookNode, path: str) -> None

# router.py
match(traceback: str, cell_source: str) -> Skill | None

# diagnoser.py
diagnose(traceback: str, cell_source: str, prior_cells: list[str]) -> DiagnosisResult
# DiagnosisResult: fix_code, explanation, confidence

# distiller.py
distill(traceback: str, fix_code: str, explanation: str) -> str  # returns skill file path

# applier.py
apply(nb_path: str, after_idx: int, fix_code: str) -> bool  # True = rerun succeeded

# dashboard.py
update(event: str, tokens_used: int, tokens_saved: int, path: str) -> None
```

---

## Checkpoints

| Time | Must be true |
|---|---|
| T+1h | `notebook.py` round-trips a notebook. Watcher catches an error and prints the traceback. |
| T+2h | Router matches `KeyError` traceback to `pandas-keyerror` skill. Returns template. |
| T+3h | Diagnoser returns valid JSON for an unknown error. Applier inserts and reruns a cell. |
| T+4h | Full loop: error → router → fix applied → dashboard updated. Both FAST and SLOW paths. |
| T+5h | `demo.ipynb` runs end-to-end cleanly. Distiller writes a new skill file. |
| T+6h | Submitted. |

---

## What to cut if behind

1. Distiller (mention it in pitch, skip the code — dashboard still works)
2. Approval gate (auto-apply everything, set confidence threshold to 0)
3. Provider fallback chain (hardcode one LLM)
4. Dashboard polish (bare print statements are fine)

**Never cut:** Router (keyword match) + Diagnoser + Applier. These three are the whole demo.
