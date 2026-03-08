from sqlalchemy import or_
from sqlalchemy.orm import Session

from ect_app.models.entity import Entity
from ect_app.schemas.entity import EntityCreate, EntityUpdate


def list_entities(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    jurisdiction: str | None = None,
    entity_type: str | None = None,
    search: str | None = None,
) -> list[Entity]:
    query = db.query(Entity)
    if jurisdiction:
        query = query.filter(Entity.jurisdiction == jurisdiction)
    if entity_type:
        query = query.filter(Entity.entity_type == entity_type)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(Entity.name.ilike(pattern), Entity.jurisdiction.ilike(pattern))
        )
    return query.order_by(Entity.name).offset(skip).limit(limit).all()


def get_entity(db: Session, entity_id: int) -> Entity | None:
    return db.query(Entity).filter(Entity.id == entity_id).first()


def create_entity(db: Session, data: EntityCreate) -> Entity:
    entity = Entity(**data.model_dump())
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


def update_entity(db: Session, entity_id: int, data: EntityUpdate) -> Entity | None:
    entity = get_entity(db, entity_id)
    if not entity:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(entity, key, value)
    db.commit()
    db.refresh(entity)
    return entity


def delete_entity(db: Session, entity_id: int) -> bool:
    entity = get_entity(db, entity_id)
    if not entity:
        return False
    db.delete(entity)
    db.commit()
    return True
