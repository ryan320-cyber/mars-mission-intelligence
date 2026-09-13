# Architecture Document: Mars Mission Intelligence

A NASA Data + AI Scientific Analysis Platform for Mars Exploration.

```mermaid
flowchart TD
    subgraph Authoritative_Sources ["NASA Authoritative Data Sources"]
        PDS_InSight["NASA PDS InSight TWINS/APSS<br/>(Elysium Planitia, Level 4)"]
        NASA_MSL["NASA Curiosity MSL REMS<br/>(Gale Crater, 4,745+ Sols)"]
        PDS_MCS["NASA PDS MRO Mars Climate Sounder<br/>(Atmospheric Sounding Profiles)"]
    end

    subgraph Backend_Core ["FastAPI Backend Architecture"]
        Ingestion["Data Ingestion & Automated Quality Checks<br/>(Schema, Type, Physical Range, Gap Analysis)"]
        LocalStorage["Offline Local Storage Cache<br/>(Parquet / Structured JSON)"]
        TimeSeriesEngine["Time-Series & Downsampling Engine<br/>(Sol Synchronization, Decimation)"]
        StatisticalEngine["Statistical Boundary Layer Engine<br/>(Non-Parametric Mann-Whitney U, Pearson/Spearman)"]
        AnomalyEngine["Dual-Mode Anomaly Intelligence<br/>(Robust Z-Score MAD + Isolation Forest)"]
        MECIEngine["Martian Environmental Challenge Index<br/>(Thermal Stress + Barometric Waves + Anomaly + Dust)"]
        ModelLabEngine["ML Model Lab<br/>(Chronological Partition, Persistence Baseline, Random Forest, SHAP)"]
        AIEngine["Grounded Mars AI Scientist<br/>(AI Answer Contract, Clickable Evidence Links)"]
    end

    subgraph Frontend_UI ["React + TypeScript + Tailwind Frontend"]
        M01["01 Mission Overview Dashboard"]
        M02["02 Multi-Mission Explorer & Table"]
        M03["03 Vertical Atmospheric Profiles"]
        M04["04 Anomaly Timeline & Event Replay"]
        M05["05 Mars Spatial & Topographic Map"]
        M06["06 Challenge Index & Scenario Simulator"]
        M07["07 Model Lab & Error Analysis"]
        M08["08 Grounded AI Scientist & Evidence Trace"]
        M09["09 NASA Data Catalog & Provenance"]
        M10["10 Science Notebook & Disclaimers"]
        DEMO["NASA Space Apps Judge Demo Mode"]
    end

    Authoritative_Sources --> Ingestion
    Ingestion --> LocalStorage
    LocalStorage --> TimeSeriesEngine & StatisticalEngine & AnomalyEngine & MECIEngine & ModelLabEngine
    TimeSeriesEngine & StatisticalEngine & AnomalyEngine & MECIEngine & ModelLabEngine --> AIEngine

    Backend_Core --> Frontend_UI
```

## System Components

### 1. Data Ingestion & Quality Layer (`backend/app/data/`)
- **Adapters**: Connects to the official NASA Mars Weather API feeds and mirrors NASA PDS4 collections.
- **Data Quality Scorecard**:
  - Schema integrity check (typed Pydantic validation)
  - Physical sanity checks (-130°C to +35°C for surface temperatures, 500 Pa to 1250 Pa for surface pressure)
  - Duplicate detection and chronological monotonicity verification
  - Sensor gap tagging ($\Delta \text{Sol} > 1$) with zero silent interpolation
- **Offline Cache**: Ensures 100% platform availability even during external NASA server downtimes.

### 2. Analytical & Statistical Subsystem (`backend/app/analytics/`)
- **Martian Ephemeris & Solar Longitude ($L_s$)**: Bins observations by true orbital position, capturing eccentricity and seasonal dust liftoff.
- **Parametric & Non-Parametric Correlation**: Pearson ($r$) and Spearman ($\rho$) with sample size ($N$) and two-tailed p-values.
- **Cross-Mission Comparative Testing**: Mann-Whitney U test between Gale Crater (-4.5 km MOLA) and Elysium Planitia (-2.6 km MOLA), proving hydrostatic scale height elevation effects.

### 3. Dual-Mode Anomaly Intelligence (`backend/app/analytics/anomaly.py`)
- **Univariate**: Robust Modified Z-Score based on Median Absolute Deviation (MAD), avoiding Gaussian distortion.
- **Multivariate**: Scikit-Learn `IsolationForest` detecting anomalous joint planetary states $[T_{max}, T_{min}, \Delta T, P]$.
- **Signature Wow Moment #1 (Event Replay)**: Reconstructs surrounding telemetry ($T-12 \to T+12$ Sols) with interactive scrubbing and scientific narration.

### 4. Martian Environmental Challenge Index (MECI)
- Transparent engineering metric on a 0–100 scale:
  $$MECI = 0.35 \cdot F_{thermal} + 0.25 \cdot F_{pressure} + 0.25 \cdot F_{anomaly} + 0.15 \cdot F_{season}$$
- Factor breakdown bars and simulated What-If scenario sensitivity tool.

### 5. ML Model Lab (`backend/app/ml/`)
- Chronological time-series partition: 70% Train, 15% Validation, 15% Test.
- Compares Persistence Baseline ($y_t = y_{t-1}$) and Rolling 7-Sol Mean vs. Ridge Regression and Random Forest Regressor.
- Honest slice-based failure analysis exposing error spikes during perihelion dust storm onset.

### 6. Grounded Mars AI Scientist (`backend/app/ai/`)
- AI Answer Contract:
  - `FINDING`
  - `DATA EVIDENCE` (exact figures, Sols, and p-values)
  - `ANALYTICAL INTERPRETATION`
  - `LIMITATIONS`
  - `SOURCE`
- Refusal of false certainty for out-of-scope or unmeasured variables.
- Signature Wow Moment #2: Clickable evidence trace links directly highlighting the corresponding raw charts.
