"""
Staffing Agent - Match tasks to team members using semantic skill search.

Uses AlloyDB pgvector for cosine similarity search when embeddings are available,
with a keyword-matching fallback for local development.
"""
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentResult
from core.database import db
from core.embeddings import generate_task_embedding

import structlog

logger = structlog.get_logger()


class StaffingAgent(BaseAgent):
    """Match tasks to best available team member using vector similarity."""
    
    name = "staffing"
    
    async def run(self, context: Dict[str, Any]) -> AgentResult:
        """
        Assign tasks to team members based on skill match and availability.
        
        Args:
            context: Must contain 'tasks' list and optionally 'team_members'
            
        Returns:
            AgentResult with task assignments
        """
        tasks = context.get("tasks", [])
        
        # Get team members from database or context
        team_members = await self._get_team_members(context)
        
        if not team_members:
            return AgentResult(
                success=False,
                confidence=0.0,
                data={"assignments": []},
                reasoning="No team members available for assignment",
                escalation_reason="No team members in database"
            )
        
        # Assign each task
        assignments = []
        total_confidence = 0.0
        
        for task in tasks:
            assignment = await self._assign_task(task, team_members)
            assignments.append(assignment)
            total_confidence += assignment["confidence"]
        
        # Calculate overall confidence
        avg_confidence = total_confidence / len(tasks) if tasks else 0.0
        
        # Build reasoning
        reasoning = self._build_reasoning(assignments)
        
        # Check for escalation
        escalation_reason = None
        low_confidence_count = sum(1 for a in assignments if a["confidence"] < 0.6)
        if low_confidence_count > len(tasks) * 0.3:
            escalation_reason = f"{low_confidence_count} tasks have low-confidence assignments"
        
        return AgentResult(
            success=True,
            confidence=avg_confidence,
            data={"assignments": assignments},
            reasoning=reasoning,
            escalation_reason=escalation_reason
        )
    
    async def _get_team_members(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get team members from database or context."""
        if "team_members" in context:
            return context["team_members"]
        
        try:
            # Query from database
            query = """
                SELECT id, name, email, role, skills, 
                       current_load_hours, availability_hours_per_week,
                       skill_embedding
                FROM team_members
                WHERE current_load_hours < availability_hours_per_week * 0.9
                ORDER BY current_load_hours ASC
            """
            members = await db.fetch(query)
            return members
        except Exception:
            # Return mock data for development
            return self._get_mock_team_members()
    
    def _get_mock_team_members(self) -> List[Dict[str, Any]]:
        """Mock team members for development."""
        return [
            {
                "id": "1",
                "name": "Sahil Prajapati",
                "email": "sahil@techsarathi.com",
                "role": "Full Stack Developer",
                "skills": ["Python", "React", "FastAPI", "PostgreSQL"],
                "current_load_hours": 20,
                "availability_hours_per_week": 40,
                "skill_embedding": None
            },
            {
                "id": "2",
                "name": "Amit Yadav",
                "email": "amit@techsarathi.com",
                "role": "AI/ML Engineer",
                "skills": ["Python", "TensorFlow", "AI", "Machine Learning"],
                "current_load_hours": 15,
                "availability_hours_per_week": 40,
                "skill_embedding": None
            },
            {
                "id": "3",
                "name": "Khush Patel",
                "email": "khush@techsarathi.com",
                "role": "Frontend Developer",
                "skills": ["React", "TypeScript", "UI/UX", "Tailwind"],
                "current_load_hours": 25,
                "availability_hours_per_week": 40,
                "skill_embedding": None
            },
            {
                "id": "4",
                "name": "Bishal Dubey",
                "email": "bishal@techsarathi.com",
                "role": "Backend Developer",
                "skills": ["Python", "FastAPI", "Database", "Cloud"],
                "current_load_hours": 10,
                "availability_hours_per_week": 40,
                "skill_embedding": None
            }
        ]
    
    async def _assign_task(
        self, 
        task: Dict[str, Any], 
        team_members: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assign a single task to the best team member."""
        task_title = task.get("title", "")
        task_desc = f"{task_title} {task.get('phase', '')}"
        
        # Try vector similarity search first
        vector_result = await self._find_best_match_vector(task_title, task_desc, task.get("phase", ""))
        
        if vector_result:
            return self._build_assignment(task, vector_result)
        
        # Fall back to keyword matching
        logger.debug("Falling back to keyword matching for task assignment", task=task_title)
        return self._assign_task_keyword(task, team_members)
    
    async def _find_best_match_vector(
        self,
        title: str,
        description: str,
        phase: str
    ) -> Optional[Dict[str, Any]]:
        """Find the best team member match using vector similarity search."""
        try:
            # Generate embedding for the task
            task_embedding = await generate_task_embedding(title, description, phase)
            
            if task_embedding is None:
                return None
            
            # Query AlloyDB with pgvector cosine similarity
            results = await db.vector_search(
                embedding=task_embedding,
                table="team_members",
                column="skill_embedding",
                limit=5,
                where_clause="AND current_load_hours < availability_hours_per_week * 0.9",
            )
            
            if not results:
                return None
            
            # Return the best match with similarity score
            best = results[0]
            logger.info(
                "Vector match found",
                task=title,
                member=best.get("name"),
                similarity=round(best.get("similarity", 0), 3),
            )
            return best
            
        except Exception as e:
            logger.warning(f"Vector search failed, will use keyword fallback: {e}")
            return None
    
    def _build_assignment(
        self,
        task: Dict[str, Any],
        member: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build assignment result from a vector search match."""
        similarity = member.get("similarity", 0.0)
        
        # Calculate confidence from similarity + availability
        confidence = self._calculate_assignment_confidence(similarity, member)
        
        return {
            "task_id": task.get("task_id"),
            "task_title": task.get("title", ""),
            "assigned_to": member["id"],
            "assigned_to_name": member["name"],
            "match_score": round(similarity, 3),
            "match_method": "vector_similarity",
            "confidence": confidence,
            "reasoning": (
                f"Vector similarity match ({round(similarity, 2)}) with "
                f"{round(member['current_load_hours']/member['availability_hours_per_week']*100, 0)}% current load"
            )
        }
    
    def _assign_task_keyword(
        self,
        task: Dict[str, Any],
        team_members: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assign a task using keyword matching (fallback)."""
        task_title = task.get("title", "")
        task_desc = f"{task_title} {task.get('phase', '')}".lower()
        
        # Calculate match scores for each team member
        candidates = []
        for member in team_members:
            score = self._calculate_match_score(task_desc, member)
            candidates.append({
                "member": member,
                "score": score
            })
        
        # Sort by score
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        if not candidates:
            return {
                "task_id": task.get("task_id"),
                "task_title": task_title,
                "assigned_to": None,
                "confidence": 0.0,
                "match_method": "none",
                "reasoning": "No suitable team member found"
            }
        
        # Select best candidate
        best = candidates[0]
        member = best["member"]
        
        # Calculate confidence
        confidence = self._calculate_assignment_confidence(best["score"], member)
        
        return {
            "task_id": task.get("task_id"),
            "task_title": task_title,
            "assigned_to": member["id"],
            "assigned_to_name": member["name"],
            "match_score": round(best["score"], 2),
            "match_method": "keyword",
            "confidence": confidence,
            "reasoning": f"Keyword match ({round(best['score'], 2)}) with {round(member['current_load_hours']/member['availability_hours_per_week']*100, 0)}% current load"
        }
    
    def _calculate_match_score(
        self, 
        task_desc: str, 
        member: Dict[str, Any]
    ) -> float:
        """Calculate skill match score (simplified keyword matching)."""
        skills = [s.lower() for s in member.get("skills", [])]
        
        # Count skill keyword matches
        matches = sum(1 for skill in skills if skill in task_desc)
        
        if not skills:
            return 0.0
        
        # Base score from keyword matches
        base_score = matches / len(skills)
        
        # Boost for specific matches
        if "frontend" in task_desc or "ui" in task_desc:
            if any(s in skills for s in ["react", "frontend", "ui/ux"]):
                base_score += 0.3
        
        if "backend" in task_desc or "api" in task_desc:
            if any(s in skills for s in ["python", "fastapi", "backend"]):
                base_score += 0.3
        
        if "ai" in task_desc or "ml" in task_desc:
            if any(s in skills for s in ["ai", "machine learning", "tensorflow"]):
                base_score += 0.3
        
        if "database" in task_desc:
            if any(s in skills for s in ["postgresql", "database", "sql"]):
                base_score += 0.3
        
        return min(1.0, base_score)
    
    def _calculate_assignment_confidence(
        self, 
        match_score: float, 
        member: Dict[str, Any]
    ) -> float:
        """Calculate confidence in the assignment."""
        confidence = match_score
        
        # Adjust for workload
        load_pct = member["current_load_hours"] / member["availability_hours_per_week"]
        
        if load_pct > 0.8:
            confidence -= 0.20
        elif load_pct > 0.6:
            confidence -= 0.10
        
        # Boost for low workload
        if load_pct < 0.4:
            confidence += 0.10
        
        return max(0.0, min(1.0, confidence))
    
    def _build_reasoning(self, assignments: List[Dict[str, Any]]) -> str:
        """Build human-readable reasoning."""
        total = len(assignments)
        high_conf = sum(1 for a in assignments if a["confidence"] > 0.8)
        low_conf = sum(1 for a in assignments if a["confidence"] < 0.6)
        vector_count = sum(1 for a in assignments if a.get("match_method") == "vector_similarity")
        keyword_count = sum(1 for a in assignments if a.get("match_method") == "keyword")
        
        reasoning = f"Assigned {total} tasks. "
        reasoning += f"{high_conf} high-confidence, {low_conf} low-confidence. "
        
        if vector_count > 0:
            reasoning += f"Used vector similarity for {vector_count} assignments. "
        if keyword_count > 0:
            reasoning += f"Used keyword matching for {keyword_count} assignments. "
        
        if low_conf > 0:
            reasoning += "Some assignments may need review due to skill mismatch or capacity constraints."
        
        return reasoning
