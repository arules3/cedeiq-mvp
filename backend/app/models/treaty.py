import enum
from datetime import date, datetime
from sqlalchemy import String, Numeric, Date, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base


class TreatyType(str, enum.Enum):
    """MVP scope: only the two 'mainstream' treaty types (see CLAUDE.md).
    Facultative and Surplus are documented but not implemented — see
    specs/mvp-spec.md §6 Out of Scope.
    """

    QUOTA_SHARE = "quota_share"
    EXCESS_OF_LOSS = "excess_of_loss"


class Treaty(Base):
    __tablename__ = "treaties"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    type: Mapped[TreatyType] = mapped_column(Enum(TreatyType))

    # Matching criteria — which policies this treaty applies to
    line_of_business: Mapped[str] = mapped_column(String(80))
    peril: Mapped[str | None] = mapped_column(String(80), nullable=True)  # None = all perils

    # Quota Share fields (used when type == QUOTA_SHARE)
    cession_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)  # e.g. 30.00 = 30%

    # Excess of Loss fields (used when type == EXCESS_OF_LOSS)
    attachment_point: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    limit: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)

    # Shared
    capacity: Mapped[float] = mapped_column(Numeric(15, 2))  # max total treaty can absorb
    effective_from: Mapped[date] = mapped_column(Date)
    effective_to: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Treaty {self.id} {self.name} ({self.type})>"
