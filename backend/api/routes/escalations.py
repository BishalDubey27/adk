"""Escalation queue endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.database import db

router = APIRouter()


class EscalationDecision(BaseModel):
    decision: str  # approve, reject, override
    reviewed_by: str


@router.get("/escalations")
async def list_escalations(status: str = "pending"):
    """List escalations by status."""
    try:
        query = """
            SELECT e.*, p.name as project_name
            FROM escalations e
            LEFT JOIN projects p ON e.project_id = p.id
            WHERE e.status = $1
            ORDER BY e.created_at DESC
        """
        escalations = await db.fetch(query, status)
        return {"escalations": escalations}
    except Exception as e:
        # Return empty list if database is not available
        return {"escalations": []}


@router.get("/escalations/{escalation_id}")
async def get_escalation(escalation_id: str):
    """Get escalation details."""
    try:
        query = """
            SELECT e.*, p.name as project_name
            FROM escalations e
            LEFT JOIN projects p ON e.project_id = p.id
            WHERE e.id = $1
        """
        escalation = await db.fetchrow(query, escalation_id)
        
        if not escalation:
            raise HTTPException(status_code=404, detail="Escalation not found")
        
        return {"escalation": dict(escalation)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/escalations/{escalation_id}/approve")
async def approve_escalation(escalation_id: str, decision: EscalationDecision):
    """Approve an escalation."""
    try:
        query = """
            UPDATE escalations
            SET status = $2, reviewed_by = $3, reviewed_at = now()
            WHERE id = $1
            RETURNING *
        """
        result = await db.fetchrow(query, escalation_id, decision.decision, decision.reviewed_by)
        
        if not result:
            raise HTTPException(status_code=404, detail="Escalation not found")
        
        return {"escalation": dict(result)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
