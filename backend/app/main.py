from contextlib import asynccontextmanager
from decimal import Decimal
import json
import logging
from pathlib import Path
import threading
import traceback

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.base import Base
from app.db.models import (
    ActivityPreference,
    Attraction,
    Destination,
    Hotel,
    Restaurant,
    TransportOption,
    User,
    UserPreference,
)
from app.db.session import get_engine
from app.routers import assistant, auth, catalogues, health, plans, reports, trips, users
from app.services.auth_service import hash_password
from app.services.seeder import get_catalogue_counts, get_seed_dir, seed_master_catalogues

logger = logging.getLogger("uvicorn.error")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure database schema tables and seed records exist on startup."""
    try:
        engine = get_engine()
        if engine is not None:
            logger.info("Verifying and creating database tables...")
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables verified.")

            def _background_seeder():
                try:
                    with Session(engine) as db:
                        # 1. Ensure admin accounts exist
                        existing_admin = db.execute(select(User).where(User.email == "admin@roamgenie.internal")).scalar_one_or_none()
                        if not existing_admin:
                            admin = User(
                                email="admin@roamgenie.internal",
                                password_hash=hash_password("AdminPass123!"),
                                full_name="System Administrator",
                                role="admin",
                            )
                            traveller1 = User(
                                email="traveller@roamgenie.internal",
                                password_hash=hash_password("TravellerPass123!"),
                                full_name="Arun Kumar",
                                role="traveller",
                            )
                            traveller2 = User(
                                email="ananya@roamgenie.internal",
                                password_hash=hash_password("TravellerPass123!"),
                                full_name="Ananya Sharma",
                                role="traveller",
                            )
                            db.add_all([admin, traveller1, traveller2])
                            db.commit()

                        # 2. Check if destinations exist
                        dest_count = db.execute(select(func.count(Destination.id))).scalar() or 0
                        if dest_count == 0:
                            seed_dir = get_seed_dir()
                            if seed_dir and (seed_dir / "destinations_master_d1.json").exists():
                                with open(seed_dir / "destinations_master_d1.json", "r", encoding="utf-8") as f:
                                    dests_data = json.load(f)
                                bulk_dests = [
                                    Destination(
                                        city=d["city"],
                                        country=d["country"],
                                        description=d.get("description", ""),
                                        average_daily_cost=Decimal(str(d.get("average_daily_cost", 3500))),
                                        active=d.get("active", True),
                                    )
                                    for d in dests_data
                                ]
                                db.add_all(bulk_dests)
                                db.commit()
                                logger.info("Seeded %d master destinations.", len(bulk_dests))

                        # 3. Seed child master catalogues (Hotels, Dining, Sights, Transit)
                        seed_master_catalogues(db)
                except Exception as ex:
                    logger.error("Background seeding failed: %s\n%s", ex, traceback.format_exc())

            threading.Thread(target=_background_seeder, daemon=True).start()
    except Exception as e:
        logger.error("Database initialization failed on startup: %s\n%s", e, traceback.format_exc())
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    debug=settings.app_debug,
    description="Intelligent AI-powered travel planner and budget optimization platform (DBMS Course Project).",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins + [
        "https://roam-genie-six.vercel.app",
        "https://roamgenie.vercel.app",
    ],
    allow_origin_regex=r"^https:\/\/.*\.vercel\.app$|^https:\/\/.*\.onrender\.com$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router)
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(users.router, prefix=settings.api_v1_prefix)
app.include_router(catalogues.router, prefix=settings.api_v1_prefix)
app.include_router(trips.router, prefix=settings.api_v1_prefix)
app.include_router(assistant.router, prefix=settings.api_v1_prefix)
app.include_router(reports.router, prefix=settings.api_v1_prefix)
app.include_router(plans.router, prefix=settings.api_v1_prefix)


@app.get("/")
def root():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "api_v1": settings.api_v1_prefix,
    }


@app.get(f"{settings.api_v1_prefix}/system/catalogue-counts")
def catalogue_counts():
    """Retrieve row counts for all catalogue entities."""
    engine = get_engine()
    if not engine:
        return {"error": "Database not configured"}
    with Session(engine) as db:
        return get_catalogue_counts(db)


@app.post(f"{settings.api_v1_prefix}/system/seed-catalogues")
def trigger_seed_catalogues(force: bool = False):
    """Trigger seeding of master catalogue datasets."""
    engine = get_engine()
    if not engine:
        return {"error": "Database not configured"}
    with Session(engine) as db:
        return seed_master_catalogues(db, force=force)


@app.exception_handler(Exception)
async def safe_unhandled_error(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception on %s: %s\n%s", request.url, exc, traceback.format_exc())
    origin = request.headers.get("origin")
    headers = {}
    if origin:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
        headers["Access-Control-Allow-Methods"] = "*"
        headers["Access-Control-Allow-Headers"] = "*"
    return JSONResponse(
        status_code=500,
        headers=headers,
        content={
            "error": {
                "code": "internal_error",
                "message": str(exc),
            }
        },
    )
