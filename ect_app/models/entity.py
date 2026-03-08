from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ect_app.database import Base


class Entity(Base):
    __tablename__ = "entities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    jurisdiction: Mapped[str] = mapped_column(String(100))
    entity_type: Mapped[str] = mapped_column(String(50))
    formation_date: Mapped[date | None]
    registered_agent_name: Mapped[str | None] = mapped_column(String(255))
    registered_agent_address: Mapped[str | None] = mapped_column(Text)
    good_standing: Mapped[bool] = mapped_column(default=True)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    # Relationships
    officers: Mapped[list["OfficerDirector"]] = relationship(
        back_populates="entity", cascade="all, delete-orphan"
    )
    filing_deadlines: Mapped[list["FilingDeadline"]] = relationship(
        back_populates="entity", cascade="all, delete-orphan"
    )
    documents: Mapped[list["Document"]] = relationship(
        back_populates="entity", cascade="all, delete-orphan"
    )
    parent_relationships: Mapped[list["EntityRelationship"]] = relationship(
        foreign_keys="EntityRelationship.child_id", back_populates="child"
    )
    child_relationships: Mapped[list["EntityRelationship"]] = relationship(
        foreign_keys="EntityRelationship.parent_id", back_populates="parent"
    )
    notification_settings: Mapped[list["NotificationSetting"]] = relationship(
        back_populates="entity", cascade="all, delete-orphan"
    )
