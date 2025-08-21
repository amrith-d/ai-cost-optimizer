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

from main import AmazonDataLoader, ModelRouter, AmazonReviewAnalyzer, ProductReviewResult


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
        self.assertIsNotNone(self.analyzer.cost_tracker)
        self.assertIsNotNone(self.analyzer.router)


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