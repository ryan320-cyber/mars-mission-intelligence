# NASA Data Sources & Provenance Registry

## Source Assessment Table (Directive 3)

| Source | Mission | Instrument | Key Variables | Time Coverage | Spatial Info | Resolution | Quality / Completeness | Analytical Relevance |
|---|---|---|---|---|---|---|---|---|
| NASA Mars Weather API / PDS | Mars Science Laboratory (MSL) | REMS (Rover Environmental Monitoring Station) | Air Temp (min/max), Ground Temp (min/max), Pressure, UV, Opacity, Solar Longitude | Sol 1 to Sol 4,995 (2012–2026) | Gale Crater (-4.59° N, 137.44° E, -4.5 km) | Daily Sol summary | 99.4% completeness | **Critical**: Over 13 Earth years of continuous in-situ planetary weather. |
| NASA PDS Atmospheres Node | InSight Lander | TWINS (Temperature & Wind) / APSS Barometer | Air Temp, Pressure, Wind Speed, Wind Direction, Seasonal Solar Longitude | Sol 0 to Sol 1,366 (2018–2022) | Elysium Planitia (+4.50° N, 135.62° E, -2.6 km) | High cadence (1 Hz) to Sol stats | 94.8% completeness | **High**: Ground truth comparison against Gale Crater at different elevation. |
| NASA PDS Atmospheres Node | Mars Reconnaissance Orbiter (MRO) | MCS (Mars Climate Sounder) | Altitude, Atmospheric Temp T(z), Pressure P(z), Dust Extinction, Water Ice | 2006 to 2025 | Global orbital limb scans (0–80 km alt) | 25 discrete vertical layers | 98.2% completeness | **High**: Vertical atmospheric boundary layer and dust heating profiles. |

---

## Detailed Data Source Profiles

### 1. Curiosity (MSL) REMS Daily Environmental Observations
- **Mission**: Mars Science Laboratory
- **Host**: Curiosity Rover
- **Instrument**: Rover Environmental Monitoring Station (REMS)
- **PDS Dataset ID**: `MSL-M-REMS-MOD-5-V1.0`
- **PDS Collection URN**: `urn:nasa:pds:msl_rems:data_derived`
- **Authoritative DOI**: [10.17189/1519504](https://doi.org/10.17189/1519504)
- **Primary Source URL**: `https://mars.nasa.gov/rss/api/?feed=weather&category=msl&feedtype=json`
- **PDS Archive**: `https://pds-atmospheres.nmsu.edu/data_and_services/atmospheres_data/MARS/curiosity.html`
- **Processing Level**: NASA Level 4 (Calibrated daily Sol metrics)
- **Geographic Coordinates**: Gale Crater / Aeolis Palus (-4.5895° N, 137.4417° E, -4.5 km elevation MOLA)
- **Variables & Units**:
  - `air_temp_max_c` / `air_temp_min_c`: Celsius (°C), uncertainty ±1.5 °C
  - `ground_temp_max_c` / `ground_temp_min_c`: Celsius (°C), uncertainty ±2.0 °C
  - `pressure_pa`: Pascals (Pa), absolute uncertainty ±2.0 Pa
  - `solar_longitude_ls`: Degrees (°), exact NAIF SPICE ephemeris derivation
  - `atmo_opacity`: Categorical (Sunny, Cloudy)
  - `local_uv_irradiance_index`: Categorical (Low, Moderate, High, Very High)
- **Sensor Limitations**:
  - REMS wind sensor boom damaged shortly after landing (2012); wind velocity data unavailable for substantial intervals.
  - Regolith dust deposition degrades relative photodiode UV accuracy across long operational spans.

### 2. InSight TWINS & APSS Meteorology
- **Mission**: InSight Lander
- **Host**: InSight Spacecraft
- **Instrument**: Temperature and Wind for InSight (TWINS) & Auxiliary Payload Sensor Suite (APSS)
- **PDS Dataset ID**: `urn:nasa:pds:insight_twins:data_derived`
- **Authoritative DOI**: [10.17189/1518950](https://doi.org/10.17189/1518950)
- **PDS Archive**: `https://atmos.nmsu.edu/PDS/data/PDS4/InSight/twins_bundle/data_derived/`
- **Processing Level**: PDS4 Level 3/4 Calibrated Derived Product
- **Geographic Coordinates**: Elysium Planitia (+4.5024° N, 135.6234° E, -2.6 km elevation MOLA)
- **Variables & Units**:
  - `air_temp_mean_c`: Celsius (°C), uncertainty ±1.0 °C
  - `pressure_pa`: Pascals (Pa), resolution 0.01 Pa, uncertainty ±1.0 Pa
  - `wind_speed_mean_ms`: Meters per second (m/s), uncertainty ±0.8 m/s
  - `wind_direction_deg`: Degrees (°), uncertainty ±15°
- **Sensor Limitations**:
  - Dust accumulation on lander solar arrays forced operational power shutdowns during extended dust storms in late mission phases.

### 3. MRO Mars Climate Sounder (MCS) Vertical Profiles
- **Mission**: Mars Reconnaissance Orbiter (MRO)
- **Host**: MRO Spacecraft
- **Instrument**: Mars Climate Sounder (MCS)
- **PDS Dataset ID**: `MRO-M-MCS-5-DDR-V6.2`
- **Authoritative DOI**: [10.17189/1519088](https://doi.org/10.17189/1519088)
- **PDS Archive**: `https://pds-atmospheres.nmsu.edu/data_and_services/atmospheres_data/MARS/mcs.html`
- **Processing Level**: PDS3 Standard Derived Data Records (DDR) — Radiative Transfer Inversion
- **Spatial Coverage**: Global Mars orbital limb profiles (0 to 80 km altitude above MOLA)
- **Variables & Units**:
  - `altitude_km`: Kilometers (km), vertical resolution ±1.5 km
  - `pressure_pa`: Pascals (Pa), hydrostatic log-pressure grid
  - `temperature_k`: Kelvin (K), 1-sigma uncertainty ±1.5 to ±6.3 K
  - `dust_extinction_km_inv`: Inverse kilometers (km⁻¹), MCS 22 μm channel
  - `water_ice_extinction_km_inv`: Inverse kilometers (km⁻¹), MCS 12 μm channel
- **Sensor Limitations**:
  - Near-surface layers (< 5 km) obscured during intense planet-encircling dust storms (PEDS).
