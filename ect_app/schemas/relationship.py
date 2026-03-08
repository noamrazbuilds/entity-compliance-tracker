from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator


class RelationshipCreate(BaseModel):
    parent_id: int
    child_id: int
    relationship_type: str = "subsidiary"
    ownership_percentage: float | None = None

    @model_validator(mode="after")
    def parent_not_child(self) -> "RelationshipCreate":
        if self.parent_id == self.child_id:
            raise ValueError("An entity cannot be its own parent")
        return self


class RelationshipRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    parent_id: int
    child_id: int
    relationship_type: str
    ownership_percentage: float | None = None
    created_at: datetime


class OrgTreeNode(BaseModel):
    name: str
    entity_id: int
    entity_type: str
    jurisdiction: str
    good_standing: bool
    ownership_percentage: float | None = None
    relationship_type: str | None = None
    children: list["OrgTreeNode"] = []
