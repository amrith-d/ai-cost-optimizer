# Amazon Review AI Optimizer - Technical Specification

## Document Information
- **Version**: 1.0 
- **Date**: 2025-08-21
- **Status**: Week 1 Foundation Implementation
- **Repository**: https://github.com/amrith-d/ai-cost-optimizer

---

## Executive Summary

The Amazon Review AI Optimizer is a **cost-optimized AI routing system** featuring intelligent complexity-based analysis for efficient model selection. The system achieves **61.5% cost reduction** compared to baseline approaches while maintaining high processing quality through smart routing algorithms.

**System Overview**: A foundational AI optimization platform that intelligently routes Amazon review analysis tasks to the most cost-effective AI models based on complexity analysis, achieving significant cost savings without sacrificing quality.

**Validated Performance (Week 1 Foundation):**

**Core Achievements:**
- **Cost Reduction**: 61.5% compared to baseline GPT-4 usage
- **Processing Speed**: 2.70 reviews/second sustained
- **Reliability**: 100% success rate across 1,000 reviews
- **Efficiency**: 80% of reviews processed with cost-effective models

**System Integration:**
- **API Integration**: OpenRouter multi-model routing with 3 model tiers
- **Performance Optimization**: Complexity-based routing with fallback support
- **Data Processing**: Stanford Amazon Reviews dataset integration (Electronics, Books, Home & Garden)
- **Configuration Management**: YAML-based configuration system
- **Cost Tracking**: Comprehensive cost analysis and reporting

---


## Current System Capabilities

**Component Analysis (Week 1):**
- **Core Components**: 4 main Python modules
- **Test Coverage**: Comprehensive test suite with integration tests
- **Configuration**: YAML-based configuration management

**Core Components:**
- **main.py**: AmazonDataLoader, CostTracker, ModelRouter, AmazonReviewAnalyzer
- **core/smart_router_v2.py**: SmartRouterV2 with complexity analysis
- **core/cost_reporter.py**: CostTracker with reporting capabilities
- **integrations/openrouter_integration.py**: API integration with fallback support

**Testing Infrastructure:**
- **Test Files**: 
  - `test_smart_router_v2_simple.py` - Core routing logic
  - `test_cost_reporter_simple.py` - Cost tracking validation
  - `test_main_components_simple.py` - Component integration
  - `test_integration_simple.py` - End-to-end workflow validation

**Configuration Management:**
- **settings.yaml**: Core system configuration with model routing and performance settings
- **test_config.yaml**: Test-specific configuration for validation

---
- **Lines of Code**: 2,903
- **Test Coverage**: 155 tests across 11 test files
- **Configuration Files**: 12 YAML configurations
- **Automation Scripts**: 27 automated validation tools

**Core Components:**
- **universal_system_manager.py**: UniversalSystemManager (75 LOC)
- **universal_processor.py**: class, UniversalProcessor (298 LOC)
- **main.py**: class, AmazonDataLoader, CostTracker (499 LOC)
- **core/smart_router_v2.py**: class, SmartRouterV2 (219 LOC)
- **core/cost_reporter.py**: class, class, CostTracker (231 LOC)
- **integrations/enhanced_batch_processor.py**: class, class, EnhancedBatchProcessor (230 LOC)
- **integrations/openrouter_integration.py**: class, OpenRouterOptimizer, RealAPIMode (219 LOC)
- **caching/cache_manager.py**: CacheManager (116 LOC)
- **caching/l1_cache.py**: class, class, L1Cache (199 LOC)
- **demos/week1_complexity_routing_system.py**: Week1FullOptimizer (485 LOC)
- **demos/week2_caching_system.py**: Week2CachingOptimizer (300 LOC)

**Testing Infrastructure:**
- **Test Files**: test_cache_manager.py, test_integration_simple.py, test_main_components_simple.py, test_unified_validation_engine.py, test_enhanced_batch_processor.py, test_smart_router_v2.py, test_main_components.py, test_integration.py, test_cost_reporter_simple.py, test_cost_reporter.py, test_documentation_validator.py
- **Total Test Methods**: 155
- **Coverage Target**: 85%+

**Configuration Management:**
- **settings.yaml**: 11 sections (5.01 KB)
- **development_practices.yaml**: 14 sections (9.62 KB)
- **narrative_content_guidelines.yaml**: 4 sections (10.96 KB)
- **content_strategy.yaml**: 4 sections (3.27 KB)
- **content_validation_rules.yaml**: 9 sections (10.05 KB)
- **universal_system_prompts.yaml**: 14 sections (19.45 KB)
- **security.yaml**: 1 sections (0.14 KB)
- **conflict_free_content_guidelines.yaml**: 10 sections (25.17 KB)
- **project_standards.yaml**: 18 sections (7.95 KB)
- **content_urls.yaml**: 6 sections (2.21 KB)
- **readme_content_rules.yaml**: 4 sections (10.04 KB)
- **url_mappings.yaml**: 3 sections (0.6 KB)
>>>>>>> c550d2a (Update Week 2 caching system documentation and fix integration)

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    INPUT LAYER                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Electronics │  │    Books    │  │Home&Garden  │        │
│  │   Reviews   │  │   Reviews   │  │   Reviews   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                COMPLEXITY ANALYSIS LAYER                   │
│  SmartRouterV2: Technical(35%) + Sentiment(25%) +         │
│  Length(20%) + Domain(20%) → Final Complexity Score       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  MODEL ROUTING                             │
│  Score < 0.3 → GPT-4o-mini     ($0.15/M tokens)          │
│  0.3-0.5     → Claude Haiku    ($0.25/M tokens)          │
│  0.5-0.7     → GPT-3.5-turbo   ($0.50/M tokens)          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│               PROCESSING & COST TRACKING                   │
│  API Integration • Cost Monitoring • Performance Metrics   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     OUTPUT                                  │
│  Sentiment • Quality • Recommendation • Cost Analysis      │
│  61.5% Cost Reduction • 2.70 reviews/second               │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
AmazonDataLoader ──→ SmartRouterV2 ──→ OpenRouterOptimizer ──→ CostTracker
       │                  │                    │                    │
   Load Reviews      Analyze Complexity    Process with         Track Costs &
   from Dataset      Score 4 Dimensions    Selected Model       Performance
       │                  │                    │                    │
   Process Reviews ──→ Route to Tier  ──→   Return Results ──→  Generate Reports
   with Quality      (3 model tiers)       + Performance       Cost Analysis
```

## API Implementation Details

#### 3. API Integration Layer (`OpenRouterOptimizer`)
```python
@dataclass  
class OpenRouterConfig:
    api_key: str
    base_url: "https://openrouter.ai/api/v1"
    max_budget: float = 5.00
    current_spend: float = 0.00
```

**Multi-Provider Fallback Architecture:**

```python
model_tiers = {
    'ultra_lightweight': {
        'primary_models': ['openai/gpt-4o-mini'],
        'fallback_models': ['anthropic/claude-3-haiku', 'openai/gpt-3.5-turbo']
    },
    'lightweight': {
        'primary_models': ['anthropic/claude-3-haiku'],
        'fallback_models': ['openai/gpt-3.5-turbo', 'openai/gpt-4o-mini']
    },
    'medium': {
        'primary_models': ['openai/gpt-3.5-turbo'],
        'fallback_models': ['anthropic/claude-3-haiku', 'openai/gpt-4o-mini']
    }
}
```

**Fallback Logic:**
- **Sequential Attempt**: Try primary model → fallback 1 → fallback 2
- **Provider Diversity**: OpenAI ↔ Anthropic have different content moderation policies  
- **Error Handling**: Content moderation failures trigger automatic provider switching
- **Cost Preservation**: Primary models remain cost-optimized  
- **Success Rate**: 99.9% → 100% through multi-provider resilience
- **User Experience**: Enhanced error messaging provides clear failover transparency

**Model Tier Configuration:**
```yaml
models:
  ultra_lightweight:
    name: "openai/gpt-4o-mini" 
    cost_per_million_tokens: 0.15
    max_tokens: 150
  lightweight:
    name: "anthropic/claude-3-haiku:beta"
    cost_per_million_tokens: 0.25
    max_tokens: 150
  medium:
    name: "openai/gpt-3.5-turbo"
    cost_per_million_tokens: 0.50
    max_tokens: 200
  advanced:
    name: "openai/gpt-4o"
    cost_per_million_tokens: 2.50
    max_tokens: 300
  premium:
    name: "anthropic/claude-3-sonnet:beta"
    cost_per_million_tokens: 3.00
    max_tokens: 300
```

#### 4. AI Processing Layer (`ReviewOptimizer`)
```python
@dataclass
class ProductReviewResult:
    product_category: str
    sentiment: str
    product_quality: str
    purchase_recommendation: str
    key_insights: List[str]
    cost: float
    model_used: str
    cache_hit: bool
    processing_time: float
```
>>>>>>> c550d2a (Update Week 2 caching system documentation and fix integration)

---

## Installation & Usage

### Prerequisites
- Python 3.8+
- OpenRouter API key
- Required dependencies (see requirements.txt)

### Quick Start
```bash
# Clone repository
git clone [repository-url]
cd amazon-review-optimizer

# Install dependencies
pip install -r requirements.txt

# Configure settings
cp config/settings.yaml.example config/settings.yaml
# Edit config/settings.yaml with your OpenRouter API key

# Run analysis
python src/main.py
```

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test suite
python -m pytest tests/test_integration_simple.py -v
```

---

## Configuration

### Model Configuration
The system supports flexible model configuration through YAML:

```yaml
models:
  ultra_lightweight:
    models:
      - name: "openai/gpt-4o-mini"
        cost_per_million: 0.15
        max_tokens: 100
    complexity_threshold: 0.2
    
  lightweight:
    models:
      - name: "anthropic/claude-3-haiku"
        cost_per_million: 0.25
        max_tokens: 150
    complexity_threshold: 0.4
```

### Complexity Analysis Weights
```yaml
complexity_analysis:
  technical_weight: 0.35
  sentiment_weight: 0.25
  length_weight: 0.20
  domain_weight: 0.20
```

---

## Future Development

### Planned Enhancements
- **Enhanced Routing**: Performance optimizations and enhanced routing
- **Phase 3**: Enhanced model tiers and routing algorithms
- **Phase 4**: Production deployment and monitoring tools

### Scalability Considerations
- Current system validated for 1,000 reviews
- Architecture designed for horizontal scaling
- Modular design supports feature expansion

---

## Development Standards

### Code Quality
- Configuration-driven architecture
- Comprehensive error handling
- Type hints and documentation
- Unit and integration testing

### Testing Strategy
- Component-level unit tests
- Integration testing for end-to-end workflows
- Performance validation tests
- Configuration validation

---

## Support & Documentation

For additional information:
- See `README.md` for quick start guide
- Check `docs/ARCHITECTURE_OVERVIEW.md` for system architecture
- Review test files for usage examples