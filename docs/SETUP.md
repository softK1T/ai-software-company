# Setup & Troubleshooting

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.11+ (for local development without Docker)
- Git 2.30+

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/softK1T/ai-software-company.git
cd ai-software-company
```

### 2. Setup Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

**Required (Phase 2+):**
- `GITHUB_APP_ID`
- `GITHUB_APP_PRIVATE_KEY`
- `OPENAI_API_KEY`

**Optional (Phase 1):**
- Database will use PostgreSQL in Docker
- OpenAI calls mocked in Phase 1

### 3. Start Services

```bash
cd infra
docker-compose up -d

# Verify services
docker-compose ps
```

**Expected Output:**
```
CONTAINER ID  STATUS          NAMES
...           Up 2 minutes    aicompany-postgres
...           Up 2 minutes    aicompany-redis
...           Up 1 minute     aicompany-backend
...           Up 1 minute     aicompany-pgadmin
```

### 4. Run Migrations

```bash
cd infra
docker-compose exec backend alembic upgrade head
```

### 5. Seed Templates

```bash
cd infra
docker-compose exec backend python scripts/seed_templates.py
```

**Output:**
```
✅ Created template: MVP Fast v1.0.0
✅ Created template: Startup Team v1.0.0
✅ Created template: API Quality-First v1.0.0
✅ Created template: Full-Stack App v1.0.0
✅ Created template: Enterprise Strict v1.0.0
✓ All templates seeded successfully
```

### 6. Access Services

- **API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc
- **PgAdmin**: http://localhost:5050 (admin@example.com / admin)
- **Redis CLI**: `cd infra && docker-compose exec redis redis-cli`

## Testing

### Run Tests

```bash
cd backend
pytest tests/ -v
```

### Run Specific Test

```bash
pytest tests/test_templates.py::test_create_template -v
```

### Coverage Report

```bash
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

## Development Workflow

### Local Backend Development (without Docker)

```bash
# Setup virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Start backend (requires postgres + redis running)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Management

#### Connect to PostgreSQL

```bash
cd infra
docker-compose exec postgres psql -U dev -d aicompany
```

#### Create Migration

```bash
cd backend
alembic revision --autogenerate -m "Add new table"
# Edit migration file
alembic upgrade head
```

#### Reset Database

```bash
cd infra
docker-compose down -v  # Remove volumes
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

## Troubleshooting

### Issue: "Connection refused" on localhost:8000

**Check if backend is running:**
```bash
cd infra
docker-compose logs backend
```

**If not started:**
```bash
docker-compose restart backend
```

### Issue: "Database connection error"

**Check PostgreSQL:**
```bash
cd infra
docker-compose exec postgres psql -U dev -d aicompany -c "SELECT 1"
```

**Reset database:**
```bash
cd infra
docker-compose down postgres postgres_data
docker-compose up -d postgres
# Wait 10 seconds
docker-compose exec backend alembic upgrade head
```

### Issue: "Redis connection error"

**Check Redis:**
```bash
cd infra
docker-compose exec redis redis-cli ping
```

**Expected:** `PONG`

### Issue: "Migration conflicts"

**View migration history:**
```bash
cd backend
alembic history
```

**Downgrade to specific revision:**
```bash
alembic downgrade <revision>
```

### Issue: "Tests failing"

**Clean up:**
```bash
cd backend
rm -rf .pytest_cache __pycache__ tests/__pycache__
pytest --tb=short
```

## Docker Compose Profiles

### Start with Workers (Phase 2+)

```bash
cd infra
docker-compose --profile worker up -d
```

## Environment Variables

### Database
- `DATABASE_URL`: PostgreSQL connection string
- Default: `postgresql://dev:devpass@postgres:5432/aicompany`

### Redis
- `REDIS_URL`: Redis connection string
- Default: `redis://redis:6379`

### APIs
- `OPENAI_API_KEY`: OpenAI API key (required Phase 2)
- `GITHUB_APP_ID`: GitHub App ID (required Phase 2)
- `GITHUB_APP_PRIVATE_KEY`: GitHub App private key (required Phase 2)

### Logging
- `DEBUG`: Enable debug mode (default: true)
- `LOG_LEVEL`: Logging level (default: INFO)

## Production Deployment

### Prerequisites
- Kubernetes 1.24+
- Helm 3.0+
- PostgreSQL 14+
- Redis 7+

### Deploy (Phase 3)

```bash
kubectl create namespace aicompany
helm install aicompany ./infra/helm -n aicompany -f values.yaml
```

## Support

For issues, open a GitHub issue or contact the team.
