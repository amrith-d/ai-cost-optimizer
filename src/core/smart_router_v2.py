#!/usr/bin/env python3
"""
Smart Router V2: Content Complexity Scoring - Week 1 Foundation
Simple intelligent model routing for cost optimization
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
    """Smart routing with content complexity analysis - Week 1 Foundation"""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        # Load configuration from YAML
        self.config = self._load_config(config_path)
        
        # Set up complexity analysis weights
        complexity_config = self.config.get('complexity_analysis', {})
        self.weights = complexity_config.get('weights', {
            'technical': 0.35,
            'sentiment': 0.25, 
            'length': 0.20,
            'domain': 0.20
        })
        
        # Model configurations
        self.models = self.config.get('models', {})
        
        # Technical terms by category for scoring
        self.technical_terms = {
            'Electronics': [
                'processor', 'cpu', 'gpu', 'ram', 'memory', 'storage', 'ssd', 'hdd',
                'display', 'resolution', 'refresh rate', 'brightness', 'contrast',
                'battery', 'mah', 'watt', 'voltage', 'amperage', 'usb', 'hdmi',
                'bluetooth', 'wifi', 'connectivity', 'ports', 'interface'
            ],
            'Books': [
                'plot', 'character', 'narrative', 'prose', 'style', 'genre',
                'chapter', 'storyline', 'protagonist', 'antagonist', 'theme',
                'development', 'pacing', 'dialogue', 'setting', 'climax'
            ],
            'Home_and_Garden': [
                'material', 'durability', 'weather resistant', 'assembly',
                'installation', 'maintenance', 'quality', 'construction',
                'design', 'functionality', 'ergonomic', 'efficiency'
            ]
        }
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load and validate configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            # Return default config if file not found
            return self._get_default_config()
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Default configuration for Week 1"""
        return {
            'models': {
                'ultra_lightweight': {
                    'models': [{'name': 'openai/gpt-4o-mini', 'cost_per_million': 0.15}],
                    'complexity_threshold': 0.2
                },
                'lightweight': {
                    'models': [{'name': 'anthropic/claude-3-haiku', 'cost_per_million': 0.25}],
                    'complexity_threshold': 0.4
                },
                'medium': {
                    'models': [{'name': 'openai/gpt-3.5-turbo', 'cost_per_million': 0.50}],
                    'complexity_threshold': 0.7
                }
            },
            'complexity_analysis': {
                'weights': {
                    'technical': 0.35,
                    'sentiment': 0.25,
                    'length': 0.20,
                    'domain': 0.20
                }
            }
        }
    
    def analyze_complexity(self, review_text: str, category: str) -> ComplexityScore:
        """Calculate comprehensive complexity score"""
        
        # Input validation
        if not review_text or not review_text.strip():
            raise ValueError("Review text cannot be empty")
        if not category:
            raise ValueError("Category cannot be empty")
            
        review_text = review_text.strip()
        
        # Calculate individual scores
        technical_score = self._calculate_technical_score(review_text, category)
        sentiment_score = self._calculate_sentiment_score(review_text)
        length_score = self._calculate_length_score(review_text)
        domain_score = self._calculate_domain_score(review_text, category)
        
        # Calculate weighted final score
        final_score = (
            technical_score * self.weights['technical'] +
            sentiment_score * self.weights['sentiment'] +
            length_score * self.weights['length'] +
            domain_score * self.weights['domain']
        )
        
        # Determine recommended tier
        recommended_tier = self._determine_model_tier(final_score)
        
        return ComplexityScore(
            technical_score=technical_score,
            sentiment_score=sentiment_score,
            length_score=length_score,
            domain_score=domain_score,
            final_score=final_score,
            recommended_tier=recommended_tier
        )
    
    def route_request(self, review_text: str, category: str) -> Dict[str, Any]:
        """Main routing function with detailed analysis"""
        
        # Calculate complexity
        complexity = self.analyze_complexity(review_text, category)
        
        # Get model details for the recommended tier
        tier_config = self.models.get(complexity.recommended_tier, {})
        models = tier_config.get('models', [])
        
        if not models:
            # Fallback to medium tier if configuration issue
            models = self.models.get('medium', {}).get('models', [])
            if not models:
                models = [{'name': 'openai/gpt-3.5-turbo', 'cost_per_million': 0.50}]
        
        selected_model = models[0]  # Use first model in tier
        
        return {
            'model_name': selected_model['name'],
            'cost_per_million_tokens': selected_model['cost_per_million'],
            'complexity_score': complexity.final_score,
            'tier': complexity.recommended_tier,
            'reasoning': f"Complexity: {complexity.final_score:.3f} → {complexity.recommended_tier}"
        }
    
    def _calculate_technical_score(self, text: str, category: str) -> float:
        """Calculate technical complexity score"""
        technical_terms = self.technical_terms.get(category, [])
        
        if not technical_terms:
            return 0.1  # Default low score for unknown categories
        
        text_lower = text.lower()
        technical_count = sum(1 for term in technical_terms if term.lower() in text_lower)
        
        # Normalize based on text length and term availability
        text_words = len(text.split())
        if text_words == 0:
            return 0.0
        
        density = technical_count / text_words
        normalized_score = min(density * 10, 1.0)  # Scale and cap at 1.0
        
        return normalized_score
    
    def _calculate_sentiment_score(self, text: str) -> float:
        """Calculate sentiment analysis complexity"""
        # Simple heuristics for sentiment complexity
        
        # Emotional indicators
        emotional_words = [
            'love', 'hate', 'amazing', 'terrible', 'fantastic', 'awful',
            'excellent', 'horrible', 'perfect', 'worst', 'best', 'disappointed'
        ]
        
        # Nuanced sentiment indicators
        nuanced_words = [
            'however', 'although', 'despite', 'nevertheless', 'on the other hand',
            'mixed feelings', 'somewhat', 'partially', 'mostly', 'generally'
        ]
        
        text_lower = text.lower()
        emotional_count = sum(1 for word in emotional_words if word in text_lower)
        nuanced_count = sum(1 for phrase in nuanced_words if phrase in text_lower)
        
        # Sentence complexity (more sentences = more complex sentiment)
        sentence_count = len(re.split(r'[.!?]+', text))
        
        # Calculate score
        base_score = 0.1
        emotional_factor = min(emotional_count * 0.1, 0.4)
        nuanced_factor = min(nuanced_count * 0.2, 0.3)
        sentence_factor = min(sentence_count * 0.05, 0.3)
        
        return min(base_score + emotional_factor + nuanced_factor + sentence_factor, 1.0)
    
    def _calculate_length_score(self, text: str) -> float:
        """Calculate length-based complexity score"""
        char_count = len(text)
        word_count = len(text.split())
        
        # Length complexity factors
        if char_count < 50:
            return 0.1  # Very short
        elif char_count < 150:
            return 0.3  # Short
        elif char_count < 300:
            return 0.5  # Medium
        elif char_count < 500:
            return 0.7  # Long
        else:
            return 0.9  # Very long
    
    def _calculate_domain_score(self, text: str, category: str) -> float:
        """Calculate domain-specific complexity"""
        # Domain complexity indicators
        domain_indicators = {
            'Electronics': ['specs', 'specifications', 'performance', 'benchmarks'],
            'Books': ['author', 'writing style', 'literary', 'narrative'],
            'Home_and_Garden': ['installation', 'assembly', 'durability', 'weather']
        }
        
        indicators = domain_indicators.get(category, [])
        text_lower = text.lower()
        
        indicator_count = sum(1 for indicator in indicators if indicator in text_lower)
        
        # Question marks indicate analytical complexity
        question_count = text.count('?')
        
        # Comparison words indicate analytical thinking
        comparison_words = ['better', 'worse', 'compared to', 'versus', 'vs', 'than']
        comparison_count = sum(1 for word in comparison_words if word in text_lower)
        
        base_score = 0.1
        indicator_factor = min(indicator_count * 0.15, 0.4)
        question_factor = min(question_count * 0.1, 0.2)
        comparison_factor = min(comparison_count * 0.1, 0.3)
        
        return min(base_score + indicator_factor + question_factor + comparison_factor, 1.0)
    
    def _determine_model_tier(self, complexity_score: float) -> str:
        """Determine appropriate model tier based on complexity score"""
        
        for tier_name, tier_config in self.models.items():
            threshold = tier_config.get('complexity_threshold', 1.0)
            if complexity_score <= threshold:
                return tier_name
        
        # If no tier matches, return the last one (highest complexity)
        return list(self.models.keys())[-1] if self.models else 'medium'

# Example usage and testing
if __name__ == "__main__":
    # Test the router
    router = SmartRouterV2()
    
    # Test reviews
    test_reviews = [
        ("Great product!", "Electronics"),
        ("The processor performance is exceptional with 12-core architecture delivering impressive benchmarks.", "Electronics"),
        ("Love this book! Amazing story.", "Books"),
        ("The narrative structure is complex with multiple interconnected storylines and character development.", "Books")
    ]
    
    print("Smart Router V2 - Week 1 Foundation Test")
    print("=" * 50)
    
    for review, category in test_reviews:
        result = router.route_request(review, category)
        complexity = router.analyze_complexity(review, category)
        
        print(f"\nReview: {review[:50]}...")
        print(f"Category: {category}")
        print(f"Complexity: {complexity.final_score:.3f}")
        print(f"Model: {result['model_name']}")
        print(f"Cost: ${result['cost_per_million_tokens']}/M tokens")
        print(f"Reasoning: {result['reasoning']}")