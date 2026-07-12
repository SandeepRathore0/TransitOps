from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.schemas import (
    MaintenanceResponse, MaintenanceCreate, MaintenanceUpdate, MaintenanceComplete
)
from app.services.maintenance_service import MaintenanceService
from app.middleware.rbac import RoleChecker
from app.models.models import User

router = APIRouter()

allow_read = RoleChecker(["Fleet Manager", "Dispatcher", "Safety Officer", "Financial Analyst"])
allow_manager = RoleChecker(["Fleet Manager"])

@router.get("/", response_model=List[MaintenanceResponse])
def get_all_maintenance(
    vehicle_id: int = None,
    status: str = None,
    db: Session = Depends(get_db),
    user: User = Depends(allow_read)
):
    return MaintenanceService(db).get_all_maintenance(vehicle_id, status)

@router.get("/{id}", response_model=MaintenanceResponse)
def get_maintenance(id: int, db: Session = Depends(get_db), user: User = Depends(allow_read)):
    return MaintenanceService(db).get_maintenance_log(id)

@router.post("/", response_model=MaintenanceResponse, status_code=status.HTTP_201_CREATED)
def create_maintenance(
    data: MaintenanceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(allow_manager)
):
    return MaintenanceService(db).create_maintenance(data, user.id)

@router.put("/{id}", response_model=MaintenanceResponse)
def update_maintenance(
    id: int,
    data: MaintenanceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(allow_manager)
):
    return MaintenanceService(db).update_maintenance(id, data, user.id)

@router.put("/{id}/complete", response_model=MaintenanceResponse)
def complete_maintenance(
    id: int,
    data: MaintenanceComplete,
    db: Session = Depends(get_db),
    user: User = Depends(allow_manager)
):
    return MaintenanceService(db).complete_maintenance(id, data, user.id)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_maintenance(
    id: int,
    db: Session = Depends(get_db),
    user: User = Depends(allow_manager)
):
    MaintenanceService(db).delete_maintenance(id)
