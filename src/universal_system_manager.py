"""
Universal System Manager for Amazon Review Optimizer
Provides consistent conversation contexts and system prompts across all weeks
"""

import yaml
import os
from typing import Dict, List, Optional

class UniversalSystemManager:
    """Manages universal system prompts and conversation contexts"""
    
    def __init__(self, config_path: str = "config/universal_system_prompts.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"⚠️ Config file {self.config_path} not found, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default configuration if YAML file is missing"""
        return {
            'system_prompts': {
                'Electronics': {
                    'prompt': 'You are an expert at analyzing electronics product reviews. Focus on technical features, performance, build quality, value proposition, and user experience.',
                    'complexity_factors': ['technical_terminology', 'feature_analysis', 'performance_metrics']
                },
                'Books': {
                    'prompt': 'You are an expert at analyzing book reviews. Focus on content quality, narrative structure, readability, educational value, and reader engagement.',
                    'complexity_factors': ['literary_analysis', 'content_depth', 'educational_assessment']
                },
                'Home_and_Garden': {
                    'prompt': 'You are an expert at analyzing home and garden product reviews. Focus on utility, durability, practical value, ease of use, and long-term performance.',
                    'complexity_factors': ['durability_assessment', 'utility_analysis', 'practical_application']
                }
            },
            'week_enhancements': {
                'week1': {
                    'focus': 'foundational_analysis',
                    'context': 'Establish baseline methodology and validate core analysis patterns',
                    'metrics_emphasis': ['cost_efficiency', 'processing_speed', 'accuracy_validation']
                }
            }
        }
    
    def get_conversation_context(self, category: str, week: int = 1, context: str = "analysis") -> List[Dict]:
        """Get conversation context for a specific category and week"""
        
        # Get base system prompt for category
        category_config = self.config.get('system_prompts', {}).get(category, {})
        base_prompt = category_config.get('prompt', f'You are an expert at analyzing {category.lower()} product reviews.')
        
        # Get week-specific enhancements
        week_key = f'week{week}'
        week_config = self.config.get('week_enhancements', {}).get(week_key, {})
        week_focus = week_config.get('focus', 'general_analysis')
        week_context = week_config.get('context', 'Standard product review analysis')
        
        # Build enhanced system prompt
        enhanced_prompt = f"{base_prompt} {week_context} Focus on {week_focus}."
        
        # Add context-specific instructions
        if context == "analysis":
            enhanced_prompt += " Provide systematic analysis of functionality, reliability, and customer satisfaction patterns."
        elif context == "sentiment":
            enhanced_prompt += " Focus on sentiment analysis and emotional tone assessment."
        elif context == "quality":
            enhanced_prompt += " Emphasize quality assessment and value proposition analysis."
        
        return [
            {
                "role": "system",
                "content": enhanced_prompt
            }
        ]
    
    def get_complexity_factors(self, category: str) -> List[str]:
        """Get complexity factors for a category"""
        category_config = self.config.get('system_prompts', {}).get(category, {})
        return category_config.get('complexity_factors', ['general_analysis'])
    
    def get_week_config(self, week: int) -> Dict:
        """Get configuration for a specific week"""
        week_key = f'week{week}'
        return self.config.get('week_enhancements', {}).get(week_key, {})

# Global instance
universal_system_manager = UniversalSystemManager()