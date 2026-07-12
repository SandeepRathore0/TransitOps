from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    is_active = Column(Boolean, default=True)
    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    role_id = Column(Integer, ForeignKey('roles.id'))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    role = relationship("Role", back_populates="users")

class Vehicle(Base):
    __tablename__ = 'vehicles'
    id = Column(Integer, primary_key=True, index=True)
    registration_number = Column(String(50), unique=True, index=True)
    model = Column(String(100))
    vehicle_type = Column(String(50))
    capacity = Column(Integer)
    odometer = Column(Integer)
    purchase_cost = Column(Float)
    status = Column(String(50), default="Available")
    created_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

class Driver(Base):
    __tablename__ = 'drivers'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    license_number = Column(String(50), unique=True, index=True)
    license_category = Column(String(50))
    license_expiry = Column(Date)
    phone = Column(String(50), unique=True)
    safety_score = Column(Integer, default=100)
    status = Column(String(50), default="Available")
    created_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

class Trip(Base):
    __tablename__ = 'trips'
    id = Column(Integer, primary_key=True, index=True)
    trip_number = Column(String(20), unique=True, index=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'))
    driver_id = Column(Integer, ForeignKey('drivers.id'), nullable=True)
    source = Column(String(200))
    destination = Column(String(200))
    cargo_weight = Column(Float)
    planned_distance = Column(Float)
    actual_distance = Column(Float, nullable=True)
    estimated_duration = Column(String(50), nullable=True)
    dispatch_time = Column(DateTime, nullable=True)
    completion_time = Column(DateTime, nullable=True)
    fuel_consumed = Column(Float, nullable=True)
    final_odometer = Column(Integer, nullable=True)
    status = Column(String(20), default='Draft')
    remarks = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey('users.id'))
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    vehicle = relationship("Vehicle", foreign_keys=[vehicle_id])
    driver = relationship("Driver", foreign_keys=[driver_id])
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])

class TripHistory(Base):
    __tablename__ = 'trip_history'
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey('trips.id'))
    previous_status = Column(String(20))
    new_status = Column(String(20))
    changed_by = Column(Integer, ForeignKey('users.id'))
    changed_at = Column(DateTime, default=datetime.utcnow)
    remarks = Column(Text, nullable=True)
    trip = relationship("Trip", foreign_keys=[trip_id])
    user = relationship("User", foreign_keys=[changed_by])

class ActivityLog(Base):
    __tablename__ = 'activity_logs'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String(100))
    entity_type = Column(String(50))
    entity_id = Column(Integer)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", foreign_keys=[user_id])


class MaintenanceLog(Base):
    __tablename__ = 'maintenance_logs'
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False)
    maintenance_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    workshop_name = Column(String(150), nullable=False)
    estimated_cost = Column(Float, nullable=False)
    actual_cost = Column(Float, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    status = Column(String(50), nullable=False, default="Scheduled")
    remarks = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    vehicle = relationship("Vehicle", foreign_keys=[vehicle_id])
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])


class FuelLog(Base):
    __tablename__ = 'fuel_logs'
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey('trips.id'), nullable=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False)
    driver_id = Column(Integer, ForeignKey('drivers.id'), nullable=True)
    fuel_station = Column(String(150), nullable=True)
    liters = Column(Float, nullable=False)
    cost_per_liter = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    odometer = Column(Integer, nullable=False)
    fuel_date = Column(Date, nullable=False)
    receipt_number = Column(String(100), nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", foreign_keys=[trip_id])
    vehicle = relationship("Vehicle", foreign_keys=[vehicle_id])
    driver = relationship("Driver", foreign_keys=[driver_id])


class Expense(Base):
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey('trips.id'), nullable=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=True)
    expense_type = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    expense_date = Column(Date, nullable=False)
    receipt_reference = Column(String(100), nullable=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    trip = relationship("Trip", foreign_keys=[trip_id])
    vehicle = relationship("Vehicle", foreign_keys=[vehicle_id])
    creator = relationship("User", foreign_keys=[created_by])



class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    entity = Column(String(100), nullable=False)
    entity_id = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(50), nullable=True)
    user = relationship("User")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    priority = Column(String(50), default="Normal")
    is_read = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserPreference(Base):
    __tablename__ = "user_preferences"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    theme = Column(String(50), default="dark")
    notifications_enabled = Column(Boolean, default=True)
