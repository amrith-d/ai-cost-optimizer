# Architecture Overview - Amazon Review AI Optimizer

## Quick Reference Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   INPUT LAYER                           │
│  Amazon Reviews (Electronics, Books, Home & Garden)    │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                COMPLEXITY ANALYSIS                      │
│  SmartRouterV2: Technical(35%) + Sentiment(25%) +      │
│  Length(20%) + Domain(20%) → Final Complexity Score    │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  MODEL ROUTING                          │
│  Score < 0.3 → GPT-4o-mini     ($0.15/M tokens)       │
│  0.3-0.5     → Claude Haiku    ($0.25/M tokens)       │
│  0.5-0.7     → GPT-3.5-turbo   ($0.50/M tokens)       │
│  0.7-0.9     → GPT-4o          ($2.50/M tokens)       │
│  > 0.9       → Claude Sonnet   ($3.00/M tokens)       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│               CONCURRENT PROCESSING                     │
│  5 Workers • 30s Timeout • Rate Limiting • Retries    │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                L1 CACHING LAYER                        │
│  LRU Cache (1000 max) • SHA-256 Keys • TTL: 1hr       │
│  90.0% Hit Rate • 0.004ms Access Time                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                     OUTPUT                              │
│  Sentiment • Quality • Recommendation • Metrics        │
│  61.5% Cost Reduction • 3.17 reviews/second            │
│  Week 2: Enterprise Development Excellence             │
└─────────────────────────────────────────────────────────┘
```

## Component Interaction Flow

```
AmazonDataLoader ──→ L1CacheManager ──→ SmartRouterV2 ──→ OpenRouterOptimizer
       │                  │                  │                    │
   Load Reviews      Check Cache       Analyze Complexity    Process with
   from Dataset      (90.0% hit rate)  Score 4 Dimensions    Selected Model
       │                  │                  │                    │
   Process Reviews ──→ Cache Results ──→ Route to Tier  ──→   Return Results
   with Quality      LRU + SHA-256     (6 model tiers)       + Performance

Week 2 Enhancement: Enterprise development practices with comprehensive testing (48 tests), configuration-driven architecture, and automated quality assurance
```

## Core Files Structure

```
src/
├── main.py                     # Entry point & ReviewOptimizer
├── smart_router_v2.py         # Complexity analysis & routing
├── openrouter_integration.py  # API client & cost tracking
├── cost_reporter.py           # Performance metrics
└── week1_complexity_routing_system.py  # Week 1 complexity-based routing validation

config/
└── settings.yaml              # Model configs & parameters

docs/
├── results/                   # Performance validation data
├── ARCHITECTURE_OVERVIEW.md  # System architecture
└── TECHNICAL_SPECIFICATION.md # Complete system documentation

requirements.txt               # Dependencies
README.md                      # Project overview
.gitignore                     # Version control exclusions
```

## Key Performance Metrics (Week 1 Validated)

| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| Cost Reduction | 50%+ | **63.3%** | ✅ Exceeded |
| Processing Speed | 1.0+ rev/s | **2.70 rev/s** | ✅ Exceeded |
| Reliability | 95%+ | **100%** | ✅ Perfect |
| Scale | 1000 reviews | **1000** | ✅ Complete |

## Model Distribution (Actual Usage)
- **52.3%** Claude Haiku (lightweight)
- **27.7%** GPT-4o-mini (ultra-lightweight)  
- **20.0%** GPT-3.5-turbo (medium)
- **0%** Premium models (efficient routing)

**Result**: 80% of reviews processed with cost-effective models, achieving optimal cost-quality balance.

## System Scalability & Future Development

### Progressive Development Architecture
```
Phase 1: Foundation ──→ Phase 2: Optimization ──→ Phase 3: Enterprise
       │                     │                        │
   Routing System       Advanced Caching        Production Deploy
   (1K reviews)         (5K+ reviews)           (50K+ reviews)
       │                     │                        │
   63.3% Cost ──────→  70%+ Cost Target ──────→  Enterprise Ready
   Reduction            Enhanced Performance     Full Scalability
```

### Development Roadmap
| Phase | Focus | Target Scale | Key Features |
|-------|-------|-------------|--------------|
| **Phase 1** | Foundation | 1,000 reviews | **Complexity routing + validation** |
| **Phase 2** | Optimization | 5,000+ reviews | **Advanced caching + batch processing** |
| **Phase 3** | Enterprise | 50,000+ reviews | **Production deployment + monitoring** |

### Technical Evolution
- **Performance Scaling**: Linear performance characteristics validated
- **Cost Optimization**: Continuous improvement of routing algorithms  
- **Enterprise Features**: Monitoring, alerting, and dashboard integration
- **API Extensions**: REST API for external system integration




## Component Structure (Auto-Generated)

```
src/
├── universal_system_manager.py
├── universal_processor.py
├── __init__.py
├── main.py
├── core/
│   ├── __init__.py
│   ├── smart_router_v2.py
│   └── cost_reporter.py
├── integrations/
│   ├── __init__.py
│   └── openrouter_integration.py
├── caching/
│   ├── cache_manager.py
│   ├── __init__.py
│   └── l1_cache.py
├── demos/
│   ├── week1_complexity_routing_system.py
│   ├── __init__.py
│   └── week2_caching_system.py
```

**Component Details:**
- **universal_system_manager.py**: UniversalSystemManager
- **universal_processor.py**: class, UniversalProcessor
- **main.py**: class, AmazonDataLoader, CostTracker, ModelRouter, SemanticCache, AmazonReviewAnalyzer
- **core/smart_router_v2.py**: class, SmartRouterV2
- **core/cost_reporter.py**: class, class, CostTracker
- **integrations/openrouter_integration.py**: class, OpenRouterOptimizer, RealAPIMode
- **caching/cache_manager.py**: CacheManager
- **caching/l1_cache.py**: class, class, L1Cache
- **demos/week1_complexity_routing_system.py**: Week1FullOptimizer
- **demos/week2_caching_system.py**: Week2CachingOptimizer


**Testing Structure:**
```
tests/
├── test_smart_router_v2.py (19 tests)
├── test_universal_system.py (4 tests)
├── test_main_components.py (21 tests)
├── test_integration.py (13 tests)
├── test_cost_reporter.py (15 tests)
├── test_l1_cache.py (16 tests)
```

