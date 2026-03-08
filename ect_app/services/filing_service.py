from datetime import date, timedelta

from sqlalchemy.orm import Session

from ect_app.models.filing import FilingDeadline
from ect_app.schemas.filing import FilingDeadlineCreate, FilingDeadlineUpdate


def list_filings(db: Session, entity_id: int) -> list[FilingDeadline]:
    return (
        db.query(FilingDeadline)
        .filter(FilingDeadline.entity_id == entity_id)
        .order_by(FilingDeadline.due_date)
        .all()
    )


def get_filing(db: Session, filing_id: int) -> FilingDeadline | None:
    return db.query(FilingDeadline).filter(FilingDeadline.id == filing_id).first()


def create_filing(db: Session, entity_id: int, data: FilingDeadlineCreate) -> FilingDeadline:
    filing = FilingDeadline(entity_id=entity_id, **data.model_dump())
    db.add(filing)
    db.commit()
    db.refresh(filing)
    return filing


def update_filing(
    db: Session, filing_id: int, data: FilingDeadlineUpdate,
) -> FilingDeadline | None:
    filing = get_filing(db, filing_id)
    if not filing:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(filing, key, value)
    db.commit()
    db.refresh(filing)
    return filing


def delete_filing(db: Session, filing_id: int) -> bool:
    filing = get_filing(db, filing_id)
    if not filing:
        return False
    db.delete(filing)
    db.commit()
    return True


def get_upcoming_filings(db: Session, days_ahead: int = 90) -> list[FilingDeadline]:
    today = date.today()
    cutoff = today + timedelta(days=days_ahead)
    return (
        db.query(FilingDeadline)
        .filter(
            FilingDeadline.due_date >= today,
            FilingDeadline.due_date <= cutoff,
            FilingDeadline.status != "filed",
        )
        .order_by(FilingDeadline.due_date)
        .all()
    )


def get_overdue_filings(db: Session) -> list[FilingDeadline]:
    today = date.today()
    return (
        db.query(FilingDeadline)
        .filter(FilingDeadline.due_date < today, FilingDeadline.status != "filed")
        .order_by(FilingDeadline.due_date)
        .all()
    )


def mark_as_filed(
    db: Session, filing_id: int, filed_date: date | None = None,
) -> FilingDeadline | None:
    filing = get_filing(db, filing_id)
    if not filing:
        return None
    filing.status = "filed"
    filing.filed_date = filed_date or date.today()
    db.commit()
    db.refresh(filing)
    return filing


def update_overdue_statuses(db: Session) -> int:
    today = date.today()
    count = (
        db.query(FilingDeadline)
        .filter(
            FilingDeadline.due_date < today,
            FilingDeadline.status == "pending",
        )
        .update({"status": "overdue"})
    )
    db.commit()
    return count
