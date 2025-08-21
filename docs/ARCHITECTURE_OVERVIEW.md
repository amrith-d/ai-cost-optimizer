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
│                     OUTPUT                              │
│  Sentiment • Quality • Recommendation • Metrics        │
│  61.5% Cost Reduction • 2.70 reviews/second            │
│  Week 1: Foundation Implementation                      │
└─────────────────────────────────────────────────────────┘
```

## Component Interaction Flow

```
AmazonDataLoader ──→ SmartRouterV2 ──→ OpenRouterOptimizer ──→ CostTracker
       │                  │                    │                    │
   Load Reviews      Analyze Complexity    Process with         Track Costs &
   from Dataset      Score 4 Dimensions    Selected Model       Performance
       │                  │                    │                    │
   Process Reviews ──→ Route to Tier  ──→   Return Results ──→  Generate Reports
   with Quality      (3 model tiers)       + Performance       Cost Analysis

Week 1 Foundation: Complexity-based routing system with cost optimization and performance validation
```

## Core Files Structure

```
src/
├── main.py                     # Entry point & AmazonReviewAnalyzer
└── core/
    ├── smart_router_v2.py     # Complexity analysis & routing
    ├── cost_reporter.py       # Performance metrics & tracking
    └── integrations/
        └── openrouter_integration.py  # API client

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




## Component Structure

```
src/
├── main.py                    # Main analyzer class
├── core/
│   ├── smart_router_v2.py    # Complexity analysis & routing
│   ├── cost_reporter.py      # Cost tracking & reporting
│   └── integrations/
│       └── openrouter_integration.py  # API client
```

**Component Details:**
- **main.py**: AmazonDataLoader, CostTracker, ModelRouter, AmazonReviewAnalyzer
- **core/smart_router_v2.py**: SmartRouterV2
- **core/cost_reporter.py**: CostTracker
- **integrations/openrouter_integration.py**: OpenRouterOptimizer

**Testing Structure:**
```
tests/
├── test_smart_router_v2_simple.py    # Router tests
├── test_main_components_simple.py    # Component tests  
├── test_integration_simple.py        # End-to-end tests
├── test_cost_reporter_simple.py      # Cost tracking tests
```

