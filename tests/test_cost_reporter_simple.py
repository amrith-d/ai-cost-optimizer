#!/usr/bin/env python3
"""
Simple Unit Tests for CostTracker
Tests current API functionality only
"""

import unittest
import tempfile
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.cost_reporter import CostTracker, APICallRecord, WeeklyCostSummary


class TestCostTrackerSimple(unittest.TestCase):
    """Simple tests for current CostTracker functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tracker = CostTracker()
        
    def test_initialization(self):
        """Test tracker initializes correctly"""
        self.assertIsNotNone(self.tracker)
        self.assertIsInstance(self.tracker.records, list)
        
    def test_log_api_call_basic(self):
        """Test logging basic API call"""
        # Log a simple API call
        record = self.tracker.log_api_call(
            model="test-model",
            tokens_input=100,
            tokens_output=50,
            cost_usd=0.001,
            category="Electronics", 
            cache_hit=False,
            processing_time=1.5
        )
        
        # Verify call was logged
        self.assertEqual(len(self.tracker.records), 1)
        record = self.tracker.records[0]
        self.assertEqual(record.model, "test-model")
        self.assertEqual(record.tokens_input, 100)
        self.assertEqual(record.tokens_output, 50)
        self.assertEqual(record.cost_usd, 0.001)
        self.assertEqual(record.review_category, "Electronics")
        self.assertFalse(record.cache_hit)
        
    def test_get_week_summary(self):
        """Test getting week summary"""
        # Log some API calls
        for i in range(3):
            self.tracker.log_api_call(
                model=f"model-{i}",
                tokens_input=100 + i * 10,
                tokens_output=50 + i * 5,
                cost_usd=0.001 + i * 0.0001,
                category="Electronics",
                cache_hit=(i % 2 == 0),
                processing_time=1.0 + i * 0.1
            )
        
        # Get summary
        summary = self.tracker.get_week_summary(week_number=1)
        self.assertIsInstance(summary, WeeklyCostSummary)
        self.assertEqual(summary.week_number, 1)
        
    def test_export_detailed_report(self):
        """Test exporting detailed report"""
        # Log an API call
        self.tracker.log_api_call(
            model="test-model",
            tokens_input=100,
            tokens_output=50,
            cost_usd=0.001,
            category="Electronics",
            cache_hit=False,
            processing_time=1.5
        )
        
        # Test export (should not raise exception)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
            
        try:
            self.tracker.export_detailed_report(temp_path)
            self.assertTrue(os.path.exists(temp_path))
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestAPICallRecord(unittest.TestCase):
    """Test APICallRecord dataclass"""
    
    def test_api_call_record_creation(self):
        """Test APICallRecord can be created with current fields"""
        record = APICallRecord(
            timestamp=1234567890.0,
            model="test-model",
            tokens_input=100,
            tokens_output=50,
            cost_usd=0.001,
            review_category="Electronics",
            cache_hit=False,
            processing_time=1.5
        )
        
        # Test field access
        self.assertEqual(record.timestamp, 1234567890.0)
        self.assertEqual(record.model, "test-model")
        self.assertEqual(record.tokens_input, 100)
        self.assertEqual(record.tokens_output, 50)
        self.assertEqual(record.cost_usd, 0.001)
        self.assertEqual(record.review_category, "Electronics")
        self.assertFalse(record.cache_hit)
        self.assertEqual(record.processing_time, 1.5)


if __name__ == '__main__':
    unittest.main()