FROM python:3.11.7-bullseye as runner

ENV POETRY_CACHE_DIR="/var/cache/pypoetry" \
    POETRY_HOME="/usr/local" \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONUNBUFFERED=1
RUN \
  apt-get -y update && \
  apt-get install -y busybox curl dnsutils gettext netcat tmux xfonts-base xfonts-75dpi && \
  apt-get clean

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install

FROM runner as base
ARG APP_VERSION=version
WORKDIR /app
ADD . ./