# venv created with 'uv venv --python /Users/sanjaykapoor/.pyenv/shims/python3.12'
VENV = .venv
PIP = pip
PYTHON = $(VENV)/bin/python3

.PHONY: build clean dev dev-docker install test

build:
	./scripts/vps/vps-utils build

dev: docker
	. $(VENV)/bin/activate && ./bin/app-server --port 8001

docker:
	docker compose -f docker-compose.yml up -d --no-recreate qdrant
	docker compose -f docker-compose.yml up -d --no-recreate typesense

install: pyproject.toml
	uv sync

prd:
	. $(VENV)/bin/activate && ./bin/app-server --port 8001

test:
	. $(VENV)/bin/activate && pytest

clean:
	rm -rf __pycache__
	rm -rf $(VENV)