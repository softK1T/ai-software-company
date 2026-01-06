# ... (imports)
from app.core.database import SessionLocal
from app.worker.tasks import execute_agent_task
# ... (router def)

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db)
):
    """Create a new task and optionally schedule execution."""
    # ... (existing creation logic) ...
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    # NEW: Schedule task if it's ready (Phase 2)
    if new_task.status == "PENDING":
        # Send to Celery
        execute_agent_task.delay(str(new_task.id), str(new_task.project_run_id))
        
    return new_task
