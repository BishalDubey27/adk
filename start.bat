@echo off
echo Starting Tech Sarathi...
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Docker is not running. Please start Docker first.
    exit /b 1
)

echo Starting services with Docker Compose...
docker-compose up -d

echo.
echo Waiting for services to start...
timeout /t 10 /nobreak >nul

echo.
echo Tech Sarathi is running!
echo.
echo Backend API:  http://localhost:8000
echo Frontend UI:  http://localhost:5173
echo API Docs:     http://localhost:8000/docs
echo.
echo To stop: docker-compose down
echo To view logs: docker-compose logs -f
