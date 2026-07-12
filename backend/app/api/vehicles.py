from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.schemas import VehicleResponse, VehicleCreate, VehicleBase
from app.services.vehicle_service import VehicleService
from app.middleware.rbac import RoleChecker
from app.models.models import User

router = APIRouter()
allow_manager = RoleChecker(["Fleet Manager"])

@router.get("/", response_model=List[VehicleResponse])
def get_vehicles(db: Session = Depends(get_db)):
    return VehicleService(db).get_all_vehicles()

@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(data: VehicleCreate, db: Session = Depends(get_db)):
    return VehicleService(db).create_vehicle(data)

@router.put("/{id}", response_model=VehicleResponse)
def update_vehicle(id: int, data: VehicleBase, db: Session = Depends(get_db)):
    return VehicleService(db).update_vehicle(id, data)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(id: int, db: Session = Depends(get_db)):
    VehicleService(db).delete_vehicle(id)
