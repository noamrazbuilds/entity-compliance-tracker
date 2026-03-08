from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ect_app.database import Base


class NotificationSetting(Base):
    __tablename__ = "notification_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_id: Mapped[int | None] = mapped_column(
        ForeignKey("entities.id", ondelete="CASCADE"), nullable=True
    )
    channel: Mapped[str] = mapped_column(String(20))  # email, slack
    reminder_days_before: Mapped[str] = mapped_column(
        String(100), default="30,14,7"
    )  # comma-separated
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    recipients: Mapped[str | None] = mapped_column(Text)  # comma-separated emails or channels
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    entity: Mapped["Entity | None"] = relationship(back_populates="notification_settings")

    @property
    def reminder_days_list(self) -> list[int]:
        if not self.reminder_days_before:
            return []
        return [int(d.strip()) for d in self.reminder_days_before.split(",") if d.strip()]


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    filing_deadline_id: Mapped[int] = mapped_column(
        ForeignKey("filing_deadlines.id", ondelete="CASCADE")
    )
    channel: Mapped[str] = mapped_column(String(20))
    reminder_days_before: Mapped[int]
    sent_at: Mapped[datetime] = mapped_column(server_default=func.now())
    status: Mapped[str] = mapped_column(String(20))  # sent, failed
    error_message: Mapped[str | None] = mapped_column(Text)

    filing_deadline: Mapped["FilingDeadline"] = relationship(back_populates="notification_logs")
