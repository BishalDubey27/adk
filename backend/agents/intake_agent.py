"""
Intake Agent - Parse and validate user requests.
"""
import re
from typing import Dict, Any, List
from datetime import datetime, date
from .base_agent import BaseAgent, AgentResult


class IntakeAgent(BaseAgent):
    """Parse raw user input, validate completeness, and classify request type."""
    
    name = "intake"
    
    REQUIRED_FIELDS = ["name", "description", "deadline", "priority"]
    VALID_PRIORITIES = ["low", "medium", "high", "critical"]
    VALID_REQUEST_TYPES = [
        "new_project", "add_task", "status_check", 
        "risk_report", "escalation_review"
    ]
    
    async def run(self, context: Dict[str, Any]) -> AgentResult:
        """
        Parse and validate user request.
        
        Args:
            context: Must contain 'user_request' (str or dict)
            
        Returns:
            AgentResult with parsed project specification
        """
        raw_input = context.get("user_request", {})
        
        # Parse input
        if isinstance(raw_input, str):
            parsed = self._parse_text_input(raw_input)
        else:
            parsed = raw_input
        
        # Validate fields
        missing_fields = self._validate_fields(parsed)
        
        # Classify request type
        request_type = self._classify_request(parsed)
        parsed["request_type"] = request_type
        
        # Calculate confidence
        confidence = self._calculate_confidence(parsed, missing_fields)
        
        # Build reasoning
        reasoning = self._build_reasoning(parsed, missing_fields)
        
        success = len(missing_fields) == 0
        escalation_reason = None
        
        if not success:
            escalation_reason = f"Missing required fields: {', '.join(missing_fields)}"
        
        return AgentResult(
            success=success,
            confidence=confidence,
            data=parsed,
            reasoning=reasoning,
            escalation_reason=escalation_reason
        )
    
    def _parse_text_input(self, text: str) -> Dict[str, Any]:
        """Parse plain text input using regex patterns."""
        parsed = {}
        
        # Extract project name
        name_match = re.search(r'(?:project|name):\s*([^\n]+)', text, re.IGNORECASE)
        if name_match:
            parsed["name"] = name_match.group(1).strip()
        
        # Extract description
        desc_match = re.search(r'(?:description|desc):\s*([^\n]+)', text, re.IGNORECASE)
        if desc_match:
            parsed["description"] = desc_match.group(1).strip()
        
        # Extract deadline
        deadline_match = re.search(
            r'(?:deadline|due):\s*(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})',
            text,
            re.IGNORECASE
        )
        if deadline_match:
            parsed["deadline"] = deadline_match.group(1).strip()
        
        # Extract priority
        priority_match = re.search(
            r'(?:priority):\s*(low|medium|high|critical)',
            text,
            re.IGNORECASE
        )
        if priority_match:
            parsed["priority"] = priority_match.group(1).lower()
        
        # Extract skills
        skills_match = re.search(r'(?:skills|required skills):\s*([^\n]+)', text, re.IGNORECASE)
        if skills_match:
            skills_text = skills_match.group(1).strip()
            parsed["required_skills"] = [s.strip() for s in skills_text.split(',')]
        
        # Extract team size
        team_match = re.search(r'(?:team size):\s*(\d+)', text, re.IGNORECASE)
        if team_match:
            parsed["team_size"] = int(team_match.group(1))
        
        return parsed
    
    def _validate_fields(self, parsed: Dict[str, Any]) -> List[str]:
        """Check for missing required fields."""
        missing = []
        
        for field in self.REQUIRED_FIELDS:
            if field not in parsed or not parsed[field]:
                missing.append(field)
        
        # Validate priority value
        if "priority" in parsed and parsed["priority"] not in self.VALID_PRIORITIES:
            missing.append("valid_priority")
        
        # Validate deadline is in future
        if "deadline" in parsed:
            try:
                deadline_str = parsed["deadline"]
                if "/" in deadline_str:
                    deadline = datetime.strptime(deadline_str, "%m/%d/%Y").date()
                else:
                    deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()
                
                if deadline <= date.today():
                    missing.append("future_deadline")
            except (ValueError, TypeError):
                missing.append("valid_deadline_format")
        
        return missing
    
    def _classify_request(self, parsed: Dict[str, Any]) -> str:
        """Classify the type of request."""
        # Simple classification logic
        if "task" in parsed.get("description", "").lower():
            return "add_task"
        elif "status" in parsed.get("description", "").lower():
            return "status_check"
        elif "risk" in parsed.get("description", "").lower():
            return "risk_report"
        else:
            return "new_project"
    
    def _calculate_confidence(
        self, 
        parsed: Dict[str, Any], 
        missing_fields: List[str]
    ) -> float:
        """Calculate confidence score based on completeness."""
        base_confidence = 1.0
        
        # Penalize for missing fields
        confidence = base_confidence - (len(missing_fields) * 0.15)
        
        # Boost for clear priority
        if parsed.get("priority") in self.VALID_PRIORITIES:
            confidence += 0.05
        
        # Boost for recognized skills
        if parsed.get("required_skills"):
            confidence += 0.05
        
        # Penalize for vague description
        description = parsed.get("description", "")
        if len(description) < 20:
            confidence -= 0.10
        
        return max(0.0, min(1.0, confidence))
    
    def _build_reasoning(
        self, 
        parsed: Dict[str, Any], 
        missing_fields: List[str]
    ) -> str:
        """Build human-readable reasoning."""
        field_count = len(parsed)
        
        if not missing_fields:
            return (
                f"Successfully parsed {field_count} fields. "
                f"All required information present. "
                f"Request classified as: {parsed.get('request_type', 'unknown')}"
            )
        else:
            return (
                f"Parsed {field_count} fields. "
                f"Missing required fields: {', '.join(missing_fields)}. "
                f"Request classified as: {parsed.get('request_type', 'unknown')}"
            )
