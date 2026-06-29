from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.alert import AlertSeverity, AlertStatus

class AlertResponse(BaseModel):
    id: int
    timestamp: datetime
    hostname: Optional[str]
    rule_name: str
    severity: AlertSeverity
    description: Optional[str]
    status: AlertStatus
    assigned_to: Optional[str]
    resolved_at: Optional[datetime]
    source_ip: Optional[str]
    username: Optional[str]

    class Config:
        from_attributes = True

class AlertResolve(BaseModel):
    status: AlertStatus
    assigned_to: Optional[str] = None