from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, date
from app.repositories.fuel_repo import FuelRepository
from app.repositories.vehicle_repo import VehicleRepository
from app.repositories.trip_repo import TripRepository
from app.repositories.driver_repo import DriverRepository
from app.models.models import FuelLog, ActivityLog
from app.schemas.schemas import FuelLogCreate

class FuelService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = FuelRepository(db)
        self.vehicle_repo = VehicleRepository(db)
        self.trip_repo = TripRepository(db)
        self.driver_repo = DriverRepository(db)

    def get_fuel_log(self, id: int) -> FuelLog:
        log = self.repo.get_by_id(id)
        if not log:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fuel log not found")
        return log

    def get_all_fuel(self, vehicle_id: int = None, trip_id: int = None, driver_id: int = None):
        return self.repo.get_all(vehicle_id, trip_id, driver_id)

    def create_fuel_log(self, data: FuelLogCreate) -> FuelLog:
        # Validations
        if data.liters <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fuel liters must be positive")
        if data.cost_per_liter <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cost per liter must be positive")
        if data.fuel_date > date.today():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fuel date cannot be in the future")

        vehicle = self.vehicle_repo.get_by_id(data.vehicle_id)
        if not vehicle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")

        # Odometer check against previous fuel logs and current vehicle odometer
        latest_fuel = self.repo.get_latest_for_vehicle(data.vehicle_id)
        if latest_fuel and data.odometer <= latest_fuel.odometer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Odometer must be greater than previous fuel log reading of {latest_fuel.odometer} km"
            )
        if data.odometer < vehicle.odometer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Odometer cannot be less than current vehicle odometer of {vehicle.odometer} km"
            )

        # Validate trip/driver if provided
        if data.trip_id:
            trip = self.trip_repo.get_by_id(data.trip_id)
            if not trip:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
        if data.driver_id:
            driver = self.driver_repo.get_by_id(data.driver_id)
            if not driver:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")

        total_cost = round(data.liters * data.cost_per_liter, 2)

        log = FuelLog(
            trip_id=data.trip_id,
            vehicle_id=data.vehicle_id,
            driver_id=data.driver_id,
            fuel_station=data.fuel_station,
            liters=data.liters,
            cost_per_liter=data.cost_per_liter,
            total_cost=total_cost,
            odometer=data.odometer,
            fuel_date=data.fuel_date,
            receipt_number=data.receipt_number,
            remarks=data.remarks
        )

        try:
            self.repo.create(log)
            # Update vehicle odometer
            vehicle.odometer = data.odometer

            # Log activity
            act_log = ActivityLog(
                user_id=1,  # System/default fallback or updated from auth context
                action="Fuel Logged",
                entity_type="Vehicle",
                entity_id=vehicle.id,
                details=f"Logged {data.liters} L fuel for {vehicle.registration_number}. Cost: {total_cost}"
            )
            self.db.add(act_log)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to log fuel: {str(e)}")

        self.db.refresh(log)
        return log

    def update_fuel_log(self, id: int, data: FuelLogCreate) -> FuelLog:
        log = self.get_fuel_log(id)

        # Validations
        if data.liters <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fuel liters must be positive")
        if data.cost_per_liter <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cost per liter must be positive")
        if data.fuel_date > date.today():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fuel date cannot be in the future")

        vehicle = self.vehicle_repo.get_by_id(data.vehicle_id)
        if not vehicle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")

        total_cost = round(data.liters * data.cost_per_liter, 2)

        # Update attributes
        log.trip_id = data.trip_id
        log.vehicle_id = data.vehicle_id
        log.driver_id = data.driver_id
        log.fuel_station = data.fuel_station
        log.liters = data.liters
        log.cost_per_liter = data.cost_per_liter
        log.total_cost = total_cost
        log.odometer = data.odometer
        log.fuel_date = data.fuel_date
        log.receipt_number = data.receipt_number
        log.remarks = data.remarks

        try:
            self.repo.update(log)
            if data.odometer > vehicle.odometer:
                vehicle.odometer = data.odometer
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update fuel log: {str(e)}")

        self.db.refresh(log)
        return log

    def delete_fuel_log(self, id: int):
        log = self.get_fuel_log(id)
        try:
            self.repo.delete(log)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete fuel log: {str(e)}")
