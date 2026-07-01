from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import logging
import os
from app.config import get_settings
from prometheus_fastapi_instrumentator import Instrumentator
from app.api import auth, hosts, logs, alerts, dashboard, search, ui

settings = get_settings()

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/application.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Mini SIEM Platform for security log analysis",
    lifespan=lifespan,
)
app.include_router(auth.router)
app.include_router(hosts.router)
app.include_router(logs.router)
app.include_router(alerts.router)
app.include_router(dashboard.router)
app.include_router(search.router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(ui.router)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


Instrumentator().instrument(app).expose(app, endpoint="/metrics")
