from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.schemas import FuelLogResponse, FuelLogCreate
from app.services.fuel_service import FuelService
from app.middleware.rbac import RoleChecker
from app.models.models import User

router = APIRouter()

allow_read = RoleChecker(["Fleet Manager", "Dispatcher", "Safety Officer", "Financial Analyst"])
allow_write = RoleChecker(["Fleet Manager", "Dispatcher", "Financial Analyst"])
allow_manager = RoleChecker(["Fleet Manager"])

@router.get("/", response_model=List[FuelLogResponse])
def get_all_fuel(
    vehicle_id: int = None,
    trip_id: int = None,
    driver_id: int = None,
    db: Session = Depends(get_db),
    user: User = Depends(allow_read)
):
    return FuelService(db).get_all_fuel(vehicle_id, trip_id, driver_id)

@router.get("/{id}", response_model=FuelLogResponse)
def get_fuel_log(id: int, db: Session = Depends(get_db), user: User = Depends(allow_read)):
    return FuelService(db).get_fuel_log(id)

@router.post("/", response_model=FuelLogResponse, status_code=status.HTTP_201_CREATED)
def create_fuel_log(
    data: FuelLogCreate,
    db: Session = Depends(get_db),
    user: User = Depends(allow_write)
):
    return FuelService(db).create_fuel_log(data)

@router.put("/{id}", response_model=FuelLogResponse)
def update_fuel_log(
    id: int,
    data: FuelLogCreate,
    db: Session = Depends(get_db),
    user: User = Depends(allow_manager)
):
    return FuelService(db).update_fuel_log(id, data)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fuel_log(
    id: int,
    db: Session = Depends(get_db),
    user: User = Depends(allow_manager)
):
    FuelService(db).delete_fuel_log(id)
