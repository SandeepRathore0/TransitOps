from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

class RoleBase(BaseModel):
    name: str

class RoleResponse(RoleBase):
    id: int
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role_id: int

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    role: RoleResponse
    class Config:
        from_attributes = True

class VehicleBase(BaseModel):
    registration_number: str
    model: str
    vehicle_type: str
    capacity: int
    odometer: int
    purchase_cost: float
    status: str = "Available"

class VehicleCreate(VehicleBase):
    pass

class VehicleResponse(VehicleBase):
    id: int
    class Config:
        from_attributes = True

class DriverBase(BaseModel):
    name: str
    license_number: str
    license_category: str
    license_expiry: date
    phone: str
    safety_score: int = 100
    status: str = "Available"

class DriverCreate(DriverBase):
    pass

class DriverResponse(DriverBase):
    id: int
    class Config:
        from_attributes = True

# --- Trip Schemas ---
class TripCreate(BaseModel):
    source: str
    destination: str
    vehicle_id: int
    driver_id: Optional[int] = None
    cargo_weight: float
    planned_distance: float
    estimated_duration: Optional[str] = None
    remarks: Optional[str] = None

class TripUpdate(BaseModel):
    source: Optional[str] = None
    destination: Optional[str] = None
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None
    cargo_weight: Optional[float] = None
    planned_distance: Optional[float] = None
    estimated_duration: Optional[str] = None
    remarks: Optional[str] = None

class TripDispatch(BaseModel):
    remarks: Optional[str] = None

class TripComplete(BaseModel):
    actual_distance: float
    fuel_consumed: Optional[float] = None
    final_odometer: Optional[int] = None
    remarks: Optional[str] = None

class TripCancel(BaseModel):
    remarks: Optional[str] = None

class TripResponse(BaseModel):
    id: int
    trip_number: str
    vehicle_id: int
    driver_id: Optional[int] = None
    source: str
    destination: str
    cargo_weight: float
    planned_distance: float
    actual_distance: Optional[float] = None
    estimated_duration: Optional[str] = None
    dispatch_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None
    fuel_consumed: Optional[float] = None
    final_odometer: Optional[int] = None
    status: str
    remarks: Optional[str] = None
    created_by: int
    updated_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # Nested info
    vehicle: Optional[VehicleResponse] = None
    driver: Optional[DriverResponse] = None
    class Config:
        from_attributes = True

class TripHistoryResponse(BaseModel):
    id: int
    trip_id: int
    previous_status: Optional[str] = None
    new_status: str
    changed_by: int
    changed_at: Optional[datetime] = None
    remarks: Optional[str] = None
    class Config:
        from_attributes = True

class ActivityLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    entity_type: str
    entity_id: int
    details: Optional[str] = None
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_vehicles: int = 0
    available_vehicles: int = 0
    vehicles_in_maintenance: int = 0
    active_trips: int = 0
    pending_trips: int = 0
    completed_today: int = 0
    cancelled_today: int = 0
    drivers_on_duty: int = 0
    fleet_utilization: float = 0.0
    total_drivers: int = 0
    available_drivers: int = 0


# --- Maintenance Log Schemas ---
class MaintenanceBase(BaseModel):
    vehicle_id: int
    maintenance_type: str
    description: str
    workshop_name: str
    estimated_cost: float
    actual_cost: Optional[float] = None
    start_date: date
    end_date: Optional[date] = None
    status: str = "Scheduled"
    remarks: Optional[str] = None

class MaintenanceCreate(MaintenanceBase):
    pass

class MaintenanceUpdate(BaseModel):
    maintenance_type: Optional[str] = None
    description: Optional[str] = None
    workshop_name: Optional[str] = None
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    remarks: Optional[str] = None

class MaintenanceComplete(BaseModel):
    actual_cost: float
    end_date: date
    remarks: Optional[str] = None

class MaintenanceResponse(MaintenanceBase):
    id: int
    created_by: int
    updated_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    vehicle: Optional[VehicleResponse] = None
    class Config:
        from_attributes = True


# --- Fuel Log Schemas ---
class FuelLogBase(BaseModel):
    trip_id: Optional[int] = None
    vehicle_id: int
    driver_id: Optional[int] = None
    fuel_station: Optional[str] = None
    liters: float
    cost_per_liter: float
    total_cost: float
    odometer: int
    fuel_date: date
    receipt_number: Optional[str] = None
    remarks: Optional[str] = None

class FuelLogCreate(BaseModel):
    trip_id: Optional[int] = None
    vehicle_id: int
    driver_id: Optional[int] = None
    fuel_station: Optional[str] = None
    liters: float
    cost_per_liter: float
    odometer: int
    fuel_date: date
    receipt_number: Optional[str] = None
    remarks: Optional[str] = None

class FuelLogResponse(FuelLogBase):
    id: int
    created_at: datetime
    vehicle: Optional[VehicleResponse] = None
    driver: Optional[DriverResponse] = None
    trip: Optional[TripResponse] = None
    class Config:
        from_attributes = True


# --- Expense Schemas ---
class ExpenseBase(BaseModel):
    trip_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    expense_type: str
    amount: float
    description: str
    expense_date: date
    receipt_reference: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseResponse(ExpenseBase):
    id: int
    created_by: int
    created_at: datetime
    vehicle: Optional[VehicleResponse] = None
    trip: Optional[TripResponse] = None
    class Config:
        from_attributes = True


# --- Dashboard Operations Schemas ---
class DashboardOperationsStats(BaseModel):
    vehicles_available: int = 0
    vehicles_in_shop: int = 0
    fuel_cost_today: float = 0.0
    maintenance_cost: float = 0.0
    operational_cost: float = 0.0
    trips_completed: int = 0
    avg_fuel_consumption: float = 0.0
    vehicles_under_maintenance: int = 0
    monthly_expenses: float = 0.0

