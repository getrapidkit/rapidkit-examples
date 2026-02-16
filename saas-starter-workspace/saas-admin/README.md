# saas-admin

Admin operations API for internal tools, user management, and support workflows. Domain-driven FastAPI service generated with [RapidKit](https://github.com/getrapidkit/rapidkit-core).

**Related:** Part of [saas-starter-workspace](../README.md) - Production SaaS architecture with 4 microservices.

---

## ⚡ Quick Start

```bash
# Load the project-aware RapidKit CLI
source .rapidkit/activate

# Bootstrap dependencies
rapidkit init

# Copy env templates and install hooks/tooling
./bootstrap.sh

# Start development server on port 8001
rapidkit dev --port 8001
# Or: make dev

# Run tests
rapidkit test

# Type-check and lint
make typecheck
make lint
```

**API running at:** http://localhost:8001

**Endpoints:**
- API Docs: http://localhost:8001/docs
- Health Check: http://localhost:8001/health
- Module Health: http://localhost:8001/api/health/module/*

> **Tip:** Run on port 8001 to avoid conflicts with `saas-api` (port 8000).

---

## 🎯 Features

### Admin Operations

- **User Management:**
  - List all users with filtering
  - View user details and activity
  - User impersonation capabilities (TODO)
  - Account suspension/activation (TODO)

- **Support Tools:**
  - User search by email/ID
  - Session management
  - Activity audit trails (TODO)
  - Support ticket integration (TODO)

- **Internal Dashboards:**
  - System metrics
  - User statistics
  - Subscription analytics (TODO)
  - Revenue reports (TODO)

### Security

- **Admin Authentication:**
  - Same auth modules as `saas-api`
  - JWT + session cookie support
  - Admin role verification (TODO)

- **Access Control:**
  - Admin-only endpoints
  - Permission-based operations (TODO)
  - Audit logging for sensitive actions (TODO)

---

## 📦 Installed Modules

### Core Modules

**`auth_core`** - Authentication primitive
- PBKDF2 password hashing (100K iterations)
- Token signing and verification
- Health: `/api/health/module/auth-core`

**`auth_session`** - Session management
- Cookie-based sessions
- Server-side validation
- Health: `/api/health/module/session`

**`users_core`** - User service
- User CRUD operations
- Email uniqueness
- Health: `/api/health/module/users-core`

**`settings`** - Configuration management
- Multi-source config (env, yaml, custom)
- Hot-reload in development
- Health: `/api/health/module/settings`

---

## 📁 Project Structure

```
saas-admin/
├── src/
│   ├── main.py              # Application entrypoint
│   ├── app/
│   │   ├── main.py          # FastAPI factory
│   │   ├── application/     # Use cases
│   │   ├── domain/          # Business entities
│   │   ├── infrastructure/  # External adapters
│   │   └── presentation/    # API layer
│   ├── routing/
│   │   ├── __init__.py      # Router assembly
│   │   ├── admin.py         # Admin-specific routes (TODO)
│   │   ├── health.py        # Health checks
│   │   └── notes.py         # Example feature
│   ├── modules/
│   │   └── free/
│   │       ├── auth/
│   │       ├── users/
│   │       └── settings/
│   └── health/
├── tests/
│   ├── test_admin_ops.py
│   └── conftest.py
├── config/
├── .env.example
├── docker-compose.yml
└── Makefile
```

### DDD Architecture

Same clean architecture as `saas-api`:
- **Domain** – Business rules
- **Application** – Use case orchestration
- **Infrastructure** – External services
- **Presentation** – HTTP API layer

---

## 🔧 Example Usage

### Admin User Management

```python
import requests

BASE = 'http://localhost:8001/api'

# Admin login (same as saas-api)
r = requests.post(f'{BASE}/auth/login', json={
    'email': 'admin@example.com',
    'password': 'AdminPass123!'
})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# List all users (admin endpoint - TODO)
users = requests.get(f'{BASE}/admin/users', headers=headers)
print(users.json())

# Get user details (admin endpoint - TODO)
user = requests.get(f'{BASE}/admin/users/usr_123', headers=headers)
print(user.json())

# Impersonate user (admin endpoint - TODO)
impersonate = requests.post(f'{BASE}/admin/impersonate/usr_123', 
    headers=headers
)
print(impersonate.json())
```

### Health Monitoring

```python
# Check admin API health
health = requests.get(f'{BASE}/health')
print(health.json())

# Check module health
auth_health = requests.get(f'{BASE}/api/health/module/auth-core')
print(auth_health.json())
```

---

## 🚀 Add More Modules

```bash
source .rapidkit/activate

# Add database for audit logs
rapidkit add module db_postgres

# Add Redis for session storage
rapidkit add module redis

# Add email for admin notifications
rapidkit add module email

# Add monitoring
rapidkit add module observability.core
```

---

## 🔐 Environment Configuration

**`.env` template:**
```bash
# Auth Configuration (same as saas-api)
RAPIDKIT_AUTH_CORE_PEPPER="your_pepper_here"
RAPIDKIT_SESSION_SECRET="your_session_secret"

# Admin-specific
ADMIN_AUTH_REQUIRED=true
ADMIN_ALLOWED_EMAILS="admin@example.com,support@example.com"
```

**Generate secrets:**
```bash
openssl rand -base64 48  # Auth pepper
openssl rand -base64 32  # Session secret
```

---

## 🧪 Testing

```bash
# Run all tests
rapidkit test

# Test admin operations
pytest tests/test_admin_ops.py -v

# With coverage
pytest --cov=src tests/
```

---

## 🏗️ Production Deployment

### Isolation Strategy

**Why separate admin API?**
- Customer traffic doesn't affect admin operations
- Different authentication/authorization rules
- Independent scaling
- Enhanced security (internal network only)

### Docker

```bash
docker build -t saas-admin:latest .
docker-compose up -d
```

### Network Security

**Production best practices:**
- Deploy admin API on internal network
- Require VPN/bastion for access
- Use different JWT secrets than product API
- Enable audit logging for all operations

---

## 📚 Learn More

**Architecture guides:**
- [Workspace Overview](../README.md)
- [Building Production SaaS Architecture (Medium)](https://medium.com/@rapidkit/building-production-saas-architecture-13)

**Related services:**
- [saas-api](../saas-api/README.md) - Product API
- [saas-webhooks](../saas-webhooks/README.md) - Webhook processor
- [saas-nest](../saas-nest/README.md) - NestJS service

**RapidKit documentation:**
- [Modules Catalog](https://getrapidkit.com/docs/modules)
- [CLI Reference](https://getrapidkit.com/docs/cli)

---

## 🛠️ Troubleshooting

**Port conflict with saas-api:**
```bash
# Always run admin API on port 8001
rapidkit dev --port 8001
```

**Authentication issues:**
```bash
# Use same secrets as saas-api
# Check .env matches saas-api/.env
```

**Need help?**
- Documentation: https://getrapidkit.com/docs
- GitHub Issues: https://github.com/getrapidkit/rapidkit-core/issues
