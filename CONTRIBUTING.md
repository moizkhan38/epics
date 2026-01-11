# Contributing Guide

Thank you for your interest in contributing to the Epics Generator API! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Bugs

1. **Check existing issues** to avoid duplicates
2. **Create a new issue** with:
   - Clear, descriptive title
   - Steps to reproduce the bug
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Relevant logs or screenshots

### Suggesting Features

1. **Open a feature request issue** with:
   - Clear description of the feature
   - Use cases and benefits
   - Potential implementation approach
   - Examples if applicable

### Contributing Code

#### Setup Development Environment

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/epics.git
   cd epics
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   ```

4. **Set up pre-commit hooks** (recommended)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

5. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. **Start PostgreSQL**
   ```bash
   docker run -d --name epics_postgres \
     -e POSTGRES_PASSWORD=postgres \
     -e POSTGRES_DB=epics_db \
     -p 5432:5432 \
     ankane/pgvector:latest
   ```

7. **Run migrations**
   ```bash
   alembic upgrade head
   ```

#### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

2. **Make your changes**
   - Follow the coding standards (see below)
   - Write tests for new functionality
   - Update documentation as needed

3. **Run tests**
   ```bash
   pytest
   pytest --cov=app --cov-report=html
   ```

4. **Format code**
   ```bash
   black app tests
   isort app tests
   ```

5. **Lint code**
   ```bash
   flake8 app tests
   mypy app
   ```

6. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: add feature description"
   ```

   Use conventional commit messages:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `style:` Code style changes (formatting, etc.)
   - `refactor:` Code refactoring
   - `test:` Adding or updating tests
   - `chore:` Maintenance tasks

7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill in the PR template

#### Pull Request Guidelines

- **Title**: Clear, descriptive title following conventional commits
- **Description**:
  - What changes were made
  - Why these changes were necessary
  - Related issue numbers
  - Breaking changes (if any)
- **Tests**: All tests must pass
- **Documentation**: Update relevant documentation
- **Code Review**: Be responsive to feedback

## Coding Standards

### Python Style Guide

Follow PEP 8 with these specifics:

- **Line Length**: 100 characters maximum
- **Imports**: Use `isort` for organizing imports
- **Formatting**: Use `black` for code formatting
- **Type Hints**: Add type hints to all functions
- **Docstrings**: Use Google-style docstrings

### Example Code Style

```python
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.repositories.base_repository import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project model.

    This class provides data access methods for the Project entity,
    including vector similarity search capabilities.

    Attributes:
        model: The SQLAlchemy model class
        db: Database session
    """

    def __init__(self, db: AsyncSession):
        """Initialize the repository.

        Args:
            db: Async database session
        """
        super().__init__(Project, db)

    async def find_similar_projects(
        self,
        embedding: List[float],
        limit: int = 5,
        threshold: float = 0.7
    ) -> List[Project]:
        """Find similar projects using vector similarity.

        Args:
            embedding: Query embedding vector
            limit: Maximum number of results to return
            threshold: Minimum similarity score (0-1)

        Returns:
            List of similar Project instances

        Raises:
            ValueError: If embedding dimension is invalid
        """
        if len(embedding) != 384:
            raise ValueError("Embedding must have 384 dimensions")

        # Implementation...
        pass
```

### Testing Guidelines

1. **Test Coverage**: Aim for >80% code coverage
2. **Test Organization**:
   - Unit tests in `tests/unit/`
   - Integration tests in `tests/integration/`
3. **Test Naming**: Use descriptive names
   ```python
   def test_create_project_with_valid_data():
       """Test creating a project with valid input data"""
       pass

   def test_create_project_fails_with_invalid_email():
       """Test that project creation fails with invalid email"""
       pass
   ```

4. **Test Structure**: Follow Arrange-Act-Assert pattern
   ```python
   @pytest.mark.asyncio
   async def test_generate_epics_success(db_session, sample_project):
       # Arrange
       service = GenerationService(db_session)
       request = GenerationRequest(
           project_name="Test Project",
           project_description="A test project description..."
       )

       # Act
       result = await service.generate_epics(request)

       # Assert
       assert result.project_id is not None
       assert len(result.epics) > 0
       assert result.status == "pending"
   ```

5. **Fixtures**: Use pytest fixtures for reusable test data
   ```python
   @pytest.fixture
   async def sample_project(db_session):
       """Create a sample project for testing"""
       project = Project(
           name="Test Project",
           description="Test description"
       )
       db_session.add(project)
       await db_session.commit()
       return project
   ```

### API Design Guidelines

1. **RESTful Conventions**:
   - Use plural nouns for resources (`/projects`, not `/project`)
   - Use proper HTTP methods (GET, POST, PUT, DELETE)
   - Return appropriate status codes

2. **Response Format**:
   ```python
   # Success
   {
       "data": {...},
       "message": "Success message"
   }

   # Error
   {
       "error": "error_code",
       "message": "Human-readable message",
       "details": {...}
   }
   ```

3. **Validation**: Use Pydantic models for request/response validation

4. **Documentation**: Add OpenAPI documentation
   ```python
   @router.post(
       "/projects",
       response_model=ProjectResponse,
       status_code=status.HTTP_201_CREATED,
       summary="Create a new project",
       description="Creates a new project with the provided details",
       tags=["Projects"]
   )
   async def create_project(
       request: ProjectCreate,
       db: AsyncSession = Depends(get_db)
   ):
       """Create a new project"""
       pass
   ```

## Database Migrations

### Creating Migrations

1. **Make model changes** in `app/models/`

2. **Generate migration**
   ```bash
   alembic revision --autogenerate -m "description of changes"
   ```

3. **Review generated migration** in `alembic/versions/`

4. **Test migration**
   ```bash
   # Apply migration
   alembic upgrade head

   # Rollback to test downgrade
   alembic downgrade -1

   # Reapply
   alembic upgrade head
   ```

5. **Commit migration file**

### Migration Guidelines

- Always review auto-generated migrations
- Test both upgrade and downgrade
- Keep migrations small and focused
- Add comments for complex operations
- Never modify existing migrations

## Documentation

### Code Documentation

- Add docstrings to all public functions and classes
- Use type hints
- Include examples for complex functions
- Keep docstrings up to date with code changes

### API Documentation

- Update OpenAPI schema when adding/changing endpoints
- Provide examples in endpoint descriptions
- Document all request/response models
- Include error responses

### README Updates

- Update README.md when adding new features
- Keep installation instructions current
- Add examples for new functionality
- Update architecture diagrams if needed

## Performance Considerations

- Use async/await for I/O operations
- Batch database queries when possible
- Add database indexes for frequently queried fields
- Use connection pooling
- Profile code to identify bottlenecks

## Security Guidelines

- Never commit secrets or API keys
- Use environment variables for configuration
- Validate all user input
- Use parameterized queries (SQLAlchemy handles this)
- Implement rate limiting for public endpoints
- Keep dependencies updated

## Questions?

If you have questions about contributing:

1. Check existing documentation
2. Search closed issues
3. Ask in a new issue with the `question` label
4. Join our community chat (if available)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

## Recognition

Contributors will be recognized in the project README and release notes.

Thank you for contributing! 🎉
