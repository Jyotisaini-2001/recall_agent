# SkillForge

> **Procedural memory for AI agents.** Every bug your team fixes becomes a permanent capability — and tomorrow's tokens cost a fraction of today's.

Built for the **Paytm × 100xdevs Agentic AI Hackathon**, May 2026.

---

## The pitch in one breath

Companies are firing engineers to "save costs" while burning millions on AI tokens that re-solve the same bugs over and over. AI agents have **conversation memory**. They have **factual memory**. They don't have **procedural memory** — the structured "if you see X, do Y" patterns that senior engineers build over a career.

**SkillForge gives agents the missing memory.** First fix is normal cost. Every subsequent fix of the same class is ~50× cheaper, because the fix has been distilled into a reusable skill.

---

## What it actually does

SkillForge is a local agent that:

1. **Watches** your `.ipynb` notebook (the demo medium — the engine generalizes to any code-execution surface).
2. **Catches** cell errors, captures the traceback + cell source + recent context.
3. **Retrieves** matching skills from a local skill library via embedding similarity. **Fast path**: ~80 tokens, ~200ms.
4. **Diagnoses** with an LLM if no skill matches. **Slow path**: ~3000 tokens, ~8s.
5. **Distills** every successful fix into a portable Claude Skill (YAML + Markdown), saved to `skills/`. Next time the same class of bug appears, retrieval beats reasoning.
6. **Applies** the fix by inserting a corrected cell directly below the failing one.

Architecture, demo arc, and component contracts in [ARCHITECTURE.md](ARCHITECTURE.md). Full V1→V3 plan in [ROADMAP.md](ROADMAP.md). Day-of build plan in [TODO.md](TODO.md). Pitch in [PITCH.md](PITCH.md).

---

## The 30-second demo arc

```
1. Open demo.ipynb. Run All. Cell 4 errors with pandas dtype mismatch (object column in arithmetic).
2. SkillForge: SLOW PATH. ~8s. Cell 5 inserted, green. Skill written to skills/pandas-dtype-mismatch.md.
   Dashboard: tokens_spent: 3,012   library: 1 skill
3. Re-run a similar pandas cell with the same bug class on a different column.
   SkillForge: FAST PATH. ~200ms. Cached skill applied. ~80 tokens.
   Dashboard: tokens_spent: 3,094  tokens_saved: 2,920  cache_hit: 50%  library: 1 skill
4. Trigger a NEW class of bug (e.g. ModuleNotFoundError for a missing package).
   SLOW PATH again. New skill distilled (pip-install fix). Library: 2 skills.
5. Repeat with a different missing package.
   FAST PATH. Library: 2 skills. Cache hit: 66%. Dashboard ticks.
6. Drop the contents of skills/ into a separate Claude Code project's .claude/skills/.
   Claude itself can now use them. Same skill, different agent.
```

The "wow" is the **dashboard counter** ticking up `tokens_saved` while `library` grows. By demo end: cache hit rate >50%, 3+ skills, several thousand tokens saved.

---

## Why now

LinkedIn this month is full of two posts. Post A: "We laid off 30% of engineering to fund AI tooling." Post B: "Our Claude bill is up 200% this quarter." Read in sequence, those two posts describe the same company.

The unspoken assumption is that AI assistance has a **flat per-token cost** — every problem costs the same to solve, forever. That's only true if the AI is amnesiac. If agents accumulated institutional knowledge the way senior engineers do, marginal cost would trend toward zero. SkillForge is a concrete step toward that future, demoable in 7 hours.

---

## Stack

| Layer | V1 (hackathon) | V2 (post-hackathon) |
|---|---|---|
| Notebook surgery | `nbformat` + `nbclient` | unchanged |
| Reasoning LLM | Minimax (paid, primary) → Gemini (free fallback) → Claude (gold) | + [llm-council](https://github.com/karpathy/llm-council) consensus voting |
| Embeddings | `sentence-transformers` local | + [PageIndex](https://github.com/VectifyAI/PageIndex) for indexed retrieval |
| Skill store | folder of `.md` with YAML frontmatter | + [graphify](https://github.com/safishamsi/graphify) for skill relationships |
| Approval gate | confidence threshold + `input()` | [HumanLayer](https://github.com/humanlayer/humanlayer) workflows |
| External interface | **CLI only** (`skillforge run/watch/skills/stats`) | MCP server (any agent can use) |
| Codebase context | none — notebook + 2 prior cells is enough | AST extraction (primary) + [graphify](https://github.com/safishamsi/graphify) + [repomix](https://github.com/yamadashy/repomix) fallback |

Provider rationale: we explicitly use cheap/free models because **the demo IS the cost story**. SOTA models would make us faster but the point is that the skill cache means we don't need them.

See [ROADMAP.md](ROADMAP.md) for the V1.5/V2/V3 evolution.

---

## Quick start (placeholder — wired up day-of)

```bash
# 1. Clone and enter
git clone <repo-url> && cd skillforge

# 2. Install
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. Configure
cp .env.example .env  # add your Minimax/Gemini/Anthropic keys

# 4. Run
python -m skillforge run demo.ipynb
# OR launch the MCP server
python -m skillforge mcp
```

---

## Repo layout (planning)

```
.
├── README.md           # this file
├── PITCH.md            # judges-facing pitch (slide-format)
├── ARCHITECTURE.md     # system design deep-dive
├── ROADMAP.md          # V1 → V3 evolution plan
├── TODO.md             # hour-by-hour hackathon execution
├── architecture.mmd    # mermaid diagrams
├── .env.example        # API key template
├── requirements.txt    # Python deps
└── skillforge/         # (populated day-of) the actual code
    ├── notebook.py     # ipynb mutation
    ├── watcher.py      # error capture
    ├── retriever.py    # skill matching
    ├── diagnoser.py    # LLM reasoning
    ├── distiller.py    # skill creation
    └── mcp_server.py   # external interface
```

---

## Status

| | |
|---|---|
| Phase | Pre-hackathon planning |
| Built by | [Allmight-456](https://github.com/Allmight-456) + 0–1 teammate |
| License | TBD (likely MIT) |
| Hackathon | Paytm × 100xdevs Agentic AI, May 2026 |

---

## Acknowledgments

This project is essentially "what would happen if we wired together the best ideas in [Allmight-456's GitHub stars](https://github.com/Allmight-456?tab=stars)." Specific debts:

- **DreamOps** (Warpspeed 2025 winner) for the confidence-gated incident-response loop pattern
- **Jupyter AI / Datalayer Jupyter MCP** for the prior art that made it clear what was missing (procedural memory)
- **Anthropic** for the MCP standard and Claude Skills format we ship into

Built in 7 hours. Dreamed for years.
