from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.authentication.dependencies import get_current_user
from app.models.log import Log
from app.schemas.log import LogBatchIngest, LogIngest, LogResponse
from app.utils.database import get_db
from app.utils.log_parser import parse_log

router = APIRouter(prefix="/logs", tags=["Log Ingestion"])


def _save_and_analyze(
    raw: str,
    hostname: str,
    source: str,
    db: Session,
):
    parsed = parse_log(raw, source)

    log = Log(
        timestamp=parsed.timestamp,
        hostname=hostname or parsed.hostname,
        source=source,
        severity=parsed.severity,
        program=parsed.program,
        pid=parsed.pid,
        username=parsed.username,
        source_ip=parsed.source_ip,
        action=parsed.action,
        message=parsed.message,
        raw_log=raw,
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    from app.detection.engine import run_detection

    run_detection(db, log)

    return log


@router.post("/", response_model=LogResponse, status_code=201)
def ingest_log(
    data: LogIngest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return _save_and_analyze(
        data.raw_log,
        data.hostname,
        data.source,
        db,
    )


@router.post("/batch", status_code=201)
def ingest_batch(
    data: LogBatchIngest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    results = []

    for raw in data.logs:
        log = _save_and_analyze(
            raw,
            data.hostname,
            data.source,
            db,
        )
        results.append(log.id)

    return {
        "saved": len(results),
        "log_ids": results,
    }


@router.get("/", response_model=List[LogResponse])
def list_logs(
    skip: int = 0,
    limit: int = 100,
    severity: str = None,
    hostname: str = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(Log)

    if severity:
        query = query.filter(Log.severity == severity)

    if hostname:
        query = query.filter(Log.hostname == hostname)

    return query.order_by(Log.timestamp.desc()).offset(skip).limit(limit).all()


@router.get("/{log_id}", response_model=LogResponse)
def get_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    log = db.query(Log).filter(Log.id == log_id).first()

    if not log:
        raise HTTPException(
            status_code=404,
            detail="Log not found",
        )

    return log
