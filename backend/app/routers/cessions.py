from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.treaty import Treaty
from app.models.policy import Policy
from app.models.cession import Cession
from app.models.audit_log import AuditLog
from app.schemas import CessionOut, BlindSpotOut
from app.services.rules_engine import process_policy, CessionResult, BlindSpot

router = APIRouter(tags=["cessions"])


@router.post("/cessions/run")
def run_cessions(db: Session = Depends(get_db)):
    """Process every policy that doesn't already have a cession or blind-spot
    audit entry. This is the endpoint that embodies spec US-3 and US-4:
    automated treaty application + blind spot detection, both fully audited.
    """
    treaties = db.query(Treaty).all()

    already_processed_ids = {
        row[0] for row in db.query(AuditLog.policy_id).filter(AuditLog.policy_id.isnot(None)).all()
    }
    policies = db.query(Policy).filter(~Policy.id.in_(already_processed_ids)).all()

    cessions_created, blind_spots_flagged = 0, 0

    for policy in policies:
        result = process_policy(policy, treaties)

        if isinstance(result, CessionResult):
            cession = Cession(
                policy_id=result.policy_id,
                treaty_id=result.treaty_id,
                ceded_premium=result.ceded_premium,
                ceded_exposure=result.ceded_exposure,
                rule_applied=result.rule_applied,
            )
            db.add(cession)
            db.flush()  # get cession.id before writing the audit log

            db.add(AuditLog(
                policy_id=policy.id,
                cession_id=cession.id,
                action="cession_applied",
                rule_fired=result.rule_applied,
                input_snapshot={
                    "policy_id": policy.id,
                    "sum_insured": float(policy.sum_insured),
                    "premium": float(policy.premium),
                },
                output_snapshot={
                    "treaty_id": result.treaty_id,
                    "ceded_premium": float(result.ceded_premium),
                    "ceded_exposure": float(result.ceded_exposure),
                },
            ))
            cessions_created += 1

        elif isinstance(result, BlindSpot):
            db.add(AuditLog(
                policy_id=policy.id,
                cession_id=None,
                action="blind_spot_flagged",
                rule_fired=result.reason,
                input_snapshot={"policy_id": policy.id, "sum_insured": float(policy.sum_insured)},
                output_snapshot={"flagged": True},
            ))
            blind_spots_flagged += 1

    db.commit()
    return {
        "policies_processed": len(policies),
        "cessions_created": cessions_created,
        "blind_spots_flagged": blind_spots_flagged,
    }


@router.get("/cessions", response_model=list[CessionOut])
def list_cessions(db: Session = Depends(get_db)):
    return db.query(Cession).all()


@router.get("/blind-spots", response_model=list[BlindSpotOut])
def list_blind_spots(db: Session = Depends(get_db)):
    rows = db.query(AuditLog).filter(AuditLog.action == "blind_spot_flagged").all()
    return [BlindSpotOut(policy_id=r.policy_id, reason=r.rule_fired) for r in rows]
