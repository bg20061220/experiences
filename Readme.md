# TailorCV

[![Live Demo](https://img.shields.io/badge/demo-live-success)](https://tailorcvai.vercel.app)
[![GitHub](https://img.shields.io/badge/GitHub-Source-black)](https://github.com/bg20061220/Resume-Tailor-Ai-)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> Semantic search platform that intelligently matches your experiences to job requirements using vector embeddings and LLM generation. Built to solve the co-op application grind at UWaterloo.

**Live at [tailorcvai.vercel.app](https://tailorcvai.vercel.app)**

![TailorCV Landing Page](https://raw.githubusercontent.com/bg20061220/Resume-Tailor-Ai-/main/screenshot.png)

## 🎯 Why I Built This

During my first co-op search at Waterloo, I applied to 500+ positions and spent countless hours manually tailoring resumes. I realized the core problem wasn't writing bullet points—it was **finding which experiences were actually relevant** to each role.

Traditional keyword matching fails to capture semantic similarity. This system uses vector embeddings to understand that "built scalable microservices" semantically matches "distributed systems experience," even without shared keywords.

## ✨ How It Works

1. **Build your experience library** — Add work experience, projects, and volunteering manually or by importing from LinkedIn
2. **Paste a job description** — pgvector performs semantic similarity search to find your most relevant experiences
3. **Generate tailored bullets** — LLM creates ATS-optimized resume bullet points matched to the job requirements

## 📊 Project Status

**Current Phase**: Beta - functional and deployed, actively iterating based on user feedback

**What Works:**
- ✅ Semantic search with <200ms latency
- ✅ LinkedIn profile parsing with LLM
- ✅ Batch operations (up to 25 experiences)
- ✅ Google OAuth authentication
- ✅ Production deployment with uptime monitoring

**What I Learned:**
- Vector database architecture and HNSW indexing
- Cost optimization in AI systems (90% cost reduction vs OpenAI)
- Production debugging (memory leaks, cold starts, platform migration)
- Full-stack deployment strategies (Render → Railway migration)

**Beta Users**: 12+ students testing across co-op applications

**Built by**: First-year Math student at UWaterloo ([b2goel@uwaterloo.ca](mailto:b2goel@uwaterloo.ca))

## 🏗️ System Architecture
```
┌─────────────┐         ┌──────────────┐         ┌─────────────────┐
│   React     │ ──────> │   FastAPI    │ ──────> │   Supabase      │
│  (Vercel)   │  HTTPS  │  (Railway)   │  SQL    │  PostgreSQL     │
└─────────────┘         └──────────────┘         │  + pgvector     │
                               │                  └─────────────────┘
                               │                           │
                               ▼                           ▼
                        ┌─────────────┐          ┌─────────────┐
                        │  Groq LLM   │          │   Cohere    │
                        │  (Llama3.1) │          │ Embeddings  │
                        └─────────────┘          └─────────────┘
```

**Data Flow:**
1. User pastes job description → React frontend
2. Frontend sends to FastAPI backend
3. Backend generates 384-dim embedding via Cohere API
4. pgvector performs cosine similarity search using HNSW index
5. Top-3 relevant experiences retrieved (cosine distance < 0.3)
6. Retrieved experiences + job description sent to Groq
7. LLM generates tailored bullet points with action verbs and quantified results
8. Results streamed back to frontend

## 🧠 Technical Highlights

### Semantic Search Engine
- **Cohere embeddings** (embed-english-light-v3.0) for cost-effective similarity matching
- **PostgreSQL with pgvector** extension for efficient vector operations
- **HNSW indexing** for approximate nearest neighbor search
- **384-dimensional embeddings** for fast search without sacrificing accuracy
- Average search time: **<200ms** across 100+ experiences
- Cosine distance metric for normalized embeddings

### LLM Integration
- **Groq API** with Llama 3.1 for 10-50x faster generation vs OpenAI
- Context-aware prompting using retrieved experiences
- Cost: **~$0.002** per resume generation vs **~$0.02+** with GPT-4
- Structured output parsing for clean bullet points

### Production Features
- **Authentication**: Supabase Auth with Google OAuth (ES256 JWT)
- **Rate limiting**: slowapi with IP-based tracking (100 req/min)
- **LinkedIn parsing**: LLM-based extraction of structured experience data
- **Batch operations**: Efficient bulk imports (up to 25 experiences)
- **Input sanitization**: Protection against prompt injection attacks
- **Row-level security**: Users only access their own data

## 🏛️ Architecture Decisions

### Why FastAPI over Flask/Express?
- Native async support for concurrent API calls (Cohere + Groq)
- Automatic API documentation (OpenAPI/Swagger at `/docs`)
- Pydantic validation out of the box
- Better performance for I/O-bound operations (embedding generation, LLM calls)

### Why pgvector over Pinecone/Weaviate?
- **Lower cost**: Free tier on Supabase vs $70+/month for managed vector DBs
- **Unified storage**: Single database for both relational data and vectors
- **No additional service**: Reduces deployment complexity
- **Direct SQL access**: Complex queries combining vector and relational data
- **HNSW indexing**: Sub-linear query time O(log n) vs O(n)

### Why HNSW Index?
- Approximate nearest neighbor (ANN) search
- Sub-linear query time: O(log n) vs O(n) for exact search
- <200ms search across 100+ experiences
- **Trade-off**: 99% recall vs 100% (acceptable for this use case)
- Configurable parameters: `m=16`, `ef_construction=64`

### Why ES256 JWT over HS256?
- Supabase uses ES256 (ECDSA) by default
- **Asymmetric encryption**: Public key verification, private key signing
- More secure than symmetric HS256
- Industry standard for OAuth/OIDC
- Prevents token forgery (can't generate valid tokens without private key)

## 🚀 Tech Stack

| Layer | Technology | Why This Choice |
|-------|-----------|-----------------|
| **Frontend** | React + Vercel | Fast deployment, edge network, automatic preview deployments |
| **Backend** | FastAPI + Railway | Async Python, auto docs, always-on hosting (no cold starts) |
| **Database** | PostgreSQL + pgvector | Vector search + relational data in one DB, HNSW indexing |
| **Embeddings** | Cohere (384-dim) | 10x cheaper than OpenAI, sufficient quality for semantic matching |
| **LLM** | Groq (Llama 3.1 8B) | 10-50x faster than GPT-4, lower cost, good quality |
| **Auth** | Supabase Auth (ES256) | Secure OAuth, row-level security, JWT validation |
| **Rate Limiting** | slowapi | Simple IP-based limiting, prevents API abuse |

## 🔧 Production Operations

### Platform Migration: Render → Railway

**Original Setup (Render):**
- Free tier with 15-minute sleep timeout
- Required cron keepalive every 5 minutes to prevent cold starts
- Memory crashes after 4-6 hours (512MB limit)

**Problem Identified:**
After running in production, discovered three issues:
1. **Cold starts**: Users experienced 30-50s delays after idle periods
2. **Memory leaks**: App crashed hitting 512MB limit (likely unclosed DB connections)
3. **Cron reliability**: Keepalive sometimes failed during slow container restarts

**Root Cause Analysis:**
- Render free tier aggressively spins down containers
- Memory was accumulating over time (insufficient connection pooling)
- Keepalive ping timing out during 30-40s boot time

**Solution (Railway):**
- Migrated to Railway (always-on, no sleep)
- Eliminated cold start problem entirely
- 1GB memory limit (no more crashes)
- **Cost**: $5/month vs free tier

**Migration Process:**
1. Tested on Railway staging environment
2. Updated environment variables and secrets
3. Validated database connectivity and API integrations
4. Switched DNS and monitored for 24 hours
5. Shut down Render instance

**Result**: 
- ✅ <100ms response times (vs 30-50s cold starts)
- ✅ 100% uptime since migration
- ✅ Zero memory-related crashes
- ✅ Simplified architecture (no cron dependency)

### Uptime Monitoring

**Health Check System:**
- Cron job pings `/health` endpoint every 30 minutes
- Alert triggers if endpoint fails to respond
- Health endpoint validates database connectivity
- Provides basic uptime monitoring without paid tools

**Why 30 minutes:**
- Railway doesn't sleep (no need for frequent pings)
- Frequent enough to catch issues quickly
- Reduces noise from transient failures

**Future improvement**: Migrate to proper monitoring (UptimeRobot, Better Uptime)

## ⚠️ Known Limitations & Trade-offs

### Current Constraints

**Rate limiting state**: In-memory (resets on deployment)
- **Trade-off**: Simple implementation vs persistent limits
- **Impact**: Rate limits reset when Railway redeploys
- **Future**: Redis for production-grade rate limiting

**Embedding cache**: Not implemented
- Same experience text re-embeds on each search
- **Trade-off**: Simpler code vs API costs
- **Cost impact**: ~$0.0001 per search (acceptable at current scale)
- **Future**: Cache embeddings in database with hash key

**LinkedIn parsing**: LLM-based, can occasionally miss details
- **Mitigation**: Users can manually edit parsed experiences
- **Success rate**: ~95% based on beta testing
- **Edge cases**: Non-English profiles, unusual formatting

**Top-3 retrieval**: Fixed limit for experience matching
- **Reasoning**: More results = context bloat for LLM (8K token limit)
- **Trade-off**: Simplicity vs flexibility
- **Future**: Dynamic top-k based on job description length

### Design Decisions

**No PDF export**
- Users copy-paste bullets to their own resume templates
- **Reasoning**: Avoids complex formatting, respects user preferences
- **Alternative**: Users have existing resume styles/formats

**No resume parsing**
- Users build experience library manually or via LinkedIn
- **Reasoning**: Parsing is hard (different formats), error-prone
- **Benefit**: Cleaner, more structured data input

**Railway cost**: $5/month vs free tier
- **Trade-off**: Reliability vs cost
- **Justification**: User experience > $60/year
- **Math**: At 100 users, $0.05/user/month is acceptable

## 💡 Lessons Learned

### slowapi Rate Limiting Gotcha
**Problem**: Rate limiting threw 500 errors intermittently

**Root cause**: slowapi expects the Starlette `Request` parameter to be named exactly `request`, not `request_obj` or anything else. It finds it by name to extract the client IP.

**Solution**: Always name it `request` and use `body` for Pydantic models:
```python
# ❌ Wrong
def endpoint(request: MyModel, request_obj: Request):
    pass

# ✅ Correct
def endpoint(body: MyModel, request: Request):
    pass
```

**Learning**: Library behavior isn't always intuitive - read the source when docs are unclear

### Memory Leaks in Production
**Problem**: App crashed every 4-6 hours on Render

**Investigation**:
- Added memory profiling to track usage over time
- Found database connections accumulating (not being closed properly)
- Railway's higher limits revealed the issue wasn't just Render-specific

**Fix**: 
- Properly configured Supabase connection pooling (max 25 connections)
- Added connection timeout and recycling
- Implemented proper connection cleanup in FastAPI lifespan events

**Learning**: Free tiers reveal scaling issues faster (lower limits = earlier crashes = easier debugging)

### When To Pay For Infrastructure
Initially optimized for zero cost (free tier everything). After migration:
- **User experience improved dramatically** (no cold starts)
- **Maintenance simplified** (no cron to monitor)
- **Debugging easier** (consistent environment, better logs)

**Learning**: $5/month is worth it when reliability directly impacts user experience. Time saved debugging > cost.


## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 🤝 Feedback & Contact

Built by a first-year CS student at UWaterloo to solve co-op recruiting challenges. This is a learning project and I'm actively seeking feedback!

**Found a bug?** Open an issue on [GitHub](https://github.com/bg20061220/Resume-Tailor-Ai-/issues)

**Have a feature idea?** I'd love to hear it - create an issue or email me

**Questions about the tech?** Reach out at [b2goel@uwaterloo.ca](mailto:b2goel@uwaterloo.ca)

**View the code**:
- [Full Repository](https://github.com/bg20061220/Resume-Tailor-Ai-)
- Open source and transparent - verify security/implementation yourself

---

*Built with FastAPI, React, pgvector, and a lot of coffee during first-year at UWaterloo* ☕
