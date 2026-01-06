"""Tasks API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from uuid import uuid4
from datetime import datetime
from app.core.database import get_db
from app.core.models import Task, ProjectRun, TaskStatus, TaskType
from app.core.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
) -> TaskResponse:
    """Create a new task in a run (called by PM agent)."""
    # Verify run exists
    run = db.query(ProjectRun).filter(ProjectRun.id == task_data.project_run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Project run not found")

    # Verify parent task exists if specified
    if task_data.parent_task_id:
        parent = db.query(Task).filter(Task.id == task_data.parent_task_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent task not found")

    # Verify dependencies exist
    if task_data.dependencies:
        deps = db.query(Task).filter(Task.id.in_(task_data.dependencies)).all()
        if len(deps) != len(task_data.dependencies):
            raise HTTPException(status_code=404, detail="Some dependent tasks not found")

    new_task = Task(
        id=str(uuid4()),
        project_run_id=task_data.project_run_id,
        parent_task_id=task_data.parent_task_id,
        title=task_data.title,
        description=task_data.description,
        task_type=TaskType[task_data.task_type.upper()],
        status=TaskStatus.PENDING,
        priority=task_data.priority,
        dependencies=task_data.dependencies,
        acceptance_criteria=task_data.acceptance_criteria,
        estimate_hours=task_data.estimate_hours,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    logger.info(f"✅ Created task: {task_data.title} (id={new_task.id})")
    return TaskResponse.model_validate(new_task)


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    project_run_id: Optional[str] = Query(None, description="Filter by run"),
    status: Optional[str] = Query(None, description="Filter by status"),
    assigned_agent_id: Optional[str] = Query(None, description="Filter by assigned agent"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> TaskListResponse:
    """List tasks with optional filtering."""
    query = db.query(Task)

    if project_run_id:
        query = query.filter(Task.project_run_id == project_run_id)
    if status:
        try:
            status_enum = TaskStatus[status.upper()]
            query = query.filter(Task.status == status_enum)
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Choose from: {', '.join([s.value for s in TaskStatus])}"
            )
    if assigned_agent_id:
        query = query.filter(Task.assigned_agent_id == assigned_agent_id)

    total = query.count()
    tasks = query.order_by(desc(Task.priority), Task.created_at).offset(skip).limit(limit).all()

    return TaskListResponse(
        tasks=[TaskResponse.model_validate(t) for t in tasks],
        total=total,
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: Session = Depends(get_db),
) -> TaskResponse:
    """Get a specific task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    update_data: TaskUpdate,
    db: Session = Depends(get_db),
) -> TaskResponse:
    """Update task status, assignment, priority, or actual hours."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if update_data.status:
        try:
            task.status = TaskStatus[update_data.status.upper()]
            if update_data.status.upper() == "IN_PROGRESS" and not task.started_at:
                task.started_at = datetime.utcnow()
            elif update_data.status.upper() in ["DONE", "FAILED"] and not task.completed_at:
                task.completed_at = datetime.utcnow()
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Choose from: {', '.join([s.value for s in TaskStatus])}"
            )

    if update_data.assigned_agent_id is not None:
        task.assigned_agent_id = update_data.assigned_agent_id

    if update_data.priority is not None:
        task.priority = update_data.priority

    if update_data.actual_hours is not None:
        task.actual_hours = update_data.actual_hours

    db.commit()
    db.refresh(task)

    logger.info(f"✅ Updated task: {task.title}")
    return TaskResponse.model_validate(task)


@router.get("/{task_id}/subtasks", response_model=TaskListResponse)
async def get_subtasks(
    task_id: str,
    db: Session = Depends(get_db),
) -> TaskListResponse:
    """Get all subtasks of a parent task."""
    parent = db.query(Task).filter(Task.id == task_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Task not found")

    subtasks = db.query(Task).filter(Task.parent_task_id == task_id).all()
    return TaskListResponse(
        tasks=[TaskResponse.model_validate(t) for t in subtasks],
        total=len(subtasks),
    )
