# RapidKit Examples

Official example projects for RapidKit.

This repository contains production-style reference implementations that accompany RapidKit tutorials and articles.

---

## 🚀 Featured Examples

### 1. Quickstart Workspace (⚡ Beginner)

**Path:** [quickstart-workspace](quickstart-workspace)

**Description:** Production-ready FastAPI in 5 minutes

**Includes:**
- `product-api` (FastAPI): Complete API with auth, database, caching, monitoring
- JWT Authentication (register, login, refresh)
- PostgreSQL with SQLAlchemy (async & sync)
- Redis caching with connection pooling
- CORS & Security Headers
- Structured logging & Prometheus metrics
- Docker & CI/CD templates

**Modules:** `settings`, `auth_core`, `db_postgres`, `redis`, `cors`, `security_headers`, `logging`, `deployment`

**Articles:**
- Medium: [From Zero to Production API in 5 Minutes](https://medium.com/@rapidkit/from-zero-to-production-api-in-5-minutes-e2f058286a09)
- Dev.to: [From Zero to Production API in 5 Minutes](https://dev.to/rapidkit/from-zero-to-production-api-in-5-minutes-2ehl)

---

### 2. AI Agent Workspace (🤖 Intermediate)

**Path:** [my-ai-workspace](my-ai-workspace)

**Description:** Multi-provider AI assistant with FastAPI and NestJS

**Includes:**
- `ai-agent` (FastAPI): Multi-provider AI assistant (echo/template/OpenAI-ready)
- `ai-agent-nest` (NestJS): Parity implementation with `ai_assistant` module
- Streaming + caching endpoints
- Health checks & support ticket workflow
- Integrated tests and module status checks

**Modules:** `ai_assistant`, `settings`, `logging`

**Articles:**
- Medium: [Build Your First AI Agent with RapidKit in 10 Minutes](https://rapidkit.medium.com/build-your-first-ai-agent-with-rapidkit-in-10-minutes-f38a6a12088d)
- Dev.to: [Build Your First AI Agent with RapidKit in 10 Minutes](https://dev.to/rapidkit/build-your-first-ai-agent-with-rapidkit-in-10-minutes-3dj6)

---

## ⚡ Quick Start

### Quickstart Workspace (Beginner - 5 minutes)

**Production-ready FastAPI with auth, database, caching:**

```bash
git clone https://github.com/getrapidkit/rapidkit-examples.git
cd rapidkit-examples/quickstart-workspace/product-api

# Start infrastructure
docker-compose up -d postgres redis

# Install & run
source .rapidkit/activate
rapidkit init
rapidkit dev
```

**Endpoints:**
- 📚 API Docs: http://localhost:8000/docs
- ❤️ Health: http://localhost:8000/health
- 🔐 Auth: http://localhost:8000/api/health/module/auth-core
- 💾 Database: http://localhost:8000/api/health/module/postgres
- 🗄️ Redis: http://localhost:8000/api/health/module/redis
- 📊 Metrics: http://localhost:8000/metrics

---

### AI Agent Workspace (Intermediate)

**FastAPI:**

```bash
git clone https://github.com/getrapidkit/rapidkit-examples.git
cd rapidkit-examples/my-ai-workspace/ai-agent
source .rapidkit/activate
rapidkit init
rapidkit dev
```

**NestJS:**

```bash
cd rapidkit-examples/my-ai-workspace/ai-agent-nest
source .rapidkit/activate
rapidkit init
rapidkit dev -p 8013
```

**Endpoints:**
- 📚 Swagger UI: http://127.0.0.1:8000/docs (or auto-fallback port)
- 🤖 AI Providers: `GET /ai/assistant/providers`
- 💬 Completions: `POST /ai/assistant/completions`
- 📡 Streaming: `POST /ai/assistant/stream`
- 🎫 Support Ticket: `POST /support/ticket`

## 🔍 Workspace Health Check

**Quickstart Workspace:**

```bash
cd quickstart-workspace
npx rapidkit doctor --workspace
```

**AI Agent Workspace:**

```bash
cd my-ai-workspace
npx rapidkit doctor --workspace
```

**Checks:**
- ✅ Python version (3.10+)
- ✅ Poetry installation
- ✅ RapidKit Core version
- ✅ Virtual environment status
- ✅ Project dependencies
- ✅ Module configurations

## 📁 Repository Layout

```text
rapidkit-examples/
├── README.md                    # This file
├── examples.json                # Workspace metadata
│
├── quickstart-workspace/        # ⚡ Beginner (5 minutes)
│   ├── README.md               # Workspace guide
│   ├── pyproject.toml          # Workspace dependencies
│   └── product-api/            # Production-ready API
│       ├── README.md           # Project guide
│       ├── src/
│       │   ├── main.py         # FastAPI app
│       │   ├── modules/        # RapidKit modules
│       │   ├── routing/        # API routes
│       │   └── health/         # Health probes
│       ├── tests/              # Test suite
│       ├── config/             # Module configs
│       ├── docker-compose.yml  # Postgres + Redis
│       └── Dockerfile          # Production image
│
└── my-ai-workspace/            # 🤖 Intermediate (10 minutes)
    ├── README.md               # Workspace guide
    ├── ai-agent/               # FastAPI AI assistant
    │   ├── README.md
    │   └── EXAMPLE_README.md   # Tutorial walkthrough
    └── ai-agent-nest/          # NestJS implementation
        └── README.md
```

## 📚 Documentation Structure

**Quickstart Workspace:**
- [quickstart-workspace/README.md](quickstart-workspace/README.md) - Workspace setup & overview
- [quickstart-workspace/product-api/README.md](quickstart-workspace/product-api/README.md) - Project guide & usage

**AI Agent Workspace:**
- [my-ai-workspace/README.md](my-ai-workspace/README.md) - Workspace-level setup
- [my-ai-workspace/ai-agent/README.md](my-ai-workspace/ai-agent/README.md) - FastAPI run/test commands
- [my-ai-workspace/ai-agent/EXAMPLE_README.md](my-ai-workspace/ai-agent/EXAMPLE_README.md) - Tutorial walkthrough
- [my-ai-workspace/ai-agent-nest/README.md](my-ai-workspace/ai-agent-nest/README.md) - NestJS parity guide

---

## 🎓 Learn More

**RapidKit Resources:**
- 📦 **npm CLI:** https://www.npmjs.com/package/rapidkit
- 🐍 **Python Core:** https://pypi.org/project/rapidkit-core/
- 🧩 **VS Code Extension:** https://marketplace.visualstudio.com/rapidkit
- 🌐 **Website:** https://www.getrapidkit.com
- 📖 **Documentation:** https://docs.getrapidkit.com

**Tutorial Articles:**
- Medium: https://rapidkit.medium.com
- Dev.to: https://dev.to/rapidkit

---

## 🚀 Coming Soon

- **product-workspace** - Step-by-step tutorial (Article 6)
- **ecommerce-workspace** - Multi-service architecture (Article 10)
- **ddd-workspace** - DDD + CQRS patterns (Article 11)
- **AI workspaces** - Advanced AI patterns (Articles 7-8)

---

**Built with RapidKit** 🚀
