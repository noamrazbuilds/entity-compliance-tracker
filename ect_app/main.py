from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ect_app.config import settings
from ect_app.database import SessionLocal, init_db
from ect_app.notifications.scheduler import start_scheduler, stop_scheduler
from ect_app.routers import (
    dashboard,
    documents,
    entities,
    filings,
    notifications,
    officers,
    relationships,
    shutdown,
)
from ect_app.services.seed_service import seed_sample_data


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    init_db()
    # Seed sample data on first startup
    db = SessionLocal()
    try:
        seed_sample_data(db)
    finally:
        db.close()
    start_scheduler()
    yield
    stop_scheduler()


def create_app() -> FastAPI:
    application = FastAPI(
        title="Entity Compliance Tracker",
        description="Corporate Entity & Subsidiary Compliance Tracker API",
        version="0.1.0",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount routers
    application.include_router(entities.router)
    application.include_router(officers.router)
    application.include_router(filings.router)
    application.include_router(documents.router)
    application.include_router(relationships.router)
    application.include_router(dashboard.router)
    application.include_router(notifications.router)
    application.include_router(shutdown.router)

    @application.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "healthy"}

    return application


app = create_app()
