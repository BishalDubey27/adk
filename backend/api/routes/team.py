"""Team member endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import uuid

from core.database import db

router = APIRouter()


class TeamMemberCreate(BaseModel):
    name: str
    email: str
    role: str
    skills: List[str]
    availability_hours_per_week: int = 40


@router.get("/team")
async def list_team_members():
    """List all team members."""
    try:
        query = """
            SELECT id, name, email, role, skills, 
                   current_load_hours, availability_hours_per_week, created_at
            FROM team_members
            ORDER BY name
        """
        members = await db.fetch(query)
        return {"team_members": members}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/team")
async def create_team_member(member: TeamMemberCreate):
    """Add a new team member."""
    try:
        member_id = str(uuid.uuid4())
        query = """
            INSERT INTO team_members (id, name, email, role, skills, availability_hours_per_week)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *
        """
        result = await db.fetchrow(
            query,
            member_id,
            member.name,
            member.email,
            member.role,
            member.skills,
            member.availability_hours_per_week
        )
        return {"team_member": dict(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/team/{member_id}")
async def get_team_member(member_id: str):
    """Get team member details with current tasks."""
    try:
        member_query = """
            SELECT * FROM team_members WHERE id = $1
        """
        member = await db.fetchrow(member_query, member_id)
        
        if not member:
            raise HTTPException(status_code=404, detail="Team member not found")
        
        tasks_query = """
            SELECT t.*, p.name as project_name
            FROM tasks t
            JOIN projects p ON t.project_id = p.id
            WHERE t.assigned_to = $1 AND t.status != 'done'
            ORDER BY t.due_date
        """
        tasks = await db.fetch(tasks_query, member_id)
        
        return {
            "team_member": dict(member),
            "active_tasks": tasks
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
