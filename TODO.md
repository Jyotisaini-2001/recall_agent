# Hackathon Day TODO — SkillForge V1.0

This is your **executable** day-of plan. Linked from [README.md](README.md). Long-arc plan in [ROADMAP.md](ROADMAP.md). System design in [ARCHITECTURE.md](ARCHITECTURE.md).

**V1 scope reminder** (locked in):
- Interface: **CLI only** (`skillforge run`, `watch`, `skills`, `stats`). MCP server moves to V1.5.
- Codebase context: **none** — failing cell + 2 prior cells is the whole context. AST extraction is V2.
- Confidence gate: **0.80** for FAST PATH, **0.65–0.80** band for assisted, **<0.65** falls through to SLOW PATH.
- Demo bugs: **macOS-friendly only** (pandas dtype, ModuleNotFoundError, no CUDA/GPU). Your teammate generates the actual `.ipynb`.

---

## Pre-hackathon (the night before — do these now)

Setup that costs nothing on the day itself.

- [ ] Clone repo to laptop, `python -m venv .venv && source .venv/bin/activate`
- [ ] `pip install -r requirements.txt` — confirm everything resolves
- [ ] Copy `.env.example` to `.env`, fill in keys you have:
  - [ ] `MINIMAX_API_KEY` + `MINIMAX_GROUP_ID` (your paid one — primary)
  - [ ] `GEMINI_API_KEY` (free tier — fallback)
  - [ ] `ANTHROPIC_API_KEY` (optional — gold standard for distillation)
  - [ ] `OPENAI_API_KEY` (optional — for embeddings; otherwise we use sentence-transformers locally)
- [ ] Smoke-test each key with a `hello world` curl. Record response times. Pick the fastest reliable one as primary.
- [ ] Install Jupyter locally: `pip install jupyterlab`. Confirm it opens.
- [ ] Skim docs (~30 min total):
  - [ ] [nbformat cell-insertion API](https://nbformat.readthedocs.io/en/latest/) — focus on `new_code_cell` and notebook structure
  - [ ] [Anthropic MCP Python SDK quickstart](https://modelcontextprotocol.io/quickstart/server) — read once, you'll reference it tomorrow
  - [ ] [datalayer/jupyter-mcp-server](https://github.com/datalayer/jupyter-mcp-server) — skim their cell-insertion code, steal the patterns
- [ ] Decide team split if you have a teammate (see "Team parallelization" below)
- [ ] Charge laptop. Pack chargers. Bring HDMI adapter for demo.
- [ ] Sleep.

---

## Team parallelization (1 vs 2 people)

### Solo
Linear through the hours below. Cut stretch goals first. The MCP server is the first thing to drop.

### 2 people
Person A drives the **engine** (notebook surgery + agent loop). Person B drives the **demo polish** (notebook content + dashboard + pitch).

| Hour | Person A | Person B |
|---|---|---|
| 0-1 | Notebook mutation core | `.env` + LLM client wrappers + structured-output prompt |
| 1-3 | Watcher + Diagnoser → SLOW path works | Build the demo notebook with 3 staged bugs |
| 3-4 | Distiller → first skill written | Rich terminal dashboard scaffolding |
| 4-5 | Retriever → FAST path works | Wire dashboard to live token counters |
| 5-6 | Polish + edge cases | Record dry-run screencast, draft pitch script |
| 6-7 | Code freeze. Final pass. Submit. | Final screencast take. Submit. |

Sync points: end of hour 1, end of hour 3, end of hour 5. 5-minute standups, no longer.

---

## Hour 0 → 1: Notebook mutation core

**Goal:** Bulletproof `read → mutate → write` for `.ipynb`. This is THE most likely place to lose a hour silently. Get it right early.

- [ ] `git init`, push to a fresh GitHub repo
- [ ] Create `skillforge/` package directory with `__init__.py`
- [ ] Implement `skillforge/notebook.py`:
  - [ ] `read(path) -> NotebookNode` (uses `nbformat.read`)
  - [ ] `find_failing_cell(nb) -> (idx, cell)` — looks for cells with `error` output type
  - [ ] `insert_fix_cell(nb, after_idx, code, *, source_skill=None) -> int` — uses `nbformat.v4.new_code_cell`, inserts at `after_idx + 1`, returns new index
  - [ ] `write(nb, path)` — uses `nbformat.write`, preserves nbformat version
- [ ] Write a tiny manual smoke test: read a fixture notebook, insert a cell with `print('hello from skillforge')`, write to a tmp path, open in JupyterLab, eyeball it.
- [ ] **CHECKPOINT 1 (T+60min):** notebooks round-trip with inserted cells, opened in JupyterLab without errors.

If this hour overruns by 20+ minutes, escalate: stub out the insertion API and move on. You can come back; you can't ship without the rest.

---

## Hour 1 → 3: Watcher + Diagnoser (SLOW PATH)

**Goal:** A broken cell becomes a green cell, end-to-end, using a real LLM.

- [ ] `skillforge/llm.py`: provider-agnostic wrapper
  - [ ] `call(prompt: str, *, json_mode=True, model=None) -> dict | str`
  - [ ] Provider chain: Minimax → Gemini → Anthropic. First with valid key wins.
  - [ ] Token counting (request + response) — store on each call for the dashboard
- [ ] `skillforge/diagnoser.py`:
  - [ ] Prompt template that takes `{traceback, failing_cell, prior_cells, language}` and asks for JSON: `{diagnosis, fix_code, explanation, confidence: 0..1}`
  - [ ] Robust JSON parsing (regex fallback if model wraps in ```json blocks)
  - [ ] Returns a `Fix` dataclass
- [ ] `skillforge/watcher.py`:
  - [ ] `run_notebook(path)` using `nbclient.NotebookClient(allow_errors=True)`
  - [ ] After kernel runs, scan for cells with error output → call `diagnose(...)` → call `insert_fix_cell(...)` → re-run inserted cell only
  - [ ] If fix cell errors too: retry up to 2x with augmented prompt ("your previous fix failed with: ...")
- [ ] Build a minimal `demo.ipynb` with ONE deliberate bug (e.g., a NameError or an obvious dtype issue — keep it simple for hour 1-3)
- [ ] **CHECKPOINT 2 (T+3h):** `python -m skillforge run demo.ipynb` → notebook runs, broken cell triggers fix, fixed cell appears below, all-green when re-opened.

Risk: structured JSON output is flaky on smaller models. Have a regex fallback that grabs ```python blocks if JSON parse fails.

---

## Hour 3 → 4: Distiller (skill creation)

**Goal:** Each successful fix produces a `skills/{slug}.md` file with the schema below.

- [ ] `skillforge/distiller.py`:
  - [ ] After Diagnoser succeeds, call LLM with a "distill into reusable skill" prompt
  - [ ] Schema:
    ```yaml
    ---
    name: kebab-case-slug
    description: one-line description
    triggers:
      patterns: [exact substrings to match in tracebacks]
      contexts: [tags like pytorch, pandas, ml]
    confidence: 0.0–1.0
    times_used: 0
    created_at: ISO date
    ---

    # Diagnosis
    Why this happens (1-2 sentences)

    # Fix template
    ```python
    # parameterized fix code with {placeholders}
    ```

    # Verification
    What to check after applying
    ```
  - [ ] `slugify(name)` for filenames
  - [ ] Save to `skills/{slug}.md`
- [ ] Pre-compute embeddings for the new skill's `triggers.patterns` joined string, save sidecar `skills/{slug}.npy`
- [ ] **CHECKPOINT 3 (T+4h):** Running `demo.ipynb` produces a `skills/{name}.md` file that opens cleanly and has all schema fields populated.

---

## Hour 4 → 5: Retriever (FAST PATH)

**Goal:** A second similar bug is fixed without an LLM call.

- [ ] `skillforge/retriever.py`:
  - [ ] Load all `skills/*.md` + their `.npy` embeddings on startup
  - [ ] `match(traceback) -> (skill, confidence) | None`
  - [ ] Embed traceback with sentence-transformers (use `all-MiniLM-L6-v2` — 80MB, fast)
  - [ ] Cosine similarity vs all skill embeddings
  - [ ] Threshold logic (per project decision: **0.80 is the canonical FAST PATH bar**):
    - `confidence > 0.80` → return skill, FAST PATH
    - `0.65-0.80` → ask Diagnoser to validate match (cheap call), then apply if validated
    - `< 0.65` → return `None`, fall through to SLOW PATH
- [ ] Update Watcher loop to call Retriever first, fall through to Diagnoser only on miss
- [ ] When applying a skill template, fill placeholders with simple regex from traceback (e.g., extract variable names) — keep it dumb, it's the demo
- [ ] **CHECKPOINT 4 (T+5h):** Add a SECOND deliberate bug to `demo.ipynb` of the same class as the first. Run. First fix → SLOW path. Second fix → FAST path. Time the difference. Confirm <500ms on FAST path.

This is your **demo make-or-break** hour. If FAST path doesn't work, the whole pitch falls apart. Have a fallback: just keyword-match traceback against `triggers.patterns` (substring check) as a degraded mode.

---

## Hour 5 → 6: Polish + dashboard + demo notebook

**Goal:** It looks like a product, not a script.

- [ ] `skillforge/dashboard.py` using `rich`:
  - [ ] Live table with: tokens_spent, tokens_saved, cache_hit_rate, library_size, last_skill_used
  - [ ] Refreshes after every fix
  - [ ] One-line activity feed: "[FAST] applied pandas-dtype-mismatch in 213ms"
- [ ] Approval gate: if confidence < 0.95 on auto-apply, print the proposed fix and `input("Apply? [y/n] ")` — keep it simple. HumanLayer is overkill for demo.
- [ ] **Demo notebook is your teammate's deliverable.** Sync with them on the 3-bug arc:
  1. Pandas dtype mismatch (object column in arithmetic) — first encounter, SLOW path, distills skill #1
  2. Same class, different column — FAST path, applies skill #1 ← the wow moment
  3. ModuleNotFoundError for a missing package — SLOW path, distills skill #2
  - Stretch: a 4th bug = different ModuleNotFoundError → FAST path on skill #2 (proves it's not a one-trick)
- [ ] All bugs must run on macOS without GPU. **No CUDA, no torch.cuda, no GPU dependencies.**
- [ ] Practice run through full demo, time it. Should be ~90 seconds end-to-end.
- [ ] **CHECKPOINT 5 (T+6h):** Demo runs cleanly, dashboard shows the savings story, you can narrate it without checking notes.

---

## Hour 6 → 7: Submission

- [ ] Re-skim README, make sure quick-start is accurate
- [ ] 2-3 minute screencast (use OBS or QuickTime). Capture:
  - The dashboard prominently
  - The notebook beside it
  - You narrating the SLOW → FAST transition
  - Show the `skills/` folder filling up
- [ ] Make a 1-minute backup demo video in case live demo fails (always)
- [ ] Final pitch review using [PITCH.md](PITCH.md)
- [ ] Submit on the hackathon platform with: README link, demo video, GitHub repo, pitch deck

---

## Stretch goals (only after hour 6 if comfortably ahead)

- [ ] **MCP server** (`skillforge/mcp_server.py`) exposing `apply_skill`, `list_skills`, `record_fix` tools. Connect to Claude Code in a separate window, demo Claude using a SkillForge skill directly.
- [ ] **llm-council validation**: Diagnoser produces fix, second model reviews, only apply if both agree. Counter on dashboard: "fixes vetoed: N".
- [ ] **Drop-in compatibility**: copy your `skills/*.md` into a separate Claude Code project's `.claude/skills/` directory, demo Claude using one of your distilled skills natively.
- [ ] **Multi-language**: add a R or Julia kernel test. Same skill schema, different language tag in `contexts`.

---

## Cut list (if running behind, drop these in order)

1. Stretch goals (already optional)
2. Approval gate (just auto-apply everything, mention "in production we'd gate on confidence")
3. Multi-bug demo notebook (one bug class repeated twice still tells the story)
4. Provider chain (just hardcode Minimax, mention Gemini fallback in pitch)
5. Slugify edge cases (just use `name.lower().replace(' ', '-')`)

**Never cut:**
- The dashboard. The dashboard IS the demo. No dashboard = no story.
- The skill file. The skill file IS the moat. No file = no V2 story.

---

## Pre-flight checks (do at the start of each hour)

| Check | Why |
|---|---|
| API keys still valid? | Free tiers can throttle |
| Disk space for embeddings? | sentence-transformers downloads ~80MB once |
| Git committed? | Don't lose work to a typo |
| Charger connected? | Hackathons drain batteries |
| Latest commit pushed? | Backup is good |

---

## Definition of done (V1)

You can hit submit when ALL of these are true:

- [ ] `python -m skillforge run demo.ipynb` runs end-to-end without manual intervention
- [ ] At least one SLOW PATH fix completes successfully
- [ ] At least one FAST PATH cache hit completes (visible <500ms latency)
- [ ] `skills/` folder contains at least 1 valid YAML+MD skill file
- [ ] Dashboard shows non-zero `tokens_saved`
- [ ] README quickstart matches what `python -m skillforge --help` reports
- [ ] Demo video uploaded
- [ ] Pitch deck committed
- [ ] Submitted on hackathon platform with all links

Ship it.
