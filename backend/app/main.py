from contextlib import asynccontextmanager
from decimal import Decimal
import json
import logging
from pathlib import Path
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

            with Session(engine) as db:
                dest_count = db.execute(select(func.count(Destination.id))).scalar() or 0
                if dest_count == 0:
                    logger.info("Destinations table empty. Seeding catalogue...")
                    # 1. Seed default accounts
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

                    # 2. Starter destinations
                    starter_dests = [
                        Destination(city="Mysuru", country="India", description="City of palaces, royal heritage, and silk.", average_daily_cost=Decimal("3500.00"), active=True),
                        Destination(city="Kochi", country="India", description="Coastal port known for spice markets and heritage.", average_daily_cost=Decimal("4200.00"), active=True),
                        Destination(city="Jaipur", country="India", description="The Pink City of Rajasthan featuring hilltop forts.", average_daily_cost=Decimal("4000.00"), active=True),
                        Destination(city="Udaipur", country="India", description="City of Lakes surrounded by Aravalli hills.", average_daily_cost=Decimal("4500.00"), active=True),
                        Destination(city="Goa", country="India", description="Golden beaches and Portuguese colonial architecture.", average_daily_cost=Decimal("5000.00"), active=True),
                    ]
                    db.add_all(starter_dests)
                    db.commit()
                    db.refresh(starter_dests[0])

                    # 3. Starter catalogue entities for Mysuru
                    m_dest = starter_dests[0]
                    h1 = Hotel(destination_id=m_dest.id, name="Heritage Garden Stay", price_per_night=Decimal("2800.00"), rating=Decimal("4.3"))
                    h2 = Hotel(destination_id=m_dest.id, name="Royal Palace Hotel", price_per_night=Decimal("4200.00"), rating=Decimal("4.7"))
                    r1 = Restaurant(destination_id=m_dest.id, name="Mylari Dosa", cuisine="South Indian", average_cost_per_person=Decimal("150.00"), rating=Decimal("4.8"))
                    r2 = Restaurant(destination_id=m_dest.id, name="Gufha Cave Dining", cuisine="Multi-cuisine", average_cost_per_person=Decimal("600.00"), rating=Decimal("4.2"))
                    a1 = Attraction(destination_id=m_dest.id, name="Mysore Palace", category="Heritage", entry_fee=Decimal("100.00"), rating=Decimal("4.9"))
                    a2 = Attraction(destination_id=m_dest.id, name="Chamundi Hills", category="Nature", entry_fee=Decimal("0.00"), rating=Decimal("4.6"))
                    t1 = TransportOption(origin="Bengaluru", destination_id=m_dest.id, mode="train", provider="KSRTC & Railway", estimated_cost=Decimal("300.00"), duration_minutes=180)
                    db.add_all([h1, h2, r1, r2, a1, a2, t1])
                    db.commit()

                    # 4. Master destinations JSON
                    seed_paths = [
                        Path(__file__).resolve().parent.parent.parent / "database" / "seeds" / "destinations_master_d1.json",
                        Path(__file__).resolve().parent.parent / "database" / "seeds" / "destinations_master_d1.json",
                        Path("database/seeds/destinations_master_d1.json"),
                    ]
                    for sp in seed_paths:
                        if sp.exists():
                            with open(sp, "r", encoding="utf-8") as f:
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
                            break
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
