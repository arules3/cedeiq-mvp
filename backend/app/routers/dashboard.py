from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.policy import Policy
from app.models.treaty import Treaty
from app.models.cession import Cession
from app.models.audit_log import AuditLog
from app.models.recoverable import Recoverable
from app.schemas import DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db)):
    total_policies = db.query(func.count(Policy.id)).scalar() or 0
    total_treaties = db.query(func.count(Treaty.id)).scalar() or 0
    total_cessions = db.query(func.count(Cession.id)).scalar() or 0

    total_ceded_premium = db.query(func.sum(Cession.ceded_premium)).scalar() or 0
    total_ceded_exposure = db.query(func.sum(Cession.ceded_exposure)).scalar() or 0
    total_gross_premium = db.query(func.sum(Policy.premium)).scalar() or 0

    ceded_ratio = (
        float(total_ceded_premium) / float(total_gross_premium)
        if total_gross_premium else 0.0
    )

    blind_spot_count = (
        db.query(func.count(AuditLog.id))
        .filter(AuditLog.action == "blind_spot_flagged")
        .scalar() or 0
    )

    outstanding_recoverables = (
        db.query(func.sum(Recoverable.amount))
        .filter(Recoverable.status == "outstanding")
        .scalar() or 0
    )

    return DashboardSummary(
        total_policies=total_policies,
        total_treaties=total_treaties,
        total_cessions=total_cessions,
        total_ceded_premium=float(total_ceded_premium),
        total_ceded_exposure=float(total_ceded_exposure),
        ceded_ratio=round(ceded_ratio, 4),
        blind_spot_count=blind_spot_count,
        outstanding_recoverables=float(outstanding_recoverables),
    )
