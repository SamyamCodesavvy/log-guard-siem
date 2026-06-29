from sqlalchemy import Column, Integer, String, DateTime, Enum, Text
from sqlalchemy.sql import func
from app.utils.database import Base
import enum

class HostStatus(str, enum.Enum):
    active = "active"  
    inactive = "inactive"
    unknown = "unknown"

class Host(Base):
    __tablename__ = "hosts"
    
    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String(100), unique=True, nullable=False, index=True)
    ip_address = Column(String(45), nullable=False)
    operating_system = Column(String(100))
    description = Column(Text)
    ssh_port = Column(Integer, default=22)
    status = Column(Enum(HostStatus), default=HostStatus.unknown)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())