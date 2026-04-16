"""
Planning Agent - Break projects into tasks with estimates and dependencies.
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from .base_agent import BaseAgent, AgentResult


class PlanningAgent(BaseAgent):
    """Decompose projects into tasks with time estimates and dependencies."""
    
    name = "planning"
    
    async def run(self, context: Dict[str, Any]) -> AgentResult:
        """
        Break down project into discrete tasks.
        
        Args:
            context: Must contain 'project_spec' from Intake Agent
            
        Returns:
            AgentResult with task list, estimates, and dependencies
        """
        project_spec = context.get("project_spec", {})
        
        # Generate tasks based on project description
        tasks = self._generate_tasks(project_spec)
        
        # Identify dependencies
        tasks_with_deps = self._identify_dependencies(tasks)
        
        # Calculate milestones and critical path
        milestones = self._calculate_milestones(tasks_with_deps, project_spec)
        
        # Check capacity vs deadline
        capacity_check = self._check_capacity(tasks_with_deps, project_spec)
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            project_spec, 
            tasks_with_deps, 
            capacity_check
        )
        
        # Build reasoning
        reasoning = self._build_reasoning(
            tasks_with_deps, 
            milestones, 
            capacity_check
        )
        
        result_data = {
            "tasks": tasks_with_deps,
            "milestones": milestones,
            "total_estimated_hours": sum(t["estimated_hours"] for t in tasks_with_deps),
            "capacity_check": capacity_check
        }
        
        escalation_reason = None
        if not capacity_check["feasible"]:
            escalation_reason = capacity_check["reason"]
        
        return AgentResult(
            success=True,
            confidence=confidence,
            data=result_data,
            reasoning=reasoning,
            escalation_reason=escalation_reason
        )
    
    def _generate_tasks(self, project_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate task list from project description."""
        description = project_spec.get("description", "").lower()
        tasks = []
        
        # Rule-based task generation (simplified)
        # In production, this would use LLM for better decomposition
        
        common_tasks = [
            {"title": "Project Setup", "estimated_hours": 4, "phase": "setup"},
            {"title": "Requirements Analysis", "estimated_hours": 8, "phase": "planning"},
            {"title": "Design Architecture", "estimated_hours": 16, "phase": "design"},
        ]
        
        if "frontend" in description or "ui" in description or "dashboard" in description:
            common_tasks.extend([
                {"title": "UI/UX Design", "estimated_hours": 16, "phase": "design"},
                {"title": "Frontend Development", "estimated_hours": 40, "phase": "development"},
                {"title": "Frontend Testing", "estimated_hours": 16, "phase": "testing"},
            ])
        
        if "backend" in description or "api" in description or "database" in description:
            common_tasks.extend([
                {"title": "Database Schema Design", "estimated_hours": 8, "phase": "design"},
                {"title": "API Development", "estimated_hours": 40, "phase": "development"},
                {"title": "Backend Testing", "estimated_hours": 16, "phase": "testing"},
            ])
        
        if "ai" in description or "ml" in description or "agent" in description:
            common_tasks.extend([
                {"title": "AI Model Setup", "estimated_hours": 24, "phase": "development"},
                {"title": "Agent Development", "estimated_hours": 32, "phase": "development"},
                {"title": "AI Testing & Tuning", "estimated_hours": 16, "phase": "testing"},
            ])
        
        # Always add integration and deployment
        common_tasks.extend([
            {"title": "Integration Testing", "estimated_hours": 16, "phase": "testing"},
            {"title": "Deployment Setup", "estimated_hours": 8, "phase": "deployment"},
            {"title": "Documentation", "estimated_hours": 8, "phase": "deployment"},
        ])
        
        return common_tasks[:15]  # Limit to 15 tasks
    
    def _identify_dependencies(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add dependency information to tasks."""
        # Simple phase-based dependencies
        phase_order = ["setup", "planning", "design", "development", "testing", "deployment"]
        
        for i, task in enumerate(tasks):
            task["task_id"] = i + 1
            task["dependencies"] = []
            
            # Tasks depend on previous phase tasks
            current_phase = task.get("phase", "")
            if current_phase in phase_order:
                phase_idx = phase_order.index(current_phase)
                if phase_idx > 0:
                    # Depend on last task of previous phase
                    for j in range(i - 1, -1, -1):
                        if tasks[j].get("phase") == phase_order[phase_idx - 1]:
                            task["dependencies"].append(tasks[j]["task_id"])
                            break
        
        return tasks
    
    def _calculate_milestones(
        self, 
        tasks: List[Dict[str, Any]], 
        project_spec: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Calculate project milestones."""
        milestones = []
        phases = {}
        
        # Group tasks by phase
        for task in tasks:
            phase = task.get("phase", "other")
            if phase not in phases:
                phases[phase] = []
            phases[phase].append(task)
        
        # Create milestone for each phase
        for phase, phase_tasks in phases.items():
            total_hours = sum(t["estimated_hours"] for t in phase_tasks)
            milestones.append({
                "name": f"{phase.title()} Complete",
                "tasks": len(phase_tasks),
                "estimated_hours": total_hours
            })
        
        return milestones
    
    def _check_capacity(
        self, 
        tasks: List[Dict[str, Any]], 
        project_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if project is feasible within deadline."""
        total_hours = sum(t["estimated_hours"] for t in tasks)
        team_size = project_spec.get("team_size", 3)
        
        # Parse deadline
        deadline_str = project_spec.get("deadline", "")
        try:
            if "/" in deadline_str:
                deadline = datetime.strptime(deadline_str, "%m/%d/%Y")
            else:
                deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
            
            days_available = (deadline - datetime.now()).days
            
            # Assume 6 productive hours per person per day
            available_hours = days_available * team_size * 6
            
            feasible = total_hours <= available_hours
            utilization = (total_hours / available_hours * 100) if available_hours > 0 else 999
            
            return {
                "feasible": feasible,
                "total_hours": total_hours,
                "available_hours": available_hours,
                "utilization": round(utilization, 1),
                "days_available": days_available,
                "reason": "" if feasible else f"Need {total_hours}h but only {available_hours}h available"
            }
        except (ValueError, TypeError):
            return {
                "feasible": False,
                "reason": "Invalid deadline format",
                "total_hours": total_hours,
                "available_hours": 0,
                "utilization": 0,
                "days_available": 0
            }
    
    def _calculate_confidence(
        self,
        project_spec: Dict[str, Any],
        tasks: List[Dict[str, Any]],
        capacity_check: Dict[str, Any]
    ) -> float:
        """Calculate planning confidence score."""
        confidence = 1.0
        
        # Penalize for too many tasks
        if len(tasks) > 20:
            confidence -= 0.20
        elif len(tasks) > 15:
            confidence -= 0.10
        
        # Penalize for vague description
        description = project_spec.get("description", "")
        if len(description) < 30:
            confidence -= 0.15
        
        # Penalize for infeasible timeline
        if not capacity_check["feasible"]:
            confidence -= 0.25
        elif capacity_check["utilization"] > 90:
            confidence -= 0.10
        
        # Boost for clear scope
        if len(description) > 100:
            confidence += 0.05
        
        return max(0.0, min(1.0, confidence))
    
    def _build_reasoning(
        self,
        tasks: List[Dict[str, Any]],
        milestones: List[Dict[str, Any]],
        capacity_check: Dict[str, Any]
    ) -> str:
        """Build human-readable reasoning."""
        total_hours = capacity_check["total_hours"]
        
        reasoning = (
            f"Generated {len(tasks)} tasks across {len(milestones)} milestones. "
            f"Total estimated effort: {total_hours} hours. "
        )
        
        if capacity_check["feasible"]:
            reasoning += (
                f"Timeline is feasible with {capacity_check['utilization']}% team utilization."
            )
        else:
            reasoning += f"Warning: {capacity_check['reason']}"
        
        return reasoning
