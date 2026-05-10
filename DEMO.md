# SkillForge — Live Demo Guide

## How it works (3 steps)

```
1. Run SkillForge on a notebook with errors
2. It scans all cells, fixes each error, saves fix to skills/*.md
3. Next time same error appears → instant fix from skill file (no LLM needed)
```

---

## The two paths

### FAST PATH — error already in skill library
```
Notebook error → router reads skills/*.md → keyword match found
→ fix inserted in ~200ms → 0 tokens spent → tokens saved counter goes up
```

### SLOW PATH — new error, never seen before
```
Notebook error → no skill match → Claude diagnoses it
→ fix inserted in ~6s → fix distilled into new skills/*.md
→ next time same error = FAST PATH
```

---

## Step-by-step demo

### Step 1 — First run (mix of FAST + SLOW)

```bash
# Create the notebook with errors
python3 make_test_notebook.py

# Run SkillForge
python3 -m skillforge run test_errors.ipynb
```

**What you see in terminal:**
```
[FAST] pandas-keyerror       — 200ms  | ~2,940 tokens saved   ← from skill file
[FAST] nameError-import      — 190ms  | ~2,940 tokens saved   ← from skill file
[SLOW] claude-local          — 6.2s   | 847 tokens used       ← new error, Claude diagnoses
[NEW SKILL] type-error-string-column added to library          ← saved for next time
[SLOW] claude-local          — 5.8s   | 912 tokens used       ← another new error
[NEW SKILL] index-out-of-range added to library
```

**Dashboard shows:**
```
errors processed    7
fast path (cached)  5
slow path (llm)     2
cache hit rate      71%
tokens spent        1,759
tokens saved        14,700
est. cost saved     ~$0.029
skills in library   2
```

**Open Jupyter → Kernel → Restart & Run All**
→ Fix cells are inserted after each error, notebook runs cleaner

---

### Step 2 — Second run (same notebook, all FAST now)

```bash
python3 make_test_notebook.py   # reset to clean state
python3 -m skillforge run test_errors.ipynb
```

**What you see:**
```
[FAST] pandas-keyerror              — 180ms   ← skill file
[FAST] type-error-string-column     — 160ms   ← NEW: learned from Step 1
[FAST] sklearn-nan-input            — 200ms   ← skill file
[FAST] nameError-import-missing     — 190ms   ← skill file
[FAST] index-out-of-range           — 155ms   ← NEW: learned from Step 1
[FAST] sklearn-string-to-float      — 170ms   ← skill file
[FAST] pandas-append-deprecated     — 5ms     ← skill file
```

**Dashboard shows:**
```
errors processed    7
fast path (cached)  7          ← 100% cache hit
slow path (llm)     0          ← zero LLM calls
cache hit rate      100%
tokens spent        0          ← nothing spent
tokens saved        20,580     ← all from skill library
est. cost saved     ~$0.041
skills in library   2
```

**This is the money moment** — same 7 errors, 0 tokens, instant fixes.

---

### Step 3 — New notebook, new errors (SLOW → FAST cycle repeats)

```bash
python3 -m skillforge run your_new_notebook.ipynb
```

- Errors matching existing skills → FAST PATH instantly
- New errors → SLOW PATH → Claude fixes → new skill saved
- Run again → all FAST

---

## Skill file example

After SLOW PATH runs, a new file appears in `skills/`:

```
skills/
├── pandas-keyerror.md          ← pre-baked
├── nameError-import-missing.md ← pre-baked
├── sklearn-nan-input.md        ← pre-baked
├── type-error-string-column.md ← learned in Step 1
└── index-out-of-range.md       ← learned in Step 1
```

Each file looks like:
```markdown
---
name: type-error-string-column
description: Fix TypeError when multiplying string column with numeric
keywords: ["TypeError: can't multiply sequence"]
confidence: 0.91
---

# Diagnosis
The column contains string values. Must convert to float first.

# Fix template
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df['total'] = df['price'] * df['units']

# Verification
Check df.dtypes — price should be float64
```

---

## Key commands

| Action | Command |
|---|---|
| Reset demo notebook | `python3 reset_demo.py` |
| Reset test notebook | `python3 make_test_notebook.py` |
| Run SkillForge | `python3 -m skillforge run <notebook.ipynb>` |
| See all skills | `ls skills/` |
| Run on your notebook | `python3 -m skillforge run your_notebook.ipynb` |

---

## The pitch in one line

> First fix costs tokens. Every repeat is free. Library grows with every session.
