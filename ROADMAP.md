# SkillForge Roadmap

> **Procedural memory for AI agents.** First fix costs full tokens. Every repeat fix of the same class costs ~50x less because the skill is cached. AI gets cheaper as it learns.

---

## V1.0 — Hackathon Demo (7 hours)

**Context:** Paytm x Harkirat Singh (100xdevs) hackathon. Theme: agentic engineering (MCP, A2A, agent skills). 7-hour in-person build window. Demo medium: Jupyter notebooks. Team: 1-2 people.

**Core thesis to prove in demo:** distill each LLM-generated fix into a reusable skill so the second occurrence of the same bug class costs a cache hit, not another LLM call.

---

### Hour-by-Hour Plan

| Hour | Block | Deliverable | Risk Level | Owner (2-person split) |
|------|-------|-------------|------------|------------------------|
| 0–1 | Notebook mutation core | `notebook.py`: read/write `.ipynb`, locate error cell by index, insert fix cell at the correct position, preserve output metadata and kernel state | HIGH — get this wrong, nothing else works | Person A |
| 1–3 | Watcher + Diagnoser (Slow Path) | `nbclient` catches `CellExecutionError`, ships traceback + cell source + surrounding context to Minimax (primary) / Gemini (fallback), parses structured fix JSON, applies it. End-to-end demo: broken cell → green cell | MEDIUM — prompt engineering must return reliable structured output | Person A |
| 3–4 | Distiller | After fix succeeds, second LLM call distills fix into `skills/{name}.md` with YAML frontmatter. `sentence-transformers` computes and caches embedding locally | LOW | Person B |
| 4–5 | Retriever (Fast Path) | On new error, embed traceback, cosine-match against cached skill embeddings. `>0.80` → apply skill template directly (zero LLM call). `0.65–0.80` → quick LLM validation only. `<0.65` → slow path | MEDIUM — threshold tuning needed | Person B |
| 5–6 | Polish | `rich` terminal dashboard with live tokens-spent / tokens-saved / cache-hit-rate counters. HumanLayer or `input()` approval gate. Demo notebook with 3 staged bugs: one new, one repeat (cache hit), one different class | LOW | Both |
| 6–7 | Submit | Screencast recording, README quick-start, pitch deck (5 slides max), submission form | LOW | Both |

---

### Must-Have for Submission

These four items are non-negotiable. If time pressure forces cuts, cut everything else first.

- **[MUST]** End-to-end slow path working: broken notebook cell is caught, diagnosed by LLM, fix applied, cell turns green
- **[MUST]** At least one cached skill being applied via fast path: same bug class re-triggered, resolved without a new LLM call, terminal shows "CACHE HIT"
- **[MUST]** Terminal dashboard showing live token-savings number (even if approximate)
- **[MUST]** README with the LinkedIn token-cost narrative (see Token-Savings Math section)

---

### Stretch Goals (if time allows)

Priority order — attempt top to bottom only after must-haves are locked.

- MCP server wrapper: `Applier` agent exposed as an MCP server via Anthropic Python MCP SDK so external agents can call `apply_skill(error_class, context)`
- llm-council fix validation: Sonnet proposes fix, Haiku reviews, Gemini tiebreaks — apply only if 2/3 agree (see ARCHITECTURE.md for council component design)
- Drop generated skills into `.claude/skills/` of a separate Claude Code project and show Claude itself using them during a live demo moment
- Multi-error demo notebook: 5+ bug classes, run full notebook end-to-end, show cumulative savings

---

### Team Parallelization Plan (2-person split)

| Person A | Person B | Sync points |
|----------|----------|-------------|
| Hour 0–1: `notebook.py` mutation core | Hour 0–1: Environment setup, API key validation, `sentence-transformers` smoke test | End of hour 1: verify A can write a cell, B can embed a string |
| Hour 1–3: Watcher + Diagnoser, slow path end-to-end | Hour 1–3: Skill schema design, Distiller skeleton, skill folder structure | End of hour 3: A hands working fix to B for distillation |
| Hour 3–4: Integrate Distiller output back into Watcher loop | Hour 3–4: Distiller complete, embeddings cached on disk | End of hour 4: full slow path + distillation works together |
| Hour 4–5: Retriever cosine matching, threshold logic | Hour 4–5: Rich dashboard, approval gate | End of hour 5: fast path triggers on repeat bug |
| Hour 5–6: Demo notebook (3 bugs staged), rehearsal | Hour 5–6: README, pitch deck | End of hour 6: full rehearsal done |
| Hour 6–7: Screencast co-presenter | Hour 6–7: Submit form, backup screencast | Submission |

**If solo (1 person):** collapse hours 3–4 and 4–5 into a single pass. Accept that Retriever threshold tuning will be rough. Dashboard is a stretch, not a must.

---

## V1.5 — Productization (2-4 weeks post-hackathon)

**Goal:** Go from "hackathon demo" to "something people can actually install and try."

**Window:** Week 1–4 post-hackathon day.

### Week 1: Stabilize and Clean

- Refactor `notebook.py` and agent modules from hackathon-speed code to readable, tested code
- Write unit tests for cell mutation (insert at index, edge cases: first cell, last cell, empty notebook)
- Pin dependency versions, write `pyproject.toml`
- Threshold tuning: collect 20–30 real error / fix pairs, run offline evaluation on cosine threshold, lock in values
- Instrument real token usage with Anthropic SDK response metadata (not estimates)

### Week 2: Publish MCP Server

- Package `Applier` as a standalone MCP server, publish to PyPI as `skillforge-mcp`
- Write MCP tool spec for `apply_skill`, `list_skills`, `record_fix` (see ARCHITECTURE.md for tool signatures)
- Test with Claude Desktop as the MCP client
- Write one-command install: `pip install skillforge-mcp && skillforge serve`

### Week 3: Claude Code Skill Plugin

- Productize as a Claude Code Skill Plugin so any Claude Code user can run `claude plugin install skillforge`
- Plugin exposes: `watcher start`, `watcher stop`, `skills list`, `skills search <query>`, `stats` (shows token savings)
- Publish skill library format spec as a standalone document so third parties can write compatible skill stores

### Week 4: Open Source Launch

- Open-source repo with MIT license
- README narrative: the LinkedIn engineer-firing / token-burn story (see Token-Savings Math)
- Demo GIF in README showing cache hit moment
- Post to Hacker News, tweet thread, LinkedIn post
- Accept first external skill contributions (a few hand-curated skills for common pandas / numpy / sklearn errors)

### V1.5 Acceptance: Done when

- `pip install skillforge-mcp` works on a fresh machine in under 2 minutes
- Claude Desktop can call `apply_skill` via MCP
- `claude plugin install skillforge` works
- Public GitHub repo with 50+ stars in first week

---

## V2.0 — Self-Improving Memory (2-3 months)

**Goal:** Replace the flat folder + cosine similarity skill store with a graph-based memory that understands relationships between skills and validates fixes with a council before applying.

**Window:** Month 1–3 post-hackathon.

### Graph-Based Skill Memory

- Replace folder + sentence-transformers with **VectifyAI/PageIndex** for indexed vector retrieval at scale (see ARCHITECTURE.md for memory layer design)
- Add **safishamsi/graphify** for skill relationship graph: skill A is a generalization of B, C, D; applying A implies B and C are likely relevant too
- Graph enables: "I know how to fix `KeyError` on dict, and `AttributeError` on None — are these related? Yes, both are null/missing value class — merge into one skill"
- Skill confidence scores stored in graph edges; edges decay if skill stops working on new versions of dependencies

### LLM Council Fix Validation

- Adopt **karpathy/llm-council** pattern before any fix is applied:
  - Sonnet proposes fix
  - Haiku reviews proposed fix (is it safe? does it match the error class?)
  - Gemini tiebreaks if Sonnet and Haiku disagree
  - Fix applied only if 2/3 agree
- Council adds latency (~1-2s) but dramatically reduces bad-fix rate
- Council vote rationale stored alongside skill — helps Distiller write better skills

### Confidence-Gated Approval

- Integrate **humanlayer/humanlayer** for human-in-the-loop approval on low-confidence or risky fixes (e.g., fixes that modify more than one cell, or touch imports)
- Three tiers: auto-apply (confidence > 0.9, council 3/3 agree), human-approve (0.7–0.9 or council 2/3), human-required (< 0.7 or destructive change)
- Approval audit log stored per fix

### Multi-Language Kernels

- Extend Watcher to support R, Julia, and SQL kernels in addition to Python
- Language-aware Diagnoser: prompt includes kernel type, language-specific idioms
- Skills are tagged by language; retrieval filters by kernel type first

### Repo-Wide Context for Diagnoser

When SkillForge expands beyond notebooks into application-code bug fixes, the Diagnoser needs more than the failing cell — it needs the function definitions, classes, and modules referenced by the error.

- **Primary: AST-based extraction.** Parse the failing source with Python's stdlib `ast` + `jedi`. When the error mentions `process_data()` defined in `utils/helpers.py`, walk imports and pull only that function's definition. ~10-100x more efficient than whole-repo bundling.
- **Secondary: graphify.** For cross-file dependency questions ("what calls this?", "what does this depend on?"), query the code graph rather than re-parsing source files every fix.
- **Fallback: repomix.** Used only when the LLM genuinely needs whole-repo context (e.g., a config-driven fix touching many files).
- Diagnoser receives: traceback + cell + targeted AST context, with graphify/repomix invoked only when the AST pass returns insufficient signal.

### V2.0 Acceptance: Done when

- Skill library handles 500+ skills without retrieval quality degrading
- Graph correctly clusters at least 3 skill families from real-world errors
- Council validation reduces bad-fix rate to < 5% on a benchmark of 100 errors
- R and Python kernels both supported in Watcher
- humanlayer approval flow working end-to-end

---

## V3.0 — Skill Marketplace (vision, 6-12 months)

**Goal:** "npm for agent procedural memory." A public marketplace where engineers search, install, and share skills. The enterprise wedge: team-shared skill libraries with org-level token-savings dashboards.

**Window:** Month 4–12 post-hackathon.

### Public Skill Marketplace

- Hosted registry: search skills by error class, language, library, version range
- Install: `skillforge install pandas-missing-column` pulls the skill and its embeddings locally
- Publish: `skillforge publish my-skill.md` — community review gate before listing
- Versioning: skills are versioned; old versions available for older dependency stacks
- Quality signals: install count, success rate (reported back by agents with consent), last-verified date

### Enterprise Team Skill Libraries

- Org-level skill library: all agents in an org share a private skill pool
- Token-savings dashboard per team, per project, per developer:
  - Daily token spend (baseline vs. with SkillForge)
  - Cache hit rate trending over time
  - Top 10 most-reused skills (what problems your team re-solves most)
  - Projected annual savings at current trajectory
- This is the LinkedIn narrative made real: "Companies are firing engineers while burning millions on tokens re-solving the same bugs. Here is the receipt."
- SSO, RBAC, audit log — standard enterprise requirements

### A2A Skill Exchange Protocol

- Agents on different machines, different orgs, pull skills from each other on-demand via a standardized A2A protocol (see ARCHITECTURE.md for protocol spec)
- Agent A fixes a bug it has never seen, distills a skill, publishes to shared pool with consent
- Agent B on another machine encounters same error class, pulls skill from pool — zero LLM call, instant fix
- Privacy controls: skills can be marked private, org-only, or public

### Self-Improving Agent

- Agents periodically (nightly or weekly) replay old fixes against current skills
- If a better skill exists now, propose an upgrade
- Skills that haven't matched any error in 90 days are flagged for review or deprecation
- Skill quality improves over time without human curation

### V3.0 Acceptance: Done when

- Public marketplace has 1,000+ community-contributed skills
- 10+ enterprise teams using org-level dashboards
- A2A skill pull working between two separate agent instances on different machines
- Monthly active agent count (skills applied per month) reported on public stats page

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| `nbclient` cell index off-by-one corrupts notebook | High | Critical | Write cell mutation tests first (hour 0); keep backup copy of demo notebook |
| Minimax API rate limit hit during demo | Medium | High | Gemini free tier as fallback already wired in; keep fallback warm |
| Gemini free tier also rate-limited during demo | Low | High | Pre-record screencast of full demo as insurance; show recording if live breaks |
| Prompt engineering returns malformed fix JSON | High | High | Use strict JSON schema in system prompt + retry with parse error feedback; test 10 error types before demo |
| sentence-transformers slow on first load (~3-5s) | High | Low | Pre-warm embeddings model at startup; show loading spinner, not silence |
| Cosine threshold too tight — no cache hits in demo | Medium | High | Pre-seed skill library with exact demo bug class before showtime; threshold is a config value |
| Cosine threshold too loose — wrong skill applied | Medium | Medium | HumanLayer / `input()` approval gate prevents silent bad fix |
| LLM council (V2) adds too much latency | Medium | Medium | Council is async; show result in dashboard, don't block cell execution |
| Graph (V2) relationship edges go stale with library upgrades | Medium | Low | Edge decay scoring + last-verified date field on skills |
| Marketplace skill quality control (V3) | High | Medium | Community review gate + reported success rate signal + deprecation flags |
| Enterprise SSO complexity delays V3 | Medium | Medium | Start with API-key org scoping; SSO is a V3.1 add-on |
| Team coordination (1-2 people, 7 hours) | Medium | High | Explicit sync points every hour; Person A owns notebook/slow-path, Person B owns skill store/fast-path — clean interface boundary |
| Demo live coding fragility | High | Medium | Demo notebook is pre-staged with bugs; no live typing required; fallback is screencast |
| Mic / AV issues at in-person hackathon | Low | Medium | Bring own USB mic; test AV 15 minutes before demo slot |
| Claude Pro rate limit during distillation (V1 gold standard) | Low | Low | Distillation is post-fix, non-blocking; queue and retry; Minimax handles the critical path |

---

## Milestones & Acceptance Criteria

### V1.0 — Hackathon Day (7 hours)

- [ ] `notebook.py` correctly inserts a fix cell at the right index for a 10-cell notebook without corrupting metadata
- [ ] Watcher catches `CellExecutionError` and routes traceback to Diagnoser within 500ms of cell failure
- [ ] Diagnoser returns a structured fix (cell source + explanation) in < 10 seconds via Minimax
- [ ] Fix cell applied to notebook, re-execution succeeds (cell output is green)
- [ ] Distiller produces a valid `skills/{name}.md` with YAML frontmatter including: `error_class`, `fix_pattern`, `embedding_vector`, `created_at`
- [ ] Retriever cosine-matches a repeat error to the correct skill with confidence > 0.80
- [ ] Fast path applies skill template without an LLM call — terminal shows "CACHE HIT"
- [ ] Terminal dashboard shows: tokens spent (slow path), tokens saved (fast path), cache hit rate — all live-updating
- [ ] Demo notebook has 3 staged bugs; full run completes with first bug slow-pathed, second bug cache-hit, third bug slow-pathed
- [ ] README has quick-start in < 5 steps and token-cost narrative

**Done means:** judges can watch a 3-minute screencast and see the cache hit moment with the token counter.

---

### V1.5 — Productization (Week 4 post-hackathon)

- [ ] `pip install skillforge-mcp` on a fresh Python 3.11 environment installs and starts in < 2 minutes
- [ ] Claude Desktop successfully calls `apply_skill` MCP tool and receives a structured response
- [ ] `claude plugin install skillforge` works and `skillforge watcher start` begins monitoring a notebook
- [ ] Skill library format spec is a published document with examples and a JSON schema validator
- [ ] Unit test suite covers cell mutation edge cases with > 80% line coverage
- [ ] Real token usage instrumented from API responses (not estimates)
- [ ] GitHub repo is public, MIT licensed, has a demo GIF, and has received at least 10 external issues or PRs

**Done means:** a stranger can install it and run it without asking us anything.

---

### V2.0 — Self-Improving Memory (Month 3 post-hackathon)

- [ ] PageIndex retrieval returns top-3 skill candidates in < 200ms on a library of 500 skills
- [ ] Graphify correctly groups related skills into at least 3 families when seeded with 50 real-world Python errors
- [ ] LLM council (Sonnet + Haiku + Gemini) runs on every slow-path fix and records vote rationale in skill metadata
- [ ] humanlayer approval flow correctly gates low-confidence fixes and records approval/rejection in audit log
- [ ] R kernel errors are caught by Watcher and diagnosed by Diagnoser (basic R error types)
- [ ] Repomix context bundling tested on a real repo with 10+ source files; Diagnoser fix quality improves on cross-file errors
- [ ] Bad-fix rate < 5% on 100-error benchmark (measured with and without council)

**Done means:** the system handles a 500-skill library and catches errors in R notebooks.

---

### V3.0 — Skill Marketplace (Month 12 post-hackathon)

- [ ] Public marketplace has 1,000+ indexed skills searchable by error class, language, and library
- [ ] `skillforge install <skill-name>` pulls a skill and pre-warms its embedding in < 5 seconds
- [ ] `skillforge publish` flow includes community review queue and automatic embedding generation
- [ ] 10 enterprise teams have active org-level dashboards with > 1 month of token-savings data
- [ ] A2A skill pull protocol tested between two agent instances on different machines in different network environments
- [ ] Nightly self-improvement job runs, proposes at least one skill upgrade per week on an active org
- [ ] Monthly active agent count (skills applied per month) is publicly reported

**Done means:** the marketplace has real traffic and an org is showing SkillForge savings to their CFO.

---

## Token-Savings Math

> "Companies are firing engineers while burning millions on AI tokens that re-solve the same bugs. SkillForge teaches AI to remember."

### The Problem in Numbers

A mid-size engineering team of 50 developers using AI coding assistants generates roughly:

| Metric | Estimate | Basis |
|--------|----------|-------|
| LLM-assisted debugging sessions per dev per day | 8–12 | Common usage survey baseline |
| Sessions that re-solve a previously seen error class | ~40% | Conservative estimate; real codebases are repetitive |
| Tokens per slow-path diagnosis (traceback + context + fix) | ~3,000–5,000 | Measured on GPT-4 / Claude Sonnet |
| Cost per slow-path call (Claude Sonnet, input+output) | ~$0.018–$0.030 | At published API rates |
| Cost per fast-path cache hit | ~$0.0003–$0.0006 | Embedding call only (local) or minimal validation call |

### Per-Developer Daily Savings

Assuming:
- 10 debugging sessions/day per dev
- 40% are repeat error classes (4 sessions hit cache)
- 6 sessions are slow path: `6 × $0.024 = $0.144`
- 4 sessions hit fast path: `4 × $0.0004 = $0.0016`
- Without SkillForge: `10 × $0.024 = $0.240/dev/day`
- With SkillForge: `$0.144 + $0.0016 = $0.146/dev/day`

| Metric | Value |
|--------|-------|
| Savings per developer per day | ~$0.09 |
| Savings per developer per year | ~$33 |
| Savings for 50-dev team per year | ~$1,650 |
| Token reduction on cached calls | ~50x |

Note: these numbers are conservative. Teams debugging production systems often have much higher token volumes. A team burning $50,000/year on LLM API calls with 40% repeat errors saves $20,000/year. That is a full junior engineer salary.

### The Break-Even Math

| Scenario | Break-even |
|----------|------------|
| SaaS subscription at $50/team/month | Day 1 — savings exceed cost from first week of use |
| Enterprise license at $500/org/month | Break-even in < 3 months for a 20-dev team |
| Self-hosted (open core) | $0 cost, all savings captured |

### The LinkedIn Pitch (Quantitative Version)

> In 2024 and 2025, companies laid off thousands of engineers citing AI efficiency gains. Those same companies are paying LLM API bills where 40% of tokens are spent re-diagnosing bugs their AI already fixed last Tuesday. A 50-engineer team burning $50K/year on AI tokens is wasting $20K re-solving the same classes of problems. SkillForge is a one-line install that cuts that waste by ~50x on repeat errors. The AI remembers. The bill goes down. You stop pretending that firing engineers was about efficiency and start actually being efficient.

### V3.0 Enterprise Dashboard Numbers

At scale, the org-level dashboard will show:

| Dashboard Metric | What It Tells the CFO |
|-----------------|----------------------|
| Total tokens spent (baseline) | What you would have paid without SkillForge |
| Total tokens spent (actual) | What you paid |
| Cache hit rate (%) | How "mature" your org's skill library is — improves over time |
| Top 10 re-solved error classes | Where your team's bugs cluster — actionable for tech debt |
| Projected annual savings | The number that justifies the license renewal |
| Skills contributed to public marketplace | Community ROI and employer branding signal |

The cache hit rate is the north-star metric. A new org starts at ~10% (skill library is thin). After 30 days it is typically 35–50%. After 90 days, mature teams hit 60–70%. At 60% cache hit rate on a $50K/year token budget, the savings are $30K/year — before accounting for the productivity time saved from faster fixes.

---

*See ARCHITECTURE.md for component diagrams, agent role specifications, MCP tool signatures, and the A2A skill exchange protocol design.*

*This roadmap is versioned alongside the codebase. Update after each version ships.*
