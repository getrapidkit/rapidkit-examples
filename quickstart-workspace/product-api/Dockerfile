
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_HTTP_TIMEOUT=120

WORKDIR /app

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock* /app/

COPY . /app

RUN pip install --no-cache-dir --retries 10 --timeout 60 setuptools==78.1.1 \
    && pip install --no-cache-dir --retries 10 --timeout 60 poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi \
    && apt-get purge -y --auto-remove build-essential curl \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]


