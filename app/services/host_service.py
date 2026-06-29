from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.host import Host
from app.schemas import host
from app.schemas.host import HostCreate, HostUpdate

def create_host(db: Session, data: HostCreate) -> Host:
    if db.query(Host).filter(Host.hostname == data.hostname).first():
        raise HTTPException(400, f"Host {data.hostname} already registered")
    host = Host(**data.model_dump())
    db.add(host)
    db.commit()
    db.refresh(host)
    return host

def get_hosts(db: Session, skip: int = 0, limit: int = 100) -> list[Host]:
    return db.query(Host).offset(skip).limit(limit).all()

def get_host_by_id(db: Session, host_id: int) -> Host:
    host = db.query(Host).filter(Host.id == host_id).first()
    if not host:
        raise HTTPException(404, "Host not found")
    return host

def update_host(db: Session, host_id: int, data: HostUpdate) -> Host:
    host = get_host_by_id(db, host_id)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(host, field, value)
    db.commit()
    db.refresh(host)
    return host

def delete_host(db: Session, host_id: int) -> dict:
    host = get_host_by_id(db, host_id)
    db.delete(host)
    db.commit()
    return {"message": f"Host {host.hostname} deleted"}