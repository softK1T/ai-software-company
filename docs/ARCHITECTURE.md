# AI Software Company Platform - Architecture

## Overview

The AI Software Company Platform is a sophisticated multi-agent orchestration system built on:

- **LangGraph**: State machine for agent coordination
- **FastAPI**: High-performance REST API with async support
- **PostgreSQL**: Persistent storage with JSONB for flexible configs
- **Redis**: Real-time pub/sub and caching
- **Celery**: Distributed task execution

## Core Concepts

### Project Lifecycle

```
┌─────────┐     ┌────────┐     ┌────────┐     ┌────────┐     ┌──────────┐
│  DRAFT  │────▶│ READY  │────▶│ RUNNING│────▶│COMPLETED│     │  FAILED  │
└─────────┘     └────────┘     └────────┘     └──────────┘     └──────────┘
                                    │
                                    ▼
                             (Pause/Resume)
```

### Run Execution Flow

```
QUEUED → RUNNING → COMPLETED/FAILED/STOPPED_*
```

### Agent Roles

| Role | Responsibilities | Models |
|------|------------------|--------|
| **PM** | Requirements analysis, task decomposition, planning | gpt-4o / o3 |
| **Dev Lead** | Code review, architectural guidance, mentoring | gpt-4o |
| **Developer** | Feature implementation, testing, commits | gpt-4o-mini |
| **QA** | Test strategy, test execution, bug reporting | gpt-4o-mini |
| **Docs** | Documentation, ADRs, runbooks | gpt-4o-mini |
| **DevOps** | Infrastructure, CI/CD, containerization | gpt-4o |
| **Security** | SAST, DAST, scanning, compliance | gpt-4o |

## Data Model

### Core Entities

```
┌──────────────┐
│   Project    │
└──────────────┘
       │
       │ 1:N
       ▼
┌──────────────┐      ┌──────────────┐
│ ProjectRun   │     │    Config    │ (JSONB)
└──────────────┘      └──────────────┘
       │
       │ 1:N
       ▼
┌──────────────┐
│     Task     │ (tree structure: parent_task_id)
└──────────────┘
       │
       │ 1:N
       ▼
┌──────────────┐
│  TaskComment │ (audit trail)
└──────────────┘
       │
       │ 1:N
       ▼
┌──────────────┐
│    Reply     │ (threaded)
└──────────────┘
```

### Key Tables

- **projects**: Metadata, status, active run
- **project_runs**: Immutable config snapshot, token tracking, final report
- **project_templates**: Versioned presets (immutable)
- **tasks**: Decomposed work units, dependencies, acceptance criteria
- **task_comments**: Full audit trail with metrics, blockers, next steps
- **artifacts**: Metadata for generated code/docs/configs

## API Architecture

### Endpoint Groups

```
/api/templates      - Template management (CRUD)
/api/projects       - Project management (CRUD)
/api/runs           - Run lifecycle (start, pause, resume, status)
/api/tasks          - Task management (create, update, list)
/api/comments       - Audit trail (create, list, thread replies)
```

### Request/Response Pattern

- **Input**: Pydantic models (v2) with validation
- **Output**: Standardized JSON with timestamps
- **Errors**: Consistent error structure with 4xx/5xx status codes
- **Pagination**: `skip` and `limit` for list endpoints

## Workflow (LangGraph)

### Phase 1 Structure (Skeleton)

```
start
  │
  ├─▶ pm_analyze_requirements
  ├─▶ pm_create_tasks
  ├─▶ bootstrap_github_repo (Phase 2)
  ├─▶ dev_work_cycle (Phase 2)
  ├─▶ lead_review_cycle (Phase 2)
  ├─▶ qa_test_cycle (Phase 2)
  ├─▶ security_scan_cycle (Phase 2)
  ├─▶ docs_finalize (Phase 2)
  ├─▶ devops_prepare (Phase 2)
  ├─▶ final_decision
  │
  └─▶ end
```

### Conditional Routing

```
if budget_exceeded && on_exceed=="stop":
  → STOPPED_BUDGET

if security_findings && gate=="block_critical":
  → back to fix_cycle

if review_iterations_remaining > 0 && issues_found:
  → back to fix_cycle

else:
  → next_node
```

## Database Design

### Indexing Strategy

```sql
-- Query patterns
INDEX idx_project_status_created (status, created_at)
INDEX idx_run_status_created (status, created_at)
INDEX idx_task_status_assigned (status, assigned_agent_id)
INDEX idx_comment_type_agent (comment_type, agent_id)
INDEX idx_comment_task_created (task_id, created_at)
```

### JSONB Strategy

- **config_snapshot**: Immutable at run creation (no queries on this)
- **config_patch**: Template overlay (rarely queried)
- **metrics**: Agent reports (no queries, just storage)
- **acceptance_criteria**: Task requirements (no queries)

## Security Architecture

### Auth (Phase 2)

- GitHub App for Git operations (minimal OAuth scopes)
- Optional JWT for API consumers
- No secrets in repo (use environment variables)

### SAST/DAST (Phase 2)

- Static analysis on code commits
- Dynamic testing on running services
- Dependency scanning (requirements.txt, package.json)
- Secret scanning (regex + entropy detection)
- Docker image scanning

## Deployment

### Local Development

```bash
docker-compose up -d
# Starts: postgres, redis, backend, pgadmin (optional)
```

### Production (Phase 3)

- Kubernetes manifests (Deployment, Service, ConfigMap, Secret)
- Horizontal Pod Autoscaling (HPA)
- Prometheus metrics
- Grafana dashboards
- ELK stack for logging

## Scalability

### Horizontal

- **Stateless backend**: Multiple FastAPI replicas behind load balancer
- **Distributed workers**: Celery workers on separate nodes
- **Shared Redis**: Pub/sub for realtime updates across replicas

### Vertical

- **Connection pooling**: PostgreSQL with PgBouncer
- **Caching**: Redis with intelligent TTLs
- **Async I/O**: Uvicorn with multiple workers

## Monitoring & Observability

### Logs

- JSON structured logging (python-json-logger)
- Correlation IDs for request tracing
- Agent action tracking in TaskComment

### Metrics

- Token usage per agent/role
- Task completion times
- Budget burn rate
- PR review cycles
- Security gate violations

### Tracing

- Request IDs propagated through workflow
- Agent decision points logged with rationale
- Cost attribution per agent/run
