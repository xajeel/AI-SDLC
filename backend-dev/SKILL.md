---
name: backend-dev
description: "**WORKFLOW SKILL** — Python backend development with FastAPI, SQLAlchemy, Alembic, Pydantic, and pytest. USE FOR: creating new API endpoints, adding database models, writing migrations, implementing business logic in interactors, building services, writing tests, adding schemas, creating custom exceptions, and following project architecture rules. DO NOT USE FOR: frontend work, DevOps/Docker configuration, or non-Python tasks."
argument-hint: "Describe the backend feature or change you need (e.g., 'add a payments endpoint', 'create Lead model', 'write tests for auth')"
---

# Python Backend Development

Enforces project architecture, coding standards, and conventions for a FastAPI + SQLAlchemy + Alembic + Pydantic + pytest backend.

## Stack

- **Framework**: FastAPI (async)
- **ORM**: SQLAlchemy (async via `asyncpg`)
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Testing**: pytest + pytest-asyncio + httpx
- **Auth**: JWT (access + refresh tokens)

## Project Structure

```
backend/
├── config/setting.py          # All env vars / secrets (BaseSettings)
├── schema/*.py                # Pydantic request/response models
├── database/
│   ├── models/*.py            # SQLAlchemy ORM models
│   ├── migrations/*.py        # DB CRUD operations (repository layer)
│   └── session.py             # Engine, SessionLocal, get_db
├── interactors/*.py           # Business logic (plain functions, no classes)
├── services/                  # External integrations (email, JWT, Twilio, etc.)
├── routes/*.py                # FastAPI routers (zero logic, delegate to interactors)
├── utils/
│   ├── custom_exceptions.py   # All HTTPException subclasses
│   ├── enums.py               # All Enum types
│   ├── constants.py           # Named constants (no magic literals)
│   ├── logger.py              # Logging config
│   └── prompt_hub/            # LLM prompt templates
├── tests/                     # pytest test suites
├── alembic/versions/          # Alembic migration files
└── main.py                    # App entry point
```

## Layer Rules

Follow these strictly when creating or modifying code. Never violate layer boundaries.

| Layer | Responsibility | NEVER Does |
|---|---|---|
| **Routes** | Accept request, delegate to interactor, return response | Business logic, DB access |
| **Interactors** | All business logic, orchestrate models + services | Direct DB queries |
| **Models (migrations/)** | All DB CRUD operations | Business logic |
| **Services** | External integrations (stateless) | DB access |
| **Schema** | Pydantic validation only | Logic or DB calls |
| **Utils** | Exceptions, enums, constants, logging | Business logic |
| **Config** | Load env vars and secrets | Nothing else |

## Procedure: Adding a New Feature

### Step 1 — Schema

Create Pydantic models in `backend/schema/<module>.py`:

```python
from pydantic import BaseModel, Field


class CreateItemRequest(BaseModel):
    """Request schema for creating an item."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
```

- Validation only — no logic or DB calls
- Every field must have type annotations
- Use `Field(...)` for constraints

### Step 2 — Database Model

Create the SQLAlchemy model in `backend/database/models/<module>.py`:

```python
import uuid

from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID

from database.session import Base


class Item(Base):
    """ORM model for the items table."""

    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
```

- Import and register in `backend/database/models/__init__.py`

### Step 3 — Migration (Repository)

Create CRUD operations in `backend/database/migrations/<module>.py`:

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.item import Item


async def create_item(db: AsyncSession, name: str, description: str | None = None) -> Item:
    """Create and persist a new item."""
    item = Item(name=name, description=description)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def get_item_by_id(db: AsyncSession, item_id: str) -> Item | None:
    """Return item by ID, or None if not found."""
    result = await db.execute(select(Item).where(Item.id == item_id))
    return result.scalar_one_or_none()
```

- Pure DB operations only — no business logic
- Every function must have type hints and docstrings

### Step 4 — Alembic Migration

Generate an Alembic migration for the new table:

```bash
cd backend
uv run alembic revision --autogenerate -m "add_items_table"
```

- Review the generated migration file before applying
- Run `uv run alembic upgrade head` to apply

### Step 5 — Interactor

Create business logic in `backend/interactors/<module>.py`:

```python
from sqlalchemy.ext.asyncio import AsyncSession

from database.migrations import item as item_repo
from schema.item import CreateItemRequest, ItemResponse
from utils.custom_exceptions import ResourceNotFoundException


async def create_item(db: AsyncSession, data: CreateItemRequest) -> ItemResponse:
    """Create a new item and return the response."""
    item = await item_repo.create_item(db, name=data.name, description=data.description)
    return ItemResponse.model_validate(item)


async def get_item(db: AsyncSession, item_id: str) -> ItemResponse:
    """Retrieve an item by ID or raise 404."""
    item = await item_repo.get_item_by_id(db, item_id)
    if not item:
        raise ResourceNotFoundException("Item")
    return ItemResponse.model_validate(item)
```

- **Plain functions only** — never classes
- Orchestrate models + services
- Raise custom exceptions from `utils/custom_exceptions.py`

### Step 6 — Route

Create the API endpoint in `backend/routes/<module>.py`:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from interactors import item as item_interactor
from schema.item import CreateItemRequest, ItemResponse

router = APIRouter(prefix="/v1/items", tags=["Items"])


@router.post("/", response_model=ItemResponse)
async def create_item(
    data: CreateItemRequest,
    db: AsyncSession = Depends(get_db),
) -> ItemResponse:
    """Create a new item."""
    return await item_interactor.create_item(db, data)
```

- **Zero logic** — only delegate to interactor and return
- Register the router in `main.py`

### Step 7 — Tests

Create tests in `backend/tests/<module>/`:

```python
import pytest
from httpx import AsyncClient


class TestCreateItem:
    """Tests for POST /v1/items/."""

    @pytest.mark.asyncio
    async def test_create_item_success(self, client: AsyncClient) -> None:
        """Happy path: create an item."""
        resp = await client.post("/v1/items/", json={"name": "Widget"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Widget"


    @pytest.mark.asyncio
    async def test_create_item_missing_name(self, client: AsyncClient) -> None:
        """Validation: name is required."""
        resp = await client.post("/v1/items/", json={})
        assert resp.status_code == 422
```

- One test file per module
- Cover: happy path, edge cases, exceptions, validation
- Use `TRUNCATE ... CASCADE` for test DB cleanup — never DROP/RECREATE tables
- Mock external services (email, APIs) — never hit real services in tests

## Coding Standards

### Mandatory Type Hints

Every parameter and return type must be annotated:

```python
# ✅
async def get_user(db: AsyncSession, user_id: str) -> User | None: ...

# ❌
async def get_user(db, user_id): ...
```

### Formatting

- **Two blank lines** between every function/method
- **Space after every comma** in signatures, calls, lists, dicts
- **Max ~30 lines** per function — extract helpers if longer

### Import Order

Three groups, one blank line between each:

```python
# 1. Standard library
from typing import Optional

# 2. Third-party
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

# 3. Local
from schema.auth import SignupRequest
from database.session import get_db
```

### Error Handling

- All custom exceptions in `utils/custom_exceptions.py`
- Never expose raw errors — always raise custom exceptions
- Log before raising: `logger.error(f"Failed: {e}")`
- Never bare `except:` or silent `pass`
- Never `raise HTTPException(...)` inline — define a named exception class

### Naming

- `snake_case` for variables, functions, files
- `PascalCase` for classes
- `UPPER_SNAKE_CASE` for constants
- `PascalCase` for enum members (`UserRole.ADMIN`)

### Hard Rules

- **No `print()`** — use `logger` from `utils/logger.py`
- **No hardcoded secrets** — use `config/setting.py`
- **No `os.environ`** outside config — use `setting.VAR_NAME`
- **No raw strings for option sets** — use enums from `utils/enums.py`
- **No magic literals** — use constants from `utils/constants.py`
- **Guard clauses** — return/raise early, never nest deeply
- **DRY** — extract duplicated logic into utility functions
- **Docstrings** — required on every class and public function

## OOP Rules

- **Models, Services, Routes** → classes with instance methods
- **Interactors** → plain module-level functions only
- Default to `self`. Use `@staticmethod` only when zero instance state. Use `@classmethod` only for factory patterns.

## Test Database Setup

Use this pattern for test fixtures (TRUNCATE, not DROP/RECREATE):

```python
@pytest_asyncio.fixture(autouse=True)
async def clean_tables():
    """Ensure tables exist and are clean before each test."""
    async with test_engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()

    async with test_engine.connect() as conn:
        await conn.execute(
            text("TRUNCATE TABLE <tables> CASCADE")
        )
        await conn.commit()
    yield
```

- `NullPool` to avoid lingering connections
- Mock all external services (email, APIs)
- Override `get_db` dependency for test sessions
