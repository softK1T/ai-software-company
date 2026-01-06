# API Reference

## Base URL

```
http://localhost:8000/api
```

## Authentication

Currently: None (Phase 2 will add GitHub App OAuth)

## Status Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Validation error
- `404 Not Found` - Resource not found
- `409 Conflict` - Duplicate or conflict
- `500 Internal Server Error` - Server error

---

## Templates

### List Templates

```http
GET /templates?tag=startup&is_system=true&skip=0&limit=50
```

**Query Parameters:**
- `tag` (optional): Filter by tag
- `is_system` (optional): Filter by system templates
- `skip` (default: 0): Pagination offset
- `limit` (default: 50, max: 500): Results per page

**Response:**
```json
{
  "templates": [
    {
      "id": "uuid",
      "name": "MVP Fast",
      "version": "1.0.0",
      "description": "Quick prototype...",
      "tags": ["quick", "prototype"],
      "is_system": true,
      "created_at": "2024-01-06T20:00:00"
    }
  ],
  "total": 5
}
```

### Get Template

```http
GET /templates/{template_id}
```

**Response:** Single template object

### Create Template

```http
POST /templates
Content-Type: application/json

{
  "name": "Custom Template",
  "version": "1.0.0",
  "description": "...",
  "tags": ["custom"],
  "config_patch": {
    "team": {"agents_count": 5},
    "quality": {"complexity": "STANDARD"}
  },
  "is_system": false
}
```

**Response:** (201) Created template object

---

## Projects

### Create Project

```http
POST /projects
Content-Type: application/json

{
  "name": "My Project",
  "description": "A new project",
  "requirements_text": "Build a user management system...",
  "template_id": "uuid" (optional),
  "config_overrides": {} (optional)
}
```

### List Projects

```http
GET /projects?status=RUNNING&skip=0&limit=50
```

**Query Parameters:**
- `status` (optional): DRAFT | READY | RUNNING | COMPLETED | FAILED | PAUSED
- `skip`, `limit`: Pagination

### Get Project

```http
GET /projects/{project_id}
```

### Update Project

```http
PATCH /projects/{project_id}
Content-Type: application/json

{
  "name": "Updated Name" (optional),
  "description": "..." (optional),
  "status": "READY" (optional)
}
```

### Get Project Runs

```http
GET /projects/{project_id}/runs?skip=0&limit=50
```

---

## Runs

### Start Run

```http
POST /runs/projects/{project_id}/start
```

**Response:**
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "run_number": 1,
  "status": "QUEUED",
  "config_snapshot": {},
  "budget_spent_usd_estimate": 0.0,
  "created_at": "..."
}
```

### Get Run

```http
GET /runs/{run_id}
```

### Get Run Summary

```http
GET /runs/{run_id}/summary
```

**Response:**
```json
{
  "run_id": "uuid",
  "status": "RUNNING",
  "task_counts": {
    "total": 45,
    "done": 12,
    "in_progress": 5,
    "pending": 28
  },
  "progress_percent": 27,
  "budget_spent_usd_estimate": 2.45
}
```

### Update Run Status

```http
PATCH /runs/{run_id}/status/{new_status}
```

**Values:**
- QUEUED, RUNNING, COMPLETED, FAILED, STOPPED_BUDGET, STOPPED_MANUAL

---

## Tasks

### Create Task

```http
POST /tasks
Content-Type: application/json

{
  "project_run_id": "uuid",
  "parent_task_id": null (optional),
  "title": "Implement user authentication",
  "description": "...",
  "task_type": "FEATURE",
  "priority": 7,
  "dependencies": [],
  "acceptance_criteria": ["Login works", "Token validation"],
  "estimate_hours": 8.0
}
```

### List Tasks

```http
GET /tasks?project_run_id=uuid&status=IN_PROGRESS&assigned_agent_id=dev_agent_1&skip=0&limit=100
```

### Get Task

```http
GET /tasks/{task_id}
```

### Update Task

```http
PATCH /tasks/{task_id}
Content-Type: application/json

{
  "status": "IN_PROGRESS" (optional),
  "assigned_agent_id": "dev_agent_1" (optional),
  "priority": 8 (optional),
  "actual_hours": 6.5 (optional)
}
```

### Get Subtasks

```http
GET /tasks/{task_id}/subtasks
```

---

## Comments (Audit Trail)

### Create Comment

```http
POST /tasks/{task_id}/comments
Content-Type: application/json

{
  "agent_id": "dev_agent_1",
  "agent_role": "Senior Developer",
  "comment_type": "PROGRESS",
  "title": "Authentication module implementation started",
  "content": "Detailed work narrative...",
  "work_summary": "Set up user model and JWT strategy",
  "approach": "Using FastAPI built-in security utilities",
  "challenges": ["Password hashing library choice"],
  "solutions": ["Selected bcrypt for industry standard"],
  "files_created": ["app/models/user.py", "app/security/jwt.py"],
  "files_modified": ["app/main.py"],
  "git_commits": ["abc123def456"],
  "git_branch": "feature/auth-module",
  "pr_url": "https://github.com/...",
  "blockers": [],
  "next_steps": ["Implement token refresh", "Add test suite"],
  "metrics": {"lines_added": 450, "coverage": 0.75},
  "confidence_level": 85
}
```

### List Comments

```http
GET /tasks/{task_id}/comments?comment_type=PROGRESS&agent_id=dev_agent_1&skip=0&limit=100
```

### Get Comment

```http
GET /tasks/{task_id}/comments/{comment_id}
```

---

## Error Responses

```json
{
  "detail": "Project 'My Project' already exists",
  "error_type": "ValueError"
}
```

## Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "ai-software-company",
  "version": "0.1.0"
}
```
