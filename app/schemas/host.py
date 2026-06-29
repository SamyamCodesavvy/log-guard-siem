from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.host import HostStatus

class HostCreate(BaseModel):
    hostname: str = Field(..., min_length=1, max_length=100)
    ip_address: str
    operating_system: Optional[str] = None
    description: Optional[str] = None
    ssh_port: int = Field(default=22, ge=1, le=65535)

class HostUpdate(BaseModel):
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    operating_system: Optional[str] = None
    description: Optional[str] = None
    ssh_port: Optional[int] = None
    status: Optional[HostStatus] = None

class HostResponse(BaseModel):
    id: int
    hostname: str
    ip_address: str
    operating_system: Optional[str]
    description: Optional[str]
    ssh_port: int
    status: HostStatus
    created_at: datetime
    updated_at: Optional[datetime]

class Config:
    from_attributes = True