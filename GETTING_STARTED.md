# Getting Started with Epics Generator API

This guide will help you set up and start using the Epics Generator API in under 10 minutes.

## Prerequisites

Before you begin, ensure you have:

- ✅ **Python 3.11 or higher** installed
- ✅ **Docker Desktop** installed (for database)
- ✅ **Anthropic API key** (sign up at https://console.anthropic.com/)

## Quick Start (5 minutes)

### Windows Users

1. **Open Command Prompt or PowerShell** in the project directory

2. **Run the quickstart script**:
   ```cmd
   scripts\quickstart.bat
   ```

3. **Edit .env file** when prompted:
   - Open `.env` file in a text editor
   - Replace `your-anthropic-api-key-here` with your actual Anthropic API key
   - Save and close

4. **The script will**:
   - Create a Python virtual environment
   - Install all dependencies
   - Start PostgreSQL with pgvector
   - Run database migrations
   - Start the API server

5. **Access the API**:
   - Open browser to http://localhost:8000/docs
   - You should see the Swagger UI

### Linux/Mac Users

1. **Open Terminal** in the project directory

2. **Make script executable**:
   ```bash
   chmod +x scripts/quickstart.sh
   ```

3. **Run the quickstart script**:
   ```bash
   ./scripts/quickstart.sh
   ```

4. **Edit .env file** when prompted:
   ```bash
   nano .env
   # or use your preferred editor
   ```
   - Replace `your-anthropic-api-key-here` with your actual Anthropic API key
   - Save and exit (Ctrl+X, then Y, then Enter in nano)

5. **The script will**:
   - Create a Python virtual environment
   - Install all dependencies
   - Start PostgreSQL with pgvector
   - Run database migrations
   - Start the API server

6. **Access the API**:
   - Open browser to http://localhost:8000/docs

## Your First API Request

### 1. Get Your API Key

The default development API key is: `dev_key_123456789`

### 2. Test the API

Open a new terminal and try:

```bash
curl -X GET "http://localhost:8000/api/v1/health" \
  -H "X-API-Key: dev_key_123456789"
```

You should see:
```json
{
  "status": "healthy",
  "app_name": "Epics Generator API",
  "version": "1.0.0",
  "environment": "development"
}
```

### 3. Generate Your First Epic

```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev_key_123456789" \
  -d '{
    "project_name": "Task Management App",
    "project_description": "A simple task management application where users can create tasks, set priorities, assign due dates, mark tasks as complete, and organize tasks into categories. Users should be able to filter and search tasks, get reminders for upcoming deadlines, and view their task history.",
    "additional_context": "Target audience is individuals and small teams. Should work on web and mobile."
  }'
```

This will:
- Analyze your project description
- Find similar projects in the database
- Generate comprehensive epics and user stories
- Assign story points
- Create test cases

### 4. View Results

The response will include:
- **Project ID**: For future reference
- **Generation History ID**: For approval/rejection
- **Similar Projects**: Projects used for context
- **Epics**: Generated epics with user stories
- **Story Points**: Estimated effort for each story
- **Test Cases**: Test scenarios for each story

### 5. Approve or Reject

**To approve**:
```bash
curl -X POST "http://localhost:8000/api/v1/approve" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev_key_123456789" \
  -d '{
    "generation_history_id": 1,
    "is_approved": true
  }'
```

**To reject and provide feedback**:
```bash
curl -X POST "http://localhost:8000/api/v1/approve" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev_key_123456789" \
  -d '{
    "generation_history_id": 1,
    "is_approved": false,
    "rejection_reason": "Need more detailed user stories for the notification feature"
  }'
```

### 6. Regenerate (if rejected)

```bash
curl -X POST "http://localhost:8000/api/v1/regenerate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev_key_123456789" \
  -d '{
    "project_id": 1,
    "generation_history_id": 1,
    "rejection_reason": "Need more detailed user stories for the notification feature",
    "additional_instructions": "Please add comprehensive stories for email notifications, push notifications, and notification preferences"
  }'
```

## Using the Swagger UI (Easiest Method)

1. **Open your browser** to http://localhost:8000/docs

2. **Authorize**:
   - Click the "Authorize" button at the top
   - Enter your API key: `dev_key_123456789`
   - Click "Authorize"

3. **Try the API**:
   - Expand the `POST /api/v1/generate` endpoint
   - Click "Try it out"
   - Fill in the request body:
     ```json
     {
       "project_name": "Your Project Name",
       "project_description": "A detailed description of your project...",
       "additional_context": "Any additional requirements"
     }
     ```
   - Click "Execute"
   - View the response below

4. **Explore Other Endpoints**:
   - List projects: `GET /api/v1/projects`
   - View history: `GET /api/v1/history/{project_id}`
   - Approve/reject: `POST /api/v1/approve`

## Common Issues & Solutions

### Issue: "Docker is not running"
**Solution**: Start Docker Desktop and wait for it to fully start

### Issue: "Port 5432 is already in use"
**Solution**: Another PostgreSQL instance is running
```bash
# Stop the container
docker stop epics_postgres

# Or use a different port in docker-compose.yml
```

### Issue: "ModuleNotFoundError"
**Solution**: Activate virtual environment and install dependencies
```bash
# Windows
venv\Scripts\activate
pip install -r requirements.txt

# Linux/Mac
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "Anthropic API Error"
**Solution**: Check your API key in `.env` file
- Verify it's correct
- Ensure you have credits in your Anthropic account
- Check rate limits

### Issue: "Database connection failed"
**Solution**: Ensure PostgreSQL is running
```bash
# Check if container is running
docker ps | grep epics_postgres

# If not, start it
docker start epics_postgres

# Or restart the quickstart script
```

## Next Steps

### Learn More
- Read the [full README](README.md) for detailed documentation
- Check [API Examples](API_EXAMPLES.md) for more usage patterns
- Review [Deployment Guide](DEPLOYMENT.md) for production deployment

### Customize
- Edit `.env` to change configuration
- Add your own API keys to `API_KEYS` in `.env`
- Adjust similarity threshold and other settings

### Development
- Read [Contributing Guide](CONTRIBUTING.md) to contribute
- Run tests: `pytest`
- Format code: `make format`
- Lint code: `make lint`

### Production
- Review [Deployment Guide](DEPLOYMENT.md)
- Set up proper secrets management
- Configure production database
- Set up monitoring and logging

## Useful Commands

### Development
```bash
# Start the server
uvicorn app.main:app --reload

# Run tests
pytest

# Run tests with coverage
pytest --cov=app

# Format code
black app tests
isort app tests

# Run linters
flake8 app tests
mypy app
```

### Docker
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Restart a service
docker-compose restart api
```

### Database
```bash
# Run migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Create new migration
alembic revision --autogenerate -m "description"

# View migration history
alembic history
```

## Getting Help

- **Documentation**: Check the README and other docs
- **Issues**: Open an issue on GitHub
- **API Reference**: Visit http://localhost:8000/docs
- **Examples**: See API_EXAMPLES.md

## What's Next?

Now that you have the API running, you can:

1. **Generate epics for your own projects**
2. **Integrate with your workflow tools** (Jira, GitHub, etc.)
3. **Build a frontend** to interact with the API
4. **Deploy to production** using the deployment guide
5. **Customize the AI prompts** in `app/services/ai_service.py`

Happy coding! 🚀
