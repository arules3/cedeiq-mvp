import csv
import io

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.policy import Policy
from app.schemas import PolicyCreate, PolicyOut

router = APIRouter(prefix="/policies", tags=["policies"])

REQUIRED_COLUMNS = {
    "policy_number", "line_of_business", "peril", "geography",
    "sum_insured", "premium", "effective_date",
}


@router.post("", response_model=PolicyOut)
def create_policy(payload: PolicyCreate, db: Session = Depends(get_db)):
    policy = Policy(**payload.model_dump())
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


@router.post("/upload")
def upload_policies(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Bulk CSV upload (spec US-2). Invalid rows are rejected with a reason,
    valid rows are inserted. Returns a summary, not a 500, on partial failure —
    an analyst uploading a real book of business needs to see per-row results.
    """
    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))

    if not REQUIRED_COLUMNS.issubset(set(reader.fieldnames or [])):
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        raise HTTPException(400, f"CSV missing required columns: {missing}")

    inserted, rejected = 0, []
    for i, row in enumerate(reader, start=2):  # row 1 is the header
        try:
            policy = Policy(
                policy_number=row["policy_number"],
                line_of_business=row["line_of_business"],
                peril=row["peril"],
                geography=row["geography"],
                sum_insured=float(row["sum_insured"]),
                premium=float(row["premium"]),
                effective_date=row["effective_date"],
            )
            db.add(policy)
            db.flush()  # surface integrity errors (e.g. duplicate policy_number) per-row
            inserted += 1
        except Exception as e:
            db.rollback()
            rejected.append({"row": i, "reason": str(e)})

    db.commit()
    return {"inserted": inserted, "rejected": rejected}


@router.get("", response_model=list[PolicyOut])
def list_policies(db: Session = Depends(get_db)):
    return db.query(Policy).all()
