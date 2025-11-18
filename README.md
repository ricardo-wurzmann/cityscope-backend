# CityScope Backend

Backend service for the CityScope project, built with FastAPI, SQLAlchemy, and PostgreSQL.

## Getting Started

1. **Install dependencies**
   ```bash
   poetry install
   ```

2. **Copy environment configuration**
   ```bash
   cp .env.example .env
   ```

3. **Run database migrations (after configuring Alembic)**
   ```bash
   alembic upgrade head
   ```

4. **Start the development server**
   ```bash
   uvicorn app.main:app --reload
   ```

## Docker Compose

Alternatively, you can use Docker Compose:

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.

## Project Structure

```
cityscope-backend/
 ├─ app/
 │   ├─ core/
 │   │   ├─ config.py
 │   │   ├─ security.py
 │   │   └─ deps.py
 │   ├─ db/
 │   │   ├─ base.py
 │   │   ├─ session.py
 │   │   └─ migrations/
 │   ├─ models/
 │   │   ├─ user.py
 │   │   ├─ city.py
 │   │   ├─ indicator.py
 │   │   └─ indicator_value.py
 │   ├─ schemas/
 │   │   ├─ auth.py
 │   │   ├─ user.py
 │   │   ├─ city.py
 │   │   └─ indicator.py
 │   ├─ routers/
 │   │   ├─ auth.py
 │   │   ├─ users.py
 │   │   ├─ cities.py
 │   │   └─ indicators.py
 │   ├─ etl/
 │   │   ├─ ibge_cities.py
 │   │   └─ load_sample.py
 │   └─ main.py
 ├─ alembic.ini
 ├─ Dockerfile
 ├─ docker-compose.yml
 ├─ pyproject.toml
 └─ README.md
```
