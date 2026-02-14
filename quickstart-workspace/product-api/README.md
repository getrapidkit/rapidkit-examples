# Product API

**Part of [quickstart-workspace](../README.md)** - A production-ready FastAPI demonstrating RapidKit's 5-minute setup.

**Related Articles:**
- Medium: [From Zero to Production API in 5 Minutes](https://rapidkit.medium.com/from-zero-to-production-api-in-5-minutes)
- Dev.to: [From Zero to Production API in 5 Minutes](https://dev.to/rapidkit/from-zero-to-production-api-in-5-minutes)

---

## 🚀 What's Included

This project demonstrates a **production-ready FastAPI** built in 5 minutes with:

**Core Features:**
- ✅ JWT Authentication (register, login, refresh)
- ✅ PostgreSQL with SQLAlchemy (async & sync)
- ✅ Redis caching with connection pooling
- ✅ CORS & Security Headers
- ✅ Structured logging with request tracking
- ✅ Health checks & Prometheus metrics
- ✅ Testing setup with pytest
- ✅ Docker & docker-compose
- ✅ CI/CD templates (GitHub Actions)

**RapidKit Modules Installed:**
- `settings` - Multi-source configuration (`.env`, `config.yaml`)
- `auth_core` - PBKDF2 password hashing + HMAC token signing
- `db_postgres` - PostgreSQL with async/sync engines
- `redis` - Redis client with retry logic
- `cors` - CORS middleware configured
- `security_headers` - CSP, X-Frame-Options, etc.
- `logging` - Structured JSON logging
- `deployment` - Docker, Makefile, CI/CD templates

---

## ⚡ Quick Start

### 1. Start Infrastructure

```bash
# From product-api directory
docker-compose up -d postgres redis
```

### 2. Install Dependencies

```bash
source .rapidkit/activate
rapidkit init
```

### 3. Run the API

```bash
rapidkit dev
```

**API running at:** http://localhost:8000

**Key Endpoints:**
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Auth Core Health:** http://localhost:8000/api/health/module/auth-core
- **Postgres Health:** http://localhost:8000/api/health/module/postgres
- **Redis Health:** http://localhost:8000/api/health/module/redis
- **Metrics:** http://localhost:8000/metrics

---

## 📁 Project Structure

```
product-api/
├── src/
│   ├── main.py                    # FastAPI app entrypoint
│   ├── routing/
│   │   ├── health.py              # Health check routes
│   │   └── examples.py            # Example notes API
│   ├── modules/
│   │   └── free/
│   │       ├── auth/core/         # Authentication module
│   │       ├── database/          # PostgreSQL module
│   │       ├── cache/redis/       # Redis module
│   │       ├── security/          # CORS & headers
│   │       └── essentials/        # Settings, logging
│   └── health/
│       ├── auth_core.py           # Auth health probe
│       ├── postgres.py            # DB health probe
│       └── redis.py               # Cache health probe
├── tests/
│   ├── test_health.py             # Health endpoint tests
│   ├── test_examples.py           # Example API tests
│   └── modules/                   # Module integration tests
├── config/
│   ├── database/postgres.yaml     # DB configuration
│   ├── cache/redis.yaml           # Cache configuration
│   └── security/                  # Security configs
├── docker-compose.yml             # Postgres + Redis services
├── Dockerfile                     # Production container
├── .env.example                   # Environment template
├── Makefile                       # Development tasks
└── pyproject.toml                 # Dependencies

```

---

A minimal FastAPI service generated with the **FastAPI Standard Kit**. All domain-specific capabilities (configuration, logging, persistence, observability, authentication, etc.) are provided by RapidKit modules.

## Quick start

```bash
# Load the project-aware RapidKit CLI (adds .rapidkit/rapidkit to PATH)
source .rapidkit/activate

# Bootstrap dependencies (creates .venv + installs Poetry-managed deps)
rapidkit init  # use make init if you prefer a Make target

# Copy env templates and install hooks/tooling
./bootstrap.sh

# Run linting, typing, testing, and supply-chain audits
make lint
make typecheck
make test
make audit

# Start development server with hot reload
make dev
rapidkit dev  # same as make dev but auto-detects the project

# Prefer RapidKit CLI helpers when you want it to resolve scripts automatically
rapidkit lint
rapidkit test
rapidkit start
```

> Always run `source .rapidkit/activate` after opening a new shell so the project-local `rapidkit` launcher and helper scripts stay on your PATH.

> Re-run `rapidkit init` (or `make init`) whenever dependencies change, or use `SKIP_INIT=1 make install` if you only need to refresh tooling/hooks without reinstalling packages.

> Lockfiles are generated automatically during scaffolding. Set `RAPIDKIT_SKIP_LOCKS=1` (or `RAPIDKIT_GENERATE_LOCKS=0`) before running `rapidkit create` if you need to opt out.

> Want the full RapidKit CLI catalog? Run `rapidkit --help` or visit the CLI reference in the docs to explore every global/project command.

---

## Local development

- `rapidkit init` bootstraps dependencies via the project-local CLI (run it after sourcing `.rapidkit/activate`).
- `make init` is an optional alias for `rapidkit init` when you prefer Make targets.
- `make install` re-runs `rapidkit init` (unless you set `SKIP_INIT=1`) and refreshes developer tooling such as pre-commit hooks.
- `./bootstrap.sh` copies `.env.example` to `.env` (if missing) and runs `SKIP_INIT=1 make install` for you.
- `make dev` (or `rapidkit dev`) launches Uvicorn with the correct module path and reload settings.
- `make lint`, `make typecheck`, and `make test` wrap Ruff, mypy, and pytest for consistent CI parity.
- `make audit` shells out to `pip-audit` to surface vulnerable dependencies.
- Prefer `rapidkit lint`, `rapidkit test`, and `rapidkit start` if you want RapidKit to autodetect the virtualenv and command wiring.
```

## Available commands

```bash
rapidkit init       # 🔧 Bootstrap the project (create .venv + install deps)
make init           # 🔧 Optional alias for rapidkit init (wraps the local CLI)
./bootstrap.sh      # 🪄 Copy env template + install hooks/tooling (idempotent)
rapidkit dev        # 🚀 Start development server with hot reload
make dev            # 🚀 Alternative via Makefile helper
rapidkit start      # ⚡ Start production server
rapidkit lint       # 🔧 Run lint checks via project-aware CLI
rapidkit test       # 🧪 Run pytest through RapidKit CLI
make install        # 📦 Install Poetry deps + hooks
make lint           # ✅ Lint via Ruff + Black
make typecheck      # 🔍 Run mypy on src
make test           # 🧪 Run tests
make audit          # 🔐 Run pip-audit across dependencies
make docker-up      # 🐳 Start docker compose stack (if enabled)
```

## Project layout

- `src/main.py` – FastAPI application entrypoint
- `src/routing/` – Core routers (health) and anchors for module routers
- `src/modules/` – Module bootstrap anchors
- `pyproject.toml` – Poetry configuration and dependencies
- `Makefile` – Common developer workflows (format, lint, docker, etc.)
- `Dockerfile` / `docker-compose.yml` – Optional container setup for local dev and deployment
- `.github/workflows/ci.yml` – Optional GitHub Actions pipeline for linting and tests

## Example feature

The scaffold ships with a tiny in-memory **notes** API mounted under `/api/examples/notes`. Use it as a safe playground for wiring routers, schemas, and tests without touching your real domain logic:

```bash
# Create a note
curl -s -X POST http://localhost:8000/api/examples/notes \
	-H "Content-Type: application/json" \
	-d '{"title":"first","body":"scaffolded by RapidKit"}'

# List notes
curl -s http://localhost:8000/api/examples/notes | jq
```

The implementation intentionally stays in memory so you can replace it with a repository-backed service once you install RapidKit database modules.

## Recommended RapidKit modules

The following RapidKit modules are suggested during scaffolding; install them any time with `rapidkit add module <name>`:

- Middleware (`middleware`) – tier: free
- Shared Utils (`shared_utils`) – tier: free
- Domain User Profile (`domain_user_profile`) – tier: free
- Infrastructure User Profile (`infrastructure_user_profile`) – tier: free
- Application User Profile (`application_user_profile`) – tier: free
- Presentation Http (`presentation_http`) – tier: free
- Settings (`settings`) – tier: free
- Logging (`logging`) – tier: free
- Deployment (`deployment`, optional) – tier: free
- Db Sqlite (`db_sqlite`, optional) – tier: free
- Openapi Docs (`openapi_docs`, optional) – tier: free

## Adding features

Use `rapidkit add module <module-name>` to install optional capabilities. Modules inject imports, routes, and services through the anchors defined in `src/main.py` and `src/routing/__init__.py`.

During kit generation you can decide whether the core RapidKit modules ship with the scaffold:

```text
Install the RapidKit settings module? [Y/n]
Install the RapidKit logging module? [Y/n]
Install deployment module assets (Docker/CI)? [Y/n]
```

### Scaffold toggles vs RapidKit modules

- `enable_*` prompts (for Docker, CI, SQLite, etc.) control the starter assets generated by this kit.
- `install_*` prompts control which RapidKit modules are installed up front.
- You can always add modules later with `rapidkit add module <name>` if you skip them during scaffolding.

When you need deployment artefacts in an existing project, install the optional `deployment` module:

```bash
rapidkit add module deployment
rapidkit modules lock --overwrite
```

<!-- <<<inject:module-snippet>>> -->

## 📄 License

This project is licensed under the **MIT** License - see the `LICENSE` file included at the project root for details.

## 🔒 Security & secrets

- Copy `.env.example` to `.env` and populate secrets (`SECRET_KEY`, DB credentials, etc.) before deploying.
- **Do not** commit real secrets or `.env` to git; `.gitignore` already contains `.env` to protect accidental commits.
- For production, tighten CORS and allowed hosts rather than using wildcard settings provided for convenience in dev.
- Run `make audit` (pip-audit) before releases to catch dependency CVEs early.