from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.utils.database import get_db
from app.authentication.dependencies import get_current_user
from app.schemas.host import HostCreate, HostUpdate, HostResponse
from app.services import host_service

router = APIRouter(prefix="/hosts", tags=["Host Management"])

@router.post("/", response_model=HostResponse, status_code=201)
def create_host(data: HostCreate, db: Session = Depends(get_db),
                current_user=Depends(get_current_user)):
    return host_service.create_host(db, data)

@router.get("/", response_model=List[HostResponse])
def list_hosts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
               current_user=Depends(get_current_user)):
    return host_service.get_hosts(db, skip, limit)

@router.get("/{host_id}", response_model=HostResponse)
def get_host(host_id: int, db: Session = Depends(get_db),
             current_user=Depends(get_current_user)):
    return host_service.get_host_by_id(db, host_id)

@router.put("/{host_id}", response_model=HostResponse)
def update_host(host_id: int, data: HostUpdate, db: Session = Depends(get_db),
            current_user=Depends(get_current_user)):
    return host_service.update_host(db, host_id, data)

@router.delete("/{host_id}")
def delete_host(host_id: int, db: Session = Depends(get_db),
                current_user=Depends(get_current_user)):
    return host_service.delete_host(db, host_id)