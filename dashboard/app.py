import streamlit as st
import requests
import pandas as pd

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="CedeIQ — Ceded Execution Dashboard", layout="wide")
st.title("CedeIQ — Reinsurance Treaty & Ceded Execution")
st.caption(
    "Dashboard calls the FastAPI backend only — it never touches the database "
    "or reimplements treaty logic (see CLAUDE.md steering rules)."
)


def api_get(path: str, params: dict | None = None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error(f"Backend not reachable at {API_BASE} — run `uvicorn app.main:app --reload` in backend/")
        st.stop()
    except requests.exceptions.HTTPError as e:
        st.error(f"API error on {path}: {e}")
        st.stop()


def api_post(path: str):
    try:
        r = requests.post(f"{API_BASE}{path}", timeout=15)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error(f"Backend not reachable at {API_BASE}")
        st.stop()
    except requests.exceptions.HTTPError as e:
        st.error(f"API error on {path}: {e}")
        st.stop()


# --- Health check + manual trigger -----------------------------------------

col_health, col_action = st.columns([3, 1])
with col_health:
    health = api_get("/health")
    st.success(f"Backend status: {health.get('status')}")
with col_action:
    if st.button("Run cession processing", type="primary"):
        result = api_post("/cessions/run")
        st.toast(
            f"Processed {result['policies_processed']} policies — "
            f"{result['cessions_created']} ceded, {result['blind_spots_flagged']} blind spots flagged."
        )
        st.rerun()

st.divider()

# --- Summary metrics ---------------------------------------------------------

summary = api_get("/dashboard/summary")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Policies", summary["total_policies"])
m2.metric("Ceded Ratio", f"{summary['ceded_ratio'] * 100:.1f}%")
m3.metric("Total Ceded Premium", f"${summary['total_ceded_premium']:,.0f}")
m4.metric("Blind Spots", summary["blind_spot_count"],
          delta=None if summary["blind_spot_count"] == 0 else "needs review",
          delta_color="inverse")

m5, m6 = st.columns(2)
m5.metric("Total Ceded Exposure", f"${summary['total_ceded_exposure']:,.0f}")
m6.metric("Outstanding Recoverables", f"${summary['outstanding_recoverables']:,.0f}")

st.divider()

# --- Tabs: Cessions / Blind Spots / Audit Trail ------------------------------

tab_cessions, tab_blind_spots, tab_audit = st.tabs(["Cessions", "Blind Spots", "Audit Trail"])

with tab_cessions:
    st.subheader("Cession Results")
    cessions = api_get("/cessions")
    if cessions:
        df = pd.DataFrame(cessions)
        df = df[["id", "policy_id", "treaty_id", "ceded_premium", "ceded_exposure", "rule_applied", "created_at"]]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No cessions yet — upload policies/treaties and click 'Run cession processing' above.")

with tab_blind_spots:
    st.subheader("Blind Spots — Uncovered or Over-Limit Exposure")
    st.caption(
        "Every row here is a policy that either matched no treaty, fell below an "
        "attachment point, or exceeded a treaty's limit. None of these were silently "
        "dropped or capped — see CLAUDE.md steering rule 3."
    )
    blind_spots = api_get("/blind-spots")
    if blind_spots:
        st.dataframe(pd.DataFrame(blind_spots), use_container_width=True, hide_index=True)
    else:
        st.success("No blind spots detected in the current dataset.")

with tab_audit:
    st.subheader("Audit Trail")
    policy_filter = st.text_input("Filter by Policy ID (optional)", "")
    params = {"policy_id": int(policy_filter)} if policy_filter.strip().isdigit() else None
    audit_rows = api_get("/audit-log", params=params)
    if audit_rows:
        df = pd.DataFrame(audit_rows)
        df = df[["id", "policy_id", "cession_id", "action", "rule_fired", "created_at"]]
        st.dataframe(df, use_container_width=True, hide_index=True)
        with st.expander("View raw input/output snapshots for a row"):
            row_id = st.selectbox("Audit log ID", [r["id"] for r in audit_rows])
            selected = next(r for r in audit_rows if r["id"] == row_id)
            st.json({"input": selected["input_snapshot"], "output": selected["output_snapshot"]})
    else:
        st.info("No audit log entries yet.")