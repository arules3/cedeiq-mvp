# CLAUDE.md — CedeIQ (Reinsurance Treaty & Ceded Execution Platform)

This file is the project context Claude Code reads first. Keep it current — it is the
single source of truth for architecture, conventions, and rules Claude must follow.

## 1. Problem Statement

Global reinsurance markets have tightened capacity, increased costs, and heightened
underwriting scrutiny. Incorrect treaty application and exposure blind spots cause
capital strain, compliance gaps, and margin loss. Legacy processes are manual,
paper-based, and error-prone, leading to premium/loss leakage and delayed recoveries.

CedeIQ automates ceded reinsurance execution: it applies the correct treaty to each
policy/exposure, detects coverage blind spots, calculates ceded premium/losses and
capital relief, tracks recoverables, and keeps a full audit trail — giving carriers
faster, more accurate, more defensible ceded execution.

## 2. MVP Scope

In scope:
- Treaty repository (Quota Share, Surplus, Excess of Loss / Cat XL, Facultative)
- Rules engine that auto-applies the correct treaty to a given policy/exposure
- Exposure blind-spot detection (uncovered or over-concentrated exposure)
- Ceded premium / ceded loss / capital relief calculation
- Recoverables tracker with aging
- Audit log of every automated treaty-application decision
- Dashboard: ceded ratio, capital relief, flagged exposures, recovery aging

Out of scope for MVP (see `/specs/mvp-spec.md` §6):
- Real-time bureau/market data feeds
- Multi-currency FX conversion
- Full actuarial pricing models
- Role-based multi-tenant auth (single internal user role is fine for MVP)

## 3. Tech Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, Pydantic v2
- **Database**: SQLite (file-based, zero setup — `cedeiq.db` in `backend/`)
- **Dashboard/UI**: Streamlit — talks to the FastAPI backend over HTTP (not direct DB access)
- **Testing**: pytest (backend)
- **Package/env**: `venv` for Python (single environment for backend + Streamlit)

## 4. Repository Structure

```
cedeiq-mvp/
├── CLAUDE.md                 <- you are here
├── backend/
│   ├── app/
│   │   ├── models/           <- SQLAlchemy models (Treaty, Policy, Cession, AuditLog, Recoverable)
│   │   ├── routers/          <- FastAPI route modules
│   │   ├── services/         <- rules engine, cession calculator, blind-spot detector
│   │   ├── schemas/          <- Pydantic request/response schemas
│   │   ├── db.py             <- SQLite engine/session setup
│   │   └── main.py
│   ├── cedeiq.db              <- SQLite file (gitignored, generated on first run)
│   └── tests/
├── dashboard/                 <- Streamlit app (calls backend API, no direct DB access)
├── specs/                    <- spec-driven dev artifacts (Spec Kit / OpenSpec style)
├── skills/                   <- reusable SKILL.md files
├── .claude/
│   ├── agents/                <- subagent definitions
│   └── settings.json          <- hooks config
└── docs/
    ├── daily-log.md
    └── architecture.md
```

## 5. Domain Glossary (read before writing any treaty logic)

- **Treaty**: A reinsurance contract ceding a defined slice of risk from the carrier (cedent) to a reinsurer.
- **Quota Share (QS)**: Reinsurer takes a fixed % of every policy in a defined book.
- **Surplus**: Reinsurer takes a % above the cedent's retention line, up to treaty capacity.
- **Excess of Loss (XoL / Cat XL)**: Reinsurer pays losses above an attachment point up to a limit, per occurrence/event.
- **Facultative**: One-off cession for a single policy/risk not covered by a standing treaty.
- **Cession**: The act/amount of risk transferred to a reinsurer under a treaty.
- **Ceded Premium**: Premium passed to the reinsurer for the risk transferred.
- **Recoverable**: Amount owed back to the cedent by the reinsurer after a loss.
- **Blind spot**: Exposure with no matching treaty, or exceeding all applicable treaty limits.
- **Capital relief**: Reduction in required capital resulting from ceding risk.

## 6. Steering Rules (Claude must follow these)

1. **Never bypass the service layer.** All cession calculations happen in
   `backend/app/services/`, never inline in routers.
2. **Every automated treaty decision must write an AuditLog entry** — which rule fired,
   inputs, output, timestamp. No exceptions, even in MVP.
3. **Treaty limit checks are mandatory before any cession is finalized.** A cession that
   would breach a treaty's stated limit must be flagged, not silently capped.
4. **Money fields use `Decimal`, never `float`.**
5. **No hardcoded treaty logic in the dashboard.** Streamlit only calls the backend
   API and renders results — it never talks to the database or reimplements rules.
6. Prefer small, reviewable diffs — use Plan Mode before multi-file changes.
7. Keep `/specs/mvp-spec.md` and this file updated when scope changes; don't let
   docs drift from code.
8. SQLite is single-writer — avoid long-held write transactions; keep cession-run
   writes batched and short.

## 7. Context Management Notes

- Run `/compact` after finishing each major module (treaty engine, cession calc,
  blind-spot detector, dashboard) rather than mid-task.
- Use `/clear` when switching from backend work to Streamlit work in the same session.

## 8. MCP / Tools in Use

- **GitHub MCP** — configured in `.mcp.json` at the repo root. Once connected
  (via `GITHUB_PERSONAL_ACCESS_TOKEN`), gives Claude Code direct awareness of
  this repo's issues, PRs, and commit history — e.g. "check open issues before
  planning the next module" becomes possible without manually pasting context.
- Add further MCP servers here as they're wired in (e.g. a Postgres/SQLite
  MCP for direct DB inspection during development).

## 9. Skills

- `skills/cedeiq-endpoint-pattern/SKILL.md` — encodes this project's
  established router → schema → service → audit-log pattern so new endpoints
  stay consistent with existing ones. Reference this before adding any new
  route.

## 10. Subagents

- `.claude/agents/treaty-rules-agent.md` — scoped to `app/services/`
- `.claude/agents/dashboard-agent.md` — scoped to `dashboard/`
- `.claude/agents/test-writer-agent.md` — scoped to `backend/tests/`
- Configured, not yet exercised live in a Claude Code session (CLI budget
  constraint — see docs/daily-log.md).

## 11. Hooks

- `.claude/settings.json` configures:
  - **PreToolUse** on Bash calls → `.claude/hooks/guard_dangerous_bash.py`,
    which blocks destructive commands (force-push, `rm -rf`, dropping the
    DB) before they execute. Unit-tested standalone (feed it JSON on stdin)
    and confirmed to correctly block/allow — see docs/daily-log.md.
  - **PostToolUse** on Edit/Write → runs the pytest suite automatically
    after any file change.
  - **Stop** → reminds to update the daily log when a session ends.
- Like Subagents, configured and independently verified, but not yet run
  inside a live Claude Code session end-to-end.
