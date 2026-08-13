from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.audit_log import AuditLog
from app.schemas import AuditLogOut

router = APIRouter(prefix="/audit-log", tags=["audit-log"])


@router.get("", response_model=list[AuditLogOut])
def get_audit_log(policy_id: int | None = Query(None), db: Session = Depends(get_db)):
    q = db.query(AuditLog)
    if policy_id is not None:
        q = q.filter(AuditLog.policy_id == policy_id)
    return q.order_by(AuditLog.created_at.desc()).all()
