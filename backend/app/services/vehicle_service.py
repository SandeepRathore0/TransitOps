from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories.vehicle_repo import VehicleRepository
from app.schemas.schemas import VehicleCreate, VehicleBase
from app.models.models import Vehicle

class VehicleService:
    def __init__(self, db: Session):
        self.repo = VehicleRepository(db)
    def get_all_vehicles(self):
        return self.repo.get_all()
    def get_vehicle(self, id: int):
        vehicle = self.repo.get_by_id(id)
        if not vehicle: raise HTTPException(status_code=404, detail="Vehicle not found")
        return vehicle
    def create_vehicle(self, data: VehicleCreate):
        if self.repo.get_by_reg_number(data.registration_number):
            raise HTTPException(status_code=409, detail="Registration number already exists")
        vehicle = Vehicle(**data.dict())
        return self.repo.create(vehicle)
    def update_vehicle(self, id: int, data: VehicleBase):
        vehicle = self.get_vehicle(id)
        for key, value in data.dict().items(): setattr(vehicle, key, value)
        return self.repo.update(vehicle)
    def delete_vehicle(self, id: int):
        vehicle = self.get_vehicle(id)
        self.repo.soft_delete(vehicle)
