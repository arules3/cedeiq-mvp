# CedeIQ — Reinsurance Treaty & Ceded Execution MVP

QS AI Practitioner+ Capstone project. See `/CLAUDE.md` for full project context and
`/specs/mvp-spec.md` for the detailed spec.

## Quick Start

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
This creates `backend/cedeiq.db` (SQLite) automatically once models are defined —
no separate database server needed.

### Dashboard (Streamlit)
```bash
cd dashboard
python -m venv .venv && source .venv/bin/activate   # or reuse backend's venv
pip install -r requirements.txt
streamlit run app.py
```
Run this in a second terminal alongside the backend — the dashboard calls the
FastAPI API at `http://localhost:8000`.

## Day-by-Day Plan

See the learning plan discussion in chat / `docs/daily-log.md` for the 4-day build
schedule: Planning → Specs/Skills → Steering/MCP/Subagents → Hooks/Testing/Deploy.

## First Claude Code session

Open this folder in Claude Code and start with:
> "Read CLAUDE.md and specs/mvp-spec.md, then enter Plan Mode to break down the
> Treaty and Policy SQLAlchemy models (SQLite) plus the /treaties and
> /policies/upload endpoints."
