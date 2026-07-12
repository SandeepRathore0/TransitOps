from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role_name: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role_id: int
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

class RoleResponse(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True
