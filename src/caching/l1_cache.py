#!/usr/bin/env python3
"""
L1 Cache: Enhanced LRU Cache with Performance Metrics
High-speed in-memory cache with SHA-256 key generation and analytics
"""

import time
import hashlib
from typing import Any, Dict, Optional, Tuple
from collections import OrderedDict
from dataclasses import dataclass, field

@dataclass
class CacheMetrics:
    """Cache performance metrics tracking"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_requests: int = 0
    hit_rate: float = 0.0
    average_access_time: float = 0.0
    memory_usage: int = 0
    
    def update_hit_rate(self):
        """Update calculated hit rate"""
        if self.total_requests > 0:
            self.hit_rate = (self.hits / self.total_requests) * 100

@dataclass  
class CacheEntry:
    """Cache entry with metadata"""
    value: Any
    timestamp: float
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)

class L1Cache:
    """Enhanced LRU Cache with performance monitoring and hash-based keys"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600, metrics_enabled: bool = True):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.metrics_enabled = metrics_enabled
        
        # Cache storage using OrderedDict for LRU behavior
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        
        # Performance metrics
        self.metrics = CacheMetrics()
        
        # Performance tracking
        self._access_times = []
    
    def _generate_key(self, text: str, category: str, truncate_length: int = 16) -> str:
        """Generate SHA-256 hash key for cache lookup"""
        combined = f"{text}|{category}".encode('utf-8')
        hash_digest = hashlib.sha256(combined).hexdigest()
        return hash_digest[:truncate_length]
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry has expired"""
        if self.ttl_seconds <= 0:
            return False  # No expiration
        return (time.time() - entry.timestamp) > self.ttl_seconds
    
    def _cleanup_expired(self):
        """Remove expired entries from cache"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if (current_time - entry.timestamp) > self.ttl_seconds
        ]
        
        for key in expired_keys:
            del self._cache[key]
            if self.metrics_enabled:
                self.metrics.evictions += 1
    
    def _evict_lru(self):
        """Evict least recently used item"""
        if self._cache:
            self._cache.popitem(last=False)  # Remove oldest (LRU)
            if self.metrics_enabled:
                self.metrics.evictions += 1
    
    def get(self, text: str, category: str) -> Optional[Any]:
        """Retrieve value from cache"""
        start_time = time.time()
        
        # Generate cache key
        key = self._generate_key(text, category)
        
        # Update metrics
        if self.metrics_enabled:
            self.metrics.total_requests += 1
        
        # Clean expired entries periodically
        if len(self._cache) % 100 == 0:  # Every 100 requests
            self._cleanup_expired()
        
        # Check if key exists
        if key not in self._cache:
            if self.metrics_enabled:
                self.metrics.misses += 1
                self.metrics.update_hit_rate()
            return None
        
        entry = self._cache[key]
        
        # Check expiration
        if self._is_expired(entry):
            del self._cache[key]
            if self.metrics_enabled:
                self.metrics.misses += 1
                self.metrics.evictions += 1
                self.metrics.update_hit_rate()
            return None
        
        # Move to end (most recently used)
        self._cache.move_to_end(key)
        
        # Update entry metadata
        entry.access_count += 1
        entry.last_accessed = time.time()
        
        # Track performance
        if self.metrics_enabled:
            self.metrics.hits += 1
            self.metrics.update_hit_rate()
            
            access_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            self._access_times.append(access_time)
            
            # Keep only last 1000 access times for average calculation
            if len(self._access_times) > 1000:
                self._access_times = self._access_times[-1000:]
            
            self.metrics.average_access_time = sum(self._access_times) / len(self._access_times)
        
        return entry.value
    
    def put(self, text: str, category: str, value: Any) -> bool:
        """Store value in cache"""
        # Generate cache key
        key = self._generate_key(text, category)
        
        # Check if we need to evict
        if key not in self._cache and len(self._cache) >= self.max_size:
            self._evict_lru()
        
        # Create cache entry
        entry = CacheEntry(
            value=value,
            timestamp=time.time(),
            access_count=1,
            last_accessed=time.time()
        )
        
        # Store in cache
        self._cache[key] = entry
        self._cache.move_to_end(key)  # Mark as most recently used
        
        # Update memory usage estimate
        if self.metrics_enabled:
            self.metrics.memory_usage = len(self._cache)
        
        return True
    
    def clear(self):
        """Clear all cache entries"""
        self._cache.clear()
        if self.metrics_enabled:
            self.metrics.memory_usage = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        if not self.metrics_enabled:
            return {"metrics_disabled": True}
        
        return {
            "cache_size": len(self._cache),
            "max_size": self.max_size,
            "utilization_percent": (len(self._cache) / self.max_size) * 100,
            "hits": self.metrics.hits,
            "misses": self.metrics.misses,
            "evictions": self.metrics.evictions,
            "total_requests": self.metrics.total_requests,
            "hit_rate_percent": self.metrics.hit_rate,
            "average_access_time_ms": self.metrics.average_access_time,
            "ttl_seconds": self.ttl_seconds,
            "metrics": {
                "oldest_entry_age": self._get_oldest_entry_age(),
                "most_accessed_count": self._get_most_accessed_count(),
                "cache_efficiency": self._calculate_efficiency()
            }
        }
    
    def _get_oldest_entry_age(self) -> float:
        """Get age of oldest entry in seconds"""
        if not self._cache:
            return 0.0
        
        oldest_timestamp = min(entry.timestamp for entry in self._cache.values())
        return time.time() - oldest_timestamp
    
    def _get_most_accessed_count(self) -> int:
        """Get highest access count among cached entries"""
        if not self._cache:
            return 0
        
        return max(entry.access_count for entry in self._cache.values())
    
    def _calculate_efficiency(self) -> float:
        """Calculate cache efficiency score (0-1)"""
        if self.metrics.total_requests == 0:
            return 0.0
        
        # Efficiency based on hit rate and eviction rate
        hit_efficiency = self.metrics.hit_rate / 100
        eviction_penalty = (self.metrics.evictions / self.metrics.total_requests) * 0.1
        
        return max(0.0, hit_efficiency - eviction_penalty)


if __name__ == "__main__":
    # Test L1 Cache functionality
    print("🧪 Testing L1 Cache Implementation\n")
    
    # Initialize cache
    cache = L1Cache(max_size=5, ttl_seconds=10, metrics_enabled=True)
    
    # Test basic operations
    test_data = [
        ("Great product!", "Electronics", {"analysis": "positive", "score": 0.9}),
        ("Bad quality", "Electronics", {"analysis": "negative", "score": 0.1}),
        ("Average item", "Books", {"analysis": "neutral", "score": 0.5}),
        ("Excellent service", "Electronics", {"analysis": "positive", "score": 0.95}),
        ("Poor packaging", "Books", {"analysis": "negative", "score": 0.2}),
    ]
    
    # Fill cache
    print("1. Filling cache:")
    for text, category, analysis in test_data:
        cache.put(text, category, analysis)
        print(f"   Stored: '{text[:20]}...' -> {analysis['analysis']}")
    
    # Test cache hits
    print("\n2. Testing cache hits:")
    for text, category, expected in test_data[:3]:  # Test first 3
        result = cache.get(text, category)
        status = "HIT" if result else "MISS"
        print(f"   '{text[:20]}...' -> {status} ({result['analysis'] if result else 'None'})")
    
    # Test cache miss (new item)
    print("\n3. Testing cache miss:")
    result = cache.get("New review text", "Electronics")
    print(f"   'New review text' -> {'HIT' if result else 'MISS'}")
    
    # Test LRU eviction (add one more to exceed max_size)
    print("\n4. Testing LRU eviction:")
    cache.put("Newest review", "Electronics", {"analysis": "positive", "score": 0.8})
    print("   Added new item (should evict oldest)")
    
    # Check if oldest was evicted
    first_text, first_category, _ = test_data[0]
    result = cache.get(first_text, first_category)
    print(f"   Checking oldest item: {'FOUND' if result else 'EVICTED'}")
    
    # Display final statistics
    print("\n5. Final Cache Statistics:")
    stats = cache.get_stats()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"   {key}:")
            for subkey, subvalue in value.items():
                print(f"     {subkey}: {subvalue}")
        else:
            if isinstance(value, float):
                print(f"   {key}: {value:.2f}")
            else:
                print(f"   {key}: {value}")