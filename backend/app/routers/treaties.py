from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.treaty import Treaty
from app.schemas import TreatyCreate, TreatyOut

router = APIRouter(prefix="/treaties", tags=["treaties"])


@router.post("", response_model=TreatyOut)
def create_treaty(payload: TreatyCreate, db: Session = Depends(get_db)):
    treaty = Treaty(**payload.model_dump())
    db.add(treaty)
    db.commit()
    db.refresh(treaty)
    return treaty


@router.get("", response_model=list[TreatyOut])
def list_treaties(db: Session = Depends(get_db)):
    return db.query(Treaty).all()
