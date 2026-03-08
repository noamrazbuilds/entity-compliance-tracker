from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ect_app.database import get_db
from ect_app.schemas.filing import (
    FilingDeadlineCreate,
    FilingDeadlineRead,
    FilingDeadlineUpdate,
    FilingWithEntity,
)
from ect_app.services import filing_service

router = APIRouter(tags=["filings"])


@router.get("/api/entities/{entity_id}/filings", response_model=list[FilingDeadlineRead])
def list_filings(entity_id: int, db: Session = Depends(get_db)) -> list[FilingDeadlineRead]:
    return filing_service.list_filings(db, entity_id)


@router.post(
    "/api/entities/{entity_id}/filings", response_model=FilingDeadlineRead, status_code=201
)
def create_filing(
    entity_id: int, data: FilingDeadlineCreate, db: Session = Depends(get_db)
) -> FilingDeadlineRead:
    return filing_service.create_filing(db, entity_id, data)


@router.put("/api/filings/{filing_id}", response_model=FilingDeadlineRead)
def update_filing(
    filing_id: int, data: FilingDeadlineUpdate, db: Session = Depends(get_db)
) -> FilingDeadlineRead:
    filing = filing_service.update_filing(db, filing_id, data)
    if not filing:
        raise HTTPException(status_code=404, detail="Filing not found")
    return filing


@router.delete("/api/filings/{filing_id}", status_code=204)
def delete_filing(filing_id: int, db: Session = Depends(get_db)) -> None:
    if not filing_service.delete_filing(db, filing_id):
        raise HTTPException(status_code=404, detail="Filing not found")


@router.get("/api/filings/upcoming", response_model=list[FilingWithEntity])
def upcoming_filings(
    days: int = 90, db: Session = Depends(get_db)
) -> list[FilingWithEntity]:
    filings = filing_service.get_upcoming_filings(db, days_ahead=days)
    return [
        FilingWithEntity(
            id=f.id,
            entity_id=f.entity_id,
            filing_type=f.filing_type,
            jurisdiction=f.jurisdiction,
            due_date=f.due_date,
            status=f.status,
            filed_date=f.filed_date,
            notes=f.notes,
            created_at=f.created_at,
            entity_name=f.entity.name,
        )
        for f in filings
    ]


@router.get("/api/filings/overdue", response_model=list[FilingWithEntity])
def overdue_filings(db: Session = Depends(get_db)) -> list[FilingWithEntity]:
    filings = filing_service.get_overdue_filings(db)
    return [
        FilingWithEntity(
            id=f.id,
            entity_id=f.entity_id,
            filing_type=f.filing_type,
            jurisdiction=f.jurisdiction,
            due_date=f.due_date,
            status=f.status,
            filed_date=f.filed_date,
            notes=f.notes,
            created_at=f.created_at,
            entity_name=f.entity.name,
        )
        for f in filings
    ]


@router.post("/api/filings/{filing_id}/mark-filed", response_model=FilingDeadlineRead)
def mark_filed(
    filing_id: int,
    filed_date: date | None = None,
    db: Session = Depends(get_db),
) -> FilingDeadlineRead:
    filing = filing_service.mark_as_filed(db, filing_id, filed_date)
    if not filing:
        raise HTTPException(status_code=404, detail="Filing not found")
    return filing
