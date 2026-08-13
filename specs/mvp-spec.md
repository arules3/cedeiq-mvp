# CedeIQ — MVP Specification

Status: Draft v1
Owner: (you)
Related: `/CLAUDE.md`

## 1. Problem Statement

Global reinsurance markets have tightened capacity, increased costs, and heightened
underwriting scrutiny. Incorrect treaty application and exposure blind spots cause
capital strain, compliance gaps, and margin loss. Legacy processes are manual,
paper-based, and error-prone, leading to leakage and delayed recoveries.

## 2. Users / Personas

| Persona | Need |
|---|---|
| Ceded Re Analyst | Wants each policy correctly matched to a treaty without manual lookup |
| Underwriting Manager | Wants visibility into exposure blind spots before bind |
| Compliance Officer | Needs an auditable record of every cession decision |
| CFO / Capital Management | Wants a real-time view of capital relief and recoverables aging |

## 3. Core User Stories

**US-1 — Treaty Ingestion**
As a Ceded Re Analyst, I can upload/enter treaty definitions (type, attachment point,
limit, capacity, participants, effective dates) so the system has current treaty data.
*Acceptance:* Treaty stored with type-specific fields validated (e.g., XoL requires
attachment + limit; QS requires cession %).

**US-2 — Policy/Exposure Ingestion**
As an Analyst, I can upload policies/exposures (CSV) with line of business, sum insured,
premium, geography/peril so they can be matched against treaties.
*Acceptance:* Invalid rows rejected with a clear reason; valid rows stored.

**US-3 — Automated Treaty Application**
As an Analyst, when I run cession processing, the system applies the correct treaty(ies)
to each policy per the rules engine and calculates ceded premium.
*Acceptance:* Every cession decision references the exact treaty and rule that fired;
result is written to AuditLog.

**US-4 — Blind Spot Detection**
As an Underwriting Manager, I can see a list of policies with no matching treaty or
that exceed all applicable treaty limits.
*Acceptance:* Blind-spot list is queryable/filterable and updates on each processing run.

**US-5 — Recoverables Tracking**
As a CFO, I can see outstanding recoverables and their age (days since loss reported).
*Acceptance:* Aging buckets (0-30/31-60/61-90/90+) shown on the dashboard.

**US-6 — Audit Trail**
As a Compliance Officer, I can view a log of every automated cession decision with
inputs, rule applied, and output, for a given policy.
*Acceptance:* Immutable log entries, filterable by policy/treaty/date range.

**US-7 — Dashboard**
As any user, I can see ceded ratio, total capital relief, count of blind-spot exposures,
and recoverables aging on one screen.

## 4. Data Model (draft)

- **Treaty**: id, name, type (QS/Surplus/XoL/Facultative), attachment_point, limit,
  capacity, cession_pct, participants[], effective_from, effective_to
- **Policy**: id, line_of_business, sum_insured, premium, geography, peril, effective_date
- **Cession**: id, policy_id (FK), treaty_id (FK), ceded_premium, ceded_limit, rule_applied, created_at
- **AuditLog**: id, cession_id (FK, nullable), action, rule_fired, input_snapshot (JSON),
  output_snapshot (JSON), created_at
- **Recoverable**: id, cession_id (FK), amount, loss_date, status, reported_at, resolved_at

## 5. API Endpoints (draft)

```
POST   /treaties               create treaty
GET    /treaties                list treaties
POST   /policies/upload         bulk upload (CSV)
POST   /cessions/run            run rules engine over unprocessed policies
GET    /cessions                list cession results
GET    /blind-spots             list uncovered/over-limit exposures
GET    /recoverables            list recoverables with aging
GET    /audit-log?policy_id=    audit trail for a policy
GET    /dashboard/summary       aggregate metrics for dashboard
```

## 6. Out of Scope (MVP)

- Real-time bureau/market data feeds
- Multi-currency FX conversion
- Full actuarial pricing/pricing curves
- Multi-tenant role-based auth (single internal role assumed)
- Automated payment/settlement execution (tracking only, not payment rails)

## 7. Acceptance Criteria for MVP Demo

- Upload a sample treaty set (at least one of each type)
- Upload a sample policy set (~50-100 rows) with intentional blind spots
- Run cession processing end-to-end
- Dashboard shows ceded ratio, capital relief, blind-spot count, recoverables aging
- Every cession has a traceable audit log entry
