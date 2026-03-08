from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ect_app.database import get_db
from ect_app.schemas.officer import OfficerCreate, OfficerRead, OfficerUpdate
from ect_app.services import officer_service

router = APIRouter(tags=["officers"])


@router.get("/api/entities/{entity_id}/officers", response_model=list[OfficerRead])
def list_officers(entity_id: int, db: Session = Depends(get_db)) -> list[OfficerRead]:
    return officer_service.list_officers(db, entity_id)


@router.post(
    "/api/entities/{entity_id}/officers", response_model=OfficerRead, status_code=201
)
def create_officer(
    entity_id: int, data: OfficerCreate, db: Session = Depends(get_db)
) -> OfficerRead:
    return officer_service.create_officer(db, entity_id, data)


@router.put("/api/officers/{officer_id}", response_model=OfficerRead)
def update_officer(
    officer_id: int, data: OfficerUpdate, db: Session = Depends(get_db)
) -> OfficerRead:
    officer = officer_service.update_officer(db, officer_id, data)
    if not officer:
        raise HTTPException(status_code=404, detail="Officer not found")
    return officer


@router.delete("/api/officers/{officer_id}", status_code=204)
def delete_officer(officer_id: int, db: Session = Depends(get_db)) -> None:
    if not officer_service.delete_officer(db, officer_id):
        raise HTTPException(status_code=404, detail="Officer not found")
