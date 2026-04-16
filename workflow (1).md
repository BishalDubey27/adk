# Tech Sarathi — System Workflow
> **Team:** Tech Sarathi | **Leader:** Bishal Dubey | **Members:** Sahil Prajapati, Amit Yadav, Khush Patel
> **Hackathon:** NIRMAN — Amity University Mumbai

---

## Overview

Tech Sarathi is an AI-powered project management system built on a **multi-agent pipeline** with a confidence-based escalation model. The workflow describes how a user request flows through 7 AI agents, gets persisted in AlloyDB, and either proceeds autonomously or is escalated to a human PM.

---

## 1. End-to-End Request Flow

```
User Request
    │
    ▼
[1. Intake Agent]
    Parse → Validate → Classify
    │
    ▼
[2. Planning Agent]
    Decompose → Estimate → Dependency Map
    │
    ├─────────────────────────┐
    ▼                         ▼
[3. Staffing Agent]     [4. Risk Agent]       ← PARALLEL
    Vector skill match        Predict blockers
    Capacity check            Flag dependencies
    │                         │
    └──────────┬──────────────┘
               ▼
    [5. Execution Coordinator]
    Aggregate results → Compute confidence score
               │
               ▼
         ┌─────────────┐
         │  Escalate?  │
         └──────┬──────┘
          yes ◄─┤─► no
                │
    ┌───────────┴──────────────┐
    ▼                          ▼
[Human Review]       [Autonomous Execution]
Approve / Reject      ReAct: Observe → Reason → Act
    │                          │
    └────────────┬─────────────┘
                 ▼
    [6. Communication Agent]   → Notify stakeholders
    [7. Escalation Agent]      → Write audit trail
                 │
                 ▼
           [AlloyDB AI]        ← All state persisted
```

---

## 2. Agent-by-Agent Workflow

### Step 1 — Intake Agent
**Trigger:** A new user request arrives (text or JSON).

1. Parse the raw input using LLM (or regex fallback).
2. Extract: project name, description, deadline, priority, team size, required skills.
3. Validate all required fields; note any missing ones.
4. Classify request type: `new_project | add_task | status_check | risk_report | escalation_review`.
5. Compute confidence — decreases by 0.15 per missing field.
6. Output: structured project/task spec + confidence score.

---

### Step 2 — Planning Agent
**Trigger:** Structured spec from Intake Agent.

1. Decompose the project into discrete tasks using LLM (or rule-based templates).
2. Assign rough hour estimates per task.
3. Identify dependencies (task B requires task A to be complete first).
4. Compute the critical path and project milestones.
5. Flag if total estimated hours exceed deadline capacity.
6. Confidence drops for: vague descriptions, >20 tasks, no deadline.
7. Output: full task list with estimates, dependencies, and milestones.

---

### Step 3 — Staffing Agent *(runs in parallel with Risk Agent)*
**Trigger:** Task list from Planning Agent.

1. Convert each task description into a vector embedding.
2. Run a semantic similarity search against `team_members.skill_embedding` in AlloyDB.
3. Filter candidates whose `current_load < 90% of availability`.
4. Select the best candidate per task; check for scheduling conflicts.
5. Confidence drops when: top similarity score < 0.6, or assignee is near capacity.
6. Output: task → assignee mapping with justification.

---

### Step 4 — Risk Agent *(runs in parallel with Staffing Agent)*
**Trigger:** Task list + assignments + team availability data.

Evaluates six risk factors per task:
- Task has no assignee
- Assignee is at >80% capacity
- Deadline < 3 days away, status still `todo`
- Unresolved upstream dependency
- Similar historical tasks took 2x their estimate
- No activity logged in 48+ hours

1. Score each task with a `risk_score` (0.0 – 1.0).
2. Compile a list of specific blockers.
3. Confidence drops if historical data is unavailable (cold start).
4. Output: per-task risk scores + blocker list.

---

### Step 5 — Execution Coordinator
**Trigger:** Results from all four preceding agents.

1. Aggregate confidence scores using a weighted formula:

   | Agent    | Weight |
   |----------|--------|
   | Intake   | 15%    |
   | Planning | 20%    |
   | Staffing | 30%    |
   | Risk     | 35%    |

2. Compute the final confidence score.
3. Apply routing logic:

   | Score         | Action                              |
   |---------------|-------------------------------------|
   | > 0.85        | Auto-proceed, log decision          |
   | 0.65 – 0.85   | Proceed with warning, notify PM     |
   | < 0.65        | Pause, escalate to Escalation Agent |

4. Output: final decision + confidence score + proceed/escalate signal.

---

### Escalation Path (confidence < 0.65)

1. **Escalation Agent** writes a record to the `escalations` table.
   - Includes: which agent triggered it, reasoning, confidence score, suggested action.
2. PM receives a notification and reviews the item in the **Escalation Queue** UI.
3. PM selects: **Approve**, **Reject**, or **Override**.
4. Outcome is fed back to the relevant agent as a future training signal.
5. All actions are logged to `audit_log`.

---

### Autonomous Execution Path (confidence ≥ 0.65)

Once approved (automatically or by PM):

1. Tasks are committed to the database with assigned team members.
2. **ReAct Loop** activates (runs every 5 minutes via APScheduler):
   - **Observe** — Query current project state from AlloyDB.
   - **Reason** — Detect drift, overdue tasks, resource conflicts.
   - **Act** — Reassign, flag risk, or notify as needed.
   - **Loop** — Repeats until project status is `completed`.

---

### Step 6 — Communication Agent
**Triggers:**
- Task marked `done`
- Risk score crosses threshold
- Escalation resolved
- Deadline < 48 hours away
- Weekly scheduled summary

1. Generate formatted status update using current project state.
2. Deliver via Slack, email, or webhook.
3. Log communication to `audit_log`.

---

### Step 7 — Escalation Agent
**Triggers:** Any decision with confidence < 0.65.

1. Insert record into `escalations` table with full context.
2. Notify the assigned PM.
3. On human decision: update escalation status (`approved | rejected | overridden`).
4. Write full decision trail to `audit_log` for compliance and future analysis.

---

## 3. ReAct Continuous Monitoring Loop

Runs **every 5 minutes** while a project is `active`.

```
┌──────────────────────────────────────┐
│              REACT LOOP              │
│                                      │
│  OBSERVE  → Query AlloyDB for state  │
│     ↓                                │
│  REASON   → Check for:               │
│             - Overdue tasks          │
│             - New risk flags         │
│             - Resource conflicts     │
│     ↓                                │
│  ACT      → Reassign / Flag / Notify │
│     ↓                                │
│  LOOP     → Sleep → Repeat           │
└──────────────────────────────────────┘
```

The loop terminates when the project status changes to `completed` or `archived`.

---

## 4. Confidence Score Decision Flow

```
Agent Result
    │
    ▼
confidence > 0.85 ──────────► Auto-proceed
                               Log to audit_log
                               
confidence 0.65–0.85 ────────► Proceed
                               Notify PM (warning)
                               Log to audit_log
                               
confidence < 0.65 ───────────► PAUSE
                               Write to escalations table
                               Notify PM for review
                               Wait for Approve / Reject / Override
```

---

## 5. Data Persistence Flow

Every agent interaction writes to AlloyDB:

| Action                    | Table Updated                |
|---------------------------|------------------------------|
| Task created / assigned   | `tasks`                      |
| Team member load updated  | `team_members`               |
| Risk score computed       | `tasks.risk_score`           |
| Escalation triggered      | `escalations`                |
| Human decision made       | `escalations` + `audit_log`  |
| Any agent decision        | `audit_log`                  |
| ReAct loop action         | `audit_log`                  |
| Notification sent         | `audit_log`                  |

---

## 6. Build Phase Workflow (Development Order)

| Phase | Days   | Key Deliverable                                      |
|-------|--------|------------------------------------------------------|
| 1     | 1–2    | GCP + AlloyDB setup, FastAPI skeleton, Docker Compose |
| 2     | 3–5    | All 4 core agents (Intake, Planning, Staffing, Risk) |
| 3     | 6–7    | Execution Coordinator, parallel agent wiring, escalation routing |
| 4     | 8–9    | REST API, auth middleware, WebSocket, integration tests |
| 5     | 10     | ReAct loop (APScheduler, Observe → Reason → Act)    |
| 6     | 11–13  | Frontend: Dashboard, Task Board, Escalation Queue, Audit Log |
| 7     | 14–15  | Deploy to Cloud Run + Firebase, load test, demo script |

**First files to build:**
1. `backend/db/schema.sql`
2. `backend/agents/base_agent.py`
3. `backend/agents/intake_agent.py`
4. `backend/core/database.py`
5. `backend/api/main.py`

---

*Generated from Tech Sarathi Build Plan | NIRMAN Hackathon — Amity University Mumbai | April 2026*
