SHELL := /bin/bash


up:
	docker compose up -d

down:
	docker compose down

clean:
	docker compose down -v
	rm -rf data/postgres data/minio $(LOG_DIR)

api:
	uvicorn backend.api.main:app --port 8000 --reload

frontend:
	cd frontend && npm run dev

extractor:
	@echo "Starting extractor worker..."
	mkdir -p $(LOG_DIR)
	pkill -f "backend.workers.extractor.main" || true
	python -m backend.workers.extractor.main | tee $(LOG_DIR)/extractor.log

renderer:
	@echo "Starting renderer worker..."
	mkdir -p $(LOG_DIR)
	pkill -f "backend.workers.renderer.main" || true
	python -m backend.workers.renderer.main | tee $(LOG_DIR)/renderer.log

dev:
	@echo "Starting Aureus local development stack..."
	docker compose up -d
	sleep 5
	@echo "Infra ready. Starting all services with Honcho..."
	honcho start

stop:
	@echo "Stopping all Aureus processes..."
	-pkill -f "uvicorn backend.api.main:app" || true
	-pkill -f "npm run dev" || true
	-pkill -f "backend.workers.extractor.main" || true
	-pkill -f "backend.workers.renderer.main" || true
	@echo "Local processes stopped."