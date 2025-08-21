#!/usr/bin/env python3
"""
Simple Unit Tests for CostReporter - Week 1 Foundation
Tests basic cost tracking functionality without caching
"""

import unittest
import tempfile
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.cost_reporter import CostReporter, ReviewRecord, WeekSummary


class TestCostReporterSimple(unittest.TestCase):
    """Simple tests for Week 1 CostReporter functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.reporter = CostReporter()
        
    def test_initialization(self):
        """Test reporter initializes correctly"""
        self.assertIsNotNone(self.reporter)
        self.assertIsInstance(self.reporter.records, list)
        self.assertEqual(len(self.reporter.records), 0)
        
    def test_log_api_call_basic(self):
        """Test logging basic API call"""
        # Log a simple API call
        record = self.reporter.log_api_call(
            model="openai/gpt-4o-mini",
            input_tokens=100,
            output_tokens=50,
            cost_usd=0.001,
            category="Electronics", 
            processing_time=1.5
        )
        
        # Verify call was logged
        self.assertEqual(len(self.reporter.records), 1)
        self.assertIsInstance(record, ReviewRecord)
        self.assertEqual(record.model, "openai/gpt-4o-mini")
        self.assertEqual(record.tokens, 150)  # input + output
        self.assertEqual(record.cost_usd, 0.001)
        self.assertEqual(record.category, "Electronics")
        self.assertEqual(record.processing_time, 1.5)
        
    def test_get_week_summary(self):
        """Test getting week summary"""
        # Log some API calls
        for i in range(3):
            self.reporter.log_api_call(
                model=f"model-{i}",
                input_tokens=100 + i * 10,
                output_tokens=50 + i * 5,
                cost_usd=0.001 + i * 0.0001,
                category="Electronics",
                processing_time=1.0 + i * 0.1
            )
        
        # Get summary
        summary = self.reporter.get_week_summary(week_number=1)
        self.assertIsInstance(summary, WeekSummary)
        self.assertEqual(summary.week_number, 1)
        self.assertEqual(summary.total_reviews, 3)
        self.assertEqual(summary.api_calls, 3)  # No caching in Week 1
        
    def test_generate_report(self):
        """Test generating cost report"""
        # Log an API call
        self.reporter.log_api_call(
            model="openai/gpt-4o-mini",
            input_tokens=100,
            output_tokens=50,
            cost_usd=0.001,
            category="Electronics",
            processing_time=1.0
        )
        
        # Generate report
        report = self.reporter.generate_report(week_number=1)
        self.assertIsInstance(report, str)
        self.assertIn("Week 1 Cost Analysis Report", report)
        self.assertIn("Total Reviews: 1", report)
        
    def test_input_validation(self):
        """Test input validation"""
        # Test negative cost
        with self.assertRaises(ValueError):
            self.reporter.log_api_call("model", 100, 50, -0.001, "Electronics")
            
        # Test negative tokens
        with self.assertRaises(ValueError):
            self.reporter.log_api_call("model", -100, 50, 0.001, "Electronics")
            
        # Test empty model
        with self.assertRaises(ValueError):
            self.reporter.log_api_call("", 100, 50, 0.001, "Electronics")
            
        # Test empty category
        with self.assertRaises(ValueError):
            self.reporter.log_api_call("model", 100, 50, 0.001, "")
    
    def test_category_breakdown(self):
        """Test category breakdown functionality"""
        # Log calls for different categories
        categories = ["Electronics", "Books", "Home_and_Garden"]
        for category in categories:
            self.reporter.log_api_call(
                model="openai/gpt-4o-mini",
                input_tokens=100,
                output_tokens=50,
                cost_usd=0.001,
                category=category,
                processing_time=1.0
            )
        
        # Get breakdown
        breakdown = self.reporter.get_category_breakdown()
        self.assertEqual(len(breakdown), 3)
        for category in categories:
            self.assertIn(category, breakdown)
            self.assertEqual(breakdown[category]['reviews'], 1)
            self.assertEqual(breakdown[category]['cost'], 0.001)
    
    def test_savings_calculation(self):
        """Test savings calculation vs baseline"""
        # Log some API calls with different costs to show savings
        self.reporter.log_api_call("openai/gpt-4o-mini", 100, 50, 0.001, "Electronics")
        self.reporter.log_api_call("anthropic/claude-3-haiku", 100, 50, 0.002, "Books")
        
        # Calculate savings vs more expensive baseline
        savings = self.reporter.calculate_savings_vs_baseline(baseline_cost_per_token=0.00002)
        self.assertIsInstance(savings, dict)
        self.assertIn('actual_cost', savings)
        self.assertIn('baseline_cost', savings)
        self.assertIn('savings', savings)
        self.assertIn('savings_percentage', savings)
        
        # Verify calculations (actual cost should be lower than baseline)
        self.assertEqual(savings['actual_cost'], 0.003)
        self.assertGreater(savings['baseline_cost'], savings['actual_cost'])
        self.assertGreater(savings['savings_percentage'], 0)


if __name__ == '__main__':
    unittest.main()