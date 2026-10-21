import os
from urllib.parse import urlsplit
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "app" / "data" / "storage"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Settings
PROJECT_NAME = "Mars Mission Intelligence"
VERSION = "1.0.0"
API_V1_STR = "/api"


def get_cors_settings(environment=None, allowed_origins=None):
    """Return a restrictive CORS policy for the configured frontend origins."""
    environment = (environment if environment is not None else os.getenv("ENVIRONMENT", "development")).strip().lower()
    configured = allowed_origins if allowed_origins is not None else os.getenv("ALLOWED_ORIGINS", "")
    origins = [origin.strip().rstrip("/") for origin in configured.split(",") if origin.strip()]

    if not origins and environment != "production":
        origins = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"]
    if environment == "production" and not origins:
        raise ValueError("ALLOWED_ORIGINS must include at least one trusted frontend origin in production.")

    for origin in origins:
        parsed = urlsplit(origin)
        if (parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.path or parsed.query
                or parsed.fragment or parsed.username or parsed.password or origin == "*"):
            raise ValueError(f"Invalid CORS origin: {origin!r}")

    return {
        "allow_origins": origins,
        "allow_credentials": False,
        "allow_methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
    }

# Server
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT") or 8000)

# Planetary Constants
MARS_SOLAR_DAY_SECONDS = 88775.244  # Length of 1 Martian Sol in SI seconds
MARS_YEAR_SOLS = 668.6
MARS_RADIUS_KM = 3389.5
MARS_SURFACE_GRAVITY = 3.72076  # m/s^2

# Mission Coordinates (Planetocentric Lat, Long East, Elevation km)
LANDING_SITES = {
    "curiosity": {
        "name": "Curiosity (MSL)",
        "site": "Gale Crater (Aeolis Palus)",
        "lat": -4.5895,
        "lon": 137.4417,
        "elevation_km": -4.5,
        "landing_date": "2012-08-06",
        "instrument": "REMS (Rover Environmental Monitoring Station)",
    },
    "insight": {
        "name": "InSight Lander",
        "site": "Elysium Planitia",
        "lat": 4.5024,
        "lon": 135.6234,
        "elevation_km": -2.6,
        "landing_date": "2018-11-26",
        "instrument": "TWINS / APSS (Auxiliary Payload Sensor Suite)",
    },
    "perseverance": {
        "name": "Perseverance (Mars 2020)",
        "site": "Jezero Crater",
        "lat": 18.38,
        "lon": 77.58,
        "elevation_km": -2.5,
        "landing_date": "2021-02-18",
        "instrument": "MEDA (Mars Environmental Dynamics Analyzer)",
    }
}
