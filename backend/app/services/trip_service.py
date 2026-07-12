from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
from app.repositories.trip_repo import TripRepository
from app.repositories.vehicle_repo import VehicleRepository
from app.repositories.driver_repo import DriverRepository
from app.schemas.schemas import (
    TripCreate, TripUpdate, TripDispatch, TripComplete, TripCancel, DashboardStats
)
from app.models.models import Trip, TripHistory, ActivityLog, Vehicle, Driver, FuelLog


class TripService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TripRepository(db)
        self.vehicle_repo = VehicleRepository(db)
        self.driver_repo = DriverRepository(db)

    def get_all_trips(self, status: str = None, search: str = None):
        return self.repo.get_all(status, search)

    def get_trip(self, id: int):
        trip = self.repo.get_by_id(id)
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        return trip

    def create_trip(self, data: TripCreate, user_id: int):
        trip_number = self.repo.generate_trip_number()
        trip = Trip(
            trip_number=trip_number,
            vehicle_id=data.vehicle_id,
            driver_id=data.driver_id,
            source=data.source,
            destination=data.destination,
            cargo_weight=data.cargo_weight,
            planned_distance=data.planned_distance,
            estimated_duration=data.estimated_duration,
            remarks=data.remarks,
            status="Draft",
            created_by=user_id,
        )
        self.repo.create(trip)

        history = TripHistory(
            trip_id=trip.id,
            previous_status=None,
            new_status="Draft",
            changed_by=user_id,
        )
        self.repo.create_history(history)

        log = ActivityLog(
            user_id=user_id,
            action="Trip Created",
            entity_type="Trip",
            entity_id=trip.id,
            details=f"Trip {trip_number} created",
        )
        self.repo.create_activity_log(log)

        self.db.commit()
        self.db.refresh(trip)
        return trip

    def update_trip(self, id: int, data: TripUpdate, user_id: int):
        trip = self.get_trip(id)
        if trip.status != "Draft":
            raise HTTPException(
                status_code=400, detail="Only draft trips can be edited"
            )
        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(trip, key, value)
        trip.updated_by = user_id
        self.db.commit()
        self.db.refresh(trip)
        return trip

    def delete_trip(self, id: int):
        trip = self.get_trip(id)
        if trip.status != "Draft":
            raise HTTPException(
                status_code=400, detail="Only draft trips can be deleted"
            )
        self.repo.soft_delete(trip)
        self.db.commit()

    def dispatch_trip(self, id: int, data: TripDispatch, user_id: int):
        trip = self.get_trip(id)
        if trip.status != "Draft":
            raise HTTPException(
                status_code=400, detail="Only draft trips can be dispatched"
            )

        vehicle = self.vehicle_repo.get_by_id(trip.vehicle_id)
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")

        driver = self.driver_repo.get_by_id(trip.driver_id)
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")

        # Vehicle status validations
        if vehicle.status != "Available":
            if vehicle.status == "In Shop":
                raise HTTPException(
                    status_code=409, detail="Vehicle is currently in maintenance"
                )
            elif vehicle.status == "Retired":
                raise HTTPException(
                    status_code=409, detail="Vehicle is retired"
                )
            elif vehicle.status == "On Trip":
                raise HTTPException(
                    status_code=409, detail="Vehicle is already on a trip"
                )
            else:
                raise HTTPException(
                    status_code=400, detail=f"Vehicle status '{vehicle.status}' is not available"
                )

        # Driver status validations
        if driver.status != "Available":
            if driver.status == "On Trip":
                raise HTTPException(
                    status_code=409, detail="Driver is already on a trip"
                )
            elif driver.status == "Suspended":
                raise HTTPException(
                    status_code=400, detail="Driver is suspended"
                )
            elif driver.status == "Off Duty":
                raise HTTPException(
                    status_code=400, detail="Driver is off duty"
                )
            else:
                raise HTTPException(
                    status_code=400, detail=f"Driver status '{driver.status}' is not available"
                )

        # License expiry check
        if driver.license_expiry < date.today():
            raise HTTPException(
                status_code=400, detail="Driver license has expired"
            )

        # Cargo & route validations
        if trip.cargo_weight <= 0:
            raise HTTPException(
                status_code=400, detail="Cargo weight must be greater than 0"
            )
        if trip.cargo_weight > vehicle.capacity:
            raise HTTPException(
                status_code=400,
                detail=f"Cargo weight exceeds vehicle capacity of {vehicle.capacity} kg",
            )
        if not trip.source:
            raise HTTPException(status_code=400, detail="Source is required")
        if not trip.destination:
            raise HTTPException(status_code=400, detail="Destination is required")
        if trip.planned_distance <= 0:
            raise HTTPException(
                status_code=400, detail="Planned distance must be greater than 0"
            )

        try:
            trip.status = "Dispatched"
            trip.dispatch_time = datetime.utcnow()
            trip.updated_by = user_id
            vehicle.status = "On Trip"
            driver.status = "On Trip"

            self.db.flush()

            self.repo.create_history(
                TripHistory(
                    trip_id=trip.id,
                    previous_status="Draft",
                    new_status="Dispatched",
                    changed_by=user_id,
                    remarks=data.remarks,
                )
            )

            self.repo.create_activity_log(
                ActivityLog(
                    user_id=user_id,
                    action="Trip Dispatched",
                    entity_type="Trip",
                    entity_id=trip.id,
                    details=f"Trip {trip.trip_number} dispatched",
                )
            )
            self.repo.create_activity_log(
                ActivityLog(
                    user_id=user_id,
                    action="Vehicle Assigned",
                    entity_type="Trip",
                    entity_id=trip.id,
                    details=f"Vehicle {vehicle.registration_number} assigned to trip {trip.trip_number}",
                )
            )
            self.repo.create_activity_log(
                ActivityLog(
                    user_id=user_id,
                    action="Driver Assigned",
                    entity_type="Trip",
                    entity_id=trip.id,
                    details=f"Driver {driver.name} assigned to trip {trip.trip_number}",
                )
            )

            self.db.commit()
        except Exception:
            self.db.rollback()
            raise HTTPException(
                status_code=500, detail="Failed to dispatch trip"
            )

        self.db.refresh(trip)
        return trip

    def complete_trip(self, id: int, data: TripComplete, user_id: int):
        trip = self.get_trip(id)
        if trip.status != "Dispatched":
            raise HTTPException(
                status_code=400, detail="Only dispatched trips can be completed"
            )

        vehicle = self.vehicle_repo.get_by_id(trip.vehicle_id)
        driver = self.driver_repo.get_by_id(trip.driver_id)

        if data.actual_distance <= 0:
            raise HTTPException(
                status_code=400, detail="Actual distance must be greater than 0"
            )

        # Calculate final odometer if not provided
        final_odometer = data.final_odometer
        if final_odometer is None and vehicle:
            final_odometer = vehicle.odometer + int(data.actual_distance)

        if final_odometer and vehicle:
            if final_odometer < vehicle.odometer:
                raise HTTPException(
                    status_code=400,
                    detail=f"Final odometer ({final_odometer}) cannot be less than current odometer ({vehicle.odometer})",
                )

        try:
            trip.status = "Completed"
            trip.completion_time = datetime.utcnow()
            trip.actual_distance = data.actual_distance
            trip.fuel_consumed = data.fuel_consumed
            trip.final_odometer = final_odometer
            trip.remarks = data.remarks or trip.remarks
            trip.updated_by = user_id

            if vehicle:
                vehicle.status = "Available"
                if final_odometer:
                    vehicle.odometer = final_odometer

            if driver:
                driver.status = "Available"

            self.db.flush()

            # Store Fuel Log if fuel was consumed
            if data.fuel_consumed and data.fuel_consumed > 0:
                cost_per_liter = 100.0  # Assumed standard rate
                total_cost = round(data.fuel_consumed * cost_per_liter, 2)
                fuel_log = FuelLog(
                    trip_id=trip.id,
                    vehicle_id=trip.vehicle_id,
                    driver_id=trip.driver_id,
                    fuel_station="Auto Logged (Trip Completion)",
                    liters=data.fuel_consumed,
                    cost_per_liter=cost_per_liter,
                    total_cost=total_cost,
                    odometer=final_odometer or (vehicle.odometer if vehicle else 0),
                    fuel_date=date.today(),
                    receipt_number=f"AUTO-{trip.trip_number}",
                    remarks=f"Auto-generated on completion of Trip {trip.trip_number}"
                )
                self.db.add(fuel_log)
                self.db.flush()

                # Add a fuel log activity log
                self.repo.create_activity_log(
                    ActivityLog(
                        user_id=user_id,
                        action="Fuel Logged",
                        entity_type="Vehicle",
                        entity_id=trip.vehicle_id,
                        details=f"Auto-logged {data.fuel_consumed} L fuel for {vehicle.registration_number if vehicle else ''} on trip completion. Cost: {total_cost}"
                    )
                )

            self.repo.create_history(
                TripHistory(
                    trip_id=trip.id,
                    previous_status="Dispatched",
                    new_status="Completed",
                    changed_by=user_id,
                    remarks=data.remarks,
                )
            )

            self.repo.create_activity_log(
                ActivityLog(
                    user_id=user_id,
                    action="Trip Completed",
                    entity_type="Trip",
                    entity_id=trip.id,
                    details=f"Trip {trip.trip_number} completed. Actual distance: {data.actual_distance} km",
                )
            )

            self.db.commit()
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Failed to complete trip: {str(e)}"
            )

        self.db.refresh(trip)
        return trip

    def cancel_trip(self, id: int, data: TripCancel, user_id: int):
        trip = self.get_trip(id)
        if trip.status in ("Completed", "Cancelled"):
            raise HTTPException(
                status_code=400,
                detail="Completed or cancelled trips cannot be cancelled",
            )

        try:
            previous_status = trip.status
            trip.status = "Cancelled"
            trip.updated_by = user_id
            trip.remarks = data.remarks or trip.remarks

            if previous_status == "Dispatched":
                vehicle = self.vehicle_repo.get_by_id(trip.vehicle_id)
                if vehicle:
                    vehicle.status = "Available"

                driver = self.driver_repo.get_by_id(trip.driver_id)
                if driver:
                    driver.status = "Available"

            self.db.flush()

            self.repo.create_history(
                TripHistory(
                    trip_id=trip.id,
                    previous_status=previous_status,
                    new_status="Cancelled",
                    changed_by=user_id,
                    remarks=data.remarks,
                )
            )

            self.repo.create_activity_log(
                ActivityLog(
                    user_id=user_id,
                    action="Trip Cancelled",
                    entity_type="Trip",
                    entity_id=trip.id,
                    details=f"Trip {trip.trip_number} cancelled",
                )
            )

            self.db.commit()
        except Exception:
            self.db.rollback()
            raise HTTPException(
                status_code=500, detail="Failed to cancel trip"
            )

        self.db.refresh(trip)
        return trip

    def get_dashboard_stats(self):
        total_vehicles = (
            self.db.query(func.count(Vehicle.id))
            .filter(Vehicle.deleted_at.is_(None))
            .scalar()
        )
        available_vehicles = (
            self.db.query(func.count(Vehicle.id))
            .filter(Vehicle.deleted_at.is_(None), Vehicle.status == "Available")
            .scalar()
        )
        vehicles_in_maintenance = (
            self.db.query(func.count(Vehicle.id))
            .filter(Vehicle.deleted_at.is_(None), Vehicle.status == "In Shop")
            .scalar()
        )
        vehicles_on_trip = (
            self.db.query(func.count(Vehicle.id))
            .filter(Vehicle.deleted_at.is_(None), Vehicle.status == "On Trip")
            .scalar()
        )

        total_drivers = (
            self.db.query(func.count(Driver.id))
            .filter(Driver.deleted_at.is_(None))
            .scalar()
        )
        available_drivers = (
            self.db.query(func.count(Driver.id))
            .filter(Driver.deleted_at.is_(None), Driver.status == "Available")
            .scalar()
        )
        drivers_on_duty = (
            self.db.query(func.count(Driver.id))
            .filter(Driver.deleted_at.is_(None), Driver.status == "On Trip")
            .scalar()
        )

        active_trips = (
            self.db.query(func.count(Trip.id))
            .filter(Trip.deleted_at.is_(None), Trip.status == "Dispatched")
            .scalar()
        )
        pending_trips = (
            self.db.query(func.count(Trip.id))
            .filter(Trip.deleted_at.is_(None), Trip.status == "Draft")
            .scalar()
        )

        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        completed_today = (
            self.db.query(func.count(Trip.id))
            .filter(
                Trip.deleted_at.is_(None),
                Trip.status == "Completed",
                Trip.completion_time >= today_start,
            )
            .scalar()
        )
        cancelled_today = (
            self.db.query(func.count(Trip.id))
            .filter(
                Trip.deleted_at.is_(None),
                Trip.status == "Cancelled",
                Trip.updated_at >= today_start,
            )
            .scalar()
        )

        fleet_utilization = 0.0
        if total_vehicles > 0:
            fleet_utilization = round((vehicles_on_trip / total_vehicles) * 100, 1)

        return DashboardStats(
            total_vehicles=total_vehicles,
            available_vehicles=available_vehicles,
            vehicles_in_maintenance=vehicles_in_maintenance,
            active_trips=active_trips,
            pending_trips=pending_trips,
            completed_today=completed_today,
            cancelled_today=cancelled_today,
            drivers_on_duty=drivers_on_duty,
            fleet_utilization=fleet_utilization,
            total_drivers=total_drivers,
            available_drivers=available_drivers,
        )

    def get_trip_history(self, trip_id: int = None):
        if trip_id:
            return self.repo.get_trip_history(trip_id)
        return self.repo.get_all_history()

    def get_trip_activity_logs(self, trip_id: int):
        return self.repo.get_trip_activity_logs(trip_id)

    def get_dashboard_operations_stats(self):
        from app.models.models import Vehicle, FuelLog, MaintenanceLog, Expense, Trip
        
        vehicles_available = (
            self.db.query(func.count(Vehicle.id))
            .filter(Vehicle.deleted_at.is_(None), Vehicle.status == "Available")
            .scalar() or 0
        )
        
        vehicles_in_shop = (
            self.db.query(func.count(Vehicle.id))
            .filter(Vehicle.deleted_at.is_(None), Vehicle.status == "In Shop")
            .scalar() or 0
        )
        
        today = date.today()
        fuel_cost_today = (
            self.db.query(func.sum(FuelLog.total_cost))
            .filter(FuelLog.fuel_date == today)
            .scalar() or 0.0
        )
        
        maintenance_cost = (
            self.db.query(func.sum(MaintenanceLog.actual_cost))
            .filter(MaintenanceLog.deleted_at.is_(None), MaintenanceLog.status == "Completed")
            .scalar() or 0.0
        )
        
        first_day_of_month = date(today.year, today.month, 1)
        monthly_expenses = (
            self.db.query(func.sum(Expense.amount))
            .filter(Expense.expense_date >= first_day_of_month)
            .scalar() or 0.0
        )
        
        trips_completed = (
            self.db.query(func.count(Trip.id))
            .filter(Trip.deleted_at.is_(None), Trip.status == "Completed")
            .scalar() or 0
        )
        
        total_fuel = (
            self.db.query(func.sum(Trip.fuel_consumed))
            .filter(Trip.deleted_at.is_(None), Trip.status == "Completed", Trip.fuel_consumed > 0, Trip.actual_distance > 0)
            .scalar() or 0.0
        )
        total_distance = (
            self.db.query(func.sum(Trip.actual_distance))
            .filter(Trip.deleted_at.is_(None), Trip.status == "Completed", Trip.fuel_consumed > 0, Trip.actual_distance > 0)
            .scalar() or 0.0
        )
        avg_fuel_consumption = 0.0
        if total_distance > 0:
            avg_fuel_consumption = round((total_fuel / total_distance) * 100, 2)
            
        total_fuel_cost = (
            self.db.query(func.sum(FuelLog.total_cost))
            .scalar() or 0.0
        )
        total_expense_cost = (
            self.db.query(func.sum(Expense.amount))
            .scalar() or 0.0
        )
        operational_cost = round(total_fuel_cost + maintenance_cost + total_expense_cost, 2)
        
        from app.schemas.schemas import DashboardOperationsStats
        return DashboardOperationsStats(
            vehicles_available=vehicles_available,
            vehicles_in_shop=vehicles_in_shop,
            fuel_cost_today=fuel_cost_today,
            maintenance_cost=maintenance_cost,
            operational_cost=operational_cost,
            trips_completed=trips_completed,
            avg_fuel_consumption=avg_fuel_consumption,
            vehicles_under_maintenance=vehicles_in_shop,
            monthly_expenses=monthly_expenses
        )

