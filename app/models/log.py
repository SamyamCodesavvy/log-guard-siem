from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from sqlalchemy.sql import func
from app.utils.database import Base
import enum


class LogSeverity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"
    info = "info"


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    hostname = Column(String(100), index=True)
    source = Column(String(50))  # auth.log, syslog, nginx, etc.
    severity = Column(Enum(LogSeverity), default=LogSeverity.info)
    program = Column(String(100))  # sshd, sudo, cron...
    pid = Column(Integer)
    username = Column(String(100), index=True)
    source_ip = Column(String(45), index=True)
    action = Column(String(100))
    message = Column(Text, nullable=False)
    raw_log = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
