# ... (imports)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import uuid4
from app.core.database import get_db
from app.core.models import ProjectRun, Project
from app.core.schemas import ProjectRunCreate, ProjectRunResponse
# NEW: Import for PM kickoff
from app.core.models import Task
from app.worker.tasks import execute_agent_task

router = APIRouter(prefix="/api/runs", tags=["Runs"])

@router.post("", response_model=ProjectRunResponse, status_code=status.HTTP_201_CREATED)
async def create_run(
    project_id: str,
    run_in: ProjectRunCreate,
    db: Session = Depends(get_db)
):
    """Start a new run and trigger PM Planning."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    last_run = db.query(ProjectRun).filter(ProjectRun.project_id == project_id)\
                 .order_by(ProjectRun.run_number.desc()).first()
    next_run_number = (last_run.run_number + 1) if last_run else 1
    
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
    
    project.active_run_id = new_run.id
    db.commit()
    
    # NEW: Create Initial Planning Task for PM Agent
    pm_task = Task(
        id=uuid4(),
        project_run_id=new_run.id,
        title="Initial Project Planning",
        description=f"Analyze requirements for project '{project.name}' and decompose into development tasks.\n\nRequirements:\n{project.requirements_text}",
        task_type="PLANNING",
        priority=0,
        status="PENDING"
    )
    db.add(pm_task)
    db.commit()
    
    # Trigger execution
    execute_agent_task.delay(str(pm_task.id), str(new_run.id))
    
    return new_run

@router.get("/{run_id}", response_model=ProjectRunResponse)
async def get_run(run_id: str, db: Session = Depends(get_db)):
    """Get run details."""
    run = db.query(ProjectRun).filter(ProjectRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
