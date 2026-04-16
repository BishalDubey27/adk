"""Task management endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from core.database import db

router = APIRouter()


class TaskUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    actual_hours: Optional[int] = None


@router.get("/projects/{project_id}/tasks")
async def get_project_tasks(project_id: str):
    """Get all tasks for a project."""
    try:
        query = """
            SELECT t.*, tm.name as assigned_to_name
            FROM tasks t
            LEFT JOIN team_members tm ON t.assigned_to = tm.id
            WHERE t.project_id = $1
            ORDER BY t.created_at
        """
        tasks = await db.fetch(query, project_id)
        return {"tasks": tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/tasks/{task_id}")
async def update_task(task_id: str, update: TaskUpdate):
    """Update task status or assignment."""
    try:
        query = """
            UPDATE tasks
            SET status = COALESCE($2, status),
                assigned_to = COALESCE($3, assigned_to),
                actual_hours = COALESCE($4, actual_hours),
                updated_at = now()
            WHERE id = $1
            RETURNING *
        """
        result = await db.fetchrow(
            query, task_id, update.status, update.assigned_to, update.actual_hours
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {"task": dict(result)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
