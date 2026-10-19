# NASA Data Sources & Provenance Registry

> **Scientific Integrity Notice**: This document accurately classifies every dataset by its actual verification status.
> Curiosity REMS records are retrieved from the NASA Mars Weather API (cached PDS-backed archive).
> InSight TWINS and MRO MCS data are calibrated **demonstration simulations**; they are not sourced from
> PDS product downloads and must never be presented as authentic archived observations.

---

## Source Assessment Table

| Source | Mission | Instrument | Data Status | Time Coverage | Spatial Info | Analytical Relevance |
|---|---|---|---|---|---|---|
| NASA Mars Weather API (PDS-backed cache) | Mars Science Laboratory (MSL) | REMS | **CACHED VERIFIED ARCHIVE** | Sol 1 to Sol 4,745+ (2012–2026) | Gale Crater (-4.59° N, 137.44° E, -4.5 km) | Critical — 13+ Earth years of continuous in-situ planetary weather |
| Calibrated Simulation Baseline | InSight Lander | TWINS/APSS | **SYNTHETIC DEMONSTRATION** | 50 reference Sols (2018-epoch) | Elysium Planitia (+4.50° N, 135.62° E, -2.6 km) | Illustrative — physically plausible inter-site comparison baseline only |
| Parameterized Reference Model | Mars Reconnaissance Orbiter (MRO) | MCS | **SYNTHETIC DEMONSTRATION** | 4 reference profiles (MY 34–35) | Global limb (0–80 km altitude) | Illustrative — hydrostatic scale-height profiles calibrated against known MCS characteristics |

---

## Detailed Data Source Profiles

### 1. Curiosity (MSL) REMS Daily Environmental Observations

**Status: CACHED VERIFIED ARCHIVE (PDS-backed)**

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
- **Application Provenance Tag**: `CACHED_VERIFIED_SOURCE` — data retrieved from the NASA Mars Weather API, which serves official PDS-archived REMS derived products. Records carry multi-dimensional validation: source authenticity, structural validity, physical plausibility, completeness, and analysis suitability are tracked independently.
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

---

### 2. InSight TWINS & APSS Meteorology

**Status: SYNTHETIC DEMONSTRATION — Not sourced from PDS product downloads**

- **Represented Mission**: InSight Lander
- **Represented Instrument**: Temperature and Wind for InSight (TWINS) & Auxiliary Payload Sensor Suite (APSS)
- **Reference PDS Dataset ID**: `urn:nasa:pds:insight_twins:data_derived`
- **Reference DOI**: [10.17189/1518950](https://doi.org/10.17189/1518950)
- **PDS Archive**: `https://atmos.nmsu.edu/PDS/data/PDS4/InSight/twins_bundle/data_derived/`
- **Application Provenance Tag**: `SYNTHETIC` — 50 calibrated reference Sol records. Atmospheric values are physically plausible baselines; Sol timestamps are derived from InSight landing epoch (2018-11-26T00:00:00Z) at 88,775.244 s/sol. These records are **not** retrieved from PDS and must not be cited as authentic InSight observations.
- **Purpose**: Demonstrates inter-site atmospheric comparison (Elysium Planitia vs. Gale Crater) under controlled conditions.
- **Variables & Units** (representative):
  - `air_temp_mean_c`: Celsius (°C)
  - `pressure_pa`: Pascals (Pa)
  - `wind_speed_mean_ms`: Meters per second (m/s)
  - `wind_direction_deg`: Degrees (°)
- **Limitation**: Wind speed data sparse; dust accumulation on solar arrays forced operational shutdowns in later mission phases (authentic InSight context, not replicated in simulation).

---

### 3. MRO Mars Climate Sounder (MCS) Vertical Profiles

**Status: SYNTHETIC DEMONSTRATION — Not sourced from PDS orbital retrievals**

- **Represented Mission**: Mars Reconnaissance Orbiter (MRO)
- **Represented Instrument**: Mars Climate Sounder (MCS)
- **Reference PDS Dataset ID**: `MRO-M-MCS-5-DDR-V6.2`
- **Reference DOI**: [10.17189/1519088](https://doi.org/10.17189/1519088)
- **PDS Archive**: `https://pds-atmospheres.nmsu.edu/data_and_services/atmospheres_data/MARS/mcs.html`
- **Application Provenance Tag**: `SYNTHETIC` — 4 parameterized reference sounding profiles spanning 0–80 km altitude. Hydrostatic scale-height model calibrated against characteristic MCS Level 2 DDR structure and uncertainty envelopes. These are **not** sourced from actual orbital limb scans.
- **Purpose**: Demonstrates vertical atmospheric sounding capabilities and uncertainty visualization (1-σ temperature envelopes).
- **Variables & Units** (representative):
  - `altitude_km`: Kilometers (km), vertical resolution ±1.5 km
  - `pressure_pa`: Pascals (Pa), hydrostatic log-pressure grid
  - `temperature_k`: Kelvin (K), 1-sigma uncertainty ±1.5 to ±6.3 K
  - `dust_extinction_km_inv`: Inverse kilometers (km⁻¹), MCS 22 μm channel equivalent
  - `water_ice_extinction_km_inv`: Inverse kilometers (km⁻¹), MCS 12 μm channel equivalent
- **Limitation**: Near-surface layers (< 5 km) obscured during intense planet-encircling dust storms (PEDS) in authentic MCS retrievals.

---

## Data Provenance Transparency

| Dataset | Source Type | Application Tag | `is_synthetic` | Notes |
|---|---|---|---|---|
| Curiosity REMS | NASA Mars Weather API (PDS-backed) | `CACHED_VERIFIED_SOURCE` | `false` | 4,745+ daily Sol records; multi-dimensional provenance tags applied |
| InSight TWINS/APSS | Calibrated simulation baseline | `SYNTHETIC` | `true` | Sol dates derived from InSight landing epoch (2018-11-26 UTC); atmospheric values are reference baselines only |
| MRO MCS Profiles | Parameterized reference model | `SYNTHETIC` | `true` | 4 hydrostatic scale-height profiles; structurally consistent with PDS DDR format but not from actual orbital limb scans |

### InSight UTC Derivation Method
InSight Sol dates are computed from the documented landing epoch:
- Sol 0 = 2018-11-26T00:00:00Z (InSight landing date)
- Each Sol = 88,775.244 seconds (1 Martian solar day)
- Formula: `UTC(sol) = epoch + sol × 88775.244 seconds`

This eliminates the previously invalid date `2019-13-18` (month 13) that appeared in raw generated data.

### Provenance State Definitions

| State | Meaning |
|---|---|
| `VERIFIED_SOURCE` | Record origin traceable to authoritative NASA/PDS source with independent confirmation |
| `CACHED_VERIFIED_SOURCE` | Retrieved from API serving PDS-backed data; origin verifiable via dataset ID and DOI |
| `UNVERIFIED_SOURCE` | Origin plausible but not independently confirmed against PDS |
| `SYNTHETIC` | Generated or parameterized; not an actual archived observation |
| `DERIVED` | Computed from other records (e.g. diurnal amplitude = max − min temperature) |
| `UNAVAILABLE` | Source attempted but not reachable at retrieval time |
