from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.authentication.dependencies import get_current_user
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/")
def get_dashboard(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    return dashboard_service.get_dashboard_stats(db)
