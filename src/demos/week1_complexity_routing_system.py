#!/usr/bin/env python3
"""
Week 1 Complexity Routing System Demo - Foundation Implementation
Demonstrates intelligent model routing based on review complexity analysis
"""

import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datasets import load_dataset

# Import Week 1 foundation components
from src.core.smart_router_v2 import SmartRouterV2
from src.core.cost_reporter import CostReporter
from src.integrations.openrouter_integration import OpenRouterOptimizer


class Week1FoundationOptimizer:
    """Week 1: Complexity-based routing system foundation"""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.smart_router = SmartRouterV2(config_path)
        self.cost_reporter = CostReporter()
        self.openrouter = None
        
        # Initialize OpenRouter if API key available
        try:
            self.openrouter = OpenRouterOptimizer(config_path)
        except ValueError as e:
            print(f"⚠️  OpenRouter not initialized: {e}")
            print("📋 Running in demo mode without API calls")
    
    def run_foundation_demo(self, sample_size: int = 1000) -> Dict[str, Any]:
        """Run Week 1 foundation system demonstration"""
        
        print("🚀 Week 1 Foundation Demo - Complexity-Based Routing")
        print("=" * 55)
        
        # Load sample data
        print(f"📊 Loading {sample_size} Amazon reviews...")
        reviews = self._load_sample_reviews(sample_size)
        
        if not reviews:
            print("❌ No reviews loaded - using generated samples")
            reviews = self._generate_sample_reviews(sample_size)
        
        # Analyze complexity and routing
        print(f"🧠 Analyzing complexity for {len(reviews)} reviews...")
        start_time = time.time()
        
        routing_results = []
        model_distribution = {'ultra_lightweight': 0, 'lightweight': 0, 'medium': 0}
        
        for i, review in enumerate(reviews):
            if i % 100 == 0 and i > 0:
                print(f"   Processed {i}/{len(reviews)} reviews...")
            
            # Analyze complexity
            complexity = self.smart_router.analyze_complexity(
                review['review_text'], 
                review['category']
            )
            
            # Get routing decision
            routing = self.smart_router.route_request(
                review['review_text'], 
                review['category']
            )
            
            # Track model distribution
            model_distribution[routing['tier']] += 1
            
            # Store result
            result = {
                'review_id': review.get('review_id', f'review_{i}'),
                'category': review['category'],
                'complexity_score': complexity.final_score,
                'recommended_tier': routing['tier'],
                'model_name': routing['model_name'],
                'cost_per_million': routing['cost_per_million_tokens'],
                'reasoning': routing['reasoning']
            }
            routing_results.append(result)
            
            # Log to cost reporter (simulated costs)
            estimated_tokens = len(review['review_text'].split()) * 1.3  # Rough estimation
            estimated_cost = (estimated_tokens / 1_000_000) * routing['cost_per_million_tokens']
            
            self.cost_reporter.log_api_call(
                model=routing['model_name'],
                input_tokens=int(estimated_tokens * 0.8),
                output_tokens=int(estimated_tokens * 0.2),
                cost_usd=estimated_cost,
                category=review['category'],
                processing_time=0.01  # Simulated processing time
            )
        
        processing_time = time.time() - start_time
        reviews_per_second = len(reviews) / processing_time if processing_time > 0 else 0
        
        # Calculate model distribution percentages
        total_reviews = len(reviews)
        distribution_percentages = {
            tier: round((count / total_reviews) * 100, 1)
            for tier, count in model_distribution.items()
        }
        
        # Get cost analysis
        cost_analysis = self.cost_reporter.calculate_savings_vs_baseline()
        week_summary = self.cost_reporter.get_week_summary(week_number=1)
        
        print(f"✅ Analysis complete!")
        print(f"📈 Performance: {reviews_per_second:.2f} reviews/second")
        print(f"💰 Cost savings: {cost_analysis['savings_percentage']:.1f}% vs baseline")
        
        return {
            'system_info': {
                'week': 1,
                'system_type': 'complexity_based_routing',
                'reviews_processed': len(reviews),
                'processing_time': processing_time,
                'reviews_per_second': reviews_per_second
            },
            'model_distribution': {
                'counts': model_distribution,
                'percentages': distribution_percentages
            },
            'cost_analysis': cost_analysis,
            'week_summary': week_summary.__dict__,
            'sample_results': routing_results[:10],  # First 10 for inspection
            'performance_metrics': {
                'total_cost': cost_analysis['actual_cost'],
                'baseline_cost': cost_analysis['baseline_cost'],
                'savings_usd': cost_analysis['savings'],
                'savings_percentage': cost_analysis['savings_percentage']
            }
        }
    
    def _load_sample_reviews(self, sample_size: int) -> List[Dict[str, Any]]:
        """Load sample reviews from Stanford Amazon Reviews dataset"""
        
        try:
            # Try to load Stanford Amazon Reviews dataset
            print("   Loading from Stanford Amazon Reviews dataset...")
            dataset = load_dataset("amazon_reviews_multi", "en", split="train", streaming=True)
            
            reviews = []
            categories_map = {
                'Electronics': 'Electronics',
                'Books': 'Books', 
                'Home & Kitchen': 'Home_and_Garden',
                'Sports & Outdoors': 'Home_and_Garden'
            }
            
            count = 0
            for item in dataset:
                if count >= sample_size:
                    break
                
                # Map category
                category = categories_map.get(item.get('product_category', ''), 'Electronics')
                
                review = {
                    'review_id': f'amazon_{count:06d}',
                    'review_text': item.get('review_body', ''),
                    'category': category,
                    'product_id': item.get('product_id', f'prod_{count}'),
                    'rating': item.get('stars', 3)
                }
                
                # Filter out empty reviews
                if review['review_text'] and len(review['review_text'].strip()) > 10:
                    reviews.append(review)
                    count += 1
            
            print(f"   ✅ Loaded {len(reviews)} authentic Amazon reviews")
            return reviews
            
        except Exception as e:
            print(f"   ⚠️  Could not load dataset: {e}")
            return []
    
    def _generate_sample_reviews(self, count: int) -> List[Dict[str, Any]]:
        """Generate sample reviews for demonstration when dataset unavailable"""
        
        categories = ['Electronics', 'Books', 'Home_and_Garden']
        
        # Varied complexity sample reviews
        sample_reviews = [
            # Simple reviews (should route to ultra_lightweight)
            "Great product!",
            "Love it!",
            "Good quality.",
            "Works well.",
            "Nice item.",
            
            # Medium complexity reviews (should route to lightweight)
            "Good quality product but the price is a bit high for what you get.",
            "The book has an interesting plot and well-developed characters.",
            "Assembly was straightforward and the materials feel durable.",
            "Great battery life and the screen quality is impressive.",
            "The story flows well and keeps you engaged throughout.",
            
            # High complexity reviews (should route to medium tier)
            "The processor architecture shows impressive gains in multi-threaded workloads with significant improvements in memory bandwidth utilization and cache efficiency compared to previous generation models.",
            "The narrative structure employs sophisticated literary techniques including unreliable narration, temporal fragmentation, and metafictional elements that challenge conventional storytelling approaches while maintaining thematic coherence.",
            "The weather-resistant coating demonstrates excellent durability characteristics under varied environmental conditions, though the assembly instructions could benefit from clearer technical specifications and torque requirements."
        ]
        
        reviews = []
        for i in range(count):
            category = categories[i % len(categories)]
            review_text = sample_reviews[i % len(sample_reviews)]
            
            # Add some variation to make reviews more realistic
            if i % 50 == 0:  # Every 50th review gets additional detail
                if category == 'Electronics':
                    review_text += " The technical specifications meet expectations and performance benchmarks."
                elif category == 'Books':
                    review_text += " The author's writing style and character development create compelling narrative depth."
                else:
                    review_text += " The build quality and material selection demonstrate attention to detail."
            
            reviews.append({
                'review_id': f'demo_{i:05d}',
                'review_text': review_text,
                'category': category,
                'product_id': f'prod_{i % 100}',
                'rating': (i % 5) + 1  # Rating 1-5
            })
        
        print(f"   ✅ Generated {len(reviews)} sample reviews for demonstration")
        return reviews
    
    def save_results(self, results: Dict[str, Any], output_dir: str = "data") -> str:
        """Save demonstration results"""
        
        Path(output_dir).mkdir(exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"week1_foundation_{timestamp}.json"
        filepath = Path(output_dir) / filename
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        return str(filepath)


def main():
    """Run Week 1 foundation demonstration"""
    
    optimizer = Week1FoundationOptimizer()
    
    try:
        # Run the foundation demo
        results = optimizer.run_foundation_demo(sample_size=1000)
        
        # Save results
        results_file = optimizer.save_results(results)
        print(f"📁 Results saved to: {results_file}")
        
        # Display summary
        print("\n" + "=" * 55)
        print("📊 WEEK 1 FOUNDATION SUMMARY")
        print("=" * 55)
        print(f"Reviews Processed: {results['system_info']['reviews_processed']:,}")
        print(f"Processing Speed: {results['system_info']['reviews_per_second']:.2f} reviews/second")
        print(f"Total Processing Time: {results['system_info']['processing_time']:.2f} seconds")
        
        print(f"\n💰 Cost Optimization:")
        print(f"Actual Cost: ${results['cost_analysis']['actual_cost']:.6f}")
        print(f"Baseline Cost (GPT-4): ${results['cost_analysis']['baseline_cost']:.6f}")
        print(f"Savings: ${results['cost_analysis']['savings']:.6f} ({results['cost_analysis']['savings_percentage']:.1f}%)")
        
        print(f"\n🤖 Model Distribution:")
        for tier, percentage in results['model_distribution']['percentages'].items():
            count = results['model_distribution']['counts'][tier]
            print(f"  {tier}: {count:,} reviews ({percentage}%)")
        
        print(f"\n📈 Key Achievement: {results['cost_analysis']['savings_percentage']:.1f}% cost reduction vs baseline")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()