from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, date
from app.repositories.maintenance_repo import MaintenanceRepository
from app.repositories.vehicle_repo import VehicleRepository
from app.models.models import MaintenanceLog, Vehicle, ActivityLog
from app.schemas.schemas import MaintenanceCreate, MaintenanceUpdate, MaintenanceComplete

class MaintenanceService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = MaintenanceRepository(db)
        self.vehicle_repo = VehicleRepository(db)

    def get_maintenance_log(self, id: int) -> MaintenanceLog:
        log = self.repo.get_by_id(id)
        if not log:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance log not found")
        return log

    def get_all_maintenance(self, vehicle_id: int = None, status_filter: str = None):
        return self.repo.get_all(vehicle_id, status_filter)

    def create_maintenance(self, data: MaintenanceCreate, user_id: int) -> MaintenanceLog:
        vehicle = self.vehicle_repo.get_by_id(data.vehicle_id)
        if not vehicle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
        if vehicle.status == "Retired":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot schedule maintenance for a retired vehicle")

        # Check for duplicate active maintenance
        active = self.repo.get_active_maintenance_for_vehicle(data.vehicle_id)
        if active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Vehicle already under maintenance or scheduled"
            )

        log = MaintenanceLog(
            vehicle_id=data.vehicle_id,
            maintenance_type=data.maintenance_type,
            description=data.description,
            workshop_name=data.workshop_name,
            estimated_cost=data.estimated_cost,
            actual_cost=data.actual_cost,
            start_date=data.start_date,
            end_date=data.end_date,
            status=data.status,
            remarks=data.remarks,
            created_by=user_id
        )

        try:
            if log.status == "In Progress":
                vehicle.status = "In Shop"
                
            self.repo.create(log)

            # Activity Log
            act_log = ActivityLog(
                user_id=user_id,
                action="Maintenance Scheduled" if log.status == "Scheduled" else "Maintenance Started",
                entity_type="Vehicle",
                entity_id=vehicle.id,
                details=f"Maintenance ({log.maintenance_type}) created for {vehicle.registration_number} at {log.workshop_name}"
            )
            self.db.add(act_log)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create maintenance: {str(e)}")

        self.db.refresh(log)
        return log

    def update_maintenance(self, id: int, data: MaintenanceUpdate, user_id: int) -> MaintenanceLog:
        log = self.get_maintenance_log(id)
        if log.status in ("Completed", "Cancelled"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot edit a completed or cancelled maintenance log")

        vehicle = self.vehicle_repo.get_by_id(log.vehicle_id)
        
        update_data = data.dict(exclude_unset=True)
        old_status = log.status
        
        for key, value in update_data.items():
            setattr(log, key, value)
            
        log.updated_by = user_id

        try:
            if old_status != log.status:
                if log.status == "In Progress":
                    vehicle.status = "In Shop"
                elif log.status == "Completed":
                    log.end_date = date.today()
                    if vehicle.status == "In Shop":
                        vehicle.status = "Available"
                elif log.status == "Cancelled":
                    if vehicle.status == "In Shop":
                        vehicle.status = "Available"

            self.repo.update(log)

            act_log = ActivityLog(
                user_id=user_id,
                action="Maintenance Updated",
                entity_type="Vehicle",
                entity_id=vehicle.id,
                details=f"Maintenance for {vehicle.registration_number} status updated to {log.status}"
            )
            self.db.add(act_log)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update maintenance: {str(e)}")

        self.db.refresh(log)
        return log

    def complete_maintenance(self, id: int, data: MaintenanceComplete, user_id: int) -> MaintenanceLog:
        log = self.get_maintenance_log(id)
        if log.status in ("Completed", "Cancelled"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maintenance already completed or cancelled")

        vehicle = self.vehicle_repo.get_by_id(log.vehicle_id)
        if not vehicle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")

        log.status = "Completed"
        log.actual_cost = data.actual_cost
        log.end_date = data.end_date
        log.remarks = data.remarks or log.remarks
        log.updated_by = user_id

        try:
            if vehicle.status == "In Shop":
                vehicle.status = "Available" if vehicle.status != "Retired" else "Retired"

            self.repo.update(log)

            act_log = ActivityLog(
                user_id=user_id,
                action="Maintenance Completed",
                entity_type="Vehicle",
                entity_id=vehicle.id,
                details=f"Maintenance for {vehicle.registration_number} completed. Actual cost: {log.actual_cost}"
            )
            self.db.add(act_log)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to complete maintenance: {str(e)}")

        self.db.refresh(log)
        return log

    def delete_maintenance(self, id: int):
        log = self.get_maintenance_log(id)
        if log.status == "In Progress":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete maintenance that is currently In Progress")

        try:
            self.repo.soft_delete(log)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete maintenance log: {str(e)}")
