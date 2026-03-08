from __future__ import annotations

from datetime import datetime

from sqlalchemy import Float, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ect_app.database import Base


class EntityRelationship(Base):
    __tablename__ = "entity_relationships"
    __table_args__ = (UniqueConstraint("parent_id", "child_id", name="uq_parent_child"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("entities.id", ondelete="CASCADE"))
    child_id: Mapped[int] = mapped_column(ForeignKey("entities.id", ondelete="CASCADE"))
    relationship_type: Mapped[str] = mapped_column(String(50))  # subsidiary, branch, affiliate
    ownership_percentage: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    parent: Mapped["Entity"] = relationship(
        foreign_keys=[parent_id], back_populates="child_relationships"
    )
    child: Mapped["Entity"] = relationship(
        foreign_keys=[child_id], back_populates="parent_relationships"
    )
