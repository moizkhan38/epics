# Epics and User Stories Generator API

A powerful REST API that uses AI (Anthropic Claude) to automatically generate comprehensive epics and user stories for SaaS projects, complete with story points, test cases, and similarity-based recommendations.

## Features

- **AI-Powered Generation**: Leverages Anthropic Claude to analyze project descriptions and generate relevant epics and user stories
- **Vector Similarity Search**: Uses pgvector to find similar projects and improve generation quality
- **Automatic Story Points**: Assigns story points using Fibonacci sequence (1, 2, 3, 5, 8, 13, 21)
- **Test Case Generation**: Creates comprehensive test cases for each user story
- **Approval Workflow**: Review and approve or request regeneration with feedback
- **History Tracking**: Complete audit trail of all generations and modifications
- **Clean Architecture**: Layered architecture with separation of concerns
- **Type Safety**: Full Pydantic validation and SQLAlchemy models
- **API Key Authentication**: Secure access control
- **Docker Support**: Easy deployment with Docker Compose

## Technology Stack

- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with pgvector extension
- **AI/ML**: Anthropic Claude API, Sentence Transformers
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Testing**: Pytest with async support
- **Documentation**: OpenAPI/Swagger

## Architecture

```
epics/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/         # API route handlers
│   │       │   ├── generation.py  # Epic generation endpoints
│   │       │   ├── projects.py    # Project CRUD endpoints
│   │       │   └── health.py      # Health check endpoints
│   │       └── router.py          # API router configuration
│   ├── core/                      # Core functionality
│   │   ├── config.py              # Settings management
│   │   ├── security.py            # Authentication
│   │   └── logging.py             # Structured logging
│   ├── db/                        # Database configuration
│   │   └── session.py             # Database session management
│   ├── models/                    # SQLAlchemy models
│   │   ├── project.py
│   │   ├── epic.py
│   │   ├── user_story.py
│   │   └── generation_history.py
│   ├── repositories/              # Data access layer
│   │   ├── project_repository.py
│   │   ├── epic_repository.py
│   │   ├── user_story_repository.py
│   │   └── generation_history_repository.py
│   ├── schemas/                   # Pydantic schemas
│   │   ├── project.py
│   │   ├── epic.py
│   │   ├── user_story.py
│   │   └── generation.py
│   ├── services/                  # Business logic
│   │   ├── ai_service.py          # Anthropic Claude integration
│   │   ├── embedding_service.py   # Text embeddings
│   │   └── generation_service.py  # Generation orchestration
│   └── main.py                    # Application entry point
├── alembic/                       # Database migrations
├── tests/                         # Test suite
│   ├── unit/
│   └── integration/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ with pgvector extension
- Anthropic API key
- Docker & Docker Compose (for containerized deployment)

### Local Development Setup

1. **Clone the repository**
   ```bash
   cd epics
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and configure:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/epics_db
   ANTHROPIC_API_KEY=your-anthropic-api-key-here
   API_KEYS=your-api-key-1,your-api-key-2
   SECRET_KEY=your-secret-key
   ```

5. **Start PostgreSQL with pgvector**
   ```bash
   docker run -d \
     --name epics_postgres \
     -e POSTGRES_PASSWORD=postgres \
     -e POSTGRES_DB=epics_db \
     -p 5432:5432 \
     ankane/pgvector:latest
   ```

6. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

7. **Start the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

8. **Access the API**
   - API: http://localhost:8000
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Docker Deployment

1. **Set environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Check service status**
   ```bash
   docker-compose ps
   ```

4. **View logs**
   ```bash
   docker-compose logs -f api
   ```

5. **Stop services**
   ```bash
   docker-compose down
   ```

## API Usage

### Authentication

All endpoints (except health checks) require API key authentication via the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/v1/projects
```

### Workflow

#### 1. Generate Epics and User Stories

```bash
POST /api/v1/generate
```

**Request Body:**
```json
{
  "project_name": "Task Management SaaS",
  "project_description": "A comprehensive task management platform for teams. Users can create projects, add tasks, assign team members, set deadlines, track progress, and collaborate in real-time. Features include Kanban boards, Gantt charts, time tracking, and reporting.",
  "additional_context": "Target audience: small to medium-sized teams (5-50 people). Must support mobile apps."
}
```

**Response:**
```json
{
  "project_id": 1,
  "generation_history_id": 1,
  "version": 1,
  "status": "pending",
  "similar_projects": [
    {
      "project_id": 5,
      "name": "Project Tracker Pro",
      "description": "...",
      "similarity_score": 0.85
    }
  ],
  "epics": [
    {
      "id": 1,
      "title": "User Authentication and Authorization",
      "description": "Implement secure user authentication...",
      "story_points": 21,
      "priority": "high",
      "user_stories": [
        {
          "id": 1,
          "title": "As a user, I want to register an account so that I can access the platform",
          "description": "...",
          "acceptance_criteria": "...",
          "story_points": 5,
          "priority": "high",
          "test_cases": [
            {
              "id": "TC001",
              "title": "Successful registration",
              "description": "...",
              "steps": ["...", "..."],
              "expected_result": "...",
              "priority": "high"
            }
          ]
        }
      ]
    }
  ],
  "message": "Epics and user stories generated successfully. Please review and approve."
}
```

#### 2. Review Generated Content

Examine the generated epics, user stories, story points, and test cases.

#### 3. Approve or Reject

**Approve:**
```bash
POST /api/v1/approve
```

```json
{
  "generation_history_id": 1,
  "is_approved": true
}
```

**Reject:**
```json
{
  "generation_history_id": 1,
  "is_approved": false,
  "rejection_reason": "Need more detailed user stories for the reporting feature. Also, please include stories for mobile app support."
}
```

#### 4. Regenerate (if rejected)

```bash
POST /api/v1/regenerate
```

```json
{
  "project_id": 1,
  "generation_history_id": 1,
  "rejection_reason": "Need more detailed user stories for the reporting feature",
  "additional_instructions": "Focus on data visualization and export capabilities"
}
```

#### 5. View Generation History

```bash
GET /api/v1/history/{project_id}
```

### Additional Endpoints

#### List Projects
```bash
GET /api/v1/projects?page=1&page_size=10
```

#### Get Project Details
```bash
GET /api/v1/projects/{project_id}
```

#### Delete Project
```bash
DELETE /api/v1/projects/{project_id}
```

#### Health Check
```bash
GET /api/v1/health
GET /api/v1/health/db
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | Epics Generator API |
| `APP_VERSION` | Application version | 1.0.0 |
| `ENVIRONMENT` | Environment (development/production) | development |
| `DEBUG` | Debug mode | False |
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `ANTHROPIC_API_KEY` | Anthropic API key | Required |
| `ANTHROPIC_MODEL` | Claude model to use | claude-3-5-sonnet-20241022 |
| `API_KEYS` | Comma-separated API keys | Required |
| `SECRET_KEY` | Secret key for security | Required |
| `EMBEDDING_MODEL` | Sentence transformer model | all-MiniLM-L6-v2 |
| `SIMILARITY_THRESHOLD` | Minimum similarity score | 0.7 |
| `MAX_SIMILAR_PROJECTS` | Max similar projects to return | 5 |

## Testing

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
```

### Run specific test types
```bash
pytest tests/unit         # Unit tests only
pytest tests/integration  # Integration tests only
```

### Run specific test file
```bash
pytest tests/unit/test_embedding_service.py
```

## Database Migrations

### Create a new migration
```bash
alembic revision --autogenerate -m "description"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback migration
```bash
alembic downgrade -1
```

### View migration history
```bash
alembic history
```

## Performance Considerations

- **Response Time**: Target <200ms for simple queries
- **Database Connection Pooling**: Configured for 10 connections with 20 overflow
- **Vector Index**: Uses IVFFlat index for fast similarity search
- **Async Operations**: Full async/await support for non-blocking I/O
- **Caching**: Embedding service uses singleton pattern

## Security

- **API Key Authentication**: All endpoints protected except health checks
- **Input Validation**: Pydantic schemas validate all input
- **SQL Injection Prevention**: SQLAlchemy parameterized queries
- **CORS Configuration**: Configurable CORS policies
- **Rate Limiting**: Can be configured per endpoint
- **Secrets Management**: Environment variable based configuration

## Monitoring & Logging

- **Structured Logging**: JSON formatted logs with structlog
- **Request Logging**: All requests logged with timing
- **Error Tracking**: Detailed error logs with stack traces
- **Health Checks**: Database and application health endpoints
- **Metrics**: Process time headers on all responses

## Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check database logs
docker logs epics_postgres
```

### pgvector Extension Not Found
```sql
-- Connect to database and enable extension
CREATE EXTENSION IF NOT EXISTS vector;
```

### API Key Authentication Fails
- Verify `API_KEYS` in `.env` matches your request header
- Check header name matches `API_KEY_HEADER` setting

### Anthropic API Errors
- Verify `ANTHROPIC_API_KEY` is valid
- Check API rate limits and quota
- Review model availability

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Roadmap

- [ ] WebSocket support for real-time generation updates
- [ ] Fine-tuning support for custom datasets
- [ ] Export to Jira, GitHub Issues, Linear
- [ ] Team collaboration features
- [ ] Custom story point scales
- [ ] AI model selection per request
- [ ] Batch generation API
- [ ] GraphQL API support
