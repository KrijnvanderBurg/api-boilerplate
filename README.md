# FastAPI Boilerplate

A production-ready FastAPI boilerplate implementing industry best practices for building robust, scalable APIs.

## Features

### 🏗️ **Architecture Best Practices**
- ✅ **Dependency Injection**: Proper use of FastAPI's DI system for services and settings
- ✅ **Layered Architecture**: Clean separation between routers, services, and models
- ✅ **API Versioning**: `/api/v1` prefix for future-proof API evolution
- ✅ **Middleware Support**: CORS middleware with configurable origins
- ✅ **Exception Handling**: Global exception handlers for consistent error responses
- ✅ **Lifespan Events**: Proper startup/shutdown event management

### 🔒 **Validation & Type Safety**
- ✅ **Pydantic Models**: Comprehensive request/response validation with field constraints
- ✅ **Custom Validators**: Business logic validation (e.g., non-empty names, positive prices)
- ✅ **Type Hints**: Full type coverage throughout the codebase
- ✅ **OpenAPI Docs**: Enhanced documentation with detailed descriptions and examples

### 📊 **Observability**
- ✅ **Structured Logging**: Using `structlog` for JSON-formatted logs
- ✅ **Request Logging**: All endpoints log key operations and outcomes
- ✅ **Health Checks**: `/health` and `/ready` endpoints for monitoring

### 🧪 **Testing**
- ✅ **End-to-End Tests**: Comprehensive API testing with `TestClient`
- ✅ **Unit Tests**: Coverage for settings, logging, and core functionality
- ✅ **93% Code Coverage**: Verified by pytest-cov
- ✅ **Test Isolation**: Each test runs independently

### ⚙️ **Configuration**
- ✅ **Environment-based Settings**: Using `pydantic-settings` for configuration
- ✅ **Type-safe Config**: All settings validated and typed
- ✅ **Singleton Pattern**: Cached settings for optimal performance
- ✅ **Configurable Everything**: API prefix, CORS, debug mode, host, port, logging

## Project Structure

```
src/hello_world/
├── __init__.py           # Package initialization
├── main.py           # Application entry point with middleware & handlers
├── dependencies.py       # Dependency injection providers
├── exceptions.py         # Custom exception classes
├── settings.py          # Configuration management
├── models/              # Pydantic models
│   ├── __init__.py
│   └── item.py         # Item schemas with validation
├── routers/            # API route handlers
│   ├── __init__.py
│   ├── health.py       # Health check endpoints
│   └── items.py        # Items CRUD endpoints
├── services/           # Business logic layer
│   ├── __init__.py
│   └── item_service.py # Item service implementation
└── utils/              # Utility modules
    ├── __init__.py
    └── logger.py       # Structured logging setup

tests/
├── conftest.py         # Test configuration
├── e2e/               # End-to-end API tests
│   ├── __init__.py
│   └── test_api.py    # Complete API test suite
└── unit/              # Unit tests
    ├── __init__.py
    ├── test_settings.py
    └── utils/
        └── test_logger.py
```

## Getting Started

### Installation

```bash
# Install dependencies
.github/scripts/poetry-install.sh
```

### Configuration

Set environment variables with the `HELLO_WORLD_` prefix for application settings:

```bash
export HELLO_WORLD_LOG_LEVEL=DEBUG
export HELLO_WORLD_ENVIRONMENT=development
export HELLO_WORLD_DEBUG=true
```

**Design Note**: Configuration is separated into two levels:
- **Application Settings** (env vars): Log level, environment, debug mode - things that vary by deployment environment
- **Deployment Configuration** (code/CLI): API prefix, CORS origins, host, port - things that are typically fixed per deployment or set via CLI/orchestration

To configure CORS origins, edit `API_PREFIX` and `CORS_ORIGINS` constants in `src/hello_world/main.py`:
```python
API_PREFIX = "/api/v1"
CORS_ORIGINS = ["http://localhost:3000", "https://your-domain.com"]
```

To configure host/port at runtime:
```bash
# Via CLI arguments to uvicorn
uvicorn hello_world.main:app --host 0.0.0.0 --port 8080

# Or when running the module
python -m hello_world  # Uses defaults: 0.0.0.0:8000
```

### Running the Application

```bash
# Development mode with auto-reload
python -m hello_world

# Or with custom settings
HELLO_WORLD_PORT=8080 python -m hello_world
```

### Running Tests

```bash
# Run all tests with coverage
.github/scripts/run-pytest.sh

# Run specific test suite
python -m pytest tests/e2e/ -v
python -m pytest tests/unit/ -v

# Run with coverage report
python -m pytest --cov=hello_world --cov-report=term-missing
```

## API Documentation

Once running, access interactive documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API Endpoints

### Health Checks
- `GET /api/v1/health` - Health check endpoint
- `GET /api/v1/ready` - Readiness check endpoint

### Items CRUD
- `POST /api/v1/items` - Create a new item
- `GET /api/v1/items` - List all items
- `GET /api/v1/items/{item_id}` - Get item by ID
- `PUT /api/v1/items/{item_id}` - Update item
- `DELETE /api/v1/items/{item_id}` - Delete item

## Best Practices Implemented

### 1. Dependency Injection
```python
from fastapi import Depends
from hello_world.dependencies import get_item_service

@router.post("/items")
def create_item(
    item: ItemCreate,
    service: ItemService = Depends(get_item_service)
) -> Item:
    return service.create_item(item)
```

### 2. Response Models & Validation
```python
@router.post(
    "/items",
    status_code=status.HTTP_201_CREATED,
    response_model=Item,
    summary="Create a new item",
)
def create_item(item: ItemCreate) -> Item:
    # Pydantic handles validation automatically
    ...
```

### 3. Structured Logging
```python
from hello_world.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Creating item", item_name=item.name, price=item.price)
```

### 4. Exception Handling
```python
@app.exception_handler(HelloWorldError)
async def error_handler(request: Request, e: HelloWorldError):
    return JSONResponse(
        status_code=500,
        content={"detail": str(e), "exit_code": e.exit_code}
    )
```

### 5. Lifespan Management
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Application starting up")
    yield
    # Shutdown
    logger.info("Application shutting down")

app = FastAPI(lifespan=lifespan)
```

