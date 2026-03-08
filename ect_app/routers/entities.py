from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ect_app.database import get_db
from ect_app.schemas.entity import EntityCreate, EntityRead, EntitySummary, EntityUpdate
from ect_app.services import entity_service

router = APIRouter(prefix="/api/entities", tags=["entities"])


@router.get("/", response_model=list[EntitySummary])
def list_entities(
    skip: int = 0,
    limit: int = 100,
    jurisdiction: str | None = None,
    entity_type: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
) -> list[EntitySummary]:
    return entity_service.list_entities(
        db, skip=skip, limit=limit, jurisdiction=jurisdiction,
        entity_type=entity_type, search=search,
    )


@router.post("/", response_model=EntityRead, status_code=201)
def create_entity(data: EntityCreate, db: Session = Depends(get_db)) -> EntityRead:
    return entity_service.create_entity(db, data)


@router.get("/{entity_id}", response_model=EntityRead)
def get_entity(entity_id: int, db: Session = Depends(get_db)) -> EntityRead:
    entity = entity_service.get_entity(db, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity


@router.put("/{entity_id}", response_model=EntityRead)
def update_entity(
    entity_id: int, data: EntityUpdate, db: Session = Depends(get_db)
) -> EntityRead:
    entity = entity_service.update_entity(db, entity_id, data)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity


@router.delete("/{entity_id}", status_code=204)
def delete_entity(entity_id: int, db: Session = Depends(get_db)) -> None:
    if not entity_service.delete_entity(db, entity_id):
        raise HTTPException(status_code=404, detail="Entity not found")
