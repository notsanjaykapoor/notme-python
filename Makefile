VENV = .venv
PIP = pip
PYTHON = $(VENV)/bin/python3

.PHONY: clean dev dev-docker install test

dev: docker
	. $(VENV)/bin/activate
	./bin/api-server --port 8001

docker:
	docker compose -f docker-compose.yml up -d --no-recreate qdrant
	docker compose -f docker-compose.yml up -d --no-recreate typesense

install: requirements.txt
	uv pip install -r requirements.txt

test:
	. $(VENV)/bin/activate
	pytest

clean:
	rm -rf __pycache__
	rm -rf $(VENV)