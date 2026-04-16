"""Team member endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
import structlog

from core.database import db
from core.embeddings import generate_skill_embedding

logger = structlog.get_logger()

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
        # Return empty list if database is not available
        return {"team_members": []}


@router.post("/team")
async def create_team_member(member: TeamMemberCreate):
    """Add a new team member with skill embedding."""
    try:
        member_id = str(uuid.uuid4())
        
        # Generate skill embedding for vector search
        skill_embedding = await generate_skill_embedding(member.skills)
        
        if skill_embedding:
            embedding_str = "[" + ",".join(str(x) for x in skill_embedding) + "]"
            query = """
                INSERT INTO team_members (id, name, email, role, skills, availability_hours_per_week, skill_embedding)
                VALUES ($1, $2, $3, $4, $5, $6, $7::vector)
                RETURNING id, name, email, role, skills, availability_hours_per_week, current_load_hours, created_at
            """
            result = await db.fetchrow(
                query,
                member_id,
                member.name,
                member.email,
                member.role,
                member.skills,
                member.availability_hours_per_week,
                embedding_str,
            )
            logger.info("Team member created with skill embedding", member=member.name)
        else:
            query = """
                INSERT INTO team_members (id, name, email, role, skills, availability_hours_per_week)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id, name, email, role, skills, availability_hours_per_week, current_load_hours, created_at
            """
            result = await db.fetchrow(
                query,
                member_id,
                member.name,
                member.email,
                member.role,
                member.skills,
                member.availability_hours_per_week,
            )
            logger.warning("Team member created WITHOUT embedding", member=member.name)
        
        return {"team_member": dict(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/team/{member_id}")
async def get_team_member(member_id: str):
    """Get team member details with current tasks."""
    try:
        member_query = """
            SELECT id, name, email, role, skills, 
                   current_load_hours, availability_hours_per_week, created_at
            FROM team_members WHERE id = $1
        """
        member = await db.fetchrow(member_query, member_id)
        
        if not member:
            raise HTTPException(status_code=404, detail="Team member not found")
        
        tasks_query = """
            SELECT t.id, t.title, t.description, t.status, 
                   t.estimated_hours, t.due_date, t.risk_score,
                   p.name as project_name
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


@router.put("/team/{member_id}/refresh-embedding")
async def refresh_member_embedding(member_id: str):
    """Regenerate skill embedding for a team member."""
    try:
        # Get member skills
        member = await db.fetchrow(
            "SELECT id, name, skills FROM team_members WHERE id = $1",
            member_id
        )
        
        if not member:
            raise HTTPException(status_code=404, detail="Team member not found")
        
        # Generate new embedding
        embedding = await generate_skill_embedding(member["skills"])
        
        if not embedding:
            raise HTTPException(status_code=500, detail="Failed to generate embedding")
        
        embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
        
        await db.execute(
            "UPDATE team_members SET skill_embedding = $2::vector WHERE id = $1",
            member_id,
            embedding_str,
        )
        
        logger.info("Embedding refreshed", member=member["name"])
        return {"success": True, "member": member["name"], "embedding_dimensions": len(embedding)}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/team/refresh-all-embeddings")
async def refresh_all_embeddings():
    """Regenerate skill embeddings for all team members."""
    try:
        members = await db.fetch("SELECT id, name, skills FROM team_members")
        
        results = []
        for member in members:
            try:
                embedding = await generate_skill_embedding(member["skills"])
                
                if embedding:
                    embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
                    await db.execute(
                        "UPDATE team_members SET skill_embedding = $2::vector WHERE id = $1",
                        member["id"],
                        embedding_str,
                    )
                    results.append({"name": member["name"], "status": "success"})
                    logger.info("Embedding refreshed", member=member["name"])
                else:
                    results.append({"name": member["name"], "status": "failed"})
                    
            except Exception as e:
                results.append({"name": member["name"], "status": f"error: {str(e)}"})
        
        success_count = sum(1 for r in results if r["status"] == "success")
        return {
            "total": len(members),
            "success": success_count,
            "failed": len(members) - success_count,
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
