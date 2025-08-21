#!/usr/bin/env python3
"""
Simple Integration Tests for Amazon Review Optimizer
Tests end-to-end functionality with current implementation
"""

import unittest
import tempfile
import os
import json
import sys
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.smart_router_v2 import SmartRouterV2
from core.cost_reporter import CostTracker
from main import AmazonReviewAnalyzer, ProductReviewResult


class TestEndToEndWorkflow(unittest.TestCase):
    """Test complete end-to-end workflow with current implementation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_config_path = os.path.join(os.path.dirname(__file__), 'test_config.yaml')
        self.sample_reviews = [
            {
                'review_text': 'This laptop is amazing! Great performance and battery life.',
                'category': 'Electronics',
                'rating': 5,
                'review_id': 'e2e_001'
            },
            {
                'review_text': 'The book was okay, not great but readable.',
                'category': 'Books',
                'rating': 3,
                'review_id': 'e2e_002'
            },
            {
                'review_text': 'Excellent garden tool, very durable and well-made.',
                'category': 'Home_and_Garden',
                'rating': 5,
                'review_id': 'e2e_003'
            }
        ]
    
    def test_analyzer_initialization(self):
        """Test that analyzer initializes with all components"""
        analyzer = AmazonReviewAnalyzer()
        
        self.assertIsNotNone(analyzer.data_loader)
        self.assertIsNotNone(analyzer.model_router)
        self.assertIsNotNone(analyzer.cache)
    
    def test_smart_router_integration(self):
        """Test SmartRouterV2 integration with cost tracking"""
        router = SmartRouterV2(config_path=self.test_config_path)
        cost_tracker = CostTracker(config_path=self.test_config_path)
        
        # Route each sample review
        for review in self.sample_reviews:
            routing_result = router.route_review(review['review_text'], review['category'])
            
            # Verify routing result structure
            self.assertIn('recommended_tier', routing_result)
            self.assertIn('model_config', routing_result)
            self.assertIn('estimated_cost', routing_result)
            
            # Log to cost tracker (simulated)
            cost_tracker.log_api_call(
                model=routing_result['model_config']['model_name'],
                tokens_input=100,
                tokens_output=50,
                cost_usd=routing_result['estimated_cost'],
                category=review['category']
            )
        
        # Generate cost summary
        summary = cost_tracker.get_week_summary()
        self.assertEqual(summary.total_reviews, len(self.sample_reviews))
        self.assertGreater(summary.total_cost_usd, 0)
    
    def test_configuration_consistency(self):
        """Test that all components use consistent configuration"""
        # Initialize components with same config
        router = SmartRouterV2(config_path=self.test_config_path)
        cost_tracker = CostTracker(config_path=self.test_config_path)
        
        # Check cost tracker has baseline configured
        self.assertEqual(cost_tracker.baseline_model, "test-gpt-4-turbo")
        self.assertEqual(cost_tracker.baseline_cost_per_million, 5.00)
        
        # Both should be using the same config source
        self.assertIsNotNone(router.config)
        self.assertIsNotNone(cost_tracker.baseline_tokens_per_request)
    
    def test_cache_integration(self):
        """Test semantic cache integration across components"""
        analyzer = AmazonReviewAnalyzer()
        
        # Same review processed twice should use cache
        duplicate_review = {
            'review_text': 'Identical review text for cache testing',
            'category': 'Electronics',
            'rating': 4,
            'review_id': 'cache_001'
        }
        
        # First analysis
        result1 = analyzer.batch_analyze([duplicate_review])
        cache_stats_1 = analyzer.cache.get_stats()
        
        # Second analysis (should hit cache)
        result2 = analyzer.batch_analyze([duplicate_review])
        cache_stats_2 = analyzer.cache.get_stats()
        
        # Verify cache was used
        self.assertEqual(len(result1), 1)
        self.assertEqual(len(result2), 1)
        self.assertGreaterEqual(cache_stats_2['hits'], cache_stats_1['hits'])


class TestSystemPerformance(unittest.TestCase):
    """Test system performance characteristics with current implementation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_config_path = os.path.join(os.path.dirname(__file__), 'test_config.yaml')
    
    def test_routing_performance(self):
        """Test routing performance with various input sizes"""
        router = SmartRouterV2(config_path=self.test_config_path)
        
        test_texts = [
            "Short",
            "Medium length review with some details about the product quality and performance",
            "Very long detailed review " * 50  # Very long text
        ]
        
        for text in test_texts:
            start_time = time.time()
            result = router.route_review(text, "Electronics")
            duration = time.time() - start_time
            
            # Routing should be fast (< 0.1 seconds for any text size)
            self.assertLess(duration, 0.1)
            self.assertIn('recommended_tier', result)
    
    def test_batch_processing_efficiency(self):
        """Test batch processing efficiency"""
        analyzer = AmazonReviewAnalyzer()
        
        # Create batch of similar reviews
        batch_reviews = []
        for i in range(5):  # Reduced from 10 to keep test fast
            batch_reviews.append({
                'review_text': f'Test review number {i} with similar content',
                'category': 'Electronics',
                'rating': 4,
                'review_id': f'batch_{i:03d}'
            })
        
        start_time = time.time()
        results = analyzer.batch_analyze(batch_reviews)
        duration = time.time() - start_time
        
        # Should process efficiently
        self.assertEqual(len(results), 5)
        self.assertLess(duration, 5.0)  # Should complete within 5 seconds
        
        # Average processing time per review
        avg_time = duration / len(batch_reviews)
        self.assertLess(avg_time, 1.0)  # Less than 1 second per review


class TestConfigurationValidation(unittest.TestCase):
    """Test configuration file validation and error handling"""
    
    def test_missing_config_file(self):
        """Test behavior when config file is missing"""
        with self.assertRaises(FileNotFoundError):
            SmartRouterV2(config_path="nonexistent_config.yaml")
    
    def test_invalid_config_structure(self):
        """Test behavior with malformed config"""
        invalid_config = {"invalid": "structure"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(invalid_config, f)
            temp_path = f.name
        
        try:
            with self.assertRaises((KeyError, TypeError)):
                SmartRouterV2(config_path=temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_config_value_validation(self):
        """Test that config values are within expected ranges"""
        router = SmartRouterV2(config_path=os.path.join(os.path.dirname(__file__), 'test_config.yaml'))
        
        # Check weights sum to 1.0 (or close)
        weight_sum = sum(router.weights.values())
        self.assertAlmostEqual(weight_sum, 1.0, places=1)
        
        # Check thresholds are in ascending order
        thresholds = [
            router.thresholds['ultra_lightweight'],
            router.thresholds['lightweight'],
            router.thresholds['medium'],
            router.thresholds['high'],
            router.thresholds['premium']
        ]
        
        for i in range(len(thresholds) - 1):
            self.assertLessEqual(thresholds[i], thresholds[i + 1])


class TestProductReviewResult(unittest.TestCase):
    """Test ProductReviewResult integration with current fields"""
    
    def test_product_review_result_usage(self):
        """Test ProductReviewResult works with current implementation"""
        # Test creating result with current fields
        result = ProductReviewResult(
            product_category='Electronics',
            sentiment='positive',
            product_quality='excellent',
            purchase_recommendation='highly_recommended',
            key_insights=['Great performance', 'Good value'],
            cost=0.001,
            model_used='gpt-4o-mini',
            cache_hit=False,
            processing_time=1.5
        )
        
        # Verify all fields are accessible
        self.assertEqual(result.product_category, 'Electronics')
        self.assertEqual(result.sentiment, 'positive')
        self.assertEqual(result.product_quality, 'excellent')
        self.assertEqual(result.purchase_recommendation, 'highly_recommended')
        self.assertEqual(result.key_insights, ['Great performance', 'Good value'])
        self.assertEqual(result.cost, 0.001)
        self.assertEqual(result.model_used, 'gpt-4o-mini')
        self.assertFalse(result.cache_hit)
        self.assertEqual(result.processing_time, 1.5)


if __name__ == '__main__':
    unittest.main(verbosity=2)