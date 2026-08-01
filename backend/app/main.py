from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.routers import health, plans

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0-starter", debug=settings.app_debug)
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(health.router)
app.include_router(plans.router, prefix=settings.api_v1_prefix)

@app.exception_handler(Exception)
async def safe_unhandled_error(_: Request, __: Exception) -> JSONResponse:
    # TODO(M2/Yasmin): add structured server-side logging with request IDs.
    return JSONResponse(status_code=500, content={"error": {"code": "internal_error", "message": "An unexpected error occurred."}})
