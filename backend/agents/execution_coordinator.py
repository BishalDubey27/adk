"""
Execution Coordinator - Orchestrate all agents and aggregate confidence scores.
"""
import asyncio
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResult
from .intake_agent import IntakeAgent
from .planning_agent import PlanningAgent
from .staffing_agent import StaffingAgent
from .risk_agent import RiskAgent


class ExecutionCoordinator(BaseAgent):
    """Orchestrate agent pipeline and compute final confidence score."""
    
    name = "execution_coordinator"
    
    # Confidence weights for each agent
    AGENT_WEIGHTS = {
        "intake": 0.15,
        "planning": 0.20,
        "staffing": 0.30,
        "risk": 0.35
    }
    
    def __init__(self, escalate_threshold: float = 0.65, auto_threshold: float = 0.85):
        super().__init__(escalate_threshold)
        self.auto_threshold = auto_threshold
        
        # Initialize agents
        self.intake_agent = IntakeAgent()
        self.planning_agent = PlanningAgent()
        self.staffing_agent = StaffingAgent()
        self.risk_agent = RiskAgent()
    
    async def run(self, context: Dict[str, Any]) -> AgentResult:
        """
        Execute full agent pipeline and aggregate results.
        
        Args:
            context: Must contain 'user_request'
            
        Returns:
            AgentResult with final decision and aggregated confidence
        """
        results = {}
        
        # Step 1: Intake Agent
        intake_result = await self.intake_agent.run(context)
        results["intake"] = intake_result
        
        if not intake_result.success:
            return self._build_early_exit_result(results, "intake")
        
        # Step 2: Planning Agent
        planning_context = {
            "project_spec": intake_result.data
        }
        planning_result = await self.planning_agent.run(planning_context)
        results["planning"] = planning_result
        
        # Step 3 & 4: Staffing and Risk Agents (PARALLEL)
        staffing_context = {
            "tasks": planning_result.data.get("tasks", []),
            "team_members": context.get("team_members")
        }
        
        risk_context = {
            "tasks": planning_result.data.get("tasks", []),
            "assignments": []  # Will be updated after staffing
        }
        
        # Run in parallel
        staffing_result, risk_result_temp = await asyncio.gather(
            self.staffing_agent.run(staffing_context),
            self.risk_agent.run(risk_context)
        )
        
        results["staffing"] = staffing_result
        
        # Re-run risk agent with staffing results
        risk_context["assignments"] = staffing_result.data.get("assignments", [])
        risk_result = await self.risk_agent.run(risk_context)
        results["risk"] = risk_result
        
        # Step 5: Aggregate confidence scores
        final_confidence = self._aggregate_confidence(results)
        
        # Step 6: Determine action
        action = self._determine_action(final_confidence)
        
        # Build final result
        reasoning = self._build_reasoning(results, final_confidence, action)
        
        escalation_reason = None
        if action == "escalate":
            escalation_reason = self._build_escalation_reason(results)
        
        return AgentResult(
            success=True,
            confidence=final_confidence,
            data={
                "action": action,
                "agent_results": {
                    "intake": intake_result.data,
                    "planning": planning_result.data,
                    "staffing": staffing_result.data,
                    "risk": risk_result.data
                },
                "individual_confidences": {
                    "intake": intake_result.confidence,
                    "planning": planning_result.confidence,
                    "staffing": staffing_result.confidence,
                    "risk": risk_result.confidence
                }
            },
            reasoning=reasoning,
            escalation_reason=escalation_reason
        )
    
    def _aggregate_confidence(self, results: Dict[str, AgentResult]) -> float:
        """Calculate weighted average confidence across all agents."""
        weighted_sum = 0.0
        
        for agent_name, weight in self.AGENT_WEIGHTS.items():
            if agent_name in results:
                weighted_sum += results[agent_name].confidence * weight
        
        return round(weighted_sum, 3)
    
    def _determine_action(self, confidence: float) -> str:
        """Determine what action to take based on confidence score."""
        if confidence >= self.auto_threshold:
            return "auto_proceed"
        elif confidence >= self.escalate_threshold:
            return "proceed_with_warning"
        else:
            return "escalate"
    
    def _build_reasoning(
        self, 
        results: Dict[str, AgentResult], 
        final_confidence: float,
        action: str
    ) -> str:
        """Build comprehensive reasoning from all agents."""
        reasoning_parts = [
            f"Pipeline executed successfully. Final confidence: {final_confidence:.2f}",
            ""
        ]
        
        for agent_name in ["intake", "planning", "staffing", "risk"]:
            if agent_name in results:
                result = results[agent_name]
                reasoning_parts.append(
                    f"{agent_name.title()}: {result.reasoning} (confidence: {result.confidence:.2f})"
                )
        
        reasoning_parts.append("")
        reasoning_parts.append(f"Decision: {action.replace('_', ' ').title()}")
        
        return "\n".join(reasoning_parts)
    
    def _build_escalation_reason(self, results: Dict[str, AgentResult]) -> str:
        """Build escalation reason from agent results."""
        reasons = []
        
        for agent_name, result in results.items():
            if result.escalation_reason:
                reasons.append(f"{agent_name.title()}: {result.escalation_reason}")
        
        if not reasons:
            reasons.append("Overall confidence below threshold")
        
        return "; ".join(reasons)
    
    def _build_early_exit_result(
        self, 
        results: Dict[str, AgentResult], 
        failed_agent: str
    ) -> AgentResult:
        """Build result when pipeline exits early due to failure."""
        failed_result = results[failed_agent]
        
        return AgentResult(
            success=False,
            confidence=failed_result.confidence,
            data={
                "action": "escalate",
                "failed_at": failed_agent,
                "agent_results": {failed_agent: failed_result.data}
            },
            reasoning=f"Pipeline failed at {failed_agent}: {failed_result.reasoning}",
            escalation_reason=failed_result.escalation_reason or f"{failed_agent} validation failed"
        )
