from datetime import date, datetime
from sqlalchemy import ForeignKey, Numeric, String, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base


class Recoverable(Base):
    """Simplified for the 1-day MVP scope: flat list, no aging-bucket logic
    (see specs/mvp-spec.md — aging buckets cut from scope)."""

    __tablename__ = "recoverables"

    id: Mapped[int] = mapped_column(primary_key=True)
    cession_id: Mapped[int] = mapped_column(ForeignKey("cessions.id"))
    amount: Mapped[float] = mapped_column(Numeric(15, 2))
    loss_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="outstanding")  # outstanding | recovered
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Recoverable cession={self.cession_id} {self.status}>"
