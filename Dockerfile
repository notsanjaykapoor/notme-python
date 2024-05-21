FROM python:3.11.7-bullseye as runner
ENV PYTHONUNBUFFERED 1

RUN \
  apt-get -y update && \
  apt-get install -y busybox curl dnsutils gettext netcat tmux xfonts-base xfonts-75dpi && \
  apt-get clean

ADD ./pyproject.toml ./
ADD ./poetry.lock ./
RUN pip install poetry && poetry install

FROM runner as base
ARG APP_VERSION=version
WORKDIR /app
ADD . ./