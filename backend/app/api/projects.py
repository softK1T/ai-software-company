from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import uuid4
from app.core.database import get_db
from app.core.models import Project, ProjectTemplate
from app.core.schemas import ProjectCreate, ProjectResponse, ProjectListResponse

router = APIRouter(prefix="/api/projects", tags=["Projects"])

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db)
):
    """Create a new project from a template or scratch."""
    # Validate template if provided
    if project_in.template_id:
        template = db.query(ProjectTemplate).filter(ProjectTemplate.id == project_in.template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
            
    # Check name uniqueness
    existing = db.query(Project).filter(Project.name == project_in.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Project with this name already exists")
        
    new_project = Project(
        id=uuid4(),
        name=project_in.name,
        description=project_in.description,
        requirements_text=project_in.requirements_text,
        template_id=project_in.template_id,
        # config_overrides handled later during Run creation
    )
    
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@router.get("", response_model=ProjectListResponse)
async def list_projects(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List all projects."""
    total = db.query(Project).count()
    projects = db.query(Project).order_by(Project.updated_at.desc()).offset(skip).limit(limit).all()
    
    return ProjectListResponse(
        projects=projects,
        total=total
    )

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Get project details."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
