# Daily Activity Log — CedeIQ Capstone

Fill one entry per day. Required fields per QS AI Practitioner+ guidelines:
Tool used | Feature explored | Prompt examples | Output generated | Learnings | Issues faced

## Day 1 — 13-Aug-2026

Note: due to a compressed timeline (no CLI Claude Code budget available — see
"Issues faced"), this single day covers ground that would normally span
several program sessions: Project Info Files, Plan Mode concepts, Spec-Driven
Development, Steering, and initial rules-engine implementation.

**Tool used:** Claude (chat interface, with file-creation tools) instead of
the Claude Code CLI, due to no available Pro/Max subscription or API credit
budget for this capstone.

**Feature explored:**
- Project Info Files — wrote `CLAUDE.md` (project context, domain glossary,
  steering rules) as the single source of truth for the project.
- Spec-Driven Development — wrote `specs/mvp-spec.md` with user stories,
  data model, and API endpoint definitions before writing any code.
- Steering — defined explicit rules in `CLAUDE.md` §6 (e.g. "never silently
  cap a cession that exceeds a treaty limit — flag it instead"), then
  verified the rules engine actually follows them.

**Prompt examples:**
- "Read the QS AI Practitioner+ PDF and identify all prerequisites needed to
  make this capstone MVP-ready."
- "Build the SQLAlchemy models for Treaty, Policy, Cession, AuditLog, and
  Recoverable based on specs/mvp-spec.md §4."
- "Implement a rules engine that matches policies to Quota Share and Excess
  of Loss treaties, calculates cessions, and flags blind spots without
  silently capping exceeded limits."

**Output generated:**
- `CLAUDE.md`, `specs/mvp-spec.md`, `docs/daily-log.md` (this file)
- Backend: 5 SQLAlchemy models, Pydantic schemas, rules engine
  (`services/rules_engine.py`), 5 FastAPI routers, `main.py` wiring
- `seed_data.py` — synthetic treaty/policy data with deliberate blind-spot
  and limit-breach scenarios for demoing the rules engine
- Verified locally: `POST /cessions/run` correctly ceded matching policies
  and flagged blind spots per the seeded scenarios
- Git repo initialized and pushed to GitHub with real commit history

**Learnings:**
- FastAPI's `/docs` page (Swagger UI) is generated automatically from route
  type hints and Pydantic schemas — no separate documentation step needed.
  This is why schemas.py exists as strongly-typed classes rather than raw
  dicts: validation, docs, and type safety all come from the same source.
- Encoding steering rules explicitly in `CLAUDE.md` (e.g. "never silently
  cap") turned into a concrete, testable behavior in the rules engine
  (`apply_excess_of_loss` returns a flagged remainder rather than truncating)
  — this made the abstract idea of "governance" tangible.
- Keeping the rules engine pure (no DB calls inside `rules_engine.py`) made
  it straightforward to reason about and will make it easy to unit test.

**Issues faced:**
- Anthropic's $5 new-account API credit, expected to fund a few short Claude
  Code CLI sessions for Plan Mode / Subagents / Hooks / MCP demonstration,
  was not available/was already exhausted, and a Pro subscription ($20/mo)
  wasn't reimbursable for this internal capstone. Resolution: built the
  application logic entirely via the chat interface (still Claude, still
  file-creation tooling) and will document Plan Mode, Subagents, Hooks, and
  MCP as designed-and-configured (see `.claude/agents/` and
  `.claude/settings.json`) rather than executed live in a paid terminal.

## Day 2 — [fill in today's date when you do this work]

**Tool used:**
**Feature explored:** (e.g., Skills — reusable test patterns; Context Management)
**Prompt examples:**
-
**Output generated:** (pytest suite for rules_engine.py, Streamlit dashboard)
**Learnings:**
**Issues faced:**

## Day 3 — [date]

**Tool used:**
**Feature explored:** (e.g., Steering, MCP, Subagents)
**Prompt examples:**
-
**Output generated:**
**Learnings:**
**Issues faced:**

## Day 4 — [date]

**Tool used:**
**Feature explored:** (e.g., Hooks, Testing, Deployment)
**Prompt examples:**
-
**Output generated:**
**Learnings:**
**Issues faced:**
