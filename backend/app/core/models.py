"""SQLAlchemy ORM models for AI Software Company Platform."""
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey,
    Enum, JSONB, ARRAY, Index, UniqueConstraint, CheckConstraint, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from uuid import uuid4
from datetime import datetime
import enum

Base = declarative_base()


class ProjectStatus(str, enum.Enum):
    """Project lifecycle states."""
    DRAFT = "DRAFT"
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PAUSED = "PAUSED"


class ProjectRunStatus(str, enum.Enum):
    """Run execution states."""
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    STOPPED_BUDGET = "STOPPED_BUDGET"
    STOPPED_MANUAL = "STOPPED_MANUAL"


class TaskStatus(str, enum.Enum):
    """Task execution states."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    REVIEW = "REVIEW"
    DONE = "DONE"
    FAILED = "FAILED"


class TaskType(str, enum.Enum):
    """Task categories."""
    FEATURE = "FEATURE"
    BUGFIX = "BUGFIX"
    REFACTOR = "REFACTOR"
    TEST = "TEST"
    DOCS = "DOCS"
    DEVOPS = "DEVOPS"
    SECURITY = "SECURITY"
    CHORE = "CHORE"


class CommentType(str, enum.Enum):
    """Task comment classifications."""
    STATUS_UPDATE = "STATUS_UPDATE"
    PROGRESS = "PROGRESS"
    DECISION = "DECISION"
    BLOCKED = "BLOCKED"
    CODE_REVIEW = "CODE_REVIEW"
    TEST_REPORT = "TEST_REPORT"
    BUG_FOUND = "BUG_FOUND"
    SECURITY_REVIEW = "SECURITY_REVIEW"
    COMPLETED = "COMPLETED"
    QUESTION = "QUESTION"
    ANSWER = "ANSWER"


class ArtifactType(str, enum.Enum):
    """Artifact categories."""
    CODE = "CODE"
    TEST = "TEST"
    DOCS = "DOCS"
    CONFIG = "CONFIG"
    DOCKERFILE = "DOCKERFILE"
    MANIFEST = "MANIFEST"
    REPORT = "REPORT"


class Project(Base):
    """Represents a software project."""
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    requirements_text = Column(Text, nullable=True)
    status = Column(Enum(ProjectStatus), nullable=False, default=ProjectStatus.DRAFT, index=True)
    template_id = Column(String(36), ForeignKey("project_templates.id"), nullable=True)
    active_run_id = Column(String(36), ForeignKey("project_runs.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    runs = relationship("ProjectRun", back_populates="project", foreign_keys="ProjectRun.project_id")
    template = relationship("ProjectTemplate", foreign_keys=[template_id])

    __table_args__ = (
        Index("idx_project_status_created", "status", "created_at"),
    )


class ProjectRun(Base):
    """Represents a single execution of a project."""
    __tablename__ = "project_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    run_number = Column(Integer, nullable=False)
    config_snapshot = Column(JSONB, nullable=False)  # Immutable ProjectConfig copy
    status = Column(Enum(ProjectRunStatus), nullable=False, default=ProjectRunStatus.QUEUED, index=True)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    budget_spent_input_tokens = Column(Integer, nullable=False, default=0)
    budget_spent_output_tokens = Column(Integer, nullable=False, default=0)
    budget_spent_usd_estimate = Column(Float, nullable=False, default=0.0)
    final_report = Column(JSONB, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    project = relationship("Project", back_populates="runs", foreign_keys=[project_id])
    tasks = relationship("Task", back_populates="run")

    __table_args__ = (
        UniqueConstraint("project_id", "run_number", name="uq_project_run_number"),
        Index("idx_run_status_created", "status", "created_at"),
    )


class ProjectTemplate(Base):
    """Preset project configurations (immutable, versioned)."""
    __tablename__ = "project_templates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False, index=True)
    version = Column(String(20), nullable=False)  # semver
    description = Column(Text, nullable=True)
    tags = Column(ARRAY(String(50)), nullable=False, default=[])
    config_patch = Column(JSONB, nullable=False)  # Partial ProjectConfig overlay
    is_system = Column(Boolean, nullable=False, default=False, index=True)
    created_by_user_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("name", "version", name="uq_template_name_version"),
        Index("idx_template_is_system_created", "is_system", "created_at"),
    )


class Task(Base):
    """Represents a unit of work within a run."""
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    project_run_id = Column(String(36), ForeignKey("project_runs.id"), nullable=False, index=True)
    parent_task_id = Column(String(36), ForeignKey("tasks.id"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    task_type = Column(Enum(TaskType), nullable=False, default=TaskType.FEATURE, index=True)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.PENDING, index=True)
    priority = Column(Integer, nullable=False, default=5, index=True)  # 0-10
    assigned_agent_id = Column(String(100), nullable=True, index=True)  # e.g., "dev_agent_1"
    dependencies = Column(ARRAY(String(36)), nullable=False, default=[])  # task IDs
    acceptance_criteria = Column(JSONB, nullable=False, default=[])  # array of strings
    estimate_hours = Column(Float, nullable=True)
    actual_hours = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    run = relationship("ProjectRun", back_populates="tasks", foreign_keys=[project_run_id])
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")
    subtasks = relationship("Task", remote_side=[id], foreign_keys=[parent_task_id])

    __table_args__ = (
        Index("idx_task_status_assigned", "status", "assigned_agent_id"),
        Index("idx_task_run_priority", "project_run_id", "priority"),
    )


class TaskComment(Base):
    """Audit trail: agent actions with full context."""
    __tablename__ = "task_comments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False, index=True)
    agent_id = Column(String(100), nullable=False, index=True)  # e.g., "dev_agent_1"
    agent_role = Column(String(100), nullable=False, index=True)  # e.g., "Senior Developer"
    comment_type = Column(Enum(CommentType), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)  # Main narrative
    work_summary = Column(Text, nullable=True)
    approach = Column(Text, nullable=True)
    challenges = Column(ARRAY(Text), nullable=False, default=[])
    solutions = Column(ARRAY(Text), nullable=False, default=[])
    time_spent_hours = Column(Float, nullable=True)
    files_created = Column(ARRAY(String(500)), nullable=False, default=[])
    files_modified = Column(ARRAY(String(500)), nullable=False, default=[])
    git_commits = Column(ARRAY(String(40)), nullable=False, default=[])  # commit SHAs
    git_branch = Column(String(255), nullable=True)
    pr_url = Column(String(500), nullable=True)
    needs_review = Column(Boolean, nullable=False, default=False)
    confidence_level = Column(Integer, nullable=True)  # 0-100
    blockers = Column(ARRAY(Text), nullable=False, default=[])
    next_steps = Column(ARRAY(Text), nullable=False, default=[])
    metrics = Column(JSONB, nullable=False, default={})  # {coverage: 75.2, quality_score: 88, ...}
    vulnerabilities_found = Column(Integer, nullable=False, default=0)
    critical_issues = Column(ARRAY(Text), nullable=False, default=[])
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    task = relationship("Task", back_populates="comments", foreign_keys=[task_id])
    replies = relationship("CommentThreadReply", back_populates="root_comment", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_comment_type_agent", "comment_type", "agent_id"),
        Index("idx_comment_task_created", "task_id", "created_at"),
    )


class CommentThreadReply(Base):
    """Threaded replies to task comments."""
    __tablename__ = "comment_thread_replies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    root_comment_id = Column(String(36), ForeignKey("task_comments.id"), nullable=False, index=True)
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False, index=True)
    agent_id = Column(String(100), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    root_comment = relationship("TaskComment", back_populates="replies", foreign_keys=[root_comment_id])

    __table_args__ = (
        Index("idx_reply_root_created", "root_comment_id", "created_at"),
    )


class Artifact(Base):
    """Metadata for generated artifacts (code, tests, docs, configs)."""
    __tablename__ = "artifacts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False, index=True)
    artifact_type = Column(Enum(ArtifactType), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)  # Repo path
    language = Column(String(50), nullable=True)  # python, javascript, yaml, markdown, etc.
    git_commit_sha = Column(String(40), nullable=False)  # Commit that created/modified this
    created_by_agent_id = Column(String(100), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("idx_artifact_task_type", "task_id", "artifact_type"),
    )
