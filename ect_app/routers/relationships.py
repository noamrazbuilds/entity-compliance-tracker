from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ect_app.database import get_db
from ect_app.schemas.relationship import RelationshipCreate, RelationshipRead
from ect_app.services import relationship_service

router = APIRouter(prefix="/api/relationships", tags=["relationships"])


@router.get("/org-tree")
def org_tree(db: Session = Depends(get_db)) -> list[dict]:
    return relationship_service.get_org_tree(db)


@router.post("/", response_model=RelationshipRead, status_code=201)
def create_relationship(
    data: RelationshipCreate, db: Session = Depends(get_db)
) -> RelationshipRead:
    try:
        return relationship_service.create_relationship(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{relationship_id}", status_code=204)
def delete_relationship(relationship_id: int, db: Session = Depends(get_db)) -> None:
    if not relationship_service.delete_relationship(db, relationship_id):
        raise HTTPException(status_code=404, detail="Relationship not found")


@router.get("/entity/{entity_id}")
def entity_relationships(entity_id: int, db: Session = Depends(get_db)) -> dict:
    rels = relationship_service.list_relationships(db, entity_id)
    return {
        "children": [RelationshipRead.model_validate(r) for r in rels["children"]],
        "parents": [RelationshipRead.model_validate(r) for r in rels["parents"]],
    }
