#!/usr/bin/env python3
"""
Week 2 Caching System Demo - Advanced Performance Optimization
Demonstrates L1 cache integration with enhanced batch processing
"""

import asyncio
import time
import json
from pathlib import Path
from typing import Dict, List, Any

# Import Week 1 foundation
from src.core.smart_router_v2 import SmartRouterV2
from src.core.cost_reporter import CostReporter

# Import Week 2 enhancements
from src.caching.cache_manager import CacheManager
from src.integrations.enhanced_batch_processor import EnhancedBatchProcessor


class Week2CachingOptimizer:
    """Week 2: Advanced caching system with performance optimization"""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        # Week 1 foundation components
        self.smart_router = SmartRouterV2(config_path)
        self.cost_reporter = CostReporter()
        
        # Week 2 enhancements
        self.cache_manager = CacheManager()
        self.batch_processor = EnhancedBatchProcessor(config_path)
        
    async def run_caching_demo(self, sample_size: int = 5000) -> Dict[str, Any]:
        """Run Week 2 caching system demonstration"""
        
        print("🚀 Week 2 Caching System Demo")
        print("=" * 50)
        
        # Load sample data
        print(f"📊 Loading {sample_size} sample reviews...")
        reviews = self._generate_sample_reviews(sample_size)
        
        # Run performance test
        start_time = time.time()
        
        print(f"⚡ Processing {len(reviews)} reviews with caching...")
        results = await self.batch_processor.process_reviews_batch(reviews)
        
        processing_time = time.time() - start_time
        reviews_per_second = len(reviews) / processing_time if processing_time > 0 else 0
        
        # Get performance metrics
        cache_stats = self.cache_manager.get_performance_stats()
        
        print(f"✅ Processing complete!")
        print(f"📈 Performance: {reviews_per_second:.0f} reviews/second")
        print(f"💾 Cache hit rate: {cache_stats.get('hit_rate', 0):.1f}%")
        
        return {
            'reviews_processed': len(reviews),
            'processing_time': processing_time,
            'reviews_per_second': reviews_per_second,
            'cache_stats': cache_stats,
            'results': results[:10]  # Sample results
        }
    
    def _generate_sample_reviews(self, count: int) -> List[Dict[str, Any]]:
        """Generate sample reviews for demonstration"""
        
        categories = ['Electronics', 'Books', 'Home_and_Garden']
        sample_reviews = [
            "Great product! Love it.",
            "The technical specifications are impressive with multi-core processing and advanced GPU architecture.",
            "Good quality but expensive.",
            "Assembly was difficult and the instructions were unclear.",
            "Excellent storytelling with complex character development and intricate plot structure.",
            "Average book, nothing special.",
            "The narrative complexity showcases sophisticated literary techniques throughout.",
            "Weather-resistant materials with excellent durability for outdoor applications."
        ]
        
        reviews = []
        for i in range(count):
            category = categories[i % len(categories)]
            review_text = sample_reviews[i % len(sample_reviews)]
            
            reviews.append({
                'review_id': f'demo_{i:05d}',
                'review_text': review_text,
                'category': category,
                'product_id': f'prod_{i % 100}'
            })
        
        return reviews
    
    def save_results(self, results: Dict[str, Any], output_dir: str = "data") -> str:
        """Save demonstration results"""
        
        Path(output_dir).mkdir(exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"week2_caching_results_{timestamp}.json"
        filepath = Path(output_dir) / filename
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        return str(filepath)


async def main():
    """Run Week 2 caching system demonstration"""
    
    optimizer = Week2CachingOptimizer()
    
    try:
        # Run the caching demo
        results = await optimizer.run_caching_demo(sample_size=5000)
        
        # Save results
        results_file = optimizer.save_results(results)
        print(f"📁 Results saved to: {results_file}")
        
        # Display summary
        print("\n" + "=" * 50)
        print("📊 WEEK 2 PERFORMANCE SUMMARY")
        print("=" * 50)
        print(f"Reviews Processed: {results['reviews_processed']:,}")
        print(f"Processing Speed: {results['reviews_per_second']:,.0f} reviews/second")
        print(f"Total Time: {results['processing_time']:.2f} seconds")
        print(f"Cache Hit Rate: {results['cache_stats'].get('hit_rate', 0):.1f}%")
        print(f"Cache Entries: {results['cache_stats'].get('total_entries', 0):,}")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())