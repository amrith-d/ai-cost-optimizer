"""
Cost tracking and reporting for Amazon Review AI Optimizer - Week 1
Simple cost analysis for model routing decisions

Provides basic cost tracking and performance metrics.
"""

import time
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from collections import defaultdict

@dataclass 
class ReviewRecord:
    """Individual review processing record"""
    timestamp: float
    model: str
    tokens: int
    cost_usd: float
    category: str
    processing_time: float = 0.0

@dataclass
class WeekSummary:
    """Weekly cost and performance summary"""  
    week_number: int
    total_reviews: int
    total_cost: float
    avg_cost_per_review: float
    api_calls: int
    avg_processing_time: float
    model_distribution: Dict[str, float]

class CostReporter:
    """Cost tracking and analysis for AI model optimization"""
    
    def __init__(self):
        self.records: List[ReviewRecord] = []
        
    def log_api_call(self, model: str, input_tokens: int, output_tokens: int, 
                     cost_usd: float, category: str, processing_time: float = 0.0) -> ReviewRecord:
        """Log an API call with cost and performance metrics"""
        
        # Input validation
        if cost_usd < 0:
            raise ValueError("Cost cannot be negative")
        if input_tokens < 0 or output_tokens < 0:
            raise ValueError("Token counts cannot be negative")
        if not model or not model.strip():
            raise ValueError("Model name cannot be empty")
        if not category or not category.strip():
            raise ValueError("Category cannot be empty")
            
        total_tokens = input_tokens + output_tokens
        
        record = ReviewRecord(
            timestamp=time.time(),
            model=model.strip(),
            tokens=total_tokens,
            cost_usd=cost_usd,
            category=category.strip(),
            processing_time=processing_time
        )
        
        self.records.append(record)
        return record
    
    def get_week_summary(self, week_number: int) -> WeekSummary:
        """Generate summary for a specific week"""
        week_records = [r for r in self.records]  # Week 1 uses all records
        
        if not week_records:
            return WeekSummary(
                week_number=week_number,
                total_reviews=0,
                total_cost=0.0,
                avg_cost_per_review=0.0,
                api_calls=0,
                avg_processing_time=0.0,
                model_distribution={}
            )
        
        total_reviews = len(week_records)
        total_cost = sum(r.cost_usd for r in week_records)
        api_calls = len(week_records)  # No caching in Week 1
        avg_processing_time = sum(r.processing_time for r in week_records) / total_reviews
        
        # Model distribution
        model_counts = defaultdict(int)
        for record in week_records:
            model_counts[record.model] += 1
            
        model_distribution = {
            model: round((count / total_reviews) * 100, 1)
            for model, count in model_counts.items()
        }
        
        return WeekSummary(
            week_number=week_number,
            total_reviews=total_reviews,
            total_cost=round(total_cost, 6),
            avg_cost_per_review=round(total_cost / total_reviews, 6),
            api_calls=api_calls,
            avg_processing_time=round(avg_processing_time, 3),
            model_distribution=model_distribution
        )
    
    def get_category_breakdown(self) -> Dict[str, Dict[str, Any]]:
        """Get cost breakdown by product category"""
        if not self.records:
            return {}
        
        categories = defaultdict(list)
        for record in self.records:
            categories[record.category].append(record)
        
        breakdown = {}
        for category, category_records in categories.items():
            total_cost = sum(r.cost_usd for r in category_records)
            
            # Model distribution for this category
            model_counts = defaultdict(int)
            for record in category_records:
                model_counts[record.model] += 1
            
            breakdown[category] = {
                'reviews': len(category_records),
                'cost': round(total_cost, 6),
                'avg_cost': round(total_cost / len(category_records), 6),
                'models': dict(model_counts)
            }
        
        return breakdown
    
    def calculate_savings_vs_baseline(self, baseline_model: str = "gpt-4", 
                                     baseline_cost_per_token: float = 0.00001) -> Dict[str, Any]:
        """Calculate cost savings compared to using only baseline model"""
        if not self.records:
            return {
                'actual_cost': 0.0,
                'baseline_cost': 0.0,
                'savings': 0.0,
                'savings_percentage': 0.0
            }
        
        actual_cost = sum(r.cost_usd for r in self.records)
        baseline_cost = sum(r.tokens * baseline_cost_per_token for r in self.records)
        savings = baseline_cost - actual_cost
        savings_percentage = (savings / baseline_cost * 100) if baseline_cost > 0 else 0
        
        return {
            'actual_cost': round(actual_cost, 6),
            'baseline_cost': round(baseline_cost, 6), 
            'savings': round(savings, 6),
            'savings_percentage': round(savings_percentage, 1)
        }
    
    def generate_report(self, week_number: int = 1) -> str:
        """Generate a formatted cost report"""
        summary = self.get_week_summary(week_number)
        category_breakdown = self.get_category_breakdown()
        savings = self.calculate_savings_vs_baseline()
        
        report = f"""
📊 Week {week_number} Cost Analysis Report
{'=' * 50}

📈 Overall Performance:
• Total Reviews: {summary.total_reviews}
• Total Cost: ${summary.total_cost:.6f}
• Average Cost per Review: ${summary.avg_cost_per_review:.6f}
• API Calls: {summary.api_calls}
• Average Processing Time: {summary.avg_processing_time:.3f}s

💰 Cost Savings vs Baseline:
• Actual Cost: ${savings['actual_cost']:.6f}
• Baseline Cost (GPT-4): ${savings['baseline_cost']:.6f}
• Savings: ${savings['savings']:.6f} ({savings['savings_percentage']:.1f}%)

🤖 Model Distribution:
"""
        for model, percentage in summary.model_distribution.items():
            report += f"• {model}: {percentage}%\n"
        
        report += f"\n📂 Category Breakdown:\n"
        for category, data in category_breakdown.items():
            report += f"• {category}: {data['reviews']} reviews, ${data['cost']:.6f}\n"
        
        return report

# Example usage and testing
if __name__ == "__main__":
    # Test cost tracking functionality
    tracker = CostReporter()
    
    # Simulate some API calls
    tracker.log_api_call("openai/gpt-4o-mini", 50, 25, 0.000008, "Electronics", 0.5)
    tracker.log_api_call("anthropic/claude-3-haiku", 75, 30, 0.000015, "Books", 0.7)
    tracker.log_api_call("openai/gpt-3.5-turbo", 100, 40, 0.000025, "Home_and_Garden", 0.9)
    
    # Generate and print report
    print(tracker.generate_report(week_number=1))
    
    # Test savings calculation
    savings = tracker.calculate_savings_vs_baseline()
    print(f"\nSavings Analysis: {savings['savings_percentage']:.1f}% cost reduction")