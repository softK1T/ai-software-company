# AI Software Company Platform

**Production-grade multi-agent AI platform for autonomous software company simulation**

A sophisticated orchestration system where AI agents collaboratively design, develop, test, document, deploy, and secure software projects in real-time.

## 🎯 Core Features

- **Multi-Agent Orchestration**: PM, Dev Lead, Developers, QA, Docs, DevOps, Security Specialist
- **Project Templates**: MVP Fast, Startup Team, API Quality-First, Full-Stack App, Enterprise Strict
- **LangGraph State Machine**: Configurable workflows with conditional routing
- **GitHub Integration**: Native Git operations, branch management, PR workflows
- **Real-time Dashboard**: WebSocket-powered task tracking and comment feeds
- **Budget Enforcement**: Token tracking, cost estimation, graceful degradation
- **Security-First**: SAST, DAST, dependency scanning, secret detection
- **Comprehensive Audit Trail**: Every agent action recorded with full context

## 📊 Phase 1: Core Infrastructure (Current)

✅ SQLAlchemy ORM models with full data schema  
✅ Pydantic schemas for type safety  
✅ FastAPI endpoints (templates, projects, runs, tasks, comments)  
✅ PostgreSQL migrations  
✅ Project templates (5 presets)  
✅ Redis event publishing  
✅ Environment configuration  

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- GitHub App credentials
- OpenAI API key

### Setup

```bash
# Clone repository
git clone https://github.com/softK1T/ai-software-company.git
cd ai-software-company

# Create environment file
cp .env.example .env
# Edit .env with your credentials

# Start services
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Seed templates
docker-compose exec backend python scripts/seed_templates.py

# Access
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
# PgAdmin: http://localhost:5050 (email: admin@example.com, password: admin)
```

## 📁 Project Structure

```
ai-software-company/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app
│   │   ├── config.py               # Settings
│   │   ├── api/                    # Endpoints
│   │   ├── core/                   # ORM models, schemas, database
│   │   ├── agents/                 # Agent logic
│   │   ├── workflow/               # LangGraph workflow
│   │   ├── github/                 # GitHub integration
│   │   └── utils/                  # Utilities
│   ├── workers/                    # Celery tasks
│   ├── migrations/                 # Alembic
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── pages/
│   ├── components/
│   ├── hooks/
│   ├── package.json
│   └── tsconfig.json
├── infra/
│   ├── docker-compose.yml
│   └── k8s/
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── SETUP.md
└── scripts/
    └── seed_templates.py
```

## 🔧 Configuration

### Project Templates

Templates control team composition, task count, review cycles, quality gates, and model allocation:

- **MVP Fast**: 3 agents, 20 tasks, minimal tests, quick turnaround
- **Startup Team**: 6 agents, 40 tasks, balanced quality/speed
- **API Quality-First**: 7 agents, 50 tasks, 80%+ coverage, strict security
- **Full-Stack App**: 8 agents, 70 tasks, UI + API + infra
- **Enterprise Strict**: 9 agents, 100 tasks, 85%+ coverage, all security gates

See `scripts/seed_templates.py` for full template specifications.

## 🔐 Security

- **GitHub App**: Minimal scopes, per-installation authentication
- **Environment Variables**: All secrets via `.env`, never committed
- **Audit Trail**: All actions timestamped and attributed
- **Security Specialist**: Automated SAST, DAST, dependency and secret scanning
- **SQL Injection Prevention**: Parameterized queries via SQLAlchemy ORM

## 📖 Documentation

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design and data flow
- [API.md](docs/API.md) - Complete API reference
- [SETUP.md](docs/SETUP.md) - Detailed setup and troubleshooting

## 📦 Stack

**Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic v2  
**Orchestration**: LangGraph, Celery, Redis  
**Database**: PostgreSQL 14+, Alembic  
**Frontend**: Next.js, React, TypeScript, WebSocket  
**DevOps**: Docker, Docker Compose  
**Git**: GitPython, GitHub REST API  

## 🗺️ Roadmap

- **Phase 1** ✅ Core infrastructure, models, endpoints
- **Phase 2** 🔄 Agent implementations, GitHub integration, Celery
- **Phase 3** ⏳ Frontend dashboard, WebSocket realtime, advanced monitoring
- **Phase 4** ⏳ Kubernetes, advanced security, cost optimization

## 🤝 Contributing

Branch strategy: `feature/{task_id}-{slug}` for features, `bugfix/{issue_id}-{slug}` for bugs.  
All PRs require code review and passing tests.

## 📄 License

MIT License - See LICENSE file for details

## 📧 Contact

For questions or contributions, open an issue or PR on GitHub.
