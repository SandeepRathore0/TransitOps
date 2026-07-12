from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.schemas import DriverResponse, DriverCreate, DriverBase
from app.services.driver_service import DriverService
from app.middleware.rbac import RoleChecker
from app.models.models import User

router = APIRouter()
allow_read = RoleChecker(["Admin", "Fleet Manager", "Dispatcher", "Safety Officer", "Financial Analyst"])
allow_write = RoleChecker(["Admin", "Fleet Manager"])

@router.get("/", response_model=List[DriverResponse], dependencies=[Depends(allow_read)])
def get_drivers(db: Session = Depends(get_db)):
    return DriverService(db).get_all_drivers()

@router.post("/", response_model=DriverResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(allow_write)])
def create_driver(data: DriverCreate, db: Session = Depends(get_db)):
    return DriverService(db).create_driver(data)

@router.put("/{id}", response_model=DriverResponse, dependencies=[Depends(allow_write)])
def update_driver(id: int, data: DriverBase, db: Session = Depends(get_db)):
    return DriverService(db).update_driver(id, data)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(allow_write)])
def delete_driver(id: int, db: Session = Depends(get_db)):
    DriverService(db).delete_driver(id)
