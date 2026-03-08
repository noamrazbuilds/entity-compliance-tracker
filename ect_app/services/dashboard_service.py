from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from ect_app.models.entity import Entity
from ect_app.models.filing import FilingDeadline
from ect_app.schemas.dashboard import DashboardSummary
from ect_app.schemas.filing import FilingWithEntity


def get_dashboard_summary(db: Session) -> DashboardSummary:
    today = date.today()
    cutoff_30d = today + timedelta(days=30)

    total = db.query(func.count(Entity.id)).scalar() or 0
    good_standing_count = (
        db.query(func.count(Entity.id)).filter(Entity.good_standing.is_(True)).scalar() or 0
    )
    good_standing_pct = (good_standing_count / total * 100) if total > 0 else 0.0

    upcoming_count = (
        db.query(func.count(FilingDeadline.id))
        .filter(
            FilingDeadline.due_date >= today,
            FilingDeadline.due_date <= cutoff_30d,
            FilingDeadline.status != "filed",
        )
        .scalar()
        or 0
    )

    overdue_count = (
        db.query(func.count(FilingDeadline.id))
        .filter(FilingDeadline.due_date < today, FilingDeadline.status != "filed")
        .scalar()
        or 0
    )

    # Entities by jurisdiction
    jurisdiction_rows = (
        db.query(Entity.jurisdiction, func.count(Entity.id))
        .group_by(Entity.jurisdiction)
        .all()
    )
    by_jurisdiction = {row[0]: row[1] for row in jurisdiction_rows}

    # Entities by type
    type_rows = (
        db.query(Entity.entity_type, func.count(Entity.id))
        .group_by(Entity.entity_type)
        .all()
    )
    by_type = {row[0]: row[1] for row in type_rows}

    # Upcoming filings with entity names
    upcoming_filings_query = (
        db.query(FilingDeadline, Entity.name)
        .join(Entity, FilingDeadline.entity_id == Entity.id)
        .filter(
            FilingDeadline.due_date >= today,
            FilingDeadline.due_date <= cutoff_30d,
            FilingDeadline.status != "filed",
        )
        .order_by(FilingDeadline.due_date)
        .limit(20)
        .all()
    )

    upcoming_filings = []
    for filing, entity_name in upcoming_filings_query:
        upcoming_filings.append(
            FilingWithEntity(
                id=filing.id,
                entity_id=filing.entity_id,
                filing_type=filing.filing_type,
                jurisdiction=filing.jurisdiction,
                due_date=filing.due_date,
                status=filing.status,
                filed_date=filing.filed_date,
                notes=filing.notes,
                created_at=filing.created_at,
                entity_name=entity_name,
            )
        )

    return DashboardSummary(
        total_entities=total,
        upcoming_deadlines_30d=upcoming_count,
        overdue_items=overdue_count,
        good_standing_pct=round(good_standing_pct, 1),
        entities_by_jurisdiction=by_jurisdiction,
        entities_by_type=by_type,
        upcoming_filings=upcoming_filings,
    )
