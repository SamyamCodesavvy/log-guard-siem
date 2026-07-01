from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.utils.database import get_db
from app.authentication.dependencies import get_current_user
from app.models.log import Log
from app.schemas.log import LogResponse

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/")
def search(
    q: Optional[str] = Query(None, description="Keyword"),
    ip: Optional[str] = Query(None),
    username: Optional[str] = Query(None),
    hostname: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(Log)
    if q:
        query = query.filter(Log.message.ilike(f"%{q}%"))
    if ip:
        query = query.filter(Log.source_ip == ip)
    if username:
        query = query.filter(Log.username.ilike(f"%{username}%"))
    if hostname:
        query = query.filter(Log.hostname.ilike(f"%{hostname}%"))
    if severity:
        query = query.filter(Log.severity == severity)
    logs = query.order_by(Log.timestamp.desc()).offset(skip).limit(limit).all()
    return {
        "results": [LogResponse.model_validate(log) for log in logs],
        "count": len(logs),
    }
