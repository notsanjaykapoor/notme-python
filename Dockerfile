FROM python:3.11.7-bullseye as runner
ENV PYTHONUNBUFFERED 1

RUN \
  apt-get -y update && \
  apt-get install -y busybox curl dnsutils gettext netcat tmux xfonts-base xfonts-75dpi && \
  apt-get clean

ADD ./requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt

FROM runner as base
ARG APP_VERSION=version
WORKDIR /app
ADD . ./