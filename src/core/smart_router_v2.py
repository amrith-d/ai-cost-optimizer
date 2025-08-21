#!/usr/bin/env python3
"""
Smart Router V2: Enhanced Content Complexity Scoring - Configuration-Based Version
Implements intelligent model routing using centralized configuration
"""

import re
import math
import yaml
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass


@dataclass
class ComplexityScore:
    """Content complexity analysis result"""
    technical_score: float  # 0-1, technical complexity
    sentiment_score: float  # 0-1, sentiment analysis difficulty  
    length_score: float     # 0-1, length-based complexity
    domain_score: float     # 0-1, domain-specific complexity
    final_score: float      # 0-1, weighted final complexity
    recommended_tier: str   # Model tier recommendation

class SmartRouterV2:
    """Enhanced smart routing with content complexity analysis using configuration"""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        # Load configuration from YAML
        self.config = self._load_config(config_path)
        
        
        # Extract complexity analysis config
        complexity_config = self.config['complexity_analysis']
        self.weights = complexity_config['weights']
        self.thresholds = complexity_config['thresholds']
        
        # Technical keywords by domain from config
        tech_keywords = complexity_config['technical_keywords']
        self.technical_keywords = {
            category: self._flatten_keyword_list(keywords) 
            for category, keywords in tech_keywords.items()
        }
        
        # Sentiment indicators from config
        sentiment_config = complexity_config['sentiment_indicators']
        self.complex_sentiment_indicators = sentiment_config['complex']
        self.simple_sentiment_indicators = sentiment_config['simple']
        
        # Complexity scoring parameters
        scoring_config = self.config['complexity_scoring']
        self.technical_density_divisor = scoring_config['technical_density_divisor']
        self.max_base_score = scoring_config['max_base_score']
        self.bonuses = scoring_config['bonuses']
        self.length_thresholds = scoring_config['length_thresholds']
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _flatten_keyword_list(self, keyword_groups: List[str]) -> List[str]:
        """Flatten comma-separated keyword groups into individual keywords"""
        keywords = []
        for group in keyword_groups:
            keywords.extend([kw.strip() for kw in group.split(',')])
        return keywords
    
    def analyze_technical_complexity(self, text: str, category: str) -> float:
        """Analyze technical complexity based on domain-specific keywords"""
        if category not in self.technical_keywords:
            return 0.3  # Default moderate complexity for unknown categories
            
        keywords = self.technical_keywords[category]
        text_lower = text.lower()
        
        # Count technical terms
        technical_matches = sum(1 for keyword in keywords if keyword in text_lower)
        
        # Calculate density-based score
        technical_density = technical_matches / len(text.split()) if len(text.split()) > 0 else 0
        base_score = min(technical_density / self.technical_density_divisor, self.max_base_score)
        
        # Bonus scoring for specific patterns
        bonus_score = 0
        
        # Technical specifications
        if re.search(r'\d+\s*(gb|mb|ghz|mhz|mp|inches?|feet|volt)', text_lower):
            bonus_score += self.bonuses['specification']
        
        # Comparative language  
        if re.search(r'(better|worse|faster|slower|compared)', text_lower):
            bonus_score += self.bonuses['comparison']
            
        # Numbers and measurements
        if re.search(r'\b\d+(\.\d+)?\s*(hours?|minutes?|days?|months?)', text_lower):
            bonus_score += self.bonuses['numbers']
        
        return min(base_score + bonus_score, 1.0)
    
    def analyze_sentiment_complexity(self, text: str) -> float:
        """Analyze sentiment complexity - mixed/nuanced vs simple emotions"""
        text_lower = text.lower()
        
        # Count complex sentiment indicators
        complex_count = sum(1 for indicator in self.complex_sentiment_indicators 
                          if indicator in text_lower)
        
        # Count simple sentiment indicators  
        simple_count = sum(1 for indicator in self.simple_sentiment_indicators
                         if indicator in text_lower)
        
        # Multiple sentiment words indicate complexity
        sentiment_word_count = complex_count + simple_count
        
        # Scoring logic
        if complex_count > 0:
            base_score = 0.7 + (complex_count * 0.1)
        elif sentiment_word_count > 3:
            base_score = 0.4  # Multiple sentiments = moderate complexity
        elif simple_count > 0:
            base_score = 0.1  # Simple clear sentiment
        else:
            base_score = 0.3  # Neutral/unclear = moderate complexity
            
        return min(base_score, 1.0)
    
    def analyze_length_complexity(self, text: str) -> float:
        """Analyze complexity based on text length and structure"""
        word_count = len(text.split())
        sentence_count = len([s for s in text.split('.') if s.strip()])
        
        # Length-based complexity using config thresholds
        thresholds = self.length_thresholds
        if word_count < thresholds['very_short']:
            length_score = 0.1
        elif word_count < thresholds['short']:
            length_score = 0.2
        elif word_count < thresholds['medium']:
            length_score = 0.4
        elif word_count < thresholds['long']:
            length_score = 0.6
        else:
            length_score = 0.8
            
        # Structure complexity (avg words per sentence)
        if sentence_count > 0:
            avg_sentence_length = word_count / sentence_count
            if avg_sentence_length > 20:
                length_score += 0.1  # Long sentences = more complex
                
        return min(length_score, 1.0)
    
    def analyze_domain_complexity(self, text: str, category: str) -> float:
        """Analyze domain-specific complexity patterns"""
        # Category-specific domain modifiers from config
        domain_modifiers = self.config['categories']
        
        if category in domain_modifiers:
            complexity_threshold = domain_modifiers[category]['complexity_threshold']
            base_score = complexity_threshold
        else:
            base_score = 0.5  # Default moderate complexity
        
        # Look for domain-specific complexity indicators
        text_lower = text.lower()
        
        # Technical comparisons and detailed analysis
        technical_patterns = [
            r'versus|vs\.?\s+', r'compared to', r'in contrast',
            r'pros and cons', r'advantages', r'disadvantages'
        ]
        
        matches = sum(1 for pattern in technical_patterns 
                     if re.search(pattern, text_lower))
        
        # Boost complexity for comparative analysis
        complexity_bonus = matches * 0.15
        
        return min(base_score + complexity_bonus, 1.0)
    
    def calculate_complexity_score(self, text: str, category: str) -> ComplexityScore:
        """Calculate comprehensive complexity score"""
        
        # Individual complexity scores
        technical = self.analyze_technical_complexity(text, category)
        sentiment = self.analyze_sentiment_complexity(text) 
        length = self.analyze_length_complexity(text)
        domain = self.analyze_domain_complexity(text, category)
        
        # Weighted final score using config weights
        final_score = (
            technical * self.weights['technical'] +
            sentiment * self.weights['sentiment'] + 
            length * self.weights['length'] +
            domain * self.weights['domain']
        )
        
        # Determine recommended tier
        recommended_tier = self.select_optimal_tier(final_score)
        
        return ComplexityScore(
            technical_score=technical,
            sentiment_score=sentiment,
            length_score=length,
            domain_score=domain,
            final_score=final_score,
            recommended_tier=recommended_tier
        )
    
    def select_optimal_tier(self, complexity_score: float) -> str:
        """Select optimal model tier based on complexity using config thresholds"""
        
        # Tier selection using config thresholds
        if complexity_score <= self.thresholds['ultra_lightweight']:
            return 'ultra_lightweight'
        elif complexity_score <= self.thresholds['lightweight']:
            return 'lightweight'
        elif complexity_score <= self.thresholds['medium']:
            return 'medium'
        elif complexity_score <= self.thresholds['high']:
            return 'high'
        else:
            return 'premium'
    
    def route_review(self, review_text: str, category: str) -> Dict:
        """Main routing function with detailed analysis and caching"""
        
        
        complexity = self.calculate_complexity_score(review_text, category)
        
        # Get model configuration for the recommended tier
        models_config = self.config['models']
        tier_config = models_config[complexity.recommended_tier]
        
        result = {
            'recommended_tier': complexity.recommended_tier,
            'complexity_analysis': {
                'technical': complexity.technical_score,
                'sentiment': complexity.sentiment_score, 
                'length': complexity.length_score,
                'domain': complexity.domain_score,
                'final': complexity.final_score
            },
            'model_config': {
                'model_name': tier_config['openrouter_name'],
                'cost_per_million': tier_config['cost_per_million_tokens'],
                'max_tokens': tier_config['max_tokens'],
                'fallback_models': tier_config['fallback_models']
            },
            'estimated_cost': self._estimate_cost(review_text, tier_config),
            'routing_explanation': self._explain_routing(complexity, category),
            'cache_hit': False
        }
        
        return result
    
    def _estimate_cost(self, text: str, tier_config: Dict) -> float:
        """Estimate cost for processing this text"""
        # Rough token estimation (1 token ≈ 4 characters)
        estimated_tokens = len(text) / 4 + tier_config['max_tokens']
        cost_per_million = tier_config['cost_per_million_tokens']
        return (estimated_tokens / 1_000_000) * cost_per_million
    
    def _explain_routing(self, complexity: ComplexityScore, category: str) -> List[str]:
        """Generate human-readable explanation of routing decision"""
        reasons = []
        
        if complexity.final_score <= 0.3:
            reasons.append("Simple analysis suitable for lightweight model")
        elif complexity.final_score <= 0.6:
            reasons.append("Moderate complexity requires balanced model")
        else:
            reasons.append("High complexity requires premium model capabilities")
            
        if complexity.technical_score > 0.5:
            reasons.append(f"High technical content detected in {category} domain")
            
        if complexity.sentiment_score > 0.6:
            reasons.append("Complex sentiment analysis required")
            
        return reasons
    
    def get_cache_statistics(self) -> Optional[Dict[str, Any]]:
        """Get comprehensive cache performance statistics"""
        if not self.cache_manager:
            return None
        return self.cache_manager.get_performance_stats()
    
    def clear_cache(self):
        """Clear all cached analysis results"""
        if self.cache_manager:
            self.cache_manager.clear_all_caches()


if __name__ == "__main__":
    # Test the configuration-based router
    router = SmartRouterV2()
    
    test_reviews = [
        {
            'text': "This laptop is great!",
            'category': 'Electronics',
            'expected': 'ultra_lightweight'
        },
        {
            'text': "The processor performance varies significantly depending on thermal throttling conditions, with sustained workloads showing decreased throughput compared to initial benchmark results.",
            'category': 'Electronics', 
            'expected': 'high'
        }
    ]
    
    print("🧪 Testing Configuration-Based Smart Router V2\n")
    
    for i, review in enumerate(test_reviews, 1):
        print(f"Test {i}: {review['text'][:50]}...")
        result = router.route_review(review['text'], review['category'])
        
        print(f"  Recommended: {result['recommended_tier']}")
        print(f"  Expected: {review['expected']}")
        print(f"  Complexity: {result['complexity_analysis']['final']:.2f}")
        print(f"  Model: {result['model_config']['model_name']}")
        print(f"  Estimated Cost: ${result['estimated_cost']:.6f}")
        print(f"  Reasons: {'; '.join(result['routing_explanation'])}")
        print()