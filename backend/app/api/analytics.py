from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.analytics_service import AnalyticsService
from app.services.report_service import ReportService
from app.middleware.rbac import RoleChecker

router = APIRouter()
allow_admin_analyst = RoleChecker(["Admin", "Fleet Manager", "Financial Analyst"])

@router.get("/kpis", dependencies=[Depends(allow_admin_analyst)])
def get_kpis(db: Session = Depends(get_db)):
    return AnalyticsService.get_dashboard_kpis(db)

@router.get("/export/{entity}", dependencies=[Depends(allow_admin_analyst)])
def export_csv(entity: str, db: Session = Depends(get_db)):
    return ReportService.generate_csv(db, entity)
