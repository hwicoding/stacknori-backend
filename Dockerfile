##########
# Base layer
##########
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl postgresql-client && \
    rm -rf /var/lib/apt/lists/*

##########
# Dependency layer
##########
FROM base AS dependencies

COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r /tmp/requirements.txt

##########
# Development layer
##########
FROM base AS dev

ENV APP_ENV=development

COPY --from=dependencies /install /usr/local
COPY . /app
COPY scripts/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

##########
# Production layer
##########
FROM base AS prod

ENV APP_ENV=production

COPY --from=dependencies /install /usr/local
COPY . /app
COPY scripts/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "90"]

