"""Audit log endpoints."""
from fastapi import APIRouter, HTTPException
from typing import Optional

from core.database import db

router = APIRouter()


@router.get("/audit")
async def get_audit_log(
    agent_name: Optional[str] = None,
    entity_id: Optional[str] = None,
    limit: int = 100
):
    """Get audit log with optional filters."""
    try:
        query = """
            SELECT *
            FROM audit_log
            WHERE ($1::text IS NULL OR agent_name = $1)
              AND ($2::uuid IS NULL OR entity_id = $2)
            ORDER BY created_at DESC
            LIMIT $3
        """
        logs = await db.fetch(query, agent_name, entity_id, limit)
        return {"audit_log": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
