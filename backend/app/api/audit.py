from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import AuditLog
from app.middleware.rbac import RoleChecker
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()
allow_admin = RoleChecker(["Admin", "Fleet Manager", "Safety Officer"])

class AuditResponse(BaseModel):
    id: int
    user_id: int
    action: str
    entity: str
    entity_id: Optional[int]
    timestamp: datetime
    ip_address: Optional[str]
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[AuditResponse], dependencies=[Depends(allow_admin)])
def get_audit_logs(db: Session = Depends(get_db), limit: int = 100):
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
