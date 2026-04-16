# Tech Sarathi — AI-Powered Project Management System
## Complete Build Plan

> **Team:** Tech Sarathi | **Leader:** Bishal Dubey | **Members:** Sahil Prajapati, Amit Yadav, Khush Patel
> **Hackathon:** NIRMAN — Amity University Mumbai

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Tech Stack Justification](#3-tech-stack-justification)
4. [Folder Structure](#4-folder-structure)
5. [Database Schema](#5-database-schema)
6. [The 7 AI Agents — Detailed Spec](#6-the-7-ai-agents--detailed-spec)
7. [Confidence Scoring System](#7-confidence-scoring-system)
8. [API Design](#8-api-design)
9. [Frontend Design](#9-frontend-design)
10. [Build Phases & Timeline](#10-build-phases--timeline)
11. [Environment Setup](#11-environment-setup)
12. [Testing Strategy](#12-testing-strategy)
13. [Deployment](#13-deployment)
14. [Known Risks & Mitigations](#14-known-risks--mitigations)

---

## 1. Project Overview

### The Problem
Project managers spend **60–70% of their time** on repetitive, low-judgment tasks:
- Assigning tasks based on skill and availability
- Monitoring progress across multiple workstreams
- Identifying risks before they become blockers
- Writing status updates and coordinating schedules

This creates a **linear scaling bottleneck**: to manage more projects, you must hire more PMs. Organizations currently need 1 PM per 2–3 active projects.

### The Solution
Replace repetitive PM decisions with a **multi-agent AI system** that:
- Automatically assigns tasks using semantic skill matching
- Monitors progress 24/7 via a ReAct loop
- Predicts and flags risks early
- Escalates to a human **only when confidence is low**
- Maintains a full audit trail of every automated decision

One PM can oversee **10+ projects** instead of 2–3.

### Core Design Principle
**Not full automation — augmented management.**

| Confidence Score | System Action |
|---|---|
| > 0.85 | Auto-proceed, log decision |
| 0.65 – 0.85 | Proceed with warning, notify PM |
| < 0.65 | Pause, escalate to human for review |

---

## 2. System Architecture

### High-Level Flow

```
User Request
    │
    ▼
[Intake Agent] ──── Parse, validate, classify request
    │
    ▼
[Planning Agent] ── Break into tasks, set milestones, estimate timeline
    │
    ├──────────────────────┐
    ▼                      ▼
[Staffing Agent]      [Risk Agent]      ← run in PARALLEL
Skill match,          Predict blockers,
capacity check        flag dependencies
    │                      │
    └──────────┬───────────┘
               ▼
    [Execution Coordinator] ── Aggregate results, compute confidence score
               │
               ▼
          ┌────────────┐
          │ Escalate?  │
          └────┬───────┘
         yes ◄─┤─► no (auto-proceed)
               │
    ┌──────────┴──────────┐
    ▼                     ▼
[Human Review]    [Autonomous Execution]
Approve/Reject     ReAct: Observe → Reason → Act
    │                     │
    └──────────┬───────────┘
               ▼
   [Communication Agent] ── Send status updates, alerts
   [Escalation Agent]    ── Log audit trail, record overrides
               │
               ▼
         [AlloyDB AI] ← All state persisted here
```

### The ReAct Loop (Continuous Monitoring)
Every N minutes (configurable, default: 5 min), the system:
1. **Observes** — Queries current project state from AlloyDB
2. **Reasons** — Detects drift, overdue tasks, resource conflicts
3. **Acts** — Reassigns, flags, or notifies as needed
4. **Loops** — Repeats indefinitely until project closes

---

## 3. Tech Stack Justification

### Google Cloud (Primary)

| Service | Purpose | Why |
|---|---|---|
| **ADK** (Agent Development Kit) | Build and orchestrate the 7 agents | Native multi-agent support, tool calling, ReAct built-in |
| **AlloyDB AI** | Main database + vector search | Postgres-compatible + pgvector for semantic skill matching + predictive analytics |
| **MCP** (Model Context Protocol) | Inter-agent communication | Shared context without redundant API calls |
| **Cloud Run** | Deploy backend | Stateless containers, auto-scales to zero |

### Core Stack

| Layer | Technology | Reason |
|---|---|---|
| Backend | Python 3.11 + FastAPI | Async support, 1000+ req/sec, native ADK integration |
| Frontend | React 18 + Vite | Fast builds, CDN-deployable |
| Database | AlloyDB AI (PostgreSQL 15) | Vector search + standard SQL + AI-native queries |
| AI | Gemini via ADK + deterministic fallback | Works offline without LLM if needed |
| Auth | Firebase Auth or GCP IAM | GCP-native, minimal setup |

### Scalability Design
- **Stateless API** → horizontal scaling on Cloud Run
- **Parallel agent execution** → Staffing + Risk run concurrently (cuts latency ~40%)
- **Event-driven ReAct** → no polling overhead, agents sleep between cycles
- **Sub-second AlloyDB queries** → vector indexes on skill embeddings

---

## 4. Folder Structure

```
tech-sarathi/
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py           # Abstract AgentResult class + confidence interface
│   │   ├── intake_agent.py         # Parse + classify incoming requests
│   │   ├── planning_agent.py       # Task breakdown + milestone generation
│   │   ├── staffing_agent.py       # Skill matching via AlloyDB vector search
│   │   ├── risk_agent.py           # Risk prediction + dependency analysis
│   │   ├── execution_coordinator.py # Orchestrate agents, compute final confidence
│   │   ├── communication_agent.py  # Status updates, Slack/email notifications
│   │   └── escalation_agent.py     # Audit trail, human escalation queue
│   │
│   ├── core/
│   │   ├── config.py               # Environment variables, GCP config
│   │   ├── database.py             # AlloyDB connection pool (asyncpg)
│   │   ├── mcp_client.py           # MCP server setup for inter-agent context
│   │   └── react_loop.py           # Continuous monitoring loop (APScheduler)
│   │
│   ├── api/
│   │   ├── main.py                 # FastAPI app entry point
│   │   ├── routes/
│   │   │   ├── projects.py         # CRUD for projects
│   │   │   ├── tasks.py            # CRUD for tasks
│   │   │   ├── team.py             # Team member management
│   │   │   ├── escalations.py      # Human review queue endpoints
│   │   │   └── audit.py            # Audit log endpoints
│   │   └── middleware/
│   │       ├── auth.py             # GCP IAM / Firebase auth middleware
│   │       └── logging.py          # Structured logging
│   │
│   ├── db/
│   │   ├── migrations/             # SQL migration files (numbered)
│   │   ├── schema.sql              # Full schema definition
│   │   └── seed.sql                # Dev seed data
│   │
│   ├── tests/
│   │   ├── unit/                   # Per-agent unit tests
│   │   ├── integration/            # Full pipeline tests
│   │   └── conftest.py
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx       # PM overview: all projects at a glance
│   │   │   ├── ProjectCard.jsx     # Single project status + confidence indicator
│   │   │   ├── EscalationQueue.jsx # List of items needing human review
│   │   │   ├── AuditLog.jsx        # Full decision history
│   │   │   ├── TaskBoard.jsx       # Kanban-style task view
│   │   │   └── TeamPanel.jsx       # Team capacity + skill heatmap
│   │   ├── api/
│   │   │   └── client.js           # Axios wrapper for backend API
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── infra/
│   ├── cloudbuild.yaml             # CI/CD pipeline
│   ├── terraform/                  # IaC for AlloyDB, Cloud Run, IAM
│   └── docker-compose.yml          # Local dev (Postgres + backend + frontend)
│
└── README.md
```

---

## 5. Database Schema

### Core Tables

```sql
-- Team members with skill embeddings for vector search
CREATE TABLE team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    role TEXT,
    skills TEXT[],                          -- e.g. ['Python', 'React', 'ML']
    skill_embedding vector(768),            -- AlloyDB AI embedding of skill profile
    availability_hours_per_week INT DEFAULT 40,
    current_load_hours INT DEFAULT 0,       -- updated by staffing agent
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Projects
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active',           -- active | paused | completed | escalated
    priority TEXT DEFAULT 'medium',         -- low | medium | high | critical
    start_date DATE,
    deadline DATE,
    pm_id UUID REFERENCES team_members(id),
    confidence_score FLOAT,                 -- last computed confidence
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Tasks
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'todo',             -- todo | in_progress | blocked | done
    assigned_to UUID REFERENCES team_members(id),
    estimated_hours INT,
    actual_hours INT,
    due_date DATE,
    dependencies UUID[],                    -- array of task IDs this depends on
    risk_score FLOAT DEFAULT 0.0,           -- computed by risk agent
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Escalation queue (items needing human review)
CREATE TABLE escalations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    task_id UUID REFERENCES tasks(id),
    agent_name TEXT NOT NULL,               -- which agent triggered escalation
    reason TEXT NOT NULL,
    confidence_score FLOAT NOT NULL,
    suggested_action JSONB,                 -- agent's recommendation
    status TEXT DEFAULT 'pending',          -- pending | approved | rejected | overridden
    reviewed_by UUID REFERENCES team_members(id),
    reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Full audit trail
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name TEXT NOT NULL,
    action TEXT NOT NULL,
    entity_type TEXT,                       -- project | task | escalation
    entity_id UUID,
    input_data JSONB,
    output_data JSONB,
    confidence_score FLOAT,
    execution_time_ms INT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX ON tasks (project_id, status);
CREATE INDEX ON tasks (assigned_to, status);
CREATE INDEX ON escalations (status, created_at DESC);
CREATE INDEX ON audit_log (agent_name, created_at DESC);
CREATE INDEX ON team_members USING ivfflat (skill_embedding vector_cosine_ops);
```

---

## 6. The 7 AI Agents — Detailed Spec

### Base Class (all agents inherit this)

```python
# backend/agents/base_agent.py
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class AgentResult:
    success: bool
    confidence: float          # 0.0 to 1.0
    data: dict[str, Any]
    reasoning: str             # human-readable explanation
    escalation_reason: Optional[str] = None

class BaseAgent:
    name: str = "base"

    async def run(self, context: dict) -> AgentResult:
        raise NotImplementedError

    def should_escalate(self, confidence: float) -> bool:
        return confidence < 0.65
```

---

### Agent 1 — Intake Agent
**Responsibility:** Parse raw user input, validate completeness, classify the request type.

**Inputs:** Raw user request (text or JSON)
**Outputs:** Structured project/task spec, confidence score

**Logic:**
- Extract: project name, description, deadline, priority, team size, required skills
- Validate: all required fields present, deadline is future, skills are recognized
- Classify: new project | add task | status check | risk report | escalation review
- Confidence drops if: fields are missing, ambiguous priority, no deadline given

**Key code pattern:**
```python
async def run(self, context: dict) -> AgentResult:
    raw_input = context["user_request"]
    parsed = await self.llm_parse(raw_input)          # or deterministic regex fallback
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

### Agent 2 — Planning Agent
**Responsibility:** Break a project description into discrete tasks with time estimates and dependencies.

**Inputs:** Validated project spec from Intake Agent
**Outputs:** List of tasks with estimates, milestones, critical path

**Logic:**
- Use LLM to decompose project into tasks (or rule-based templates for common project types)
- Assign rough hour estimates per task
- Identify dependencies (task B requires task A)
- Flag if total estimated hours exceed deadline capacity
- Confidence drops if: no deadline, very vague description, estimated hours >> available time

---

### Agent 3 — Staffing Agent
**Responsibility:** Match tasks to the best available team member using semantic skill search.

**Inputs:** Task list from Planning Agent, team member pool
**Outputs:** Task → assignee mapping with justification

**Logic (this is the AlloyDB AI star moment):**
```python
# Convert task description to embedding
task_embedding = await embed(task.description)

# Vector similarity search against team member skill embeddings
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
- Pick best candidate, check for conflicts
- Confidence drops if: top similarity < 0.6, candidate is near capacity, multiple equal candidates

---

### Agent 4 — Risk Agent
**Responsibility:** Predict which tasks or projects are likely to slip, and why.

**Inputs:** Task list + assignments + team availability + historical data
**Outputs:** Risk scores per task, list of specific blockers

**Risk factors evaluated:**
- Task has no assignee
- Assignee is at >80% capacity
- Task deadline < 3 days away, status still "todo"
- Task has unresolved upstream dependencies
- Similar past tasks took 2x their estimate
- No activity logged on a task in 48+ hours

**Confidence drops if:** no historical data to compare against (cold start problem)

---

### Agent 5 — Execution Coordinator
**Responsibility:** Orchestrate all other agents, aggregate their outputs, compute a single final confidence score, and route to escalation or auto-execution.

**Inputs:** Results from all previous agents
**Outputs:** Final decision + confidence score + escalation/proceed signal

**Confidence aggregation:**
```python
def aggregate_confidence(results: list[AgentResult]) -> float:
    # Weighted average — staffing and risk are most critical
    weights = {
        "intake": 0.15,
        "planning": 0.20,
        "staffing": 0.30,
        "risk": 0.35,
    }
    return sum(weights[r.agent] * r.confidence for r in results)
```

---

### Agent 6 — Communication Agent
**Responsibility:** Generate and send status updates to stakeholders.

**Inputs:** Project state, recent changes, escalation outcomes
**Outputs:** Formatted messages sent via Slack/email/webhook

**Triggers:**
- Task marked complete
- Risk score crosses threshold
- Escalation resolved
- Weekly summary (scheduled)
- Deadline < 48 hours away

---

### Agent 7 — Escalation Agent
**Responsibility:** Manage the human review queue and maintain the audit trail.

**Inputs:** Any decision with confidence < 0.65
**Outputs:** Entry in escalations table, notification to PM

**On human approval/rejection:**
- Update the escalation record
- Feed outcome back to relevant agent as training signal (future improvement)
- Log everything to audit_log

---

## 7. Confidence Scoring System

This is the heart of the system. Every agent returns a confidence float between 0.0 and 1.0.

### Per-Agent Confidence Factors

| Agent | Boosts Confidence | Drops Confidence |
|---|---|---|
| Intake | All fields present, clear priority | Missing deadline, vague description |
| Planning | Short project, clear scope | >20 tasks, vague requirements |
| Staffing | Strong skill match (>0.85 similarity), low load | Weak match (<0.6), near-capacity assignee |
| Risk | No blockers detected, slack in timeline | Multiple blockers, overloaded team |

### Decision Thresholds

```
0.85 ────────────────── AUTO-PROCEED (log only)
0.65 ────────────────── PROCEED WITH WARNING (notify PM, continue)
0.00 ────────────────── ESCALATE (pause, wait for human)
```

### Why This Matters
This design means the system gets **progressively more autonomous** as your team builds history. On day 1, many decisions escalate (not enough data). By month 3, most run automatically because the system has learned your team's skill profiles and project patterns.

---

## 8. API Design

### Base URL: `https://api.techsarathi.app/v1`

### Projects
```
POST   /projects              Create new project (triggers Intake → Planning)
GET    /projects              List all projects with status
GET    /projects/{id}         Get project detail + task list
PATCH  /projects/{id}         Update project metadata
DELETE /projects/{id}         Archive project
```

### Tasks
```
GET    /projects/{id}/tasks   List tasks for a project
POST   /projects/{id}/tasks   Add task manually
PATCH  /tasks/{id}            Update task status/assignee
```

### Escalations (Human Review Queue)
```
GET    /escalations           List pending escalations
GET    /escalations/{id}      Get escalation detail + agent reasoning
POST   /escalations/{id}/approve    Approve agent's suggested action
POST   /escalations/{id}/reject     Reject + provide alternative
```

### Audit
```
GET    /audit                 Full audit log (filterable by agent, date, project)
GET    /audit/{entity_id}     All decisions for a specific project or task
```

### WebSocket (real-time updates)
```
WS     /ws/projects/{id}      Live updates for a project (task changes, new risks)
```

---

## 9. Frontend Design

### Views

**1. Dashboard** (main view)
- Cards for each active project showing: name, health indicator (green/amber/red based on confidence), deadline, % complete
- Escalation count badge — most urgent item shown inline
- "New Project" button

**2. Project Detail**
- Task board (Kanban: Todo | In Progress | Blocked | Done)
- Risk panel (right sidebar): current risk flags from Risk Agent
- Team panel: who's assigned to what, capacity bars
- Confidence timeline: how system confidence has changed over time

**3. Escalation Queue**
- List of pending items needing human decision
- Each card shows: which agent escalated, confidence score, reasoning, suggested action
- Approve / Reject / Override buttons

**4. Audit Log**
- Full timeline of every automated decision
- Filterable by agent, project, date, confidence range
- Export to CSV

---

## 10. Build Phases & Timeline

### Phase 1 — Foundation (Days 1–2)
- [ ] GCP project setup, AlloyDB instance provisioned
- [ ] Database schema created and migrated
- [ ] FastAPI skeleton running locally
- [ ] Docker Compose for local dev (Postgres + backend)
- [ ] ADK installed and hello-world agent working
- [ ] Environment variables configured (`.env`)

### Phase 2 — Core Agents (Days 3–5)
- [ ] `BaseAgent` class and `AgentResult` dataclass
- [ ] Intake Agent — parse + validate requests
- [ ] Planning Agent — task decomposition (use LLM)
- [ ] Staffing Agent — vector search against team_members
- [ ] Risk Agent — rule-based risk scoring
- [ ] Unit tests for each agent in isolation

### Phase 3 — Orchestration (Days 6–7)
- [ ] Execution Coordinator — wire all agents together
- [ ] Parallel execution of Staffing + Risk
- [ ] Confidence aggregation logic
- [ ] Escalation routing (< 0.65 → escalation queue)
- [ ] Communication Agent — basic notification stub
- [ ] Escalation Agent — write to audit_log

### Phase 4 — API Layer (Days 8–9)
- [ ] All REST endpoints implemented and tested
- [ ] Auth middleware (Firebase or GCP IAM)
- [ ] WebSocket for real-time project updates
- [ ] Integration tests (full pipeline, end to end)

### Phase 5 — ReAct Loop (Day 10)
- [ ] APScheduler job running every 5 minutes
- [ ] Observe → Reason → Act cycle implemented
- [ ] Loop tested against a live project in dev

### Phase 6 — Frontend (Days 11–13)
- [ ] Dashboard component
- [ ] Project detail + task board
- [ ] Escalation queue (approve/reject working end-to-end)
- [ ] Audit log view
- [ ] Connected to backend API

### Phase 7 — Polish & Deploy (Days 14–15)
- [ ] Deploy backend to Cloud Run
- [ ] Deploy frontend to Firebase Hosting or Cloud CDN
- [ ] Load test (100 concurrent projects)
- [ ] Demo script prepared
- [ ] README complete

---

## 11. Environment Setup

### Prerequisites
```bash
# Python 3.11+
python --version

# Node 18+ for frontend
node --version

# Google Cloud CLI
gcloud --version

# Docker (for local dev)
docker --version
```

### GCP Setup
```bash
# Create project
gcloud projects create tech-sarathi --name="Tech Sarathi"
gcloud config set project tech-sarathi

# Enable APIs
gcloud services enable alloydb.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable aiplatform.googleapis.com

# Create AlloyDB cluster (takes ~10 min)
gcloud alloydb clusters create sarathi-cluster \
  --region=asia-south1 \
  --password=YOUR_PASSWORD
```

### Backend Local Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy and fill in .env
cp .env.example .env

# Run migrations
python -m db.migrate

# Start dev server
uvicorn api.main:app --reload --port 8000
```

### Frontend Local Setup
```bash
cd frontend
npm install
npm run dev     # starts on http://localhost:5173
```

### Key Environment Variables
```env
# GCP
GOOGLE_CLOUD_PROJECT=tech-sarathi
GOOGLE_APPLICATION_CREDENTIALS=./service-account.json

# AlloyDB
ALLOYDB_HOST=your-alloydb-ip
ALLOYDB_DATABASE=sarathi
ALLOYDB_USER=postgres
ALLOYDB_PASSWORD=your-password

# ADK / Gemini
GOOGLE_ADK_API_KEY=your-adk-key
GEMINI_MODEL=gemini-1.5-pro

# App
CONFIDENCE_AUTO_THRESHOLD=0.85
CONFIDENCE_ESCALATE_THRESHOLD=0.65
REACT_LOOP_INTERVAL_SECONDS=300
```

---

## 12. Testing Strategy

### Unit Tests (per agent)
```python
# tests/unit/test_staffing_agent.py
async def test_staffing_high_confidence():
    agent = StaffingAgent()
    result = await agent.run({
        "task": {"description": "Build React dashboard"},
        "team": MOCK_TEAM   # includes a React-specialist with 20h free
    })
    assert result.confidence > 0.80
    assert result.data["assignee"]["skills"] includes "React"

async def test_staffing_escalates_when_no_match():
    agent = StaffingAgent()
    result = await agent.run({
        "task": {"description": "Quantum cryptography implementation"},
        "team": MOCK_TEAM   # no matching skills
    })
    assert result.confidence < 0.65
    assert agent.should_escalate(result.confidence) == True
```

### Integration Tests
- Full pipeline from user request → audit log entry
- Parallel Staffing + Risk execution within 2 seconds
- Escalation queue correctly populated on low confidence
- Human approve/reject correctly updates task state

### Load Test
- 100 concurrent project creation requests
- ReAct loop stability over 30-minute run
- AlloyDB vector query latency < 200ms at p99

---

## 13. Deployment

### Backend → Cloud Run
```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/sarathi-backend', './backend']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/sarathi-backend']
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    args:
      - 'run'
      - 'deploy'
      - 'sarathi-backend'
      - '--image=gcr.io/$PROJECT_ID/sarathi-backend'
      - '--region=asia-south1'
      - '--platform=managed'
      - '--allow-unauthenticated'
```

### Frontend → Firebase Hosting
```bash
cd frontend
npm run build
firebase deploy --only hosting
```

---

## 14. Known Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| AlloyDB provisioning takes too long | Medium | High | Develop with local Postgres + pgvector first, swap connection string for demo |
| LLM latency too high in agent pipeline | Medium | Medium | Deterministic fallback for every agent — system works without LLM |
| Cold start: no historical data → low confidence on everything | High | Low | Seed database with realistic dummy data for demo |
| ADK breaking changes during development | Low | High | Pin ADK version in requirements.txt, read changelog before updating |
| Vector embeddings give poor skill matches | Medium | Medium | Fall back to keyword/tag matching when similarity < 0.5 |
| Parallel agent execution causes race conditions | Low | Medium | Use asyncio.gather() with independent contexts per agent |

---

## Quick Reference

### Confidence Score Cheat Sheet
- `> 0.85` → Auto-proceed
- `0.65 – 0.85` → Proceed with PM notification
- `< 0.65` → Stop, escalate, wait for human

### Agent Execution Order
1. Intake (sequential)
2. Planning (sequential)
3. Staffing + Risk (parallel)
4. Execution Coordinator (sequential)
5. Communication + Escalation (sequential, post-decision)

### Key Files to Build First
1. `backend/db/schema.sql`
2. `backend/agents/base_agent.py`
3. `backend/agents/intake_agent.py`
4. `backend/core/database.py`
5. `backend/api/main.py`

---

*Last updated: April 2026 | Tech Sarathi — NIRMAN Hackathon*
