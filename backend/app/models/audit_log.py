from datetime import datetime
from sqlalchemy import ForeignKey, String, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base


class AuditLog(Base):
    """Every automated treaty-application decision must write one of these —
    CLAUDE.md steering rule 2, no exceptions. This is what gives compliance
    officers a traceable record (spec US-6).
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    policy_id: Mapped[int | None] = mapped_column(ForeignKey("policies.id"), nullable=True)
    cession_id: Mapped[int | None] = mapped_column(ForeignKey("cessions.id"), nullable=True)

    action: Mapped[str] = mapped_column(String(80))  # e.g. "cession_applied", "blind_spot_flagged"
    rule_fired: Mapped[str] = mapped_column(String(200))
    input_snapshot: Mapped[dict] = mapped_column(JSON)
    output_snapshot: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} policy={self.policy_id}>"
