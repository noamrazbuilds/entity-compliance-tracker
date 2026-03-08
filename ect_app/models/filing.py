from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ect_app.database import Base


class FilingDeadline(Base):
    __tablename__ = "filing_deadlines"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_id: Mapped[int] = mapped_column(ForeignKey("entities.id", ondelete="CASCADE"))
    filing_type: Mapped[str] = mapped_column(String(100))
    jurisdiction: Mapped[str] = mapped_column(String(100))
    due_date: Mapped[date]
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, filed, overdue
    filed_date: Mapped[date | None]
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    entity: Mapped["Entity"] = relationship(back_populates="filing_deadlines")
    notification_logs: Mapped[list["NotificationLog"]] = relationship(
        back_populates="filing_deadline", cascade="all, delete-orphan"
    )
