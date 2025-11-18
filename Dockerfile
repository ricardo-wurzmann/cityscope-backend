# syntax=docker/dockerfile:1.6

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/

# Install dependencies directly (pyproject.toml uses setuptools format)
RUN pip install --upgrade pip && \
    pip install fastapi uvicorn python-dotenv pydantic sqlalchemy psycopg[binary] alembic bcrypt pyjwt[crypto] httpx email-validator

COPY app /app/
COPY alembic.ini /app/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
