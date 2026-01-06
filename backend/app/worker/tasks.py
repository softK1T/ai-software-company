import logging
import asyncio
from app.worker.celery_app import celery_app
from app.core.database import SessionLocal
from app.agents.orchestrator import AgentOrchestrator
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

@celery_app.task(name="app.worker.tasks.execute_agent_task")
def execute_agent_task(task_id: str, run_id: str):
    """
    Celery task wrapper for executing an AI agent task.
    Uses async_to_sync to bridge Celery (sync) and Orchestrator (async).
    """
    logger.info(f"Received Celery task for TaskID: {task_id}, RunID: {run_id}")
    
    db = SessionLocal()
    try:
        orchestrator = AgentOrchestrator(db=db, run_id=run_id)
        
        # Run async logic synchronously
        async_to_sync(orchestrator.dispatch_task)(task_id)
        
    except Exception as e:
        logger.error(f"Error executing agent task {task_id}: {e}")
        # Mark task as FAILED in DB if possible
    finally:
        db.close()
