from datetime import date, datetime
from sqlalchemy import String, Numeric, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[int] = mapped_column(primary_key=True)
    policy_number: Mapped[str] = mapped_column(String(40), unique=True)
    line_of_business: Mapped[str] = mapped_column(String(80))
    peril: Mapped[str] = mapped_column(String(80))
    geography: Mapped[str] = mapped_column(String(80))
    sum_insured: Mapped[float] = mapped_column(Numeric(15, 2))
    premium: Mapped[float] = mapped_column(Numeric(15, 2))
    effective_date: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Policy {self.policy_number} {self.line_of_business}/{self.peril}>"
