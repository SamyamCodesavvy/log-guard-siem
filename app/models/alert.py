from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from sqlalchemy.sql import func
from app.utils.database import Base
import enum

class AlertSeverity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class AlertStatus(str, enum.Enum):
    open = "open"
    investigating = "investigating"
    resolved = "resolved"
    false_positive = "false_positive"

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    hostname = Column(String(100), index=True)
    rule_name = Column(String(100), nullable=False)
    severity = Column(Enum(AlertSeverity), nullable=False)
    description = Column(Text)
    status = Column(Enum(AlertStatus), default=AlertStatus.open)
    assigned_to = Column(String(100))
    resolved_at = Column(DateTime(timezone=True))
    source_ip = Column(String(45), index=True)
    username = Column(String(100))
    log_ids = Column(Text) # JSON list of related log IDs