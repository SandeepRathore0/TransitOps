from sqlalchemy.orm import Session
from app.models.models import Vehicle
from .base_repo import BaseRepository
from datetime import datetime

class VehicleRepository(BaseRepository):
    def get_by_id(self, id: int):
        return self.db.query(Vehicle).filter(Vehicle.id == id, Vehicle.deleted_at.is_(None)).first()
    def get_by_reg_number(self, reg_number: str):
        return self.db.query(Vehicle).filter(Vehicle.registration_number == reg_number, Vehicle.deleted_at.is_(None)).first()
    def get_all(self):
        return self.db.query(Vehicle).filter(Vehicle.deleted_at.is_(None)).all()
    def create(self, vehicle: Vehicle):
        self.db.add(vehicle)
        self.db.commit()
        self.db.refresh(vehicle)
        return vehicle
    def update(self, vehicle: Vehicle):
        self.db.commit()
        self.db.refresh(vehicle)
        return vehicle
    def soft_delete(self, vehicle: Vehicle):
        vehicle.deleted_at = datetime.utcnow()
        self.db.commit()
