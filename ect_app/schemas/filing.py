from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

FILING_STATUSES = ["pending", "filed", "overdue"]


class FilingDeadlineBase(BaseModel):
    filing_type: str
    jurisdiction: str
    due_date: date
    status: str = "pending"
    filed_date: date | None = None
    notes: str | None = None


class FilingDeadlineCreate(FilingDeadlineBase):
    pass


class FilingDeadlineUpdate(BaseModel):
    filing_type: str | None = None
    jurisdiction: str | None = None
    due_date: date | None = None
    status: str | None = None
    filed_date: date | None = None
    notes: str | None = None


class FilingDeadlineRead(FilingDeadlineBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_id: int
    created_at: datetime


class FilingWithEntity(FilingDeadlineRead):
    entity_name: str
