from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import uuid4
from app.core.database import get_db
from app.core.models import ProjectRun, Project
from app.core.schemas import ProjectRunCreate, ProjectRunResponse

router = APIRouter(prefix="/api/runs", tags=["Runs"])

@router.post("", response_model=ProjectRunResponse, status_code=status.HTTP_201_CREATED)
async def create_run(
    project_id: str,
    run_in: ProjectRunCreate,
    db: Session = Depends(get_db)
):
    """Start a new run for a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Calculate run number
    last_run = db.query(ProjectRun).filter(ProjectRun.project_id == project_id)\
                 .order_by(ProjectRun.run_number.desc()).first()
    next_run_number = (last_run.run_number + 1) if last_run else 1
    
    # Merge configs (Template + Project overrides + Run overrides)
    # This is a simplified logic, real implementation needs deep merge
    final_config = {} 
    if project.template:
        final_config.update(project.template.config_patch or {})
    if run_in.config_overrides:
        final_config.update(run_in.config_overrides)
        
    new_run = ProjectRun(
        id=uuid4(),
        project_id=project_id,
        run_number=next_run_number,
        config_snapshot=final_config,
        status="STARTING"
    )
    
    db.add(new_run)
    db.commit()
    db.refresh(new_run)
    
    # Update active run
    project.active_run_id = new_run.id
    db.commit()
    
    return new_run

@router.get("/{run_id}", response_model=ProjectRunResponse)
async def get_run(run_id: str, db: Session = Depends(get_db)):
    """Get run details."""
    run = db.query(ProjectRun).filter(ProjectRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
