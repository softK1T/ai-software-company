"""Project templates API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import uuid4
from app.core.database import get_db
from app.core.models import ProjectTemplate
from app.core.schemas import (
    ProjectTemplateCreate,
    ProjectTemplateResponse,
    ProjectTemplateListResponse,
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/templates", tags=["Templates"])


@router.post("", response_model=ProjectTemplateResponse, status_code=201)
async def create_template(
    template: ProjectTemplateCreate,
    db: Session = Depends(get_db),
) -> ProjectTemplateResponse:
    """Create a new project template.
    
    Templates are immutable; create new versions instead.
    """
    # Check if template with same name/version exists
    existing = db.query(ProjectTemplate).filter(
        ProjectTemplate.name == template.name,
        ProjectTemplate.version == template.version,
    ).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Template '{template.name}' version '{template.version}' already exists"
        )

    new_template = ProjectTemplate(
        id=str(uuid4()),
        name=template.name,
        version=template.version,
        description=template.description,
        tags=template.tags,
        config_patch=template.config_patch,
        is_system=template.is_system,
        created_by_user_id=template.created_by_user_id,
    )
    db.add(new_template)
    db.commit()
    db.refresh(new_template)

    logger.info(f"✅ Created template: {template.name} v{template.version}")
    return ProjectTemplateResponse.from_attributes(new_template)


@router.get("", response_model=ProjectTemplateListResponse)
async def list_templates(
    tag: Optional[str] = Query(None, description="Filter by tag"),
    is_system: Optional[bool] = Query(None, description="Filter by system templates"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> ProjectTemplateListResponse:
    """List project templates with optional filtering."""
    query = db.query(ProjectTemplate)

    if tag:
        query = query.filter(ProjectTemplate.tags.contains([tag]))
    if is_system is not None:
        query = query.filter(ProjectTemplate.is_system == is_system)

    total = query.count()
    templates = query.order_by(ProjectTemplate.created_at.desc()).offset(skip).limit(limit).all()

    return ProjectTemplateListResponse(
        templates=[ProjectTemplateResponse.from_attributes(t) for t in templates],
        total=total,
    )


@router.get("/{template_id}", response_model=ProjectTemplateResponse)
async def get_template(
    template_id: str,
    db: Session = Depends(get_db),
) -> ProjectTemplateResponse:
    """Get a specific project template."""
    template = db.query(ProjectTemplate).filter(ProjectTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return ProjectTemplateResponse.from_attributes(template)


@router.get("/by-name/{name}", response_model=List[ProjectTemplateResponse])
async def get_template_by_name(
    name: str,
    db: Session = Depends(get_db),
) -> List[ProjectTemplateResponse]:
    """Get all versions of a template by name (ordered by version descending)."""
    templates = db.query(ProjectTemplate).filter(
        ProjectTemplate.name == name
    ).order_by(ProjectTemplate.version.desc()).all()
    
    if not templates:
        raise HTTPException(status_code=404, detail=f"No templates found with name '{name}'")
    
    return [ProjectTemplateResponse.from_attributes(t) for t in templates]
