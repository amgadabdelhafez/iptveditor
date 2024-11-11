import logging
from typing import Dict, Any, Optional

class CacheManager:
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.hits: Dict[str, int] = {}
        self.misses: Dict[str, int] = {}
        self.logger = logging.getLogger(__name__)

    def get(self, cache_type: str, key: str) -> Optional[Any]:
        """Get value from cache"""
        if cache_type not in self.cache:
            self.cache[cache_type] = {}
            self.hits[cache_type] = 0
            self.misses[cache_type] = 0

        value = self.cache[cache_type].get(key)
        if value is not None:
            self.hits[cache_type] += 1
            hit_rate = self._calculate_hit_rate(cache_type)
            self.logger.debug(f"Cache HIT for {cache_type} (Hit rate: {hit_rate:.1f}%)")
        else:
            self.misses[cache_type] += 1
            hit_rate = self._calculate_hit_rate(cache_type)
            self.logger.debug(f"Cache MISS for {cache_type} (Hit rate: {hit_rate:.1f}%)")

        return value

    def set(self, cache_type: str, key: str, value: Any) -> None:
        """Set value in cache"""
        if cache_type not in self.cache:
            self.cache[cache_type] = {}
        self.cache[cache_type][key] = value

    def _calculate_hit_rate(self, cache_type: str) -> float:
        """Calculate hit rate for cache type"""
        total = self.hits[cache_type] + self.misses[cache_type]
        return (self.hits[cache_type] / total * 100) if total > 0 else 0

    def report_stats(self) -> None:
        """Report cache statistics"""
        total_hits = sum(self.hits.values())
        total_misses = sum(self.misses.values())
        total = total_hits + total_misses
        hit_rate = (total_hits / total * 100) if total > 0 else 0
        
        self.logger.debug(
            f"Cache Statistics - "
            f"Hits: {total_hits} "
            f"Misses: {total_misses} "
            f"Hit Rate: {hit_rate:.1f}%"
        )

cache_manager = CacheManager()
