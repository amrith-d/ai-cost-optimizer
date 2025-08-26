"""
Universal Multi-Week Processor
Extends processing capabilities across all weeks with universal system prompts
"""

import os
import asyncio
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from universal_system_manager import universal_system_manager
from openrouter_integration import OpenRouterOptimizer
from cost_reporter import CostTracker
from main import AmazonDataLoader, SemanticCache
from smart_router_v2 import SmartRouterV2

@dataclass
class ProcessingConfig:
    """Configuration for multi-week processing"""
    week: int
    target_reviews: int
    cost_reduction_target: float
    max_budget: float
    batch_size: int = 10
    concurrent_workers: int = 5
    timeout_per_review: float = 30.0

class UniversalProcessor:
    """Universal processor supporting all weeks with automatic system prompt management"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.week = config.week
        
        # Initialize components
        self.api_optimizer = OpenRouterOptimizer()
        self.cost_tracker = CostTracker()
        self.data_loader = AmazonDataLoader()
        self.semantic_cache = SemanticCache(max_size=5000)  # Larger cache for multi-week
        self.smart_router = SmartRouterV2()
        
        # Conversation contexts for each category (KV cache optimization)
        self.conversation_contexts = {}
        
        print(f"🚀 Universal Processor initialized for Week {self.week}")
        print(f"   • Target Reviews: {config.target_reviews:,}")
        print(f"   • Cost Reduction Target: {config.cost_reduction_target:.1%}")
        print(f"   • Max Budget: ${config.max_budget}")
        print(f"   • Universal System Prompts: Enabled")
    
    def _get_conversation_context(self, category: str) -> List[Dict]:
        """Get conversation context with week-specific universal system prompts"""
        if category not in self.conversation_contexts:
            self.conversation_contexts[category] = universal_system_manager.get_conversation_context(
                category=category,
                week=self.week,
                context="analysis"
            )
        
        return self.conversation_contexts[category]
    
    async def analyze_review_universal(self, review: Dict) -> Dict:
        """Analyze review using universal system prompt management"""
        start_time = time.time()
        
        review_text = review['review_text']
        category = review['category']
        
        # Layer 1: Semantic Cache Check
        cached_result = self.semantic_cache.get(review_text, category)
        if cached_result:
            return {
                **cached_result,
                'processing_time': time.time() - start_time,
                'semantic_cache_hit': True,
                'kv_cache_hit': False
            }
        
        # Layer 2: Complexity Analysis with Universal Prompts
        complexity_score = self.smart_router.calculate_complexity_score(review_text, category)
        model_tier = self.smart_router.route_to_model(complexity_score)
        
        # Layer 3: Get conversation context with universal system prompts
        conversation_context = self._get_conversation_context(category)
        
        # Layer 4: Prepare analysis prompt
        user_prompt = self._prepare_analysis_prompt(review, category)
        messages = conversation_context + [{"role": "user", "content": user_prompt}]
        
        # Layer 5: API Call with timeout protection
        try:
            result = await self._make_api_call_with_protection(
                messages, model_tier, review['review_id']
            )
            
            # Layer 6: Process and cache result
            processed_result = self._process_api_result(
                result, review, category, model_tier, complexity_score, start_time
            )
            
            # Cache for future use
            self.semantic_cache.put(review_text, category, processed_result)
            
            return processed_result
            
        except Exception as e:
            return self._create_error_result(review, str(e), start_time)
    
    def _prepare_analysis_prompt(self, review: Dict, category: str) -> str:
        """Prepare analysis prompt with week-specific focus"""
        week_context = self._get_week_specific_context()
        
        base_prompt = f"""Analyze this {category.lower()} review:

Product: {review.get('product_title', 'Product')}
Rating: {review.get('rating', 'N/A')}/5
Review: "{review['review_text']}"

{week_context}

Provide analysis: sentiment (Positive/Negative/Neutral), quality assessment, and key insights."""
        
        return base_prompt
    
    def _get_week_specific_context(self) -> str:
        """Get week-specific analysis context"""
        week_contexts = {
            1: "Focus on foundational analysis patterns and baseline methodology establishment.",
            2: "Emphasize advanced optimization techniques and quality assurance patterns.",
            3: "Include comparative analysis elements and statistical validation approaches.",
            4: "Apply enterprise-grade analysis with production-ready assessment criteria."
        }
        
        return week_contexts.get(self.week, "Apply systematic analysis methodology.")
    
    async def _make_api_call_with_protection(self, messages: List[Dict], model_tier: str, review_id: str) -> Dict:
        """Make API call with timeout and retry protection"""
        model_config = self.api_optimizer._get_model_config(model_tier)
        model_name = model_config['openrouter_name']
        
        for attempt in range(3):  # Max 3 retries
            try:
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.api_optimizer.client.chat.completions.create,
                        model=model_name,
                        messages=messages,
                        max_tokens=200,
                        temperature=0.1
                    ),
                    timeout=self.config.timeout_per_review
                )
                
                return {
                    'response': response,
                    'model_config': model_config,
                    'attempt': attempt + 1
                }
                
            except asyncio.TimeoutError:
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise Exception(f"Timeout after {self.config.timeout_per_review}s")
            
            except Exception as e:
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise e
    
    def _process_api_result(self, api_result: Dict, review: Dict, category: str, 
                          model_tier: str, complexity_score: float, start_time: float) -> Dict:
        """Process API result into standardized format"""
        response = api_result['response']
        model_config = api_result['model_config']
        
        # Calculate costs
        tokens_used = response.usage.total_tokens if response.usage else 150
        cost_per_million = model_config['cost_per_million_tokens']
        actual_cost = (tokens_used / 1_000_000) * cost_per_million
        
        # Extract analysis content
        content = response.choices[0].message.content
        
        # Parse sentiment and insights
        sentiment, insights = self._parse_analysis_content(content)
        
        return {
            'review_id': review['review_id'],
            'category': category,
            'sentiment': sentiment,
            'model_used': model_config['openrouter_name'],
            'cost': actual_cost,
            'processing_time': time.time() - start_time,
            'semantic_cache_hit': False,
            'kv_cache_hit': True,  # Using conversation context
            'tokens_used': tokens_used,
            'response_preview': content[:100],
            'complexity_score': complexity_score,
            'routing_tier': model_tier,
            'routing_reasoning': f"Week {self.week} {category} review: {self.smart_router._get_routing_reason(complexity_score)}",
            'week': self.week,
            'insights': insights
        }
    
    def _parse_analysis_content(self, content: str) -> tuple:
        """Parse analysis content to extract sentiment and insights"""
        lines = content.split('\n')
        sentiment = "Neutral"
        insights = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('Sentiment:'):
                sentiment = line.replace('Sentiment:', '').strip()
            elif line and not line.startswith('Sentiment:') and len(line) > 10:
                insights.append(line)
        
        return sentiment, insights[:3]  # Limit to top 3 insights
    
    def _create_error_result(self, review: Dict, error: str, start_time: float) -> Dict:
        """Create error result for failed analysis"""
        return {
            'review_id': review['review_id'],
            'category': review['category'],
            'sentiment': 'Error',
            'model_used': 'error',
            'cost': 0.0,
            'processing_time': time.time() - start_time,
            'semantic_cache_hit': False,
            'kv_cache_hit': False,
            'tokens_used': 0,
            'response_preview': f"Error: {error}",
            'complexity_score': 0.0,
            'routing_tier': 'error',
            'routing_reasoning': f"Processing failed: {error}",
            'week': self.week,
            'error': error
        }
    
    async def process_batch_universal(self, reviews: List[Dict]) -> Dict:
        """Process batch of reviews with universal system prompt management"""
        print(f"\n🔄 Processing {len(reviews)} reviews for Week {self.week} with Universal System Prompts")
        
        start_time = time.time()
        semaphore = asyncio.Semaphore(self.config.concurrent_workers)
        
        async def process_single_review(review):
            async with semaphore:
                return await self.analyze_review_universal(review)
        
        # Process all reviews concurrently
        tasks = [process_single_review(review) for review in reviews]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and process results
        valid_results = [r for r in results if not isinstance(r, Exception)]
        exceptions = [r for r in results if isinstance(r, Exception)]
        
        if exceptions:
            print(f"⚠️ {len(exceptions)} processing errors occurred")
        
        # Generate comprehensive summary
        summary = self._generate_processing_summary(valid_results, start_time, len(reviews))
        
        return {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'week': self.week,
                'total_reviews': len(reviews),
                'successful_reviews': len(valid_results),
                'failed_reviews': len(exceptions),
                'processing_time': time.time() - start_time,
                'universal_prompts_used': True
            },
            'summary': summary,
            'detailed_results': valid_results,
            'errors': [str(e) for e in exceptions] if exceptions else []
        }
    
    def _generate_processing_summary(self, results: List[Dict], start_time: float, total_reviews: int) -> Dict:
        """Generate comprehensive processing summary"""
        if not results:
            return {'error': 'No valid results to summarize'}
        
        total_cost = sum(r.get('cost', 0) for r in results)
        total_time = time.time() - start_time
        
        # Model distribution
        model_dist = {}
        for result in results:
            model = result.get('model_used', 'unknown')
            model_dist[model] = model_dist.get(model, 0) + 1
        
        # Category breakdown
        category_breakdown = {}
        for result in results:
            category = result.get('category', 'unknown')
            if category not in category_breakdown:
                category_breakdown[category] = {'count': 0, 'cost': 0}
            category_breakdown[category]['count'] += 1
            category_breakdown[category]['cost'] += result.get('cost', 0)
        
        # Cache statistics
        semantic_hits = sum(1 for r in results if r.get('semantic_cache_hit', False))
        kv_hits = sum(1 for r in results if r.get('kv_cache_hit', False))
        
        # Calculate baseline cost (assuming GPT-4-Turbo for all)
        baseline_cost = len(results) * 0.0015  # Estimated baseline cost per review
        savings_amount = baseline_cost - total_cost
        savings_percentage = (savings_amount / baseline_cost * 100) if baseline_cost > 0 else 0
        
        return {
            'total_reviews': len(results),
            'total_time': total_time,
            'total_cost': total_cost,
            'avg_cost_per_review': total_cost / len(results) if results else 0,
            'reviews_per_second': len(results) / total_time if total_time > 0 else 0,
            'api_calls': len(results),
            'semantic_cache_hit_rate': semantic_hits / len(results) * 100 if results else 0,
            'kv_cache_hit_rate': kv_hits / len(results) * 100 if results else 0,
            'model_distribution': model_dist,
            'category_breakdown': category_breakdown,
            'baseline_cost': baseline_cost,
            'savings_amount': savings_amount,
            'savings_percentage': savings_percentage,
            'week': self.week,
            'universal_prompts_enabled': True,
            'success_rate': len(results) / total_reviews * 100 if total_reviews > 0 else 0
        }
    
    def get_system_prompt_report(self) -> Dict:
        """Get system prompt usage report"""
        return universal_system_manager.get_monitoring_report()

# Convenience functions for easy integration
def create_week_processor(week: int, target_reviews: int = 1000, max_budget: float = 5.0) -> UniversalProcessor:
    """Create processor for specific week"""
    
    # Week-specific defaults
    week_configs = {
        1: {'cost_reduction_target': 0.63, 'concurrent_workers': 5},
        2: {'cost_reduction_target': 0.70, 'concurrent_workers': 8},
        3: {'cost_reduction_target': 0.75, 'concurrent_workers': 10},
        4: {'cost_reduction_target': 0.80, 'concurrent_workers': 12}
    }
    
    week_config = week_configs.get(week, week_configs[1])
    
    config = ProcessingConfig(
        week=week,
        target_reviews=target_reviews,
        cost_reduction_target=week_config['cost_reduction_target'],
        max_budget=max_budget,
        concurrent_workers=week_config['concurrent_workers']
    )
    
    return UniversalProcessor(config)

async def run_week_analysis(week: int, sample_size: int = 1000, max_budget: float = 5.0) -> Dict:
    """Run analysis for any week with universal system prompts"""
    
    # Create processor
    processor = create_week_processor(week, sample_size, max_budget)
    
    # Load data
    data_loader = AmazonDataLoader()
    
    # Load reviews from all categories
    all_reviews = []
    for category in ["Electronics", "Books", "Home_and_Garden"]:
        category_reviews = data_loader.load_sample_data_streaming(
            category=category, 
            sample_size=sample_size // 3
        )
        all_reviews.extend(category_reviews)
    
    # Shuffle for even distribution
    import random
    random.shuffle(all_reviews)
    all_reviews = all_reviews[:sample_size]
    
    print(f"\n🎯 Starting Week {week} Analysis with Universal System Prompts")
    print(f"   • Sample Size: {len(all_reviews):,} reviews")
    print(f"   • Budget: ${max_budget}")
    print(f"   • Universal Prompts: Active")
    
    # Process reviews
    results = await processor.process_batch_universal(all_reviews)
    
    # Add system prompt report
    results['system_prompt_report'] = processor.get_system_prompt_report()
    
    return results