FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      curl \
    && rm -rf /var/lib/apt/lists/*
# No PDF/OCR system deps here — those live in the docling container.

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src

RUN pip install --upgrade pip && pip install -e .

RUN useradd --create-home --uid 1000 lumen && \
    mkdir -p /data /models && chown -R lumen:lumen /app /data /models

USER lumen

EXPOSE 8000

CMD ["uvicorn", "lumen.main:app", "--host", "0.0.0.0", "--port", "8000"]
