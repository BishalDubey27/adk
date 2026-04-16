"""
Project management endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
import uuid

from core.database import db
from agents.execution_coordinator import ExecutionCoordinator

router = APIRouter()


class ProjectCreate(BaseModel):
    """Request model for creating a project."""
    name: str
    description: str
    priority: str = "medium"
    deadline: str
    required_skills: Optional[List[str]] = None
    team_size: Optional[int] = 3


class ProjectResponse(BaseModel):
    """Response model for project."""
    id: str
    name: str
    description: Optional[str]
    status: str
    priority: str
    deadline: Optional[str]
    confidence_score: Optional[float]
    created_at: str


@router.post("/projects")
async def create_project(project: ProjectCreate):
    """
    Create a new project and trigger AI agent pipeline.
    """
    try:
        # Initialize execution coordinator
        coordinator = ExecutionCoordinator()
        
        # Prepare context for agents
        context = {
            "user_request": {
                "name": project.name,
                "description": project.description,
                "priority": project.priority,
                "deadline": project.deadline,
                "required_skills": project.required_skills or [],
                "team_size": project.team_size
            }
        }
        
        # Run agent pipeline
        result = await coordinator.run(context)
        
        # Extract project data
        project_data = result.data["agent_results"]["intake"]
        tasks_data = result.data["agent_results"]["planning"]["tasks"]
        assignments = result.data["agent_results"]["staffing"]["assignments"]
        
        # Insert project into database
        project_id = str(uuid.uuid4())
        
        insert_query = """
            INSERT INTO projects (id, name, description, status, priority, deadline, confidence_score)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id, name, description, status, priority, deadline, confidence_score, created_at
        """
        
        project_row = await db.fetchrow(
            insert_query,
            project_id,
            project.name,
            project.description,
            "active" if result.data["action"] != "escalate" else "escalated",
            project.priority,
            project.deadline,
            result.confidence
        )
        
        # Insert tasks
        task_ids = []
        for task in tasks_data:
            task_id = str(uuid.uuid4())
            task_ids.append(task_id)
            
            # Find assignment for this task
            assignment = next(
                (a for a in assignments if a["task_id"] == task["task_id"]),
                None
            )
            
            task_insert = """
                INSERT INTO tasks (id, project_id, title, description, status, estimated_hours, assigned_to)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """
            
            await db.execute(
                task_insert,
                task_id,
                project_id,
                task["title"],
                f"Phase: {task.get('phase', 'N/A')}",
                "todo",
                task["estimated_hours"],
                assignment["assigned_to"] if assignment else None
            )
        
        # If escalated, create escalation record
        if result.data["action"] == "escalate":
            escalation_id = str(uuid.uuid4())
            escalation_insert = """
                INSERT INTO escalations (id, project_id, agent_name, reason, confidence_score, suggested_action, status)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """
            
            await db.execute(
                escalation_insert,
                escalation_id,
                project_id,
                "execution_coordinator",
                result.escalation_reason or "Low confidence score",
                result.confidence,
                result.data,
                "pending"
            )
        
        # Log to audit trail
        audit_id = str(uuid.uuid4())
        audit_insert = """
            INSERT INTO audit_log (id, agent_name, action, entity_type, entity_id, confidence_score, output_data)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        """
        
        await db.execute(
            audit_insert,
            audit_id,
            "execution_coordinator",
            "project_created",
            "project",
            project_id,
            result.confidence,
            result.data
        )
        
        return {
            "success": True,
            "project": dict(project_row),
            "confidence": result.confidence,
            "action": result.data["action"],
            "reasoning": result.reasoning,
            "tasks_created": len(task_ids)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects")
async def list_projects():
    """List all projects."""
    try:
        query = """
            SELECT id, name, description, status, priority, deadline, confidence_score, created_at
            FROM projects
            ORDER BY created_at DESC
        """
        
        projects = await db.fetch(query)
        return {"projects": projects}
        
    except Exception as e:
        # Return empty list if database is not available
        return {"projects": []}


@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Get project details with tasks."""
    try:
        # Get project
        project_query = """
            SELECT id, name, description, status, priority, deadline, confidence_score, created_at
            FROM projects
            WHERE id = $1
        """
        
        project = await db.fetchrow(project_query, project_id)
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get tasks
        tasks_query = """
            SELECT t.id, t.title, t.description, t.status, t.estimated_hours, 
                   t.actual_hours, t.due_date, t.risk_score,
                   tm.name as assigned_to_name, tm.id as assigned_to_id
            FROM tasks t
            LEFT JOIN team_members tm ON t.assigned_to = tm.id
            WHERE t.project_id = $1
            ORDER BY t.created_at
        """
        
        tasks = await db.fetch(tasks_query, project_id)
        
        return {
            "project": dict(project),
            "tasks": tasks
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/projects/{project_id}")
async def update_project(project_id: str, status: Optional[str] = None):
    """Update project status."""
    try:
        update_query = """
            UPDATE projects
            SET status = COALESCE($2, status), updated_at = now()
            WHERE id = $1
            RETURNING id, name, status
        """
        
        result = await db.fetchrow(update_query, project_id, status)
        
        if not result:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {"project": dict(result)}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Archive a project."""
    try:
        delete_query = """
            UPDATE projects
            SET status = 'archived', updated_at = now()
            WHERE id = $1
            RETURNING id
        """
        
        result = await db.fetchrow(delete_query, project_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {"success": True, "message": "Project archived"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
