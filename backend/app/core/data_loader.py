"""
Singleton Data Loader with LRU caching for authoritative NASA Planetary Data System datasets.
Prevents repeated disk reads and ensures clear boundary isolation between authentic NASA observations
and synthetic / demonstration data.
"""

from functools import lru_cache
from typing import List, Dict, Any
import copy
import logging

from app.data.ingestion import ingestion_engine

logger = logging.getLogger(__name__)

class DataLoaderSingleton:
    """Thread-safe cached data loader for Curiosity, InSight, and MRO MCS."""

    def __init__(self):
        self._curiosity_cache: List[Dict[str, Any]] = []
        self._insight_cache: List[Dict[str, Any]] = []
        self._mcs_cache: List[Dict[str, Any]] = []
        self._is_warmed: bool = False

    def warm_cache(self) -> None:
        """Preloads datasets into in-memory cache during application lifespan startup."""
        logger.info("Warming PDS dataset caches...")
        self._curiosity_cache = ingestion_engine.ingest_curiosity_rems()
        self._insight_cache = ingestion_engine.ingest_insight_meteorology()
        self._mcs_cache = ingestion_engine.ingest_mcs_profiles()
        self._is_warmed = True
        logger.info(
            f"Cache warmed successfully: {len(self._curiosity_cache)} Curiosity Sols, "
            f"{len(self._insight_cache)} InSight Sols, {len(self._mcs_cache)} MRO MCS profiles."
        )

    def get_curiosity_records(self) -> List[Dict[str, Any]]:
        """Returns verified Curiosity REMS observational records."""
        if not self._is_warmed or not self._curiosity_cache:
            self._curiosity_cache = ingestion_engine.ingest_curiosity_rems()
        return self._curiosity_cache

    def get_insight_records(self) -> List[Dict[str, Any]]:
        """Returns verified InSight TWINS observational records."""
        if not self._is_warmed or not self._insight_cache:
            self._insight_cache = ingestion_engine.ingest_insight_meteorology()
        return self._insight_cache

    def get_mcs_profiles(self) -> List[Dict[str, Any]]:
        """Returns verified MRO Mars Climate Sounder vertical sounding profiles."""
        if not self._is_warmed or not self._mcs_cache:
            self._mcs_cache = ingestion_engine.ingest_mcs_profiles()
        return self._mcs_cache

# Global singleton instance
data_loader = DataLoaderSingleton()

@lru_cache(maxsize=32)
def get_cached_curiosity_tuple():
    """Tuple-based lru_cache for fast immutable access when needed."""
    return tuple(data_loader.get_curiosity_records())
