from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    entity: str
    entity_id: Optional[int]
    timestamp: datetime
    ip_address: Optional[str]
    class Config:
        from_attributes = True

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    priority: str
    is_read: bool
    created_at: datetime
    class Config:
        from_attributes = True

class PaginatedResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[Any]
