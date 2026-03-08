from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ect_app.database import Base


class OfficerDirector(Base):
    __tablename__ = "officers_directors"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_id: Mapped[int] = mapped_column(ForeignKey("entities.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(50))  # officer, director, both
    role: Mapped[str] = mapped_column(String(100))  # CEO, CFO, Secretary, Director, etc.
    term_start: Mapped[date | None]
    term_end: Mapped[date | None]
    email: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    entity: Mapped["Entity"] = relationship(back_populates="officers")
