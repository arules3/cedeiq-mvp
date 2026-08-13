from datetime import datetime
from sqlalchemy import ForeignKey, Numeric, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base


class Cession(Base):
    """A cession is the recorded result of applying one treaty to one policy.
    Created by the rules engine (see services/rules_engine.py), never by hand.
    """

    __tablename__ = "cessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    policy_id: Mapped[int] = mapped_column(ForeignKey("policies.id"))
    treaty_id: Mapped[int] = mapped_column(ForeignKey("treaties.id"))

    ceded_premium: Mapped[float] = mapped_column(Numeric(15, 2))
    ceded_exposure: Mapped[float] = mapped_column(Numeric(15, 2))  # sum insured ceded
    rule_applied: Mapped[str] = mapped_column(String(200))  # human-readable rule description
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Cession policy={self.policy_id} treaty={self.treaty_id}>"
