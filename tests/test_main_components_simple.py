#!/usr/bin/env python3
"""
Simple Unit Tests for Main Components
Tests current API functionality only - matches actual implementation
"""

import unittest
import tempfile
import os
import json
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import AmazonDataLoader, ModelRouter, SemanticCache, AmazonReviewAnalyzer, ProductReviewResult


class TestAmazonDataLoader(unittest.TestCase):
    """Test AmazonDataLoader functionality with current API"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_config_path = os.path.join(os.path.dirname(__file__), 'test_config.yaml')
        self.loader = AmazonDataLoader(config_path=self.test_config_path)
    
    def test_initialization_with_config(self):
        """Test loader initializes with configuration"""
        self.assertIsNotNone(self.loader.data_config)
        self.assertEqual(self.loader.data_config['default_sample_size'], 10)
        self.assertEqual(self.loader.data_config['default_batch_size'], 5)
        self.assertIn('Electronics', self.loader.categories)
        self.assertIn('Books', self.loader.categories)
        self.assertIn('Home_and_Garden', self.loader.categories)
    
    def test_config_loading(self):
        """Test configuration loading works"""
        self.assertIsNotNone(self.loader.config)
        self.assertIn('data_loading', self.loader.config)
        
    def test_categories_available(self):
        """Test that valid categories are defined"""
        expected_categories = ["Electronics", "Books", "Home_and_Garden"]
        self.assertEqual(self.loader.categories, expected_categories)


class TestModelRouter(unittest.TestCase):
    """Test ModelRouter functionality with current API"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_config_path = os.path.join(os.path.dirname(__file__), 'test_config.yaml')
        self.router = ModelRouter(config_path=self.test_config_path)
    
    def test_initialization_with_config(self):
        """Test router initializes with model costs from config"""
        self.assertIsNotNone(self.router.model_costs)
        self.assertGreater(len(self.router.model_costs), 0)
        
        # Check some expected models are loaded
        model_names = list(self.router.model_costs.keys())
        self.assertTrue(any('gpt' in model.lower() for model in model_names))
    
    def test_route_request(self):
        """Test request routing logic"""
        # Test different text lengths and categories
        test_cases = [
            {"text": "Short review", "category": "Books"},
            {"text": "A much longer review with more detailed analysis and multiple aspects covered", "category": "Electronics"},
            {"text": "Medium length review with some technical details", "category": "Home_and_Garden"}
        ]
        
        for case in test_cases:
            model = self.router.route_request(case["text"], case["category"])
            self.assertIsInstance(model, str)
            self.assertIn(model, self.router.model_costs.keys())
    
    def test_different_text_lengths(self):
        """Test routing for different text lengths"""
        short_text = "Good"
        medium_text = "This product works well and I'm satisfied with the purchase"
        long_text = "This is a very detailed review covering multiple aspects of the product including performance, build quality, value for money, comparison with competitors, and detailed analysis of pros and cons based on extended usage"
        
        short_model = self.router.route_request(short_text, "Electronics")
        medium_model = self.router.route_request(medium_text, "Electronics")
        long_model = self.router.route_request(long_text, "Electronics")
        
        # All should return valid models
        self.assertIn(short_model, self.router.model_costs.keys())
        self.assertIn(medium_model, self.router.model_costs.keys())
        self.assertIn(long_model, self.router.model_costs.keys())


class TestSemanticCache(unittest.TestCase):
    """Test SemanticCache functionality - matches current implementation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cache = SemanticCache(max_size=5)
    
    def test_initialization(self):
        """Test cache initializes correctly"""
        self.assertEqual(self.cache.max_size, 5)
        self.assertEqual(len(self.cache.cache), 0)
        self.assertEqual(self.cache.hits, 0)
        self.assertEqual(self.cache.misses, 0)
    
    def test_cache_key_generation(self):
        """Test cache key generation is consistent"""
        text1 = "Sample review text"
        text2 = "Sample review text"  # Identical
        text3 = "Different review text"
        
        key1 = self.cache._generate_cache_key(text1, "Electronics")
        key2 = self.cache._generate_cache_key(text2, "Electronics")
        key3 = self.cache._generate_cache_key(text3, "Electronics")
        key4 = self.cache._generate_cache_key(text1, "Books")  # Different category
        
        self.assertEqual(key1, key2)  # Same content should generate same key
        self.assertNotEqual(key1, key3)  # Different content should generate different key
        self.assertNotEqual(key1, key4)  # Different category should generate different key
    
    def test_cache_put_and_get(self):
        """Test storing and retrieving from cache"""
        review_text = "Sample review"
        category = "Electronics"
        result = {"sentiment": "positive", "score": 0.8}
        
        # Put item in cache
        self.cache.put(review_text, category, result)
        self.assertEqual(len(self.cache.cache), 1)
        
        # Get item from cache
        cached_result = self.cache.get(review_text, category)
        self.assertEqual(cached_result, result)
        self.assertEqual(self.cache.hits, 1)
        self.assertEqual(self.cache.misses, 0)
    
    def test_cache_miss(self):
        """Test cache miss behavior"""
        result = self.cache.get("Non-existent review", "Electronics")
        self.assertIsNone(result)
        self.assertEqual(self.cache.hits, 0)
        self.assertEqual(self.cache.misses, 1)
    
    def test_cache_size_limit(self):
        """Test cache eviction when size limit is reached"""
        # Fill cache to capacity
        for i in range(6):  # max_size is 5, so this should trigger eviction
            self.cache.put(f"Review {i}", "Electronics", {"score": i})
        
        # Cache should not exceed max size
        self.assertEqual(len(self.cache.cache), 5)
        
        # First item should be evicted (FIFO)
        first_result = self.cache.get("Review 0", "Electronics")
        self.assertIsNone(first_result)
        
        # Last item should still be there
        last_result = self.cache.get("Review 5", "Electronics")
        self.assertEqual(last_result, {"score": 5})
    
    def test_cache_statistics(self):
        """Test cache statistics calculation"""
        # Add some cache hits and misses
        self.cache.put("Review 1", "Electronics", {"score": 1})
        self.cache.get("Review 1", "Electronics")  # Hit
        self.cache.get("Review 2", "Electronics")  # Miss
        self.cache.get("Review 1", "Electronics")  # Hit
        
        stats = self.cache.get_stats()
        
        self.assertEqual(stats['hits'], 2)
        self.assertEqual(stats['misses'], 1)
        self.assertEqual(stats['total_requests'], 3)
        self.assertEqual(stats['hit_rate'], 2/3)
        self.assertEqual(stats['cache_size'], 1)
        self.assertEqual(stats['max_size'], 5)


class TestAmazonReviewAnalyzer(unittest.TestCase):
    """Test AmazonReviewAnalyzer with current implementation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = AmazonReviewAnalyzer()
        
        self.sample_review = {
            'review_text': 'This product is excellent and works perfectly',
            'category': 'Electronics',
            'rating': 5,
            'review_id': 'test_001'
        }
    
    def test_initialization(self):
        """Test analyzer initializes with all components"""
        # These components exist based on the current implementation
        self.assertIsNotNone(self.analyzer.data_loader)
        self.assertIsNotNone(self.analyzer.model_router)
        self.assertIsNotNone(self.analyzer.cache)


class TestProductReviewResult(unittest.TestCase):
    """Test ProductReviewResult dataclass with current fields"""
    
    def test_product_review_result_creation(self):
        """Test ProductReviewResult can be created with current fields"""
        result = ProductReviewResult(
            product_category='Electronics',
            sentiment='positive',
            product_quality='excellent',
            purchase_recommendation='highly_recommended',
            key_insights=['Great build quality', 'Fast performance'],
            cost=0.001,
            model_used='gpt-4o-mini',
            cache_hit=False,
            processing_time=1.5
        )
        
        self.assertEqual(result.product_category, 'Electronics')
        self.assertEqual(result.sentiment, 'positive')
        self.assertEqual(result.product_quality, 'excellent')
        self.assertEqual(result.purchase_recommendation, 'highly_recommended')
        self.assertEqual(result.key_insights, ['Great build quality', 'Fast performance'])
        self.assertEqual(result.cost, 0.001)
        self.assertEqual(result.model_used, 'gpt-4o-mini')
        self.assertEqual(result.cache_hit, False)
        self.assertEqual(result.processing_time, 1.5)


if __name__ == '__main__':
    unittest.main(verbosity=2)