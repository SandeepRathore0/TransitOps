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
