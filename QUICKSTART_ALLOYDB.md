# AlloyDB Quick Start — Tech Sarathi

Get the Tech Sarathi backend running with AlloyDB in 5 minutes.

## Option A: Local Development (Docker Compose)

No GCP account needed. Uses local PostgreSQL + pgvector.

```powershell
# 1. Start all services
docker-compose up -d

# 2. Wait for health check, then verify
curl http://localhost:8000/health

# 3. Generate skill embeddings (uses fallback hash-based embeddings locally)
curl -X POST http://localhost:8000/api/v1/team/refresh-all-embeddings

# 4. Open the frontend
# http://localhost:5173
```

## Option B: AlloyDB on GCP

### Prerequisites
- GCP project: `nirman-project-493414`
- `gcloud` CLI authenticated
- Billing enabled

### Steps

```powershell
# 1. Run the setup script (provisions AlloyDB cluster + instance)
.\setup-alloydb.ps1

# 2. Initialize the database (creates schema + seed data)
.\init-database.ps1

# 3. Update backend/.env with connection details from step 1 output

# 4. Start the backend
cd backend
python -m uvicorn api.main:app --reload

# 5. Generate real skill embeddings via Vertex AI
curl -X POST http://localhost:8000/api/v1/team/refresh-all-embeddings
```

## Connection Modes

| Mode | When to Use | Config |
|---|---|---|
| **Direct** (raw asyncpg) | Local dev, Docker Compose | `ALLOYDB_USE_CONNECTOR=false` |
| **AlloyDB Connector** | Cloud Run, GKE, production | `ALLOYDB_USE_CONNECTOR=true` |
| **IAM Auth** | Service accounts, no passwords | `ALLOYDB_IAM_AUTH=true` |

## Embedding Modes

| Mode | When Used | Quality |
|---|---|---|
| **Vertex AI** | GCP credentials available | ⭐⭐⭐ Best |
| **Gemini API** | `GEMINI_API_KEY` set | ⭐⭐ Good |
| **Hash fallback** | No credentials | ⭐ Dev only |

## Verify Everything Works

```powershell
# Health check
curl http://localhost:8000/health
# Expected: {"status":"healthy","database":"connected","environment":"development"}

# List team members
curl http://localhost:8000/api/v1/team

# Create a project (triggers full AI pipeline with vector search)
curl -X POST http://localhost:8000/api/v1/projects `
  -H "Content-Type: application/json" `
  -d '{"name":"Test Project","description":"A test project with backend API","priority":"high","deadline":"2026-12-31"}'
```
