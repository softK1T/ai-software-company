# ... (imports)
from app.core.database import SessionLocal
from app.worker.tasks import execute_agent_task
# ... (router def)

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db)
):
    """Create a new task manually."""
    run = db.query(ProjectRun).filter(ProjectRun.id == task_in.project_run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
        
    new_task = Task(
        id=uuid4(),
        project_run_id=task_in.project_run_id,
        parent_task_id=task_in.parent_task_id,
        title=task_in.title,
        description=task_in.description,
        task_type=task_in.task_type,
        priority=task_in.priority,
        dependencies=task_in.dependencies,
        acceptance_criteria=task_in.acceptance_criteria,
        estimate_hours=task_in.estimate_hours,
        status="PENDING"
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # Trigger async execution via Celery
    execute_agent_task.delay(str(new_task.id), str(new_task.project_run_id))
    
    return new_task

@router.get("", response_model=TaskListResponse)
async def list_tasks(
    run_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List tasks for a specific run."""
    query = db.query(Task).filter(Task.project_run_id == run_id)
    total = query.count()
    tasks = query.order_by(Task.created_at.asc()).offset(skip).limit(limit).all()
    
    return TaskListResponse(
        tasks=tasks,
        total=total
    )

@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_in: TaskUpdate,
    db: Session = Depends(get_db)
):
    """Update task status or assignment."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
        
    db.commit()
    db.refresh(task)
    return task
