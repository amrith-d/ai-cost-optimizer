"""
Amazon Product Review Analysis Optimizer - Week 1 Foundation
Simple complexity-based routing system for cost optimization

Repository: Amazon Review AI Optimizer - Week 1 Foundation
"""

import time
import json
import yaml
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from collections import defaultdict
import random

# For real dataset integration
try:
    from datasets import load_dataset
    import pandas as pd
    DATASETS_AVAILABLE = True
    print("✅ Dataset libraries available")
except ImportError:
    DATASETS_AVAILABLE = False
    print("📦 Install datasets: pip install datasets pandas")

@dataclass
class ProductReviewResult:
    product_category: str
    sentiment: str
    product_quality: str
    purchase_recommendation: str
    key_insights: List[str]
    cost: float
    model_used: str
    processing_time: float

class AmazonDataLoader:
    """Load and preprocess Amazon Reviews 2023 dataset"""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.categories = ["Electronics", "Books", "Home_and_Garden"]
        
        # Load configuration
        self.config = self._load_config(config_path)
        self.data_config = self.config['data_loading']
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load and validate YAML configuration"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Validate required sections
            required_sections = ['data_loading']
            for section in required_sections:
                if section not in config:
                    raise ValueError(f"Missing required config section: {section}")
            
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in config file: {e}")
        
    def load_sample_data(self, category: str = "Electronics", sample_size: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load REAL Amazon reviews data"""
        # Early validation
        if not DATASETS_AVAILABLE:
            raise ImportError("Dataset libraries required: pip install datasets pandas huggingface_hub")
        
        if category not in self.categories:
            raise ValueError(f"Invalid category '{category}'. Must be one of: {self.categories}")
        
        # Use config default if not provided
        if sample_size is None:
            sample_size = self.data_config['sample_size']
        
        # Validate parameters
        if sample_size <= 0:
            raise ValueError("Sample size must be positive")
        
        print(f"📊 Loading {sample_size} {category} reviews...", flush=True)
        
        # Dataset loading attempts
        dataset_attempts = [
            {
                "name": "amazon_polarity",
                "config": None,
                "description": "3.6M Amazon reviews"
            },
            {
                "name": "amazon_reviews_multi",
                "config": "en",
                "description": "Multilingual Amazon reviews (English subset)"
            }
        ]
        
        for attempt in dataset_attempts:
            try:
                print(f"📦 Attempting to load: {attempt['description']}", flush=True)
                
                if attempt['config']:
                    dataset = load_dataset(attempt['name'], attempt['config'], split='train')
                else:
                    dataset = load_dataset(attempt['name'], split='train')
                
                return self._process_dataset(dataset, category, sample_size, attempt["name"])
                
            except Exception as e:
                print(f"   ❌ Failed to load {attempt['name']}: {str(e)[:100]}", flush=True)
                continue
        
        # If all attempts fail, fall back to synthetic data
        print("⚠️  All dataset attempts failed. Generating synthetic data for testing...", flush=True)
        return self._generate_synthetic_reviews(category, sample_size)

    def _process_dataset(self, dataset, category: str, sample_size: int, source_name: str) -> List[Dict]:
        """Process dataset into review format"""
        reviews = []
        processed_count = 0
        
        print(f"\n📦 Processing {sample_size} reviews from {source_name}:", flush=True)
        
        for idx, item in enumerate(dataset):
            if processed_count >= sample_size:
                break
            
            try:
                # Extract review text and rating
                if 'content' in item:
                    review_text = item['content']
                elif 'text' in item:
                    review_text = item['text']
                elif 'review_body' in item:
                    review_text = item['review_body']
                else:
                    continue
                
                # Basic filtering
                if not review_text or len(review_text.strip()) < 10:
                    continue
                
                # Create standardized review format
                review = {
                    'review_text': review_text.strip(),
                    'category': category,
                    'review_id': f'{source_name}_{idx:06d}',
                    'rating': item.get('label', item.get('stars', 3)) + 1 if 'label' in item else item.get('stars', 3),
                }
                
                reviews.append(review)
                processed_count += 1
                
                # Progress reporting
                if processed_count % 100 == 0:
                    progress_percent = (processed_count / sample_size) * 100
                    print(f"📊 Progress: {processed_count}/{sample_size} ({progress_percent:.1f}%) loaded", flush=True)
                
            except Exception as e:
                continue
        
        print(f"✅ Successfully loaded {len(reviews)} {category} reviews", flush=True)
        return reviews

    def _generate_synthetic_reviews(self, category: str, sample_size: int) -> List[Dict[str, Any]]:
        """Generate synthetic reviews for testing when dataset loading fails"""
        
        review_templates = {
            "Electronics": [
                "Great phone with excellent battery life. Highly recommended!",
                "The screen quality is amazing but the price is too high.",
                "Poor build quality. Broke after just 2 weeks.",
                "Amazing performance for gaming. Worth every penny.",
                "The camera quality is disappointing compared to the marketing claims."
            ],
            "Books": [
                "Fantastic storyline with well-developed characters.",
                "The plot was predictable but still enjoyable to read.",
                "Couldn't put it down! A real page-turner.",
                "The writing style was hard to follow. Not recommended.",
                "Great book for anyone interested in this topic."
            ],
            "Home_and_Garden": [
                "This tool makes gardening so much easier!",
                "Good quality but overpriced for what you get.",
                "Broke after minimal use. Poor construction.",
                "Perfect for small gardens. Highly recommend.",
                "Instructions were unclear but the product works well."
            ]
        }
        
        templates = review_templates.get(category, review_templates["Electronics"])
        reviews = []
        
        for i in range(sample_size):
            template = random.choice(templates)
            review = {
                'review_text': template,
                'category': category,
                'review_id': f'synthetic_{category}_{i:04d}',
                'rating': random.randint(1, 5)
            }
            reviews.append(review)
        
        print(f"✅ Generated {len(reviews)} synthetic {category} reviews for testing", flush=True)
        return reviews

class CostTracker:
    """Track AI model costs for optimization analysis"""
    
    def __init__(self):
        self.requests: List[Dict] = []
        self.total_cost: float = 0.0
        
    def log_request(self, model: str, tokens: int, cost: float) -> float:
        """Log a single API request with cost tracking"""
        if cost < 0:
            raise ValueError("Cost cannot be negative")
        
        request = {
            'timestamp': time.time(),
            'model': model,
            'tokens': tokens,
            'cost': cost
        }
        
        self.requests.append(request)
        self.total_cost += cost
        
        return cost
    
    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive cost analysis summary"""
        if not self.requests:
            return {
                'total_requests': 0,
                'total_cost': 0.0,
                'cost_per_request': 0.0,
                'model_distribution': {}
            }
        
        total_requests = len(self.requests)
        
        # Model distribution
        model_counts = defaultdict(int)
        for request in self.requests:
            model_counts[request['model']] += 1
        
        model_distribution = {
            model: round((count / total_requests) * 100, 1)
            for model, count in model_counts.items()
        }
        
        return {
            'total_requests': total_requests,
            'total_cost': round(self.total_cost, 6),
            'cost_per_request': round(self.total_cost / total_requests, 6),
            'model_distribution': model_distribution
        }

def main():
    """Main execution function for Week 1 foundation testing"""
    print("🚀 Amazon Review AI Optimizer - Week 1 Foundation")
    print("=" * 60)
    
    try:
        # Initialize components
        loader = AmazonDataLoader()
        cost_tracker = CostTracker()
        
        # Load sample data for each category
        all_results = []
        total_start_time = time.time()
        
        for category in ["Electronics", "Books", "Home_and_Garden"]:
            print(f"\n📂 Processing {category} Reviews")
            print("-" * 40)
            
            try:
                # Load reviews
                reviews = loader.load_sample_data(category, sample_size=334)  # ~1000 total
                
                # Process reviews (simplified for Week 1)
                for review in reviews:
                    start_time = time.time()
                    
                    # Simulate analysis (Week 1 doesn't have actual API calls)
                    model_used = "gpt-4o-mini"  # Default model for Week 1
                    cost = 0.0001  # Simulated cost
                    
                    result = ProductReviewResult(
                        product_category=category,
                        sentiment="positive",  # Simplified
                        product_quality="good",  # Simplified  
                        purchase_recommendation="recommended",  # Simplified
                        key_insights=["Good value", "Quality product"],  # Simplified
                        cost=cost,
                        model_used=model_used,
                        processing_time=time.time() - start_time
                    )
                    
                    all_results.append(result)
                    cost_tracker.log_request(model_used, 100, cost)
                
                print(f"✅ Completed {len(reviews)} {category} reviews")
                
            except Exception as e:
                print(f"❌ Error processing {category}: {str(e)}")
                continue
        
        # Final summary
        total_time = time.time() - total_start_time
        summary = cost_tracker.get_summary()
        
        print(f"\n🎯 Week 1 Foundation Results")
        print("=" * 60)
        print(f"📊 Total Reviews Processed: {len(all_results)}")
        print(f"💰 Total Cost: ${summary['total_cost']:.6f}")
        print(f"⚡ Processing Time: {total_time:.2f} seconds")
        print(f"🏃 Speed: {len(all_results)/total_time:.2f} reviews/second")
        print(f"📈 Model Distribution:")
        for model, percentage in summary['model_distribution'].items():
            print(f"   • {model}: {percentage}%")
        
        # Save results
        timestamp = int(time.time())
        output_file = f"data/week1_foundation_{timestamp}.json"
        
        output_data = {
            'metadata': {
                'timestamp': timestamp,
                'total_reviews': len(all_results),
                'processing_time': total_time,
                'version': 'week1_foundation'
            },
            'cost_summary': summary,
            'results': [
                {
                    'category': r.product_category,
                    'cost': r.cost,
                    'model': r.model_used,
                    'processing_time': r.processing_time
                }
                for r in all_results
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Critical error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)