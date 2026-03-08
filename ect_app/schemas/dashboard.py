from pydantic import BaseModel

from ect_app.schemas.filing import FilingWithEntity


class DashboardSummary(BaseModel):
    total_entities: int
    upcoming_deadlines_30d: int
    overdue_items: int
    good_standing_pct: float
    entities_by_jurisdiction: dict[str, int]
    entities_by_type: dict[str, int]
    upcoming_filings: list[FilingWithEntity]
