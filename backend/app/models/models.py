from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Date
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
