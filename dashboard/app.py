import streamlit as st
import requests

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="CedeIQ — Ceded Execution Dashboard", layout="wide")
st.title("CedeIQ — Reinsurance Treaty & Ceded Execution")

st.caption(
    "Dashboard calls the FastAPI backend only — it never touches the database "
    "or reimplements treaty logic (see CLAUDE.md steering rules)."
)

try:
    health = requests.get(f"{API_BASE}/health", timeout=3).json()
    st.success(f"Backend status: {health.get('status')}")
except requests.exceptions.ConnectionError:
    st.error("Backend not reachable at " + API_BASE + " — run `uvicorn app.main:app --reload` in backend/")

# TODO (Day 4, ask Claude Code to build these against /specs/mvp-spec.md §7):
# - Ceded ratio, capital relief, blind-spot count, recoverables aging metrics
#   pulled from GET /dashboard/summary
# - Blind-spot table from GET /blind-spots
# - Recoverables aging chart from GET /recoverables
# - Audit trail lookup by policy_id from GET /audit-log
