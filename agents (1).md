# Tech Sarathi — AI Agents Specification
> **Team:** Tech Sarathi | **Leader:** Bishal Dubey | **Members:** Sahil Prajapati, Amit Yadav, Khush Patel
> **Hackathon:** NIRMAN — Amity University Mumbai

---

## Overview

Tech Sarathi uses **7 specialised AI agents** orchestrated via Google ADK. Each agent inherits from a common `BaseAgent` class, returns a standardised `AgentResult`, and contributes a confidence score that drives the system's escalation logic.

### Agent Execution Order

```
[1] Intake Agent         → sequential
[2] Planning Agent       → sequential
[3] Staffing Agent  ─┐
                      ├─ parallel
[4] Risk Agent      ─┘
[5] Execution Coordinator → sequential
[6] Communication Agent  → sequential (post-decision)
[7] Escalation Agent     → sequential (post-decision)
```

---

## Base Class

All agents inherit from `BaseAgent` and return an `AgentResult`.

```python
# backend/agents/base_agent.py
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class AgentResult:
    success: bool
    confidence: float           # 0.0 – 1.0
    data: dict[str, Any]
    reasoning: str              # human-readable explanation
    escalation_reason: Optional[str] = None

class BaseAgent:
    name: str = "base"

    async def run(self, context: dict) -> AgentResult:
        raise NotImplementedError

    def should_escalate(self, confidence: float) -> bool:
        return confidence < 0.65
```

---

## Agent 1 — Intake Agent

**File:** `backend/agents/intake_agent.py`

### Responsibility
Parse raw user input, validate completeness, and classify the request type before any other agent runs.

### Inputs
- Raw user request (plain text or JSON)

### Outputs
- Structured project/task specification
- Confidence score
- Request classification label

### Logic

1. Extract fields using LLM (with deterministic regex as fallback):
   - Project name, description, deadline, priority, team size, required skills
2. Validate all required fields are present and logical (e.g. deadline is in the future).
3. Classify the request into one of:
   - `new_project` | `add_task` | `status_check` | `risk_report` | `escalation_review`
4. Compute confidence — decreases by **0.15 per missing field**.

### Confidence Factors

| Boosts Confidence | Drops Confidence |
|---|---|
| All fields present | Missing deadline |
| Clear priority set | Ambiguous or missing priority |
| Recognised skill names | Vague or unstructured description |

### Code Pattern

```python
async def run(self, context: dict) -> AgentResult:
    raw_input = context["user_request"]
    parsed = await self.llm_parse(raw_input)       # or deterministic regex fallback
    missing_fields = self.validate(parsed)
    confidence = 1.0 - (len(missing_fields) * 0.15)
    return AgentResult(
        success=len(missing_fields) == 0,
        confidence=max(0.0, confidence),
        data=parsed,
        reasoning=f"Parsed {len(parsed)} fields. Missing: {missing_fields}"
    )
```

---

## Agent 2 — Planning Agent

**File:** `backend/agents/planning_agent.py`

### Responsibility
Break a validated project description into discrete tasks, assign time estimates, map dependencies, and identify the critical path.

### Inputs
- Structured project spec from Intake Agent

### Outputs
- Full task list with hour estimates
- Dependency graph
- Milestones and critical path
- Confidence score

### Logic

1. Use LLM to decompose the project into tasks (or rule-based templates for common project types).
2. Assign rough hour estimates per task based on scope and complexity.
3. Identify task dependencies (task B requires task A).
4. Compute milestones and the critical path.
5. Flag if total estimated hours exceed available deadline capacity.

### Confidence Factors

| Boosts Confidence | Drops Confidence |
|---|---|
| Short project, clear scope | Vague or one-line description |
| Deadline well in the future | >20 tasks generated |
| Requirements clearly stated | Estimated hours >> available time |

---

## Agent 3 — Staffing Agent

**File:** `backend/agents/staffing_agent.py`

### Responsibility
Match each task to the most suitable available team member using semantic vector search against AlloyDB AI skill embeddings.

### Inputs
- Task list from Planning Agent
- Team member pool (from `team_members` table)

### Outputs
- Task → assignee mapping with justification
- Confidence score per assignment

### Logic

1. Convert each task description into a 768-dimension vector embedding.
2. Run a cosine similarity search against `team_members.skill_embedding` in AlloyDB.
3. Filter candidates to those with `current_load < 90%` of their weekly availability.
4. Select the best candidate; check for scheduling conflicts.
5. Fall back to keyword/tag matching when similarity score < 0.5.

### Key Query

```python
task_embedding = await embed(task.description)

query = """
    SELECT id, name, skills, current_load_hours, availability_hours_per_week,
           1 - (skill_embedding <=> $1) AS similarity
    FROM team_members
    WHERE current_load_hours < availability_hours_per_week * 0.9
    ORDER BY similarity DESC
    LIMIT 5
"""
candidates = await db.fetch(query, task_embedding)
```

### Confidence Factors

| Boosts Confidence | Drops Confidence |
|---|---|
| Similarity score > 0.85 | Similarity score < 0.6 |
| Assignee has low current load | Assignee at >80% capacity |
| Clear single best candidate | Multiple equally ranked candidates |

---

## Agent 4 — Risk Agent

**File:** `backend/agents/risk_agent.py`

### Responsibility
Predict which tasks or projects are likely to slip and produce a risk score and specific blocker list.

### Inputs
- Task list with assignments
- Team availability data
- Historical task performance data (from `audit_log`)

### Outputs
- Per-task `risk_score` (0.0 – 1.0)
- List of specific blockers with reasoning
- Confidence score

### Risk Factors Evaluated

| Factor | Description |
|---|---|
| No assignee | Task has no team member assigned |
| Overloaded assignee | Assignee is at >80% weekly capacity |
| Deadline proximity | Due date < 3 days, status still `todo` |
| Unresolved dependency | Upstream task is blocked or incomplete |
| Historical overrun | Similar past tasks took 2× their estimate |
| Inactivity | No activity logged on task in 48+ hours |

### Confidence Factors

| Boosts Confidence | Drops Confidence |
|---|---|
| No blockers detected | Multiple blockers present |
| Slack in timeline | Overloaded team across tasks |
| Historical data available | Cold start — no historical data |

---

## Agent 5 — Execution Coordinator

**File:** `backend/agents/execution_coordinator.py`

### Responsibility
Orchestrate all upstream agents, aggregate their confidence scores into a single final score, and route the decision to either autonomous execution or human escalation.

### Inputs
- `AgentResult` objects from Intake, Planning, Staffing, and Risk agents

### Outputs
- Final aggregated confidence score
- Proceed / escalate signal
- Consolidated decision record for audit

### Confidence Aggregation

Confidence is computed as a **weighted average** across agents:

```python
def aggregate_confidence(results: list[AgentResult]) -> float:
    weights = {
        "intake":   0.15,
        "planning": 0.20,
        "staffing": 0.30,
        "risk":     0.35,
    }
    return sum(weights[r.agent] * r.confidence for r in results)
```

### Routing Logic

| Final Score   | Action                                    |
|---------------|-------------------------------------------|
| > 0.85        | Auto-proceed, log to `audit_log`          |
| 0.65 – 0.85   | Proceed with warning, notify PM           |
| < 0.65        | Pause, route to Escalation Agent          |

### Parallel Execution

Staffing and Risk agents run concurrently to cut pipeline latency by ~40%:

```python
staffing_result, risk_result = await asyncio.gather(
    staffing_agent.run(context),
    risk_agent.run(context)
)
```

---

## Agent 6 — Communication Agent

**File:** `backend/agents/communication_agent.py`

### Responsibility
Generate and deliver status updates, risk alerts, and notifications to relevant stakeholders at the right moment.

### Inputs
- Current project state
- Recent task changes
- Escalation outcomes
- Scheduled trigger (weekly summary)

### Outputs
- Formatted messages sent via Slack, email, or webhook
- Log entry in `audit_log`

### Trigger Events

| Trigger | Message Type |
|---|---|
| Task marked `done` | Completion update |
| Risk score crosses threshold | Risk alert |
| Escalation resolved | Decision notification |
| Deadline < 48 hours away | Urgency reminder |
| Weekly schedule | Summary report |

---

## Agent 7 — Escalation Agent

**File:** `backend/agents/escalation_agent.py`

### Responsibility
Manage the human review queue for low-confidence decisions, and maintain the full audit trail for every automated action taken in the system.

### Inputs
- Any `AgentResult` with confidence < 0.65
- Human approve / reject / override decisions from the PM UI

### Outputs
- Record in the `escalations` table
- PM notification
- Updated `audit_log` entries
- (Future) Training signal fed back to the triggering agent

### Escalation Record Schema

```sql
INSERT INTO escalations (
    project_id,
    task_id,
    agent_name,         -- which agent triggered escalation
    reason,             -- human-readable explanation
    confidence_score,   -- the score that breached the threshold
    suggested_action,   -- agent's recommendation (JSONB)
    status              -- pending | approved | rejected | overridden
)
```

### On Human Decision

1. Update `escalations.status` to `approved`, `rejected`, or `overridden`.
2. Record `reviewed_by` and `reviewed_at`.
3. Write the full decision to `audit_log`.
4. Feed outcome back to the relevant agent as a future improvement signal.

---

## Confidence Score Quick Reference

```
0.85 ──────────────── AUTO-PROCEED       (log only)
0.65 ──────────────── PROCEED + WARN     (notify PM, continue)
0.00 ──────────────── ESCALATE           (pause, wait for human)
```

---

## Agent Confidence Weight Summary

| Agent                  | Pipeline Weight | Key Responsibility          |
|------------------------|-----------------|-----------------------------|
| Intake Agent           | 15%             | Parse & validate input       |
| Planning Agent         | 20%             | Task decomposition           |
| Staffing Agent         | 30%             | Skill matching               |
| Risk Agent             | 35%             | Blocker prediction           |
| Execution Coordinator  | —               | Aggregation & routing        |
| Communication Agent    | —               | Stakeholder notifications    |
| Escalation Agent       | —               | Audit trail & human review   |

---

*Generated from Tech Sarathi Build Plan | NIRMAN Hackathon — Amity University Mumbai | April 2026*
