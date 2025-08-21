"""
OpenRouter API Integration for Amazon Review Optimizer - Week 1 Foundation
Simple API integration without async/batch processing
"""

import os
import time
import yaml
from typing import Dict, List, Optional
from dataclasses import dataclass
from openai import OpenAI
import tiktoken


@dataclass
class OpenRouterConfig:
    """Configuration for OpenRouter integration"""
    api_key: str
    base_url: str
    max_budget: float = 5.00  # Safety limit in USD
    current_spend: float = 0.00


class OpenRouterOptimizer:
    """Simple LLM API integration with OpenRouter - Week 1 Foundation"""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config = self._load_config(config_path)
        self.openrouter_config = self._setup_openrouter()
        self.client = self._create_client()
        self.token_encoder = tiktoken.get_encoding("cl100k_base")
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Return default config for Week 1
            return {
                'openrouter': {
                    'base_url': "https://openrouter.ai/api/v1",
                    'timeout': 30,
                    'max_retries': 3
                }
            }
    
    def _setup_openrouter(self) -> OpenRouterConfig:
        """Setup OpenRouter configuration"""
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment")
        
        openrouter_config = self.config.get('openrouter', {})
        return OpenRouterConfig(
            api_key=api_key,
            base_url=openrouter_config.get('base_url', "https://openrouter.ai/api/v1"),
            max_budget=float(os.getenv('MAX_BUDGET', '5.00'))
        )
    
    def _create_client(self) -> OpenAI:
        """Create OpenAI client configured for OpenRouter"""
        return OpenAI(
            api_key=self.openrouter_config.api_key,
            base_url=self.openrouter_config.base_url
        )
    
    def analyze_review(self, review_data: Dict, model_tier: str = "ultra_lightweight") -> Dict:
        """Analyze a single review using the specified model tier"""
        
        # Input validation
        if not review_data or 'review_text' not in review_data:
            raise ValueError("Review data must contain 'review_text'")
        
        review_text = review_data['review_text']
        category = review_data.get('category', 'Unknown')
        
        if not review_text.strip():
            raise ValueError("Review text cannot be empty")
        
        # Get model for this tier
        model_name = self._get_model_for_tier(model_tier)
        
        # Create analysis prompt
        prompt = self._create_analysis_prompt(review_text, category)
        
        try:
            # Make API call
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are an expert product review analyzer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            processing_time = time.time() - start_time
            
            # Extract response
            analysis_text = response.choices[0].message.content
            
            # Count tokens and calculate cost
            input_tokens = len(self.token_encoder.encode(prompt))
            output_tokens = len(self.token_encoder.encode(analysis_text))
            cost = self._calculate_cost(input_tokens, output_tokens, model_tier)
            
            # Update spend tracking
            self.openrouter_config.current_spend += cost
            
            # Parse analysis (simplified for Week 1)
            analysis = self._parse_analysis_response(analysis_text)
            
            return {
                'sentiment': analysis.get('sentiment', 'neutral'),
                'product_quality': analysis.get('quality', 'average'),
                'purchase_recommendation': analysis.get('recommendation', 'maybe'),
                'key_insights': analysis.get('insights', ['Standard review']),
                'model_used': model_name,
                'cost': cost,
                'processing_time': processing_time,
                'tokens_used': input_tokens + output_tokens
            }
            
        except Exception as e:
            # Return error result
            return {
                'sentiment': 'error',
                'product_quality': 'unknown',
                'purchase_recommendation': 'error',
                'key_insights': [f'Analysis failed: {str(e)[:100]}'],
                'model_used': model_name,
                'cost': 0.0,
                'processing_time': 0.0,
                'tokens_used': 0
            }
    
    def analyze_reviews(self, reviews: List[Dict]) -> List[Dict]:
        """Analyze multiple reviews sequentially"""
        results = []
        
        for review in reviews:
            # Determine model tier based on complexity (simplified)
            model_tier = self._determine_tier_simple(review.get('review_text', ''))
            
            # Analyze review
            result = self.analyze_review(review, model_tier)
            results.append(result)
            
            # Add small delay to avoid rate limiting
            time.sleep(0.1)
        
        return results
    
    def _get_model_for_tier(self, tier: str) -> str:
        """Get model name for the specified tier"""
        tier_models = {
            'ultra_lightweight': 'openai/gpt-4o-mini',
            'lightweight': 'anthropic/claude-3-haiku',
            'medium': 'openai/gpt-3.5-turbo'
        }
        
        return tier_models.get(tier, 'openai/gpt-4o-mini')
    
    def _determine_tier_simple(self, review_text: str) -> str:
        """Simple tier determination based on review length"""
        if len(review_text) < 100:
            return 'ultra_lightweight'
        elif len(review_text) < 300:
            return 'lightweight'
        else:
            return 'medium'
    
    def _create_analysis_prompt(self, review_text: str, category: str) -> str:
        """Create analysis prompt for the review"""
        return f"""Analyze this {category} product review:

Review: "{review_text}"

Provide analysis in this format:
SENTIMENT: [positive/negative/neutral]
QUALITY: [excellent/good/average/poor]
RECOMMENDATION: [buy/maybe/avoid]
INSIGHTS: [1-2 key points about the product]

Keep the analysis concise and focused."""
    
    def _parse_analysis_response(self, response_text: str) -> Dict:
        """Parse the analysis response into structured data"""
        analysis = {
            'sentiment': 'neutral',
            'quality': 'average',
            'recommendation': 'maybe',
            'insights': ['Standard review']
        }
        
        try:
            lines = response_text.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('SENTIMENT:'):
                    analysis['sentiment'] = line.split(':', 1)[1].strip().lower()
                elif line.startswith('QUALITY:'):
                    analysis['quality'] = line.split(':', 1)[1].strip().lower()
                elif line.startswith('RECOMMENDATION:'):
                    analysis['recommendation'] = line.split(':', 1)[1].strip().lower()
                elif line.startswith('INSIGHTS:'):
                    insights_text = line.split(':', 1)[1].strip()
                    analysis['insights'] = [insights_text] if insights_text else ['Standard review']
        
        except Exception:
            # If parsing fails, return defaults
            pass
        
        return analysis
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int, model_tier: str) -> float:
        """Calculate cost for the API call"""
        # Cost per million tokens by tier (simplified)
        costs_per_million = {
            'ultra_lightweight': 0.15,
            'lightweight': 0.25,
            'medium': 0.50
        }
        
        cost_per_million = costs_per_million.get(model_tier, 0.15)
        total_tokens = input_tokens + output_tokens
        
        return (total_tokens / 1_000_000) * cost_per_million
    
    def get_spend_summary(self) -> Dict:
        """Get current spending summary"""
        return {
            'current_spend': round(self.openrouter_config.current_spend, 6),
            'max_budget': self.openrouter_config.max_budget,
            'remaining_budget': round(self.openrouter_config.max_budget - self.openrouter_config.current_spend, 6),
            'budget_used_percentage': round((self.openrouter_config.current_spend / self.openrouter_config.max_budget) * 100, 1)
        }


# Example usage and testing
if __name__ == "__main__":
    # Test the optimizer
    try:
        optimizer = OpenRouterOptimizer()
        
        # Test review
        test_review = {
            'review_text': 'Great product! Love the battery life and screen quality.',
            'category': 'Electronics',
            'review_id': 'test_001'
        }
        
        print("OpenRouter Integration - Week 1 Foundation Test")
        print("=" * 50)
        
        # Analyze single review
        result = optimizer.analyze_review(test_review)
        
        print(f"Review: {test_review['review_text']}")
        print(f"Sentiment: {result['sentiment']}")
        print(f"Quality: {result['product_quality']}")
        print(f"Recommendation: {result['purchase_recommendation']}")
        print(f"Model: {result['model_used']}")
        print(f"Cost: ${result['cost']:.6f}")
        print(f"Processing Time: {result['processing_time']:.2f}s")
        
        # Spending summary
        summary = optimizer.get_spend_summary()
        print(f"\nSpend Summary:")
        print(f"Current: ${summary['current_spend']:.6f}")
        print(f"Budget: ${summary['max_budget']:.2f}")
        print(f"Used: {summary['budget_used_percentage']:.1f}%")
        
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("Set OPENROUTER_API_KEY environment variable to test API integration")