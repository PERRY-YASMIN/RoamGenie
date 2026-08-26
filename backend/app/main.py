from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.routers import assistant, auth, catalogues, health, plans, reports, trips, users

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    debug=settings.app_debug,
    description="Intelligent AI-powered travel planner and budget optimization platform (DBMS Course Project).",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
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


@app.exception_handler(Exception)
async def safe_unhandled_error(_: Request, exc: Exception) -> JSONResponse:
    # Phase 1: Safe exception envelope hiding internal tracebacks
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_error",
                "message": "An unexpected error occurred. Please try again later.",
            }
        },
    )
