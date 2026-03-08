from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class OfficerBase(BaseModel):
    name: str
    title: str  # officer, director, both
    role: str  # CEO, CFO, Secretary, Director, etc.
    term_start: date | None = None
    term_end: date | None = None
    email: str | None = None


class OfficerCreate(OfficerBase):
    pass


class OfficerUpdate(BaseModel):
    name: str | None = None
    title: str | None = None
    role: str | None = None
    term_start: date | None = None
    term_end: date | None = None
    email: str | None = None


class OfficerRead(OfficerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_id: int
    created_at: datetime
