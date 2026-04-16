# Tech Sarathi - Setup Guide

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **Docker Desktop** - [Download](https://www.docker.com/products/docker-desktop/)
- **Git** - [Download](https://git-scm.com/downloads)

## Quick Start (Docker - Recommended)

### Windows

1. Open PowerShell or Command Prompt
2. Navigate to the project directory:
   ```bash
   cd adk
   ```
3. Run the startup script:
   ```bash
   start.bat
   ```

### Linux/Mac

1. Open Terminal
2. Navigate to the project directory:
   ```bash
   cd adk
   ```
3. Run the startup script:
   ```bash
   ./start.sh
   ```

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Manual Setup (Without Docker)

### 1. Database Setup

Install PostgreSQL 15+ and create a database:

```sql
CREATE DATABASE sarathi;
```

Run the schema:

```bash
psql -U postgres -d sarathi -f backend/db/schema.sql
```

Load seed data (optional):

```bash
psql -U postgres -d sarathi -f backend/db/seed.sql
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Edit .env with your database credentials
# Required variables:
# ALLOYDB_HOST=localhost
# ALLOYDB_DATABASE=sarathi
# ALLOYDB_USER=postgres
# ALLOYDB_PASSWORD=your_password

# Start the server
uvicorn api.main:app --reload --port 8000
```

### 3. Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Start development server
npm run dev
```

## Testing the Installation

### 1. Check Backend Health

Open http://localhost:8000/health in your browser. You should see:

```json
{
  "status": "healthy",
  "database": "connected",
  "environment": "development"
}
```

### 2. Check Frontend

Open http://localhost:5173 in your browser. You should see the Tech Sarathi dashboard.

### 3. Create a Test Project

1. Click "New Project" button
2. Fill in the form:
   - Name: "Test Project"
   - Description: "Build a web application with React and Python backend"
   - Priority: High
   - Deadline: (select a future date)
   - Team Size: 3
3. Click "Create Project"
4. The AI agents will process the request and create tasks automatically

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`
**Solution**: Make sure you activated the virtual environment and installed dependencies:
```bash
pip install -r requirements.txt
```

**Problem**: Database connection error
**Solution**: 
- Check if PostgreSQL is running
- Verify credentials in `.env` file
- Ensure database `sarathi` exists

**Problem**: `ImportError: cannot import name 'settings'`
**Solution**: Make sure you're running from the `backend` directory

### Frontend Issues

**Problem**: `Cannot find module 'react'`
**Solution**: Install dependencies:
```bash
npm install
```

**Problem**: API calls failing
**Solution**: 
- Check if backend is running on port 8000
- Verify `VITE_API_URL` in `.env` file
- Check browser console for CORS errors

**Problem**: Blank page
**Solution**: 
- Check browser console for errors
- Ensure all dependencies are installed
- Try clearing browser cache

### Docker Issues

**Problem**: `docker: command not found`
**Solution**: Install Docker Desktop and ensure it's running

**Problem**: Port already in use
**Solution**: Stop other services using ports 5173, 8000, or 5432:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

**Problem**: Database initialization fails
**Solution**: 
```bash
docker-compose down -v  # Remove volumes
docker-compose up -d    # Restart
```

## Development Workflow

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
cd frontend
npm run lint
```

### Viewing Logs

```bash
# Docker
docker-compose logs -f

# Backend (manual)
# Logs appear in terminal where uvicorn is running

# Frontend (manual)
# Logs appear in terminal where vite is running
```

### Stopping Services

```bash
# Docker
docker-compose down

# Manual
# Press Ctrl+C in each terminal
```

## Next Steps

1. **Add Team Members**: Go to Team panel and add your team members
2. **Create Projects**: Use the "New Project" button to create projects
3. **Review Escalations**: Check the Escalations queue for items needing review
4. **View Audit Log**: See all automated decisions in the Audit Log

## Support

For issues or questions:
- Check the [README.md](README.md) for more information
- Review the API documentation at http://localhost:8000/docs
- Contact the team: bishal@techsarathi.com

---

*Tech Sarathi - NIRMAN Hackathon 2026*
