from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ect_app.database import get_db
from ect_app.schemas.dashboard import DashboardSummary
from ect_app.services import dashboard_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/", response_model=DashboardSummary)
def dashboard(db: Session = Depends(get_db)) -> DashboardSummary:
    return dashboard_service.get_dashboard_summary(db)
