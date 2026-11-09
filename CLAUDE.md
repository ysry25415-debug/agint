# Product Hunter AI - Development Guide

## Project Structure

```
aigint/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── core/           # Configuration, logging, database connection
│   │   ├── models/         # SQLAlchemy database models
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── connectors/     # Source connector implementations
│   │   ├── agents/         # AI agent implementations
│   │   ├── api/            # FastAPI route handlers
│   │   └── main.py         # Application entry point
│   ├── tests/              # pytest tests
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Backend container
├── worker/                  # Celery worker for background tasks
│   ├── tasks/              # Celery task definitions
│   └── celery_app.py       # Celery application setup
├── frontend/               # Next.js dashboard
│   ├── app/                # Next.js app router pages
│   ├── components/         # UI components
│   ├── lib/                # Frontend utilities
│   └── types/              # TypeScript types
├── nginx/                   # Reverse proxy configuration
├── docker-compose.yml       # Container orchestration
├── .env.example            # Environment variables template
└── README.md               # Project documentation
```

## Development Commands

### Start all services
```bash
docker-compose up -d
```

### Start backend only
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### Start Celery worker
```bash
celery -A worker.celery_app worker --loglevel=info
```

### Run migrations (manual)
```python
from backend.app.models.base import Base
from backend.app.core.database import engine
Base.metadata.create_all(engine)
```

### Run tests
```bash
cd backend
pytest tests/ -v
```

## Adding a New Source Connector

1. Create connector in `backend/app/connectors/`
2. Inherit from `BaseConnector`
3. Implement `discover_products()` and `get_product_details()`
4. Register in the agent that uses it
5. Update database models if needed

## Adding a New Agent

1. Create agent in `backend/app/agents/`
2. Implement the agent logic
3. Add task to `worker/tasks/agents.py`
4. Add to daily pipeline sequence

## API Development

All API routes are in `backend/app/api/routes/`:
- Each route file handles a specific resource
- Use Pydantic schemas for validation
- Return `APIResponse` with `success`, `message`, and `data` fields

## Database Models

Models are in `backend/app/models/base.py`:
- Use SQLAlchemy ORM with relationship() for joins
- Add Index() for frequently queried columns
- Use ForeignKey for relationships
- All models inherit from `Base` from database.py

## Environment Variables

Required in `.env`:
- POSTGRES_PASSWORD - Database password
- TELEGRAM_BOT_TOKEN - Bot token from @BotFather
- TELEGRAM_ALERT_CHAT_ID - Chat ID for notifications
- OPENAI_API_KEY - OpenAI API key

Optional:
- ANTHROPIC_API_KEY - For Claude model
- ALIBABA_API_KEY, ALIEXPRESS_API_KEY - Supplier APIs
- AMAZON_EG_ACCESS_KEY, JUMIA_API_KEY - Marketplace APIs

## Code Style

- Python: Black + isort, type hints required
- TypeScript: Strict mode enabled
- SQL: Use camelCase for column names
- Environment variables: UPPER_SNAKE_CASE

## Testing Strategy

- Unit tests for each connector and agent
- Integration tests for API endpoints
- Start with `backend/tests/test_health.py` as template
- Use pytest-asyncio for async tests

## Deployment Checklist

1. Set all required environment variables
2. Run database migrations
3. Verify all connectors have valid credentials
4. Test Telegram bot webhook
5. Verify CDN for images (if needed)
6. Set up monitoring and alerts