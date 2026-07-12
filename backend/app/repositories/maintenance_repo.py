from sqlalchemy.orm import Session
from app.models.models import MaintenanceLog
from .base_repo import BaseRepository
from datetime import datetime

class MaintenanceRepository(BaseRepository):
    def get_by_id(self, id: int) -> MaintenanceLog:
        return self.db.query(MaintenanceLog).filter(MaintenanceLog.id == id, MaintenanceLog.deleted_at.is_(None)).first()

    def get_all(self, vehicle_id: int = None, status: str = None):
        query = self.db.query(MaintenanceLog).filter(MaintenanceLog.deleted_at.is_(None))
        if vehicle_id:
            query = query.filter(MaintenanceLog.vehicle_id == vehicle_id)
        if status:
            query = query.filter(MaintenanceLog.status == status)
        return query.order_by(MaintenanceLog.start_date.desc()).all()

    def create(self, log: MaintenanceLog) -> MaintenanceLog:
        self.db.add(log)
        self.db.flush()
        return log

    def update(self, log: MaintenanceLog) -> MaintenanceLog:
        self.db.flush()
        return log

    def soft_delete(self, log: MaintenanceLog):
        log.deleted_at = datetime.utcnow()
        self.db.flush()

    def get_active_maintenance_for_vehicle(self, vehicle_id: int) -> MaintenanceLog:
        return self.db.query(MaintenanceLog).filter(
            MaintenanceLog.vehicle_id == vehicle_id,
            MaintenanceLog.status.in_(["Scheduled", "In Progress"]),
            MaintenanceLog.deleted_at.is_(None)
        ).first()
