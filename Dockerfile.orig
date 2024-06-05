FROM python:3.11.9-slim as runner

ENV POETRY_CACHE_DIR="/var/cache/pypoetry" \
    POETRY_HOME="/usr/local" \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONUNBUFFERED=1

RUN apt-get -y update && \
    apt-get install -y busybox curl dnsutils gcc gettext libffi-dev netcat-traditional tmux && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-cache --only=main && \
    rm -rf /var/cache/pypoetry/artifacts && \
    rm -rf /var/cache/pypoetry/cache

FROM runner as base
ARG APP_VERSION=version
WORKDIR /app
ADD . ./