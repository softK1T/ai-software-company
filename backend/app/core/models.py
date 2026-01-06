from datetime import datetime
from enum import Enum
from typing import Optional, List, Any
import uuid

from sqlalchemy import (
    Column, 
    String, 
    Boolean, 
    DateTime, 
    ForeignKey, 
    Integer, 
    Text, 
    Enum as SQLEnum,
    ARRAY,
    Float
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

# Enums
class ProjectStatus(str, Enum):
    DRAFT = "DRAFT"
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    STOPPED_BUDGET = "STOPPED_BUDGET"
    STOPPED_MANUAL = "STOPPED_MANUAL"
    PAUSED = "PAUSED"

class ProjectRunStatus(str, Enum):
    STARTING = "STARTING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    STOPPED = "STOPPED"

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    REVIEW = "REVIEW"
    DONE = "DONE"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"

class TaskType(str, Enum):
    PLANNING = "PLANNING"
    CODING = "CODING"
    TESTING = "TESTING"
    REVIEW = "REVIEW"
    DEVOPS = "DEVOPS"
    DOCUMENTATION = "DOCUMENTATION"
    SECURITY = "SECURITY"

class CommentType(str, Enum):
    PROGRESS = "PROGRESS"
    BLOCKER = "BLOCKER"
    REVIEW = "REVIEW"
    DECISION = "DECISION"
    SYSTEM = "SYSTEM"

class ProjectTemplate(Base):
    __tablename__ = "project_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    version = Column(String, nullable=False)  # semver
    description = Column(Text)
    tags = Column(ARRAY(String))
    
    # Configuration override to apply on top of default
    config_patch = Column(JSONB, default=dict)
    
    is_system = Column(Boolean, default=False)
    created_by_user_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    projects = relationship("Project", back_populates="template")

class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    requirements_text = Column(Text)
    
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.DRAFT)
    
    template_id = Column(UUID(as_uuid=True), ForeignKey("project_templates.id"))
    template = relationship("ProjectTemplate", back_populates="projects")
    
    # Active run pointer
    # Fix: use_alter must be inside ForeignKey, not Column
    active_run_id = Column(UUID(as_uuid=True), ForeignKey("project_runs.id", use_alter=True), nullable=True)
    
    runs = relationship("ProjectRun", back_populates="project", foreign_keys="[ProjectRun.project_id]")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ProjectRun(Base):
    __tablename__ = "project_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    run_number = Column(Integer, nullable=False)
    
    # Snapshot of full configuration at start time
    config_snapshot = Column(JSONB, nullable=False)
    
    status = Column(SQLEnum(ProjectRunStatus), default=ProjectRunStatus.STARTING)
    
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    # Budget tracking
    budget_spent_usd = Column(Float, default=0.0)
    tokens_used = Column(Integer, default=0)
    
    # Result
    final_report = Column(JSONB, nullable=True)

    project = relationship("Project", back_populates="runs", foreign_keys=[project_id])
    tasks = relationship("Task", back_populates="run", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_run_id = Column(UUID(as_uuid=True), ForeignKey("project_runs.id"))
    
    # Tree structure
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    
    # Fix: Explicit relationship definition to avoid "too many values to unpack" error with nested relationship() calls
    subtasks = relationship("Task", back_populates="parent_task", cascade="all, delete-orphan")
    parent_task = relationship("Task", remote_side=[id], back_populates="subtasks")
    
    title = Column(String, nullable=False)
    description = Column(Text)
    task_type = Column(SQLEnum(TaskType), nullable=False)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING)
    
    priority = Column(Integer, default=5) # 0-10
    
    # Agent assignment
    assigned_agent_id = Column(String, nullable=True)
    
    # Dependencies (other task IDs)
    dependencies = Column(ARRAY(UUID(as_uuid=True)), default=list)
    
    acceptance_criteria = Column(ARRAY(Text))
    
    estimate_hours = Column(Float, nullable=True)
    actual_hours = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    run = relationship("ProjectRun", back_populates="tasks")
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")
    artifacts = relationship("Artifact", back_populates="task", cascade="all, delete-orphan")

class TaskComment(Base):
    """
    Audit trail of agent work. Every significant action creates a comment.
    """
    __tablename__ = "task_comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))
    
    agent_id = Column(String, nullable=False)
    agent_role = Column(String, nullable=False)
    comment_type = Column(SQLEnum(CommentType), default=CommentType.PROGRESS)
    
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False) # Full narrative
    
    # Structured Work Log
    work_summary = Column(Text, nullable=True)
    approach = Column(Text, nullable=True)
    challenges = Column(ARRAY(Text), default=list)
    solutions = Column(ARRAY(Text), default=list)
    
    # Metrics
    time_spent_hours = Column(Float, default=0.0)
    files_created = Column(ARRAY(String), default=list)
    files_modified = Column(ARRAY(String), default=list)
    
    # Git
    git_commits = Column(ARRAY(String), default=list)
    git_branch = Column(String, nullable=True)
    pr_url = Column(String, nullable=True)
    
    # State
    needs_review = Column(Boolean, default=False)
    confidence_level = Column(Integer, default=100) # 0-100
    
    blockers = Column(ARRAY(Text), default=list)
    next_steps = Column(ARRAY(Text), default=list)
    
    # JSONB for extra metadata (coverage, lint score, etc)
    metrics = Column(JSONB, default=dict)
    
    # Security findings
    vulnerabilities_found = Column(Integer, default=0)
    critical_issues = Column(ARRAY(Text), default=list)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    task = relationship("Task", back_populates="comments")
    replies = relationship("CommentThreadReply", back_populates="root_comment", cascade="all, delete-orphan")

class CommentThreadReply(Base):
    """Replies to a main comment thread"""
    __tablename__ = "comment_thread_replies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    root_comment_id = Column(UUID(as_uuid=True), ForeignKey("task_comments.id"))
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id")) # Denormalized for query speed
    
    agent_id = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    root_comment = relationship("TaskComment", back_populates="replies")

class Artifact(Base):
    """Outputs produced by tasks (files, diagrams, etc)"""
    __tablename__ = "artifacts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))
    
    artifact_type = Column(String, nullable=False) # code, diagram, document
    file_path = Column(String, nullable=False)
    language = Column(String, nullable=True)
    
    git_commit_sha = Column(String, nullable=True)
    
    created_by_agent_id = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    task = relationship("Task", back_populates="artifacts")
