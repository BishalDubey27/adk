# Tech Sarathi — AI-Powered Project Management System

> **Team:** Tech Sarathi | **Leader:** Bishal Dubey | **Members:** Bishal Dubey , Sushant Patil, Amit Yadav, Khush Patel  
> **Hackathon:** NIRMAN — Amity University Mumbai

## Overview

Tech Sarathi is an AI-powered project management system that uses a multi-agent pipeline to automatically assign tasks, monitor risks, and escalate low-confidence decisions to human project managers.

### Key Features

- **7 AI Agents** working in parallel to manage projects autonomously
- **Confidence-based escalation** (< 0.65 requires human review)
- **Semantic skill matching** using vector embeddings
- **Real-time risk prediction** and blocker detection
- **Full audit trail** of all automated decisions
- **ReAct loop** for continuous project monitoring

## Tech Stack

### Backend
- **Python 3.11** + FastAPI
- **AlloyDB AI** (PostgreSQL + pgvector)
- **Google ADK** for agent orchestration
- **Gemini** for LLM capabilities

### Frontend
- **React 18** + Vite
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **Recharts** for data visualization

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+ (or use Docker)

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
cd adk

# Start all services
docker-compose up -d

# Backend will be available at http://localhost:8000
# Frontend will be available at http://localhost:5173
```

### Option 2: Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your database credentials

# Run database migrations
psql -U postgres -d sarathi -f db/schema.sql

# Start the server
uvicorn api.main:app --reload --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm run dev
```

## Project Structure

```
adk/
├── backend/
│   ├── agents/              # AI agents
│   │   ├── base_agent.py
│   │   ├── intake_agent.py
│   │   ├── planning_agent.py
│   │   ├── staffing_agent.py
│   │   ├── risk_agent.py
│   │   └── execution_coordinator.py
│   ├── api/                 # FastAPI routes
│   │   ├── main.py
│   │   └── routes/
│   ├── core/                # Core utilities
│   │   ├── config.py
│   │   └── database.py
│   ├── db/                  # Database
│   │   └── schema.sql
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── Dashboard.jsx
│   │   │   ├── ProjectDetail.jsx
│   │   │   ├── EscalationQueue.jsx
│   │   │   ├── AuditLog.jsx
│   │   │   └── TeamPanel.jsx
│   │   ├── api/
│   │   │   └── client.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── tailwind.config.js
│
└── docker-compose.yml
```

## API Endpoints

### Projects
- `POST /api/v1/projects` - Create new project (triggers AI pipeline)
- `GET /api/v1/projects` - List all projects
- `GET /api/v1/projects/{id}` - Get project details
- `PATCH /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Archive project

### Tasks
- `GET /api/v1/projects/{id}/tasks` - Get project tasks
- `PATCH /api/v1/tasks/{id}` - Update task

### Escalations
- `GET /api/v1/escalations` - List escalations
- `GET /api/v1/escalations/{id}` - Get escalation details
- `POST /api/v1/escalations/{id}/approve` - Approve/reject escalation

### Audit
- `GET /api/v1/audit` - Get audit log

### Team
- `GET /api/v1/team` - List team members
- `POST /api/v1/team` - Add team member
- `GET /api/v1/team/{id}` - Get member details

## Agent Pipeline

```
User Request
    ↓
[Intake Agent] → Parse & validate
    ↓
[Planning Agent] → Break into tasks
    ↓
[Staffing Agent] ←→ [Risk Agent] (parallel)
    ↓
[Execution Coordinator] → Aggregate confidence
    ↓
Decision: Auto-proceed (>0.85) | Warn (0.65-0.85) | Escalate (<0.65)
```

## Confidence Scoring

- **> 0.85** → Auto-proceed, log decision
- **0.65 - 0.85** → Proceed with warning, notify PM
- **< 0.65** → Pause, escalate to human review

## Development

### Running Tests

```bash
cd backend
pytest tests/
```

### Code Formatting

```bash
# Backend
black backend/
ruff backend/

# Frontend
npm run lint
```

## Deployment

### Backend (Cloud Run)

```bash
gcloud run deploy sarathi-backend \
  --source ./backend \
  --region asia-south1 \
  --allow-unauthenticated
```

### Frontend (Firebase Hosting)

```bash
cd frontend
npm run build
firebase deploy --only hosting
```

## Environment Variables

### Backend (.env)

```env
ALLOYDB_HOST=your-db-host
ALLOYDB_DATABASE=sarathi
ALLOYDB_USER=postgres
ALLOYDB_PASSWORD=your-password
GEMINI_API_KEY=your-api-key
CONFIDENCE_AUTO_THRESHOLD=0.85
CONFIDENCE_ESCALATE_THRESHOLD=0.65
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Team

- **Bishal Dubey** - Team Leader
- **Sahil Prajapati** - Full Stack Developer
- **Amit Yadav** - AI/ML Engineer
- **Khush Patel** - Frontend Developer

---

*Built for NIRMAN Hackathon — Amity University Mumbai | April 2026*
