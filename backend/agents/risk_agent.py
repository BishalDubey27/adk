"""
Risk Agent - Predict task risks and identify blockers.
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from .base_agent import BaseAgent, AgentResult


class RiskAgent(BaseAgent):
    """Predict which tasks are likely to slip and identify blockers."""
    
    name = "risk"
    
    RISK_FACTORS = [
        "no_assignee",
        "overloaded_assignee",
        "tight_deadline",
        "unresolved_dependency",
        "no_historical_data",
        "task_complexity"
    ]
    
    async def run(self, context: Dict[str, Any]) -> AgentResult:
        """
        Analyze tasks for risk factors and predict blockers.
        
        Args:
            context: Must contain 'tasks' and 'assignments'
            
        Returns:
            AgentResult with risk scores and blocker list
        """
        tasks = context.get("tasks", [])
        assignments = context.get("assignments", [])
        
        # Create assignment lookup
        assignment_map = {
            a["task_id"]: a for a in assignments
        }
        
        # Analyze each task
        risk_analysis = []
        total_risk = 0.0
        blockers = []
        
        for task in tasks:
            analysis = self._analyze_task_risk(task, assignment_map)
            risk_analysis.append(analysis)
            total_risk += analysis["risk_score"]
            
            if analysis["blockers"]:
                blockers.extend(analysis["blockers"])
        
        # Calculate overall confidence
        avg_risk = total_risk / len(tasks) if tasks else 0.0
        confidence = 1.0 - avg_risk  # Inverse of risk
        
        # Build reasoning
        reasoning = self._build_reasoning(risk_analysis, blockers)
        
        # Check for escalation
        escalation_reason = None
        high_risk_count = sum(1 for r in risk_analysis if r["risk_score"] > 0.7)
        if high_risk_count > 0:
            escalation_reason = f"{high_risk_count} tasks identified as high-risk"
        
        return AgentResult(
            success=True,
            confidence=confidence,
            data={
                "risk_analysis": risk_analysis,
                "blockers": blockers,
                "average_risk": round(avg_risk, 2),
                "high_risk_count": high_risk_count
            },
            reasoning=reasoning,
            escalation_reason=escalation_reason
        )
    
    def _analyze_task_risk(
        self, 
        task: Dict[str, Any], 
        assignment_map: Dict[int, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze risk factors for a single task."""
        task_id = task.get("task_id")
        assignment = assignment_map.get(task_id, {})
        
        risk_factors = []
        risk_score = 0.0
        blockers = []
        
        # Factor 1: No assignee
        if not assignment.get("assigned_to"):
            risk_factors.append("no_assignee")
            risk_score += 0.30
            blockers.append({
                "task_id": task_id,
                "task_title": task.get("title"),
                "type": "no_assignee",
                "severity": "high",
                "description": "Task has no assigned team member"
            })
        
        # Factor 2: Low assignment confidence (proxy for overloaded/mismatched)
        assignment_confidence = assignment.get("confidence", 1.0)
        if assignment_confidence < 0.6:
            risk_factors.append("poor_assignment")
            risk_score += 0.25
            blockers.append({
                "task_id": task_id,
                "task_title": task.get("title"),
                "type": "poor_assignment",
                "severity": "medium",
                "description": f"Low assignment confidence ({assignment_confidence:.2f})"
            })
        
        # Factor 3: Task complexity (high estimated hours)
        estimated_hours = task.get("estimated_hours", 0)
        if estimated_hours > 30:
            risk_factors.append("high_complexity")
            risk_score += 0.20
            blockers.append({
                "task_id": task_id,
                "task_title": task.get("title"),
                "type": "high_complexity",
                "severity": "medium",
                "description": f"High complexity task ({estimated_hours}h estimated)"
            })
        
        # Factor 4: Dependencies
        dependencies = task.get("dependencies", [])
        if len(dependencies) > 2:
            risk_factors.append("multiple_dependencies")
            risk_score += 0.15
            blockers.append({
                "task_id": task_id,
                "task_title": task.get("title"),
                "type": "multiple_dependencies",
                "severity": "low",
                "description": f"Depends on {len(dependencies)} other tasks"
            })
        
        # Factor 5: No historical data (cold start)
        # In production, this would check audit_log for similar tasks
        risk_factors.append("no_historical_data")
        risk_score += 0.10
        
        # Normalize risk score
        risk_score = min(1.0, risk_score)
        
        return {
            "task_id": task_id,
            "task_title": task.get("title"),
            "risk_score": round(risk_score, 2),
            "risk_factors": risk_factors,
            "blockers": blockers
        }
    
    def _build_reasoning(
        self, 
        risk_analysis: List[Dict[str, Any]], 
        blockers: List[Dict[str, Any]]
    ) -> str:
        """Build human-readable reasoning."""
        total_tasks = len(risk_analysis)
        high_risk = sum(1 for r in risk_analysis if r["risk_score"] > 0.7)
        medium_risk = sum(1 for r in risk_analysis if 0.4 < r["risk_score"] <= 0.7)
        low_risk = sum(1 for r in risk_analysis if r["risk_score"] <= 0.4)
        
        reasoning = f"Analyzed {total_tasks} tasks. "
        reasoning += f"Risk distribution: {high_risk} high, {medium_risk} medium, {low_risk} low. "
        
        if blockers:
            reasoning += f"Identified {len(blockers)} potential blockers. "
        
        if high_risk > 0:
            reasoning += "Immediate attention required for high-risk tasks."
        else:
            reasoning += "No critical blockers detected."
        
        return reasoning
