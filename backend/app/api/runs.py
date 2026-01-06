"""Project runs API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional
from uuid import uuid4
from datetime import datetime
from app.core.database import get_db
from app.core.models import Project, ProjectRun, Task, ProjectRunStatus
from app.core.schemas import ProjectRunResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/runs", tags=["Runs"])


@router.post("/projects/{project_id}/start", response_model=ProjectRunResponse, status_code=201)
async def start_run(
    project_id: str,
    db: Session = Depends(get_db),
) -> ProjectRunResponse:
    """Start a new run for a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get next run number
    last_run = db.query(func.max(ProjectRun.run_number)).filter(
        ProjectRun.project_id == project_id
    ).scalar() or 0
    run_number = last_run + 1

    # Create run with default config snapshot (in Phase 2, merge with template)
    new_run = ProjectRun(
        id=str(uuid4()),
        project_id=project_id,
        run_number=run_number,
        config_snapshot={
            "team": {"agents_count": 3, "roles_enabled": {"pm": 1, "dev": 1}},
            "planning": {"target_tasks": 20},
            "process": {"review_iterations": 1},
            "quality": {"complexity": "MVP"},
            "budget": {"max_usd": 2.0},
        },
        status=ProjectRunStatus.QUEUED,
    )
    db.add(new_run)
    db.commit()
    db.refresh(new_run)

    # Update project's active run
    project.active_run_id = new_run.id
    project.updated_at = datetime.utcnow()
    db.commit()

    logger.info(f"✅ Started run {run_number} for project {project.name} (run_id={new_run.id})")
    return ProjectRunResponse.model_validate(new_run)


@router.get("/{run_id}", response_model=ProjectRunResponse)
async def get_run(
    run_id: str,
    db: Session = Depends(get_db),
) -> ProjectRunResponse:
    """Get a specific run."""
    run = db.query(ProjectRun).filter(ProjectRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return ProjectRunResponse.model_validate(run)


@router.get("/{run_id}/summary")
async def get_run_summary(
    run_id: str,
    db: Session = Depends(get_db),
):
    """Get run summary with task counts and progress."""
    run = db.query(ProjectRun).filter(ProjectRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    # Count tasks by status
    task_counts = {
        "total": 0,
        "pending": 0,
        "in_progress": 0,
        "blocked": 0,
        "review": 0,
        "done": 0,
        "failed": 0,
    }

    tasks = db.query(Task).filter(Task.project_run_id == run_id).all()
    task_counts["total"] = len(tasks)
    for task in tasks:
        task_counts[task.status.value.lower()] = task_counts.get(task.status.value.lower(), 0) + 1

    progress_percent = 0
    if task_counts["total"] > 0:
        progress_percent = int((task_counts["done"] / task_counts["total"]) * 100)

    return {
        "run_id": run.id,
        "project_id": run.project_id,
        "run_number": run.run_number,
        "status": run.status.value,
        "task_counts": task_counts,
        "progress_percent": progress_percent,
        "budget_spent_usd_estimate": run.budget_spent_usd_estimate,
        "budget_spent_tokens": {
            "input": run.budget_spent_input_tokens,
            "output": run.budget_spent_output_tokens,
        },
        "started_at": run.started_at,
        "ended_at": run.ended_at,
    }


@router.patch("/{run_id}/status/{new_status}")
async def update_run_status(
    run_id: str,
    new_status: str,
    db: Session = Depends(get_db),
):
    """Update run status (RUNNING, PAUSED, STOPPED_MANUAL, etc)."""
    run = db.query(ProjectRun).filter(ProjectRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    try:
        run.status = ProjectRunStatus[new_status.upper()]
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Choose from: {', '.join([s.value for s in ProjectRunStatus])}"
        )

    if new_status.lower() == "running" and not run.started_at:
        run.started_at = datetime.utcnow()
    elif new_status.lower() in ["completed", "failed", "stopped_budget", "stopped_manual"]:
        run.ended_at = datetime.utcnow()

    db.commit()
    logger.info(f"✅ Updated run {run_id} status to {new_status}")
    return {"run_id": run_id, "status": run.status.value}
