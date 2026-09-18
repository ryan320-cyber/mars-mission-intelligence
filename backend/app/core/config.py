import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "app" / "data" / "storage"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Settings
PROJECT_NAME = "Mars Mission Intelligence"
VERSION = "1.0.0"
API_V1_STR = "/api"

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
