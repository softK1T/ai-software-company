# 🤖 AI Software Company Platform

> **Phase 1: Core Infrastructure** ✅ Complete

An autonomous platform where AI agents build entire software projects from requirements to deployment.

## 🎯 What is This?

Describe your project idea, and a team of AI agents will:
- Decompose requirements into tasks
- Write code, tests, and documentation
- Create Docker configurations
- Set up CI/CD pipelines
- Review each other's work
- Deploy to production

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌───────────────┐
│   React     │─────▶│   FastAPI    │─────▶│  PostgreSQL   │
│  Frontend   │      │   Backend    │      │   Database    │
└─────────────┘      └──────────────┘      └───────────────┘
     (Port 80)            (Port 8000)           (Port 5432)
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### 1. Clone and Start

```bash
git clone https://github.com/softK1T/ai-software-company.git
cd ai-software-company
git checkout phase-1-core-infrastructure

# Start all services
docker-compose up -d

# Wait for services to initialize (30 seconds)
sleep 30

# Check health
curl http://localhost:8000/health
```

### 2. Access the Platform

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: `localhost:5432` (user: `aicompany`, password: `dev_password_change_in_prod`)

### 3. Run Seed Data (Optional)

The platform automatically seeds 3 default templates on startup:
- **MVP Fast Track** - Quick prototyping
- **Standard Web App** - Production-grade applications  
- **Data Pipeline** - ETL/ELT projects

To re-run manually:
```bash
docker-compose exec backend python -m app.core.seed
```

## 📚 API Examples

### List Templates
```bash
curl http://localhost:8000/api/templates
```

### Create a Project
```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-rest-api",
    "description": "User management API",
    "requirements_text": "Build a REST API with:\n- User CRUD operations\n- JWT authentication\n- PostgreSQL database\n- Docker deployment"
  }'
```

### Get Projects
```bash
curl http://localhost:8000/api/projects
```

## 🛠️ Development

### Project Structure
```
.
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Models, database, config
│   │   └── main.py       # FastAPI app
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/          # API client
│   │   ├── pages/        # React pages
│   │   └── App.tsx
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Database Migrations
```bash
# Connect to database
docker-compose exec db psql -U aicompany -d aicompany

# List tables
\dt

# Describe table
\d project_templates
```

## 🧪 Testing

### Backend Tests
```bash
docker-compose exec backend pytest
```

### API Testing with HTTPie
```bash
# Install httpie
pip install httpie

# Test endpoints
http :8000/health
http :8000/api/templates
```

## 📊 Phase 1 Features

✅ **Core Infrastructure**
- PostgreSQL database with SQLAlchemy ORM
- FastAPI REST API with auto-generated docs
- React + TypeScript frontend with Tailwind CSS
- Docker Compose orchestration
- CORS configuration
- Health check endpoints

✅ **Data Models**
- Project Templates (MVP, Standard, Data Pipeline)
- Projects
- Project Runs
- Tasks (hierarchical)
- Task Comments (audit trail)
- Artifacts

✅ **API Endpoints**
- `GET /api/templates` - List all templates
- `POST /api/templates` - Create template
- `GET /api/projects` - List projects
- `POST /api/projects` - Create project
- `GET /health` - Health check

✅ **Frontend Pages**
- Templates list with filtering
- Project creation form
- Responsive design

## 🔮 Next Steps (Phase 2)

- [ ] AI Agent System (PM, Lead Dev, Dev, QA, DevOps, Security)
- [ ] LLM Integration (OpenAI/Anthropic)
- [ ] Task Decomposition Engine
- [ ] Code Generation Pipeline
- [ ] GitHub Integration
- [ ] Real-time Progress Tracking
- [ ] Budget Management

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

MIT License - see LICENSE file for details

## 👨‍💻 Author

**Nazar Zhyliuk** ([@softK1T](https://github.com/softK1T))

Data Engineer building the future of autonomous software development.

---

**Current Status**: Phase 1 Complete ✅ | Next: Phase 2 - AI Agent System 🚀
