"""
Singleton Data Loader with thread-safe in-memory caching for NASA datasets.
Eliminates redundant disk reads and enforces strict isolation boundaries
between authentic NASA observations and synthetic / demonstration data.
"""

from functools import lru_cache
from typing import List, Dict, Any, Optional
import copy
import datetime
import logging
import threading

from app.data.ingestion import ingestion_engine
from app.analytics.anomaly import detect_multivariate_anomalies, detect_univariate_anomalies
from app.analytics.time_series import downsample_vertical_profiles

logger = logging.getLogger(__name__)

class DataLoader:
    """Thread-safe cached data loader for Curiosity, InSight, and MRO MCS."""

    def __init__(self):
        self._lock = threading.RLock()
        self._curiosity_records: List[Dict[str, Any]] = []
        self._insight_records: List[Dict[str, Any]] = []
        self._mcs_profiles: List[Dict[str, Any]] = []
        self._quality_scorecard: Optional[Dict[str, Any]] = None
        self._curiosity_sol_index: Dict[int, Dict[str, Any]] = {}
        self._multivariate_anomalies: Optional[List[Dict[str, Any]]] = None
        self._univariate_anomaly_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._ml_experiment_cache: Optional[Dict[str, Any]] = None
        self._is_preloaded: bool = False
        self._last_loaded_at: Optional[datetime.datetime] = None
        self._load_failures: int = 0

    def preload_all(self) -> None:
        """Preloads datasets into in-memory cache and builds fast O(1) indices."""
        with self._lock:
            logger.info("DataLoader: Preloading NASA Planetary Datasets into memory...")
            try:
                self._curiosity_records = ingestion_engine.ingest_curiosity_rems()
                self._insight_records = ingestion_engine.ingest_insight_meteorology()
                self._mcs_profiles = ingestion_engine.ingest_mcs_profiles()
                self._quality_scorecard = ingestion_engine.generate_quality_scorecard()

                # Build fast O(1) Sol index map
                self._curiosity_sol_index = {
                    int(r["sol"]): r for r in self._curiosity_records if r.get("sol") is not None
                }

                # Pre-compute multivariate anomalies
                logger.info("DataLoader: Pre-computing multivariate anomalies...")
                self._multivariate_anomalies = detect_multivariate_anomalies(self._curiosity_records)

                # Pre-compute common univariate anomalies
                for var in ["air_temp_max_c", "air_temp_min_c", "temp_amplitude_c", "pressure_pa"]:
                    self._univariate_anomaly_cache[var] = detect_univariate_anomalies(
                        self._curiosity_records, variable=var, threshold=3.0
                    )

                self._is_preloaded = True
                self._last_loaded_at = datetime.datetime.now(datetime.timezone.utc)
                logger.info(
                    f"DataLoader: Preload complete. {len(self._curiosity_records)} Curiosity Sols, "
                    f"{len(self._insight_records)} InSight Sols, {len(self._mcs_profiles)} MCS profiles cached."
                )
            except Exception as e:
                self._load_failures += 1
                logger.error(f"DataLoader: Preload failed: {e}")
                raise

    def warm_cache(self) -> None:
        """Alias for preload_all for backward compatibility."""
        self.preload_all()

    def is_ready(self) -> bool:
        """Returns True if the authoritative Curiosity dataset is successfully loaded."""
        with self._lock:
            return self._is_preloaded and len(self._curiosity_records) > 0

    def get_cache_metadata(self) -> Dict[str, Any]:
        """Returns structured cache freshness and volume metadata without leaking secrets."""
        with self._lock:
            return {
                "is_preloaded": self._is_preloaded,
                "is_ready": self.is_ready(),
                "last_loaded_at": self._last_loaded_at.isoformat() if self._last_loaded_at else None,
                "curiosity_count": len(self._curiosity_records),
                "insight_count": len(self._insight_records),
                "mcs_count": len(self._mcs_profiles),
                "load_failures": self._load_failures,
            }

    def get_curiosity_records(self) -> List[Dict[str, Any]]:
        """Returns defensive copies of in-memory Curiosity records to prevent cache mutation."""
        with self._lock:
            if not self._is_preloaded or not self._curiosity_records:
                self.preload_all()
            return [r.copy() for r in self._curiosity_records]

    def get_insight_records(self) -> List[Dict[str, Any]]:
        """Returns defensive copies of in-memory InSight records to prevent cache mutation."""
        with self._lock:
            if not self._is_preloaded or not self._insight_records:
                self.preload_all()
            return [r.copy() for r in self._insight_records]

    def get_mcs_profiles(self, downsample: bool = False, target_levels: int = 15) -> List[Dict[str, Any]]:
        """Returns MRO MCS vertical sounding profiles (defensive copies)."""
        with self._lock:
            if not self._is_preloaded or not self._mcs_profiles:
                self.preload_all()
            profiles = copy.deepcopy(self._mcs_profiles)
        if downsample:
            return downsample_vertical_profiles(profiles, target_levels=target_levels)
        return profiles

    def get_scorecard(self) -> Dict[str, Any]:
        """Returns dynamically computed data quality scorecard (defensive copy)."""
        with self._lock:
            if not self._is_preloaded or not self._quality_scorecard:
                self.preload_all()
            return copy.deepcopy(self._quality_scorecard) if self._quality_scorecard else {}

    def get_sol_record(self, sol: int) -> Optional[Dict[str, Any]]:
        """O(1) dictionary retrieval of Curiosity observation for a specific Sol (defensive copy)."""
        with self._lock:
            if not self._is_preloaded:
                self.preload_all()
            rec = self._curiosity_sol_index.get(sol)
            return rec.copy() if rec else None

    def get_sol_index(self) -> Dict[int, Dict[str, Any]]:
        """Returns defensive copy of full Sol index map."""
        with self._lock:
            if not self._is_preloaded:
                self.preload_all()
            return {s: r.copy() for s, r in self._curiosity_sol_index.items()}

    def get_multivariate_anomalies(self) -> List[Dict[str, Any]]:
        """Returns defensive copy of pre-computed multivariate anomalies."""
        with self._lock:
            if not self._is_preloaded or not self._multivariate_anomalies:
                self.preload_all()
            return [copy.deepcopy(a) for a in self._multivariate_anomalies]

    def get_univariate_anomalies(self, variable: str = "air_temp_max_c", threshold: float = 3.0) -> List[Dict[str, Any]]:
        """Returns pre-computed or dynamically computed univariate anomalies."""
        with self._lock:
            if not self._is_preloaded:
                self.preload_all()
            if variable in self._univariate_anomaly_cache and threshold == 3.0:
                return [copy.deepcopy(a) for a in self._univariate_anomaly_cache[variable]]
            return detect_univariate_anomalies(self._curiosity_records, variable=variable, threshold=threshold)

    def get_ml_experiment(self) -> Optional[Dict[str, Any]]:
        """Returns cached ML experiment result (defensive copy)."""
        with self._lock:
            return copy.deepcopy(self._ml_experiment_cache) if self._ml_experiment_cache else None

    def set_ml_experiment(self, exp: Dict[str, Any]) -> None:
        """Sets cached ML experiment with defensive copy."""
        with self._lock:
            self._ml_experiment_cache = copy.deepcopy(exp)

    # --- Strict Isolation Boundary for DEMONSTRATION DATA ---
    def get_demo_scenario_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Produces simulation payloads strictly isolated from real telemetry caches.
        Payload is immutably tagged DEMONSTRATION DATA and simulated.
        """
        return {
            "data_provenance": "DEMONSTRATION DATA",
            "data_origin": "simulated",
            "is_simulation": True,
            "simulation_parameters": copy.deepcopy(params)
        }

# Global singleton instance
data_loader = DataLoader()

@lru_cache(maxsize=32)
def get_cached_curiosity_tuple():
    """Tuple-based lru_cache for fast immutable access when needed."""
    return tuple(data_loader.get_curiosity_records())
