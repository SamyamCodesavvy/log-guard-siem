# app/schemas/log.py

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.log import LogSeverity


class LogIngest(BaseModel):
    hostname: str
    source: str  # auth.log, syslog, nginx
    raw_log: str


class LogBatchIngest(BaseModel):
    hostname: str
    source: str
    logs: List[str]


class LogResponse(BaseModel):
    id: int
    timestamp: datetime
    hostname: Optional[str]
    source: Optional[str]
    severity: LogSeverity
    program: Optional[str]
    username: Optional[str]
    source_ip: Optional[str]
    action: Optional[str]
    message: str
    created_at: datetime

    class Config:
        from_attributes = True
