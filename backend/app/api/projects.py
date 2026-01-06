"""Projects API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from uuid import uuid4
from datetime import datetime
from app.core.database import get_db
from app.core.models import Project, ProjectRun, ProjectTemplate, ProjectStatus
from app.core.schemas import (
    ProjectCreate,
    ProjectResponse,
    ProjectListResponse,
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/projects", tags=["Projects"])


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
) -> ProjectResponse:
    """Create a new project."""
    # Check if project with same name exists
    existing = db.query(Project).filter(Project.name == project_data.name).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Project '{project_data.name}' already exists"
        )

    # Verify template exists if specified
    if project_data.template_id:
        template = db.query(ProjectTemplate).filter(
            ProjectTemplate.id == project_data.template_id
        ).first()
        if not template:
            raise HTTPException(
                status_code=404,
                detail=f"Template '{project_data.template_id}' not found"
            )

    new_project = Project(
        id=str(uuid4()),
        name=project_data.name,
        description=project_data.description,
        requirements_text=project_data.requirements_text,
        status=ProjectStatus.DRAFT,
        template_id=project_data.template_id,
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    logger.info(f"✅ Created project: {project_data.name} (id={new_project.id})")
    return ProjectResponse.model_validate(new_project)


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> ProjectListResponse:
    """List projects with optional filtering."""
    query = db.query(Project)

    if status:
        try:
            status_enum = ProjectStatus[status.upper()]
            query = query.filter(Project.status == status_enum)
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Choose from: {', '.join([s.value for s in ProjectStatus])}"
            )

    total = query.count()
    projects = query.order_by(desc(Project.created_at)).offset(skip).limit(limit).all()

    return ProjectListResponse(
        projects=[ProjectResponse.model_validate(p) for p in projects],
        total=total,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: Session = Depends(get_db),
) -> ProjectResponse:
    """Get a specific project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse.model_validate(project)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
) -> ProjectResponse:
    """Update project metadata."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if name and name != project.name:
        # Check uniqueness
        existing = db.query(Project).filter(Project.name == name).first()
        if existing:
            raise HTTPException(status_code=409, detail=f"Project name '{name}' already exists")
        project.name = name

    if description is not None:
        project.description = description

    if status:
        try:
            project.status = ProjectStatus[status.upper()]
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Choose from: {', '.join([s.value for s in ProjectStatus])}"
            )

    project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(project)

    logger.info(f"✅ Updated project: {project.name}")
    return ProjectResponse.model_validate(project)


@router.get("/{project_id}/runs")
async def get_project_runs(
    project_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Get all runs for a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    total = db.query(ProjectRun).filter(ProjectRun.project_id == project_id).count()
    runs = db.query(ProjectRun).filter(
        ProjectRun.project_id == project_id
    ).order_by(desc(ProjectRun.created_at)).offset(skip).limit(limit).all()

    return {
        "runs": [{
            "id": r.id,
            "run_number": r.run_number,
            "status": r.status.value,
            "started_at": r.started_at,
            "ended_at": r.ended_at,
            "budget_spent_usd_estimate": r.budget_spent_usd_estimate,
            "created_at": r.created_at,
        } for r in runs],
        "total": total,
    }
