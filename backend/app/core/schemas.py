"""Pydantic request/response schemas."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum


# ============================================================================
# ProjectTemplate Schemas
# ============================================================================

class ProjectTemplateCreate(BaseModel):
    """Create a new project template."""
    name: str = Field(..., min_length=1, max_length=255)
    version: str = Field(..., min_length=5, max_length=20)  # semver
    description: Optional[str] = Field(None, max_length=1000)
    tags: List[str] = Field(default_factory=list, max_items=10)
    config_patch: Dict[str, Any] = Field(...)
    is_system: bool = Field(default=False)
    created_by_user_id: Optional[str] = Field(None, max_length=36)

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "MVP Fast",
            "version": "1.0.0",
            "tags": ["quick", "prototype"],
            "config_patch": {
                "team": {"agents_count": 3, "roles_enabled": {"pm": 1, "dev": 1}},
                "quality": {"complexity": "MVP", "min_test_coverage": 0.5}
            },
            "is_system": True
        }
    })


class ProjectTemplateResponse(ProjectTemplateCreate):
    """Project template response."""
    id: str
    created_at: datetime
    updated_at: datetime


class ProjectTemplateListResponse(BaseModel):
    """List of project templates."""
    templates: List[ProjectTemplateResponse]
    total: int


# ============================================================================
# ProjectConfig Schemas
# ============================================================================

class ProjectConfigTeam(BaseModel):
    """Team configuration."""
    agents_count: int = Field(3, ge=1, le=20)
    roles_enabled: Dict[str, int] = Field(default_factory=dict)
    max_parallel_tasks: int = Field(5, ge=1, le=50)


class ProjectConfigPlanning(BaseModel):
    """Planning configuration."""
    target_tasks: int = Field(40, ge=10, le=500)
    max_task_depth: int = Field(3, ge=1, le=10)
    decomposition_style: str = Field("feature-first", pattern="^(feature-first|component-first)$")


class ProjectConfigProcess(BaseModel):
    """Process configuration."""
    review_iterations: int = Field(3, ge=1, le=5)
    require_pr_for_tasks: bool = Field(True)
    merge_policy: str = Field("lead_approve_and_green_tests")
    comment_policy: str = Field("standard", pattern="^(minimal|standard|strict)$")


class ProjectConfigQuality(BaseModel):
    """Quality gates configuration."""
    complexity: str = Field("STANDARD", pattern="^(MVP|STANDARD|ENTERPRISE)$")
    min_test_coverage: float = Field(0.70, ge=0.0, le=1.0)
    require_docs: bool = Field(True)
    require_ci: bool = Field(True)
    require_docker: bool = Field(True)
    require_k8s: bool = Field(False)
    security: Dict[str, Any] = Field(default_factory=dict)


class ProjectConfigBudget(BaseModel):
    """Budget configuration."""
    max_usd: float = Field(3.0, ge=0.1)
    max_total_tokens: int = Field(100000, ge=10000)
    on_exceed: str = Field("degrade_models", pattern="^(stop|degrade_models)$")


class ProjectConfig(BaseModel):
    """Complete project configuration (snapshot)."""
    team: ProjectConfigTeam
    planning: ProjectConfigPlanning
    process: ProjectConfigProcess
    quality: ProjectConfigQuality
    models: Dict[str, Any] = Field(default_factory=dict)
    github: Dict[str, Any] = Field(default_factory=dict)
    budget: ProjectConfigBudget
    security: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")


# ============================================================================
# Project Schemas
# ============================================================================

class ProjectCreate(BaseModel):
    """Create a new project."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    requirements_text: str = Field(..., min_length=10, max_length=10000)
    template_id: Optional[str] = Field(None, max_length=36)
    config_overrides: Optional[Dict[str, Any]] = Field(None)


class ProjectResponse(BaseModel):
    """Project response."""
    id: str
    name: str
    description: Optional[str]
    requirements_text: str
    status: str
    template_id: Optional[str]
    active_run_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    """List of projects."""
    projects: List[ProjectResponse]
    total: int


# ============================================================================
# ProjectRun Schemas
# ============================================================================

class ProjectRunCreate(BaseModel):
    """Start a new project run."""
    config_overrides: Optional[Dict[str, Any]] = Field(None)


class ProjectRunResponse(BaseModel):
    """Project run response."""
    id: str
    project_id: str
    run_number: int
    status: str
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    budget_spent_input_tokens: int
    budget_spent_output_tokens: int
    budget_spent_usd_estimate: float
    final_report: Optional[Dict[str, Any]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Task Schemas
# ============================================================================

class TaskCreate(BaseModel):
    """Create a task (used by PM agent)."""
    project_run_id: str
    parent_task_id: Optional[str] = None
    title: str = Field(..., min_length=5, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    task_type: str = Field("FEATURE")
    priority: int = Field(5, ge=0, le=10)
    dependencies: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    estimate_hours: Optional[float] = Field(None, ge=0.5)


class TaskUpdate(BaseModel):
    """Update task status, assignment, priority."""
    status: Optional[str] = None
    assigned_agent_id: Optional[str] = None
    priority: Optional[int] = Field(None, ge=0, le=10)
    actual_hours: Optional[float] = Field(None, ge=0)


class TaskResponse(BaseModel):
    """Task response."""
    id: str
    project_run_id: str
    parent_task_id: Optional[str]
    title: str
    description: Optional[str]
    task_type: str
    status: str
    priority: int
    assigned_agent_id: Optional[str]
    dependencies: List[str]
    acceptance_criteria: List[str]
    estimate_hours: Optional[float]
    actual_hours: Optional[float]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    """List of tasks."""
    tasks: List[TaskResponse]
    total: int


# ============================================================================
# TaskComment Schemas
# ============================================================================

class TaskCommentCreate(BaseModel):
    """Create a task comment (agent audit trail)."""
    agent_id: str = Field(..., max_length=100)
    agent_role: str = Field(..., max_length=100)
    comment_type: str  # CommentType enum value
    title: str = Field(..., min_length=5, max_length=255)
    content: str = Field(..., min_length=10, max_length=50000)
    work_summary: Optional[str] = Field(None, max_length=5000)
    approach: Optional[str] = Field(None, max_length=5000)
    challenges: List[str] = Field(default_factory=list, max_items=20)
    solutions: List[str] = Field(default_factory=list, max_items=20)
    time_spent_hours: Optional[float] = Field(None, ge=0)
    files_created: List[str] = Field(default_factory=list, max_items=100)
    files_modified: List[str] = Field(default_factory=list, max_items=100)
    git_commits: List[str] = Field(default_factory=list, max_items=50)  # SHAs
    git_branch: Optional[str] = Field(None, max_length=255)
    pr_url: Optional[str] = Field(None, max_length=500)
    needs_review: bool = Field(False)
    confidence_level: Optional[int] = Field(None, ge=0, le=100)
    blockers: List[str] = Field(default_factory=list, max_items=20)
    next_steps: List[str] = Field(default_factory=list, max_items=20)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    vulnerabilities_found: int = Field(0, ge=0)
    critical_issues: List[str] = Field(default_factory=list, max_items=50)


class TaskCommentResponse(TaskCommentCreate):
    """Task comment response."""
    id: str
    task_id: str
    created_at: datetime
    updated_at: datetime


class TaskCommentListResponse(BaseModel):
    """List of task comments."""
    comments: List[TaskCommentResponse]
    total: int
