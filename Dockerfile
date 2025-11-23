FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app

RUN apt-get update && \
    apt-get install -y build-essential && \
    apt-get clean

COPY requirements.txt /app/
COPY pyproject.toml /app/
COPY alembic.ini /app/

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY app /app/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
