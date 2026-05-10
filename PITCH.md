<!--
PITCH.md — judge-facing talking points for SkillForge.
Formatted as Marp / reveal-friendly slides. Each "## " is one slide.
The `---` between sections is the slide divider.

To render as actual slides:
  npm install -g @marp-team/marp-cli
  marp PITCH.md -o pitch.html

Or just read top-to-bottom — flows as a script.
-->

---
marp: true
theme: default
paginate: true
---

# SkillForge
### Procedural memory for AI agents

Paytm × 100xdevs Hackathon · May 2026
**Allmight-456** + team

---

## The opening line

> "On LinkedIn this month, two kinds of post are everywhere.
>
> One: 'We laid off 30% of engineering to fund AI.'
> Two: 'Our Claude bill is up 200% this quarter.'
>
> They're the same company.
> And the AI is solving the same bugs over and over.
>
> **SkillForge teaches AI to remember.**"

---

## The problem (30 seconds)

- Every Claude / Cursor / Copilot session is **amnesiac**
- Same `pandas dtype error`, same merge conflict, same flaky test — re-reasoned from scratch every time
- ~3,000 tokens per fix. ~8 seconds of latency. Forever.
- Senior engineers don't work that way. They build **playbooks**.
- Agents have conversation memory. Agents have factual memory. Agents **don't have procedural memory.**
- That's a missing capability. We're building it.

---

## The wedge

**We start with Jupyter notebooks** because the pain is visceral and the demo is one-glance obvious.

But the engine is general — anything that produces a stack trace + a code snippet plugs in. CI runs. Test failures. Dev server logs. On-call alerts.

The notebook is the demo. The skill cache is the product.

---

## Live demo: SLOW PATH

```
[Notebook] Cell 4 → TypeError: pandas dtype mismatch
[SkillForge] Watcher caught it
[SkillForge] Retriever: no skill match (best 0.42)
[SkillForge] Diagnoser: thinking... (3,012 tokens, 8.2s)
[SkillForge] Cell 5 inserted ✓
[SkillForge] Distiller: skills/pandas-dtype-mismatch.md saved

Dashboard
  tokens_spent: 3,012   library: 1   cache_hit: 0%
```

**This is what every other notebook agent does.** Same as Jupyter AI, same as Cursor.

---

## Live demo: the moment that wins

```
[Notebook] Cell 7 → similar dtype error (different column)
[SkillForge] Watcher caught it
[SkillForge] Retriever: skill match (confidence 0.92)
[SkillForge] Cell 8 inserted ✓ — 84 tokens, 197ms

Dashboard
  tokens_spent: 3,096   tokens_saved: 2,928   cache_hit: 50%   library: 1
```

**This is what nobody else does.** Same problem class, ~50× cheaper, near-instant.

The library grows. The cache hit rate climbs. Marginal cost trends toward zero.

---

## The math (the slide that closes the deal)

Conservative numbers, single developer:

```
Cache MISS:  3,000 tokens × $3/Mtok (Claude Sonnet) = $0.009 per fix
Cache HIT:      80 tokens × $3/Mtok                = $0.0002 per fix

Bugs hit per dev per day:        50
% repeat-class (after warmup):   80%

Per-dev daily savings:
  50 × 0.8 × ($0.009 − $0.0002) = $0.35/day per dev
```

For a 100-engineer org: **~$1,300/month** in token spend, recovered.

Now scale that to the full agentic-IDE world. The math compounds.

---

## What it's actually built on

Four agents in an A2A pattern:

| Agent | Role |
|---|---|
| **Watcher** | nbclient hook catches `CellExecutionError` |
| **Retriever** | embedding match against skill library |
| **Diagnoser** | LLM reasoning (only on cache miss) |
| **Distiller** | turns each fix into a portable Claude Skill |

Wrapped as an **MCP server** so Claude Code, Cursor, and any other agent can read from the same library.

---

## Why this is portable, not lock-in

Every skill we distill is a **standard Claude Code Skill file**.

```
skills/
├── pandas-dtype-mismatch.md
├── pandas-dtype-mismatch.md
└── flaky-async-test.md
```

Drop them into any other Claude Code project's `.claude/skills/` — Claude itself uses them, no SkillForge runtime needed.

We're not a moat. We're a **factory** for shareable agent capabilities.

---

## V1 (today, 7 hours)

✓ Notebook self-healing loop (SLOW path)
✓ Skill distillation
✓ Embedding-based skill retrieval (FAST path)
✓ Confidence-gated approval
✓ Live token-savings dashboard
✓ Demo notebook with three staged bugs
✓ Skills are valid Claude Code Skills (drop-in compatible)

---

## V1.5 (next month)

- Publish as a Claude Code Plugin: `claude plugin install skillforge`
- MCP server on PyPI
- Multi-target watchers: CI, pytest, dev server logs
- Open-source the skill library schema

---

## V2.0 (next quarter): self-improving memory

Replace folder + cosine-match with **graph-based skill knowledge**:

- **PageIndex** — indexed retrieval over the skill graph
- **graphify** — relationships between skills (skill A is a generalization of B, C, D)
- **llm-council** consensus — Sonnet proposes, Haiku reviews, Gemini tiebreaks
- Self-replay: agent re-tries old fixes against current skills, suggests better skills

The library doesn't just grow. It **learns**.

---

## V3.0 (vision): the marketplace

> **"npm for agent procedural memory."**

- Public skill marketplace
- Org-level token-savings dashboards (the enterprise wedge)
- A2A skill exchange — agents on different machines pull skills from each other
- Skills become a tradeable, versioned, citeable unit of agent capability

---

## What we're sitting on top of

Built explicitly on the agentic-AI infrastructure already shipped:

- **DreamOps** (Warpspeed 2025 winner) — confidence-gated incident response pattern
- **HumanLayer** — approval workflows for risky fixes
- **MCP** — the standard we ship into
- **Claude Skills** — the file format our distillations conform to
- **PageIndex / graphify** — the V2 retrieval substrate
- **llm-council** — the V2 consensus pattern

We're not reinventing. We're integrating, distilling, and shipping.

---

## The ask

Three things you can do right now:

1. **Try the demo** — open `demo.ipynb`, watch the cache build live.
2. **Try the skills** — drop our `skills/` folder into your own Claude Code project's `.claude/skills/`. Watch your agent get cheaper.
3. **Imagine the V3** — public skill exchange, team libraries, org-level savings dashboards.

The companies on LinkedIn don't have to choose between layoffs and AI bills. There's a third option: AI that learns.

---

## Thank you

**SkillForge**
[github.com/Allmight-456](https://github.com/Allmight-456)

*Built in 7 hours. Dreamed for years.*

---
