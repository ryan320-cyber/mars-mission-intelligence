"""
Mars Mission Intelligence Backend Application.
NASA Data + AI Scientific Analysis Platform for Mars Exploration.
FastAPI Application Entry Point.
"""

import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import PROJECT_NAME, VERSION, API_V1_STR
from app.api.router import api_router

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("mars_mission_intelligence")

app = FastAPI(
    title=PROJECT_NAME,
    version=VERSION,
    description=(
        "NASA Planetary Data + AI Scientific Analysis Platform. "
        "Integrates Curiosity REMS, InSight TWINS, and MRO Mars Climate Sounder datasets "
        "with time-series analysis, dual anomaly detection, ML Model Lab, and Grounded AI."
    ),
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
        "https://mars-mission-intelligence-pzjo.vercel.app",
        "https://mars-mission-intelligence3.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Timing & Telemetry Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time-Sec"] = f"{process_time:.4f}"
    return response

# Structured Exception Handler (Directive 73)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected scientific processing error occurred.",
            "path": request.url.path,
            "status": "FAILED"
        }
    )

# Root Health / Ping Check
@app.get("/health")
def health_check():
    return {
        "status": "HEALTHY",
        "service": PROJECT_NAME,
        "version": VERSION,
        "authoritative_data": "CONNECTED"
    }

# Mount API routes
app.include_router(api_router, prefix=API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
