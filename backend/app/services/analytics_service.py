from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import Vehicle, Driver, Trip, FuelLog, Expense, MaintenanceLog

class AnalyticsService:
    @staticmethod
    def get_dashboard_kpis(db: Session):
        total_vehicles = db.query(func.count(Vehicle.id)).filter(Vehicle.deleted_at == None).scalar()
        available_vehicles = db.query(func.count(Vehicle.id)).filter(Vehicle.deleted_at == None, Vehicle.status == 'Available').scalar()
        on_trip_vehicles = db.query(func.count(Vehicle.id)).filter(Vehicle.deleted_at == None, Vehicle.status == 'On Trip').scalar()
        
        total_drivers = db.query(func.count(Driver.id)).filter(Driver.deleted_at == None).scalar()
        available_drivers = db.query(func.count(Driver.id)).filter(Driver.deleted_at == None, Driver.status == 'Available').scalar()

        total_fuel_cost = db.query(func.sum(FuelLog.total_cost)).scalar() or 0
        total_maintenance_cost = db.query(func.sum(MaintenanceLog.actual_cost)).scalar() or 0
        total_expenses = db.query(func.sum(Expense.amount)).scalar() or 0

        operational_cost = total_fuel_cost + total_maintenance_cost + total_expenses
        
        utilization = 0
        if total_vehicles > 0:
            utilization = (on_trip_vehicles / total_vehicles) * 100

        return {
            "total_vehicles": total_vehicles,
            "available_vehicles": available_vehicles,
            "on_trip_vehicles": on_trip_vehicles,
            "total_drivers": total_drivers,
            "available_drivers": available_drivers,
            "operational_cost": round(operational_cost, 2),
            "total_fuel_cost": round(total_fuel_cost, 2),
            "total_maintenance_cost": round(total_maintenance_cost, 2),
            "fleet_utilization": round(utilization, 2)
        }
