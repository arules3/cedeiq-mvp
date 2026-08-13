# CedeIQ — Capstone Submission Write-Up

## 1. Problem & Solution

Global reinsurance markets have tightened capacity, increased costs, and heightened
underwriting scrutiny. Incorrect treaty application and exposure blind spots cause
capital strain, compliance gaps, and margin loss — worsened by legacy processes that
are manual, paper-based, and error-prone.

**CedeIQ** automates ceded reinsurance execution: it matches each policy to the
correct treaty (Quota Share or Excess of Loss), calculates the cession, flags
exposures that fall outside any treaty's coverage or limit ("blind spots") instead
of silently mishandling them, and logs every decision for audit/compliance review.

## 2. What Was Built (MVP Scope)

- SQLite-backed data model: Treaty, Policy, Cession, AuditLog, Recoverable
- Rules engine matching policies to treaties by line of business, peril, and
  effective date, with Quota Share (% cession) and Excess of Loss (attachment/limit)
  calculation logic
- Deliberate governance behavior: exposure exceeding a treaty's limit is partially
  ceded and the uncovered remainder is explicitly flagged — never silently capped
- FastAPI backend exposing treaty/policy management, cession processing, blind-spot
  and audit-log queries, and a dashboard summary endpoint
- Synthetic demo dataset with intentionally engineered scenarios: clean matches,
  no-match blind spots, below-attachment blind spots, and a limit-breach case
- Streamlit dashboard for a non-technical view of ceded ratio, capital relief
  proxy, blind spots, and audit trail (see docs/architecture note when complete)

## 3. How AI-Native Development Was Used

| Program Concept | How it was applied here |
|---|---|
| Project Info Files | `CLAUDE.md` as the single, evolving source of project context |
| Spec-Driven Development | `specs/mvp-spec.md` written before implementation, defining user stories, data model, and API contract |
| Steering | Explicit rules in `CLAUDE.md` §6 translated directly into rules-engine behavior (e.g. flag-not-cap) |
| Skills / Agent Capability | `.claude/agents/treaty-rules-agent.md` scopes a subagent specifically to rules-engine work |
| Automation / Hooks | `.claude/settings.json` configures a PostToolUse test hook and a Stop reminder hook |
| Context Management | Modular file structure (models/services/routers separated) to keep any single working session's context focused |
| Connectors, Tools & MCP | GitHub MCP documented as the intended integration for repo-aware development (see CLAUDE.md §8) |

## 4. Constraints & Honest Limitations

- Built primarily via Claude's chat interface rather than the Claude Code CLI, due
  to budget constraints (no reimbursement available, free API credits exhausted).
  Plan Mode, Subagents, Hooks, and MCP are therefore documented as **designed and
  configured** rather than executed live in a terminal session — the configuration
  files themselves (`.claude/agents/`, `.claude/settings.json`) are the evidence.
- MVP scope deliberately excludes: Facultative/Surplus treaty types, multi-currency,
  full actuarial pricing, recoverables aging buckets, and authentication — documented
  in `specs/mvp-spec.md` §6 as explicit out-of-scope decisions, not oversights.
- Timeline was compressed from the original 8-day capstone window into a shorter,
  intensive build — documented transparently in `docs/daily-log.md`.

## 5. What a Production Version Would Add Next

- Facultative treaty support and multi-treaty layering (QS + XoL stacking)
- Alembic migrations instead of `create_all` on startup
- Authentication/authorization for multi-user carrier environments
- Real bureau/market data feeds instead of CSV upload
- Recoverables aging and automated reminder workflows
