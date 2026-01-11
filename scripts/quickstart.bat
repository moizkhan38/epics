@echo off
REM Quickstart script for Epics Generator API (Windows)

echo ============================================
echo Epics Generator API - Quick Start (Windows)
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python 3 is not installed. Please install Python 3.11+ first.
    exit /b 1
)

echo Found Python
python --version

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

echo Found Docker
docker --version
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

REM Check if .env exists
if not exist ".env" (
    echo.
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit .env and add your ANTHROPIC_API_KEY
    echo.
    pause
)

REM Start PostgreSQL with pgvector
echo.
echo Starting PostgreSQL with pgvector...
docker ps -a | findstr epics_postgres >nul 2>&1
if errorlevel 1 (
    docker run -d --name epics_postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=epics_db -p 5432:5432 ankane/pgvector:latest
) else (
    docker start epics_postgres
)

REM Wait for PostgreSQL to be ready
echo Waiting for PostgreSQL to be ready...
timeout /t 5 /nobreak >nul

REM Run migrations
echo.
echo Running database migrations...
alembic upgrade head

REM Start the application
echo.
echo Starting the application...
echo.
echo API will be available at:
echo   - Main API: http://localhost:8000
echo   - Swagger UI: http://localhost:8000/docs
echo   - ReDoc: http://localhost:8000/redoc
echo.
echo API Key: dev_key_123456789
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
