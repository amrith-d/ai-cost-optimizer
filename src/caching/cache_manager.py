#!/usr/bin/env python3
"""
Cache Manager: Unified L1/L2 Cache Interface
Coordinates multi-level caching with the SmartRouterV2 system
"""

import yaml
from typing import Dict, Any, Optional
from .l1_cache import L1Cache

class CacheManager:
    """Unified cache management with L1/L2 coordination"""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        cache_config = self.config.get('caching', {})
        self.enabled = cache_config.get('enabled', True)
        
        # Initialize L1 cache
        l1_config = cache_config.get('l1_cache', {})
        self.l1_cache = L1Cache(
            max_size=l1_config.get('max_size', 1000),
            ttl_seconds=l1_config.get('ttl_seconds', 3600),
            metrics_enabled=l1_config.get('metrics_enabled', True)
        )
        
        # L2 cache (placeholder for future implementation)
        l2_config = cache_config.get('l2_cache', {})
        self.l2_enabled = l2_config.get('enabled', False)
        self.l2_cache = None  # Will be implemented in Phase 2
        
        # Performance monitoring
        perf_config = cache_config.get('performance', {})
        self.monitoring_enabled = perf_config.get('monitoring_enabled', True)
    
    def get_analysis(self, text: str, category: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached analysis result"""
        if not self.enabled:
            return None
        
        # Try L1 cache first
        result = self.l1_cache.get(text, category)
        if result:
            return result
        
        # L2 cache would be checked here in Phase 2
        if self.l2_enabled and self.l2_cache:
            # Placeholder for L2 cache lookup
            pass
        
        return None
    
    def store_analysis(self, text: str, category: str, analysis: Dict[str, Any]) -> bool:
        """Store analysis result in appropriate cache level"""
        if not self.enabled:
            return False
        
        # Store in L1 cache
        success = self.l1_cache.put(text, category, analysis)
        
        # Store in L2 cache (Phase 2)
        if self.l2_enabled and self.l2_cache:
            # Placeholder for L2 cache storage
            pass
        
        return success
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache performance statistics"""
        if not self.monitoring_enabled:
            return {"monitoring_disabled": True}
        
        stats = {
            "cache_enabled": self.enabled,
            "l1_cache": self.l1_cache.get_stats(),
            "l2_cache": {
                "enabled": self.l2_enabled,
                "status": "Not implemented (Phase 2)"
            }
        }
        
        # Calculate combined metrics
        l1_stats = stats["l1_cache"]
        if "hits" in l1_stats and "total_requests" in l1_stats:
            stats["combined_metrics"] = {
                "total_hits": l1_stats["hits"],
                "total_misses": l1_stats["misses"],
                "total_requests": l1_stats["total_requests"],
                "combined_hit_rate": l1_stats["hit_rate_percent"],
                "cache_levels_active": 1 if not self.l2_enabled else 2
            }
        
        return stats
    
    def clear_all_caches(self):
        """Clear all cache levels"""
        self.l1_cache.clear()
        if self.l2_enabled and self.l2_cache:
            # L2 cache clear would be implemented here
            pass
    
    def is_enabled(self) -> bool:
        """Check if caching is enabled"""
        return self.enabled


if __name__ == "__main__":
    # Test cache manager functionality
    print("🧪 Testing Cache Manager Integration\n")
    
    # Initialize cache manager
    cache_manager = CacheManager()
    
    # Test data
    test_reviews = [
        ("Great product!", "Electronics"),
        ("Poor quality control", "Electronics"), 
        ("Excellent service", "Books"),
        ("Average experience", "Electronics")
    ]
    
    test_analyses = [
        {"sentiment": "positive", "score": 0.9, "complexity": 0.2},
        {"sentiment": "negative", "score": 0.1, "complexity": 0.3},
        {"sentiment": "positive", "score": 0.95, "complexity": 0.25},
        {"sentiment": "neutral", "score": 0.5, "complexity": 0.4}
    ]
    
    # Test cache storage
    print("1. Storing analysis results:")
    for (text, category), analysis in zip(test_reviews, test_analyses):
        success = cache_manager.store_analysis(text, category, analysis)
        print(f"   '{text[:20]}...' -> {'STORED' if success else 'FAILED'}")
    
    # Test cache retrieval
    print("\n2. Retrieving cached results:")
    for text, category in test_reviews:
        result = cache_manager.get_analysis(text, category)
        status = "HIT" if result else "MISS"
        sentiment = result["sentiment"] if result else "None"
        print(f"   '{text[:20]}...' -> {status} ({sentiment})")
    
    # Test cache miss
    print("\n3. Testing cache miss:")
    result = cache_manager.get_analysis("New review", "Electronics")
    print(f"   'New review' -> {'HIT' if result else 'MISS'}")
    
    # Display performance statistics
    print("\n4. Cache Performance Statistics:")
    stats = cache_manager.get_performance_stats()
    
    # Display L1 cache stats
    if "l1_cache" in stats:
        l1_stats = stats["l1_cache"]
        print("   L1 Cache:")
        print(f"     Size: {l1_stats.get('cache_size', 0)}/{l1_stats.get('max_size', 0)}")
        print(f"     Hit Rate: {l1_stats.get('hit_rate_percent', 0):.1f}%")
        print(f"     Requests: {l1_stats.get('total_requests', 0)}")
        print(f"     Efficiency: {l1_stats.get('metrics', {}).get('cache_efficiency', 0):.2f}")
    
    # Display combined stats
    if "combined_metrics" in stats:
        combined = stats["combined_metrics"]
        print("   Combined:")
        print(f"     Total Hit Rate: {combined.get('combined_hit_rate', 0):.1f}%")
        print(f"     Active Levels: {combined.get('cache_levels_active', 0)}")
    
    print(f"\n✅ Cache Manager Test Complete - Caching {'Enabled' if cache_manager.is_enabled() else 'Disabled'}")