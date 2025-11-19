# CityScope Backend - Project Structure & Alembic Flow

## Directory Tree

```
cityscope-backend/
├── alembic.ini                    # Alembic config: script_location = app/db/migrations
├── pyproject.toml                 # Dependencies (alembic, sqlalchemy, etc.)
├── Dockerfile                     # WORKDIR /app, COPY app /app/app
├── docker-compose.yml             # Services: db, api
├── .env                           # DATABASE_URL, JWT_SECRET, etc.
│
└── app/                           # Main application package
    ├── __init__.py
    ├── main.py                    # FastAPI app entrypoint
    │
    ├── core/
    │   ├── config.py              # Settings(BaseModel) with DATABASE_URL
    │   ├── security.py            # JWT & password hashing
    │   └── deps.py                # get_current_user, get_db
    │
    ├── db/
    │   ├── base.py                # Base = declarative_base() ⭐
    │   ├── session.py             # engine, SessionLocal, get_db()
    │   └── migrations/
    │       ├── env.py             # ⚠️ MISSING run_migrations functions!
    │       └── versions/          # Migration files go here
    │
    ├── models/
    │   ├── __init__.py            # Imports: City, Indicator, IndicatorValue, User
    │   ├── user.py                # class User(Base)
    │   ├── city.py                # class City(Base)
    │   ├── indicator.py           # class Indicator(Base)
    │   └── indicator_value.py     # class IndicatorValue(Base)
    │
    ├── schemas/
    │   ├── auth.py
    │   ├── user.py
    │   └── ...
    │
    └── routers/
        ├── auth.py
        └── cities.py
```

## Import Chain (How Metadata Should Be Registered)

```
alembic.ini
  └─> script_location = "app/db/migrations"
       └─> Loads: app/db/migrations/env.py
            │
            ├─> BASE_DIR = os.path.join(__file__, "../../../..")
            │   └─> Should resolve to: /app (container) or project root (host)
            │
            ├─> sys.path.insert(0, BASE_DIR)
            │   └─> Makes "app" importable
            │
            ├─> from app.db.base import Base
            │   └─> Base = declarative_base()
            │
            ├─> from app import models
            │   └─> app/models/__init__.py
            │       ├─> from app.models.user import User
            │       ├─> from app.models.city import City
            │       ├─> from app.models.indicator import Indicator
            │       └─> from app.models.indicator_value import IndicatorValue
            │           └─> Each model: class X(Base) → registers table in Base.metadata
            │
            └─> target_metadata = Base.metadata  ⭐ Should contain 4 tables
                 └─> BUT: run_migrations_offline() and run_migrations_online() are MISSING!
                      └─> They need to pass target_metadata to context.configure()
```

## Current env.py (INCOMPLETE)

```python
# app/db/migrations/env.py (lines 1-25)

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.db.base import Base
from app import models

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata  # ✅ Defined

# ❌ MISSING: run_migrations_offline()
# ❌ MISSING: run_migrations_online()
# ❌ MISSING: if context.is_offline_mode(): ... else: ...
```

## Required env.py Structure

```python
# app/db/migrations/env.py (COMPLETE VERSION)

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Path setup
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Import Base and models (registers tables in Base.metadata)
from app.db.base import Base
from app import models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# ✅ REQUIRED: Offline migration function
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,  # ⭐ Passes metadata here
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

# ✅ REQUIRED: Online migration function
def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,  # ⭐ Passes metadata here
        )
        with context.begin_transaction():
            context.run_migrations()

# ✅ REQUIRED: Entry point
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

## Container Context

```
Dockerfile:
  WORKDIR /app
  COPY app /app/app
  COPY alembic.ini /app/

Container filesystem:
  /app/
    ├── alembic.ini
    └── app/
        ├── db/
        │   └── migrations/
        │       └── env.py
        └── models/
            └── ...

alembic.ini:
  script_location = app/db/migrations
  └─> Resolves to: /app/app/db/migrations/env.py ✅

env.py BASE_DIR calculation:
  __file__ = /app/app/db/migrations/env.py
  BASE_DIR = os.path.join(__file__, "../../../..")
  └─> = /app ✅ (correct)
```

## Root Cause Analysis

### Problem
Alembic error: `environment script app/db/migrations/env.py does not provide a MetaData object or sequence of objects to the context.`

### Why
`env.py` defines `target_metadata = Base.metadata` but **never passes it to Alembic's context**. The functions `run_migrations_offline()` and `run_migrations_online()` are missing, so `context.configure(target_metadata=...)` is never called.

### Fix
Add the two migration functions and the entry point conditional to `env.py`. This is a **2-function addition** (~30 lines).

## File Dependencies Map

```
alembic.ini
  ├─> script_location → app/db/migrations/env.py
  └─> sqlalchemy.url → DATABASE_URL from .env

env.py
  ├─> sys.path manipulation → enables "app" import
  ├─> from app.db.base → Base
  ├─> from app import models → registers tables
  └─> target_metadata = Base.metadata

app/db/base.py
  └─> Base = declarative_base()

app/models/__init__.py
  ├─> from app.models.user → User(Base)
  ├─> from app.models.city → City(Base)
  ├─> from app.models.indicator → Indicator(Base)
  └─> from app.models.indicator_value → IndicatorValue(Base)
      └─> Each class definition registers __table__ in Base.metadata

app/core/config.py
  └─> Settings.DATABASE_URL → used by session.py

app/db/session.py
  ├─> from app.core.config → settings
  ├─> from app.db.base → Base
  └─> engine = create_engine(settings.DATABASE_URL)
```

## Verification Checklist

- [x] `alembic.ini` script_location points to correct path
- [x] `app/db/base.py` defines `Base = declarative_base()`
- [x] All models inherit from `app.db.base.Base`
- [x] `app/models/__init__.py` imports all models
- [x] `env.py` imports Base and models
- [x] `env.py` sets `target_metadata = Base.metadata`
- [ ] ❌ `env.py` has `run_migrations_offline()` function
- [ ] ❌ `env.py` has `run_migrations_online()` function
- [ ] ❌ `env.py` has entry point conditional



como rodar:
docker compose up -d --build
