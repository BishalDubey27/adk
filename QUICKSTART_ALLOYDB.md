# Quick Start: Tech Sarathi with AlloyDB

Get Tech Sarathi running with AlloyDB in 3 steps!

## Prerequisites

- Google Cloud account with billing enabled
- gcloud CLI installed
- ~$300-400/month budget (or use free trial credits)

## Step 1: Install gcloud CLI

**Windows:**
Download from: https://cloud.google.com/sdk/docs/install#windows

**Mac:**
```bash
brew install --cask google-cloud-sdk
```

**Linux:**
```bash
curl https://sdk.cloud.google.com | bash
```

## Step 2: Authenticate

```bash
gcloud auth login
gcloud auth application-default login
```

## Step 3: Run Setup Script

**Windows:**
```powershell
cd adk
.\setup-alloydb.ps1
```

**Linux/Mac:**
```bash
cd adk
chmod +x setup-alloydb.sh
./setup-alloydb.sh
```

Follow the prompts:
1. Enter your GCP project ID
2. Choose region (default: asia-south1)
3. Set database password
4. Wait 10-15 minutes for provisioning

## Step 4: Update Configuration

The script will output connection details. Update `backend/.env`:

```env
ALLOYDB_HOST=<your-instance-ip>
ALLOYDB_DATABASE=sarathi
ALLOYDB_USER=postgres
ALLOYDB_PASSWORD=<your-password>
```

## Step 5: Initialize Database

```bash
# Install PostgreSQL client if needed
# Windows: https://www.postgresql.org/download/windows/
# Mac: brew install postgresql
# Linux: sudo apt-get install postgresql-client

# Connect and create database
psql -h <INSTANCE_IP> -U postgres -c "CREATE DATABASE sarathi;"

# Run schema
psql -h <INSTANCE_IP> -U postgres -d sarathi -f backend/db/schema.sql

# Load seed data
psql -h <INSTANCE_IP> -U postgres -d sarathi -f backend/db/seed.sql
```

## Step 6: Start the Application

```bash
# Backend
cd backend
python -m uvicorn api.main:app --reload

# Frontend (new terminal)
cd frontend
npm run dev
```

## Access the App

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Troubleshooting

### Can't connect to AlloyDB?

AlloyDB is private by default. Use Cloud SQL Proxy:

```bash
# Download proxy
curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.0/cloud-sql-proxy.linux.amd64

# Run proxy
./cloud-sql-proxy --address 0.0.0.0 --port 5432 \
  projects/YOUR_PROJECT/locations/asia-south1/clusters/sarathi-cluster/instances/sarathi-primary
```

Then use `localhost` as ALLOYDB_HOST in your .env file.

### Need help?

See full documentation: [ALLOYDB_SETUP.md](ALLOYDB_SETUP.md)

## Clean Up (Delete Resources)

To avoid charges when not using:

```bash
gcloud alloydb instances delete sarathi-primary --cluster=sarathi-cluster --region=asia-south1
gcloud alloydb clusters delete sarathi-cluster --region=asia-south1
```

---

*Tech Sarathi - NIRMAN Hackathon 2026*
