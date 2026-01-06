import logging
import asyncio
from typing import Dict, Any, List
from app.core.models import Task, Project, ProjectRun
from app.core.schemas import TaskUpdate
from app.agents.personas import AGENTS, AgentRole
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """
    Manages the lifecycle of AI agents execution.
    Handles context switching, state management, and tool execution.
    """
    
    def __init__(self, db: Session, run_id: str):
        self.db = db
        self.run_id = run_id
        
    async def dispatch_task(self, task_id: str):
        """
        Assigns a task to the appropriate agent and executes it.
        """
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            logger.error(f"Task {task_id} not found")
            return

        # Determine required role based on task type
        role = self._map_task_type_to_role(task.task_type)
        persona = AGENTS[role]
        
        logger.info(f"Dispatching Task '{task.title}' to Agent {persona.name} ({role})")
        
        # Update task status
        task.status = "IN_PROGRESS"
        task.assigned_agent_id = persona.name
        self.db.commit()
        
        # EXECUTION LOGIC (Placeholder for LLM call)
        # In real implementation, this would call OpenAI/Anthropic API
        # with persona.system_prompt + task.description
        
        # Simulate work
        await asyncio.sleep(2) 
        
        # For now, just mark as done to test flow
        task.status = "DONE"
        self.db.commit()
        logger.info(f"Task '{task.title}' completed by {persona.name}")

    def _map_task_type_to_role(self, task_type: str) -> AgentRole:
        mapping = {
            "PLANNING": AgentRole.PM,
            "CODING": AgentRole.DEV,
            "TESTING": AgentRole.QA,
            "REVIEW": AgentRole.LEAD,
            "DEVOPS": AgentRole.DEVOPS,
            "SECURITY": AgentRole.SECURITY,
            "DOCUMENTATION": AgentRole.DEV
        }
        return mapping.get(task_type, AgentRole.DEV)

    async def run_next_pending_task(self):
        """Finds the next pending task with satisfied dependencies."""
        # Simple FIFO logic for Phase 2 MVP
        task = self.db.query(Task).filter(
            Task.project_run_id == self.run_id,
            Task.status == "PENDING"
        ).first()
        
        if task:
            await self.dispatch_task(str(task.id))
