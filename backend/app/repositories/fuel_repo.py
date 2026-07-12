from sqlalchemy.orm import Session
from app.models.models import FuelLog
from .base_repo import BaseRepository

class FuelRepository(BaseRepository):
    def get_by_id(self, id: int) -> FuelLog:
        return self.db.query(FuelLog).filter(FuelLog.id == id).first()

    def get_all(self, vehicle_id: int = None, trip_id: int = None, driver_id: int = None):
        query = self.db.query(FuelLog)
        if vehicle_id:
            query = query.filter(FuelLog.vehicle_id == vehicle_id)
        if trip_id:
            query = query.filter(FuelLog.trip_id == trip_id)
        if driver_id:
            query = query.filter(FuelLog.driver_id == driver_id)
        return query.order_by(FuelLog.fuel_date.desc()).all()

    def create(self, log: FuelLog) -> FuelLog:
        self.db.add(log)
        self.db.flush()
        return log

    def update(self, log: FuelLog) -> FuelLog:
        self.db.flush()
        return log

    def delete(self, log: FuelLog):
        self.db.delete(log)
        self.db.flush()

    def get_latest_for_vehicle(self, vehicle_id: int) -> FuelLog:
        return self.db.query(FuelLog).filter(FuelLog.vehicle_id == vehicle_id).order_by(FuelLog.fuel_date.desc(), FuelLog.id.desc()).first()
