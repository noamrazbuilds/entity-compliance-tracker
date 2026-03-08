from sqlalchemy.orm import Session

from ect_app.models.officer import OfficerDirector
from ect_app.schemas.officer import OfficerCreate, OfficerUpdate


def list_officers(db: Session, entity_id: int) -> list[OfficerDirector]:
    return (
        db.query(OfficerDirector)
        .filter(OfficerDirector.entity_id == entity_id)
        .order_by(OfficerDirector.name)
        .all()
    )


def get_officer(db: Session, officer_id: int) -> OfficerDirector | None:
    return db.query(OfficerDirector).filter(OfficerDirector.id == officer_id).first()


def create_officer(db: Session, entity_id: int, data: OfficerCreate) -> OfficerDirector:
    officer = OfficerDirector(entity_id=entity_id, **data.model_dump())
    db.add(officer)
    db.commit()
    db.refresh(officer)
    return officer


def update_officer(db: Session, officer_id: int, data: OfficerUpdate) -> OfficerDirector | None:
    officer = get_officer(db, officer_id)
    if not officer:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(officer, key, value)
    db.commit()
    db.refresh(officer)
    return officer


def delete_officer(db: Session, officer_id: int) -> bool:
    officer = get_officer(db, officer_id)
    if not officer:
        return False
    db.delete(officer)
    db.commit()
    return True
