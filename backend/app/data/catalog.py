"""
Authoritative NASA Planetary Data Catalog & Provenance Registry.
Covers real datasets: MSL Curiosity REMS, InSight TWINS/APSS, and MRO Mars Climate Sounder (MCS).
"""

from typing import Dict, Any, List

DATASET_CATALOG: Dict[str, Dict[str, Any]] = {
    "msl_curiosity_rems": {
        "id": "msl_curiosity_rems",
        "name": "Curiosity (MSL) REMS Daily Environmental Observations",
        "mission": "Mars Science Laboratory (MSL)",
        "spacecraft": "Curiosity Rover",
        "instrument": "Rover Environmental Monitoring Station (REMS)",
        "dataset_id": "MSL-M-REMS-MOD-5-V1.0",
        "pds_urn": "urn:nasa:pds:msl_rems:data_derived",
        "doi": "10.17189/1519504",
        "source_url": "https://mars.nasa.gov/rss/api/?feed=weather&category=msl&feedtype=json",
        "pds_archive_url": "https://pds-atmospheres.nmsu.edu/data_and_services/atmospheres_data/MARS/curiosity.html",
        "processing_level": "Level 4 (Calibrated & Daily Derived Statistics)",
        "spatial_coverage": {
            "site": "Gale Crater (Aeolis Palus)",
            "latitude_deg": -4.5895,
            "longitude_deg_east": 137.4417,
            "elevation_km": -4.5,
            "coordinate_system": "Planetocentric (IAU 2000)"
        },
        "temporal_coverage": {
            "start_earth_date": "2012-08-07",
            "end_earth_date": "2026-08-25",
            "start_sol": 1,
            "end_sol": 4995,
            "observation_cadence": "Daily summary (min/max/mean) + Sol cadence"
        },
        "variables": [
            {
                "id": "air_temp_min",
                "name": "Minimum Ambient Air Temperature",
                "unit": "°C",
                "sensor": "REMS Boom 1 / Boom 2 PT1000 RTD",
                "physical_range": [-130.0, 30.0],
                "uncertainty": "±1.5 °C"
            },
            {
                "id": "air_temp_max",
                "name": "Maximum Ambient Air Temperature",
                "unit": "°C",
                "sensor": "REMS Boom 1 / Boom 2 PT1000 RTD",
                "physical_range": [-130.0, 30.0],
                "uncertainty": "±1.5 °C"
            },
            {
                "id": "ground_temp_min",
                "name": "Minimum Ground Brightness Temperature",
                "unit": "°C",
                "sensor": "REMS Ground Temperature Sensor (GTS) Thermopiles",
                "physical_range": [-130.0, 40.0],
                "uncertainty": "±2.0 °C"
            },
            {
                "id": "ground_temp_max",
                "name": "Maximum Ground Brightness Temperature",
                "unit": "°C",
                "sensor": "REMS Ground Temperature Sensor (GTS) Thermopiles",
                "physical_range": [-130.0, 40.0],
                "uncertainty": "±2.0 °C"
            },
            {
                "id": "pressure",
                "name": "Atmospheric Surface Pressure",
                "unit": "Pa",
                "sensor": "Barocap silicon capacitive transducer inside rover body",
                "physical_range": [600.0, 1150.0],
                "uncertainty": "±2.0 Pa absolute, ±0.5 Pa relative"
            },
            {
                "id": "solar_longitude",
                "name": "Solar Longitude (Ls)",
                "unit": "degrees (°)",
                "sensor": "Ephemeris derivation (NAIF SPICE)",
                "physical_range": [0.0, 360.0],
                "uncertainty": "Exact celestial coordinate"
            },
            {
                "id": "uv_index",
                "name": "Local UV Irradiance Index",
                "unit": "Qualitative categorical (Low, Moderate, High, Very High)",
                "sensor": "REMS UV photodiodes on rover deck",
                "physical_range": [0, 4],
                "uncertainty": "Degraded over time due to Martian dust accumulation"
            }
        ],
        "data_quality": {
            "completeness_pct": 98.4,
            "sensor_health": "Nominal for temperature & pressure; wind sensor boom damaged in 2012 during landing; UV sensor partially dust-coated.",
            "known_limitations": [
                "Wind speed sensor experienced partial degradation shortly after landing (Sol 1); wind measurements unavailable for substantial intervals.",
                "UV sensor photodiodes have accumulated atmospheric dust, leading to relative rather than absolute long-term UV trend reliability.",
                "Ground temperature reflects radiative skin temperature within the GTS field of view."
            ]
        }
    },
    "insight_twins_apss": {
        "id": "insight_twins_apss",
        "name": "InSight TWINS / APSS Calibrated & Hourly Meteorology",
        "mission": "InSight Lander",
        "spacecraft": "InSight (Interior Exploration using Seismic Investigations, Geodesy and Heat Transport)",
        "instrument": "Temperature and Wind for InSight (TWINS) & Auxiliary Payload Sensor Suite (APSS)",
        "dataset_id": "urn:nasa:pds:insight_twins:data_derived",
        "pds_urn": "urn:nasa:pds:insight_twins:data_derived",
        "doi": "10.17189/1518950",
        "source_url": "https://mars.nasa.gov/rss/api/?feed=weather&category=insight_temperature&feedtype=json&ver=1.0",
        "pds_archive_url": "https://atmos.nmsu.edu/PDS/data/PDS4/InSight/twins_bundle/data_derived/",
        "processing_level": "Level 3/4 (PDS4 Calibrated & Sol/Diurnal Derived)",
        "spatial_coverage": {
            "site": "Elysium Planitia",
            "latitude_deg": 4.5024,
            "longitude_deg_east": 135.6234,
            "elevation_km": -2.6,
            "coordinate_system": "Planetocentric (IAU 2000)"
        },
        "temporal_coverage": {
            "start_earth_date": "2018-11-26",
            "end_earth_date": "2022-12-15",
            "start_sol": 0,
            "end_sol": 1366,
            "observation_cadence": "High cadence (0.5 - 1 Hz raw) aggregated to hourly & daily sol statistics"
        },
        "variables": [
            {
                "id": "air_temp",
                "name": "Ambient Air Temperature (Average, Min, Max)",
                "unit": "°C",
                "sensor": "TWINS Boom 1 & Boom 2 platinum resistance thermometers",
                "physical_range": [-105.0, 0.0],
                "uncertainty": "±1.0 °C"
            },
            {
                "id": "pressure",
                "name": "Atmospheric Surface Pressure",
                "unit": "Pa",
                "sensor": "APSS High-resolution micro-barometer (Troll barocap)",
                "physical_range": [650.0, 950.0],
                "uncertainty": "±0.01 Pa resolution, ±1.0 Pa absolute"
            },
            {
                "id": "wind_speed",
                "name": "Horizontal Wind Speed",
                "unit": "m/s",
                "sensor": "TWINS thermal anemometers",
                "physical_range": [0.0, 40.0],
                "uncertainty": "±0.8 m/s"
            },
            {
                "id": "wind_direction",
                "name": "Wind Direction (Degrees & Compass Points)",
                "unit": "degrees (°)",
                "sensor": "TWINS differential thermal anemometer pair",
                "physical_range": [0.0, 360.0],
                "uncertainty": "±15°"
            }
        ],
        "data_quality": {
            "completeness_pct": 91.2,
            "sensor_health": "Operational through Sol 1220; power conservation shutdowns occurred during extended dust events later in mission until decommission on Sol 1366.",
            "known_limitations": [
                "Dust accumulation on solar arrays forced intermittent payload operation and sensor sleep cycles in Martian Year 36.",
                "Thermal perturbation from lander deck requires calibration wind-vector correction models."
            ]
        }
    },
    "mro_mcs_profiles": {
        "id": "mro_mcs_profiles",
        "name": "Mars Reconnaissance Orbiter Mars Climate Sounder (MCS) Vertical Profiles",
        "mission": "Mars Reconnaissance Orbiter (MRO)",
        "spacecraft": "MRO Orbiter",
        "instrument": "Mars Climate Sounder (MCS)",
        "dataset_id": "MRO-M-MCS-5-DDR-V6.2",
        "pds_urn": "urn:nasa:pds:mrom_ddr:profiles",
        "doi": "10.17189/1519088",
        "source_url": "https://atmos.nmsu.edu/PDS/data/MROM_2062/",
        "pds_archive_url": "https://pds-atmospheres.nmsu.edu/data_and_services/atmospheres_data/MARS/mcs.html",
        "processing_level": "Level 2 (PDS3 Standard Derived Data Records - Limb Retrieval)",
        "spatial_coverage": {
            "site": "Global Martian orbital coverage (85°S to 85°N)",
            "latitude_deg": "Variable (-90 to +90)",
            "longitude_deg_east": "Variable (0 to 360)",
            "elevation_km": "0 to 80 km altitude above MOLA datum",
            "coordinate_system": "Planetocentric (IAU 2000)"
        },
        "temporal_coverage": {
            "start_earth_date": "2006-09-15",
            "end_earth_date": "2025-07-01",
            "start_sol": "N/A (Orbital)",
            "end_sol": "N/A (Orbital)",
            "observation_cadence": "Orbital limb scans (approx. 200-400 profiles per 4-hour orbit chunk)"
        },
        "variables": [
            {
                "id": "altitude",
                "name": "Altitude above MOLA Aeroid",
                "unit": "km",
                "sensor": "Limb sounder retrieval geometry",
                "physical_range": [0.0, 85.0],
                "uncertainty": "±1.5 km vertical resolution"
            },
            {
                "id": "profile_temp",
                "name": "Atmospheric Temperature Profile T(z)",
                "unit": "K",
                "sensor": "MCS Mid-IR / Far-IR thermal sounder channels (A1-A6, B1-B3)",
                "physical_range": [110.0, 260.0],
                "uncertainty": "±2.0 to ±5.0 K (1-sigma reported per level)"
            },
            {
                "id": "profile_pressure",
                "name": "Atmospheric Pressure Profile P(z)",
                "unit": "Pa",
                "sensor": "Hydrostatic retrieval from CO2 absorption bands",
                "physical_range": [0.01, 800.0],
                "uncertainty": "Log-pressure vertical grid ±3%"
            },
            {
                "id": "dust_extinction",
                "name": "Dust Aerosol Opacity Extinction",
                "unit": "km⁻¹",
                "sensor": "MCS A5 channel (22 μm dust absorption)",
                "physical_range": [0.0, 0.05],
                "uncertainty": "Reported per retrieval frame"
            },
            {
                "id": "water_ice_extinction",
                "name": "Water Ice Cloud Extinction",
                "unit": "km⁻¹",
                "sensor": "MCS A4 channel (12 μm ice absorption)",
                "physical_range": [0.0, 0.03],
                "uncertainty": "Reported per retrieval frame"
            }
        ],
        "data_quality": {
            "completeness_pct": 95.8,
            "sensor_health": "Operational limb retrieval for over 19 Earth years in Mars orbit.",
            "known_limitations": [
                "Near-surface layers (< 5 km) often obscured by high dust opacity during regional or planet-encircling dust storms (PEDS).",
                "Profiles represent spatial limb integration paths along line-of-sight."
            ]
        }
    }
}

def get_catalog_summary() -> List[Dict[str, Any]]:
    """Returns catalog items formatted for UI summary cards."""
    summaries = []
    for k, v in DATASET_CATALOG.items():
        summaries.append({
            "id": v["id"],
            "name": v["name"],
            "mission": v["mission"],
            "instrument": v["instrument"],
            "pds_urn": v["pds_urn"],
            "doi": v["doi"],
            "processing_level": v["processing_level"],
            "site": v["spatial_coverage"]["site"],
            "temporal_range": f"{v['temporal_coverage']['start_earth_date']} to {v['temporal_coverage']['end_earth_date']}",
            "variables_count": len(v["variables"]),
            "completeness": v["data_quality"]["completeness_pct"],
            "pds_archive_url": v["pds_archive_url"],
            "source_url": v["source_url"]
        })
    return summaries
