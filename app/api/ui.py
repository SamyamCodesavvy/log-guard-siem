from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.log import Log
from app.services import dashboard_service
from app.utils.database import get_db

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/ui", tags=["UI"])


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    db: Session = Depends(get_db),
):
    data = dashboard_service.get_dashboard_stats(db)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            **data,
        },
    )


@router.get("/logs", response_class=HTMLResponse)
async def logs_page(
    request: Request,
    db: Session = Depends(get_db),
):
    logs = db.query(Log).order_by(Log.timestamp.desc()).limit(100).all()

    return templates.TemplateResponse(
        "logs.html",
        {
            "request": request,
            "logs": logs,
        },
    )


@router.get("/alerts", response_class=HTMLResponse)
async def alerts_page(
    request: Request,
    db: Session = Depends(get_db),
):
    alerts = db.query(Alert).order_by(Alert.timestamp.desc()).limit(100).all()

    return templates.TemplateResponse(
        "alerts.html",
        {
            "request": request,
            "alerts": alerts,
        },
    )
