"""Task comments API endpoints (audit trail)."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from uuid import uuid4
from app.core.database import get_db
from app.core.models import Task, TaskComment, CommentType
from app.core.schemas import (
    TaskCommentCreate,
    TaskCommentResponse,
    TaskCommentListResponse,
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/tasks/{task_id}/comments", tags=["Comments"])


@router.post("", response_model=TaskCommentResponse, status_code=201)
async def create_comment(
    task_id: str,
    comment_data: TaskCommentCreate,
    db: Session = Depends(get_db),
) -> TaskCommentResponse:
    """Create a task comment (agent audit trail entry)."""
    # Verify task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Validate comment type
    try:
        comment_type = CommentType[comment_data.comment_type.upper()]
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid comment_type. Choose from: {', '.join([c.value for c in CommentType])}"
        )

    new_comment = TaskComment(
        id=str(uuid4()),
        task_id=task_id,
        agent_id=comment_data.agent_id,
        agent_role=comment_data.agent_role,
        comment_type=comment_type,
        title=comment_data.title,
        content=comment_data.content,
        work_summary=comment_data.work_summary,
        approach=comment_data.approach,
        challenges=comment_data.challenges,
        solutions=comment_data.solutions,
        time_spent_hours=comment_data.time_spent_hours,
        files_created=comment_data.files_created,
        files_modified=comment_data.files_modified,
        git_commits=comment_data.git_commits,
        git_branch=comment_data.git_branch,
        pr_url=comment_data.pr_url,
        needs_review=comment_data.needs_review,
        confidence_level=comment_data.confidence_level,
        blockers=comment_data.blockers,
        next_steps=comment_data.next_steps,
        metrics=comment_data.metrics,
        vulnerabilities_found=comment_data.vulnerabilities_found,
        critical_issues=comment_data.critical_issues,
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    logger.info(f"✅ Created comment on task {task_id}: {comment_data.title} (agent={comment_data.agent_id})")
    return TaskCommentResponse.model_validate(new_comment)


@router.get("", response_model=TaskCommentListResponse)
async def list_comments(
    task_id: str,
    comment_type: Optional[str] = Query(None, description="Filter by comment type"),
    agent_id: Optional[str] = Query(None, description="Filter by agent"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> TaskCommentListResponse:
    """List comments for a task with optional filtering."""
    # Verify task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    query = db.query(TaskComment).filter(TaskComment.task_id == task_id)

    if comment_type:
        try:
            ct = CommentType[comment_type.upper()]
            query = query.filter(TaskComment.comment_type == ct)
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid comment_type. Choose from: {', '.join([c.value for c in CommentType])}"
            )

    if agent_id:
        query = query.filter(TaskComment.agent_id == agent_id)

    total = query.count()
    comments = query.order_by(desc(TaskComment.created_at)).offset(skip).limit(limit).all()

    return TaskCommentListResponse(
        comments=[TaskCommentResponse.model_validate(c) for c in comments],
        total=total,
    )


@router.get("/{comment_id}", response_model=TaskCommentResponse)
async def get_comment(
    task_id: str,
    comment_id: str,
    db: Session = Depends(get_db),
) -> TaskCommentResponse:
    """Get a specific comment."""
    comment = db.query(TaskComment).filter(
        TaskComment.id == comment_id,
        TaskComment.task_id == task_id,
    ).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return TaskCommentResponse.model_validate(comment)
