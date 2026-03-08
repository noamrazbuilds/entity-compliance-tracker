from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from ect_app.schemas.document import DocumentRead
from ect_app.schemas.filing import FilingDeadlineRead
from ect_app.schemas.officer import OfficerRead

ENTITY_TYPES = [
    "corporation",
    "llc",
    "lp",
    "llp",
    "limited_company",
    "sole_proprietorship",
    "partnership",
    "nonprofit",
    "trust",
    "other",
]


class EntityBase(BaseModel):
    name: str
    jurisdiction: str
    entity_type: str
    formation_date: date | None = None
    registered_agent_name: str | None = None
    registered_agent_address: str | None = None
    good_standing: bool = True
    notes: str | None = None


class EntityCreate(EntityBase):
    pass


class EntityUpdate(BaseModel):
    name: str | None = None
    jurisdiction: str | None = None
    entity_type: str | None = None
    formation_date: date | None = None
    registered_agent_name: str | None = None
    registered_agent_address: str | None = None
    good_standing: bool | None = None
    notes: str | None = None


class EntitySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    jurisdiction: str
    entity_type: str
    good_standing: bool
    formation_date: date | None = None


class EntityRead(EntityBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    officers: list[OfficerRead] = []
    filing_deadlines: list[FilingDeadlineRead] = []
    documents: list[DocumentRead] = []
