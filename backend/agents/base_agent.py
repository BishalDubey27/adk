"""
Base agent class and result structure for all Tech Sarathi agents.
"""
from dataclasses import dataclass
from typing import Any, Optional, Dict
from abc import ABC, abstractmethod


@dataclass
class AgentResult:
    """Standardized result structure returned by all agents."""
    
    success: bool
    confidence: float  # 0.0 to 1.0
    data: Dict[str, Any]
    reasoning: str
    escalation_reason: Optional[str] = None
    
    def __post_init__(self):
        """Validate confidence score is in valid range."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")


class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    name: str = "base"
    
    def __init__(self, escalate_threshold: float = 0.65):
        """
        Initialize base agent.
        
        Args:
            escalate_threshold: Confidence threshold below which to escalate
        """
        self.escalate_threshold = escalate_threshold
    
    @abstractmethod
    async def run(self, context: Dict[str, Any]) -> AgentResult:
        """
        Execute the agent's main logic.
        
        Args:
            context: Dictionary containing all necessary input data
            
        Returns:
            AgentResult with success status, confidence, data, and reasoning
        """
        raise NotImplementedError("Subclasses must implement run()")
    
    def should_escalate(self, confidence: float) -> bool:
        """
        Determine if a decision should be escalated to human review.
        
        Args:
            confidence: Confidence score from 0.0 to 1.0
            
        Returns:
            True if confidence is below escalation threshold
        """
        return confidence < self.escalate_threshold
    
    def calculate_confidence(self, factors: Dict[str, float]) -> float:
        """
        Calculate weighted confidence score from multiple factors.
        
        Args:
            factors: Dictionary of factor_name -> weight pairs
            
        Returns:
            Weighted average confidence score clamped to [0.0, 1.0]
        """
        if not factors:
            return 0.0
        
        total_weight = sum(factors.values())
        if total_weight == 0:
            return 0.0
        
        weighted_sum = sum(factors.values())
        confidence = weighted_sum / len(factors)
        
        return max(0.0, min(1.0, confidence))
