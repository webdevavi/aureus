SHELL := /bin/bash
LOG_DIR := logs

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
	@echo "Infra ready. Starting all services with Honcho..."
	honcho start

stop:
	@echo "Stopping all Aureus processes..."
	-pkill -f "uvicorn backend.api.main:app" || true
	-pkill -f "npm run dev" || true
	-pkill -f "backend.workers.extractor.main" || true
	-pkill -f "backend.workers.renderer.main" || true
	@echo "Local processes stopped."

.PHONY: api frontend extractor renderer dev stop prod view-logs

prod:
	@echo "Starting Aureus in production mode..."
	mkdir -p $(LOG_DIR)
	@echo "Logs will be written to $(LOG_DIR)/honcho.log"
	nohup honcho start -f Procfile.prod > $(LOG_DIR)/honcho.log 2>&1 &
	@echo "All processes started in background."
	@echo "Use 'make view-logs' to follow logs or 'make stop' to terminate."

view-logs:
	tail -f $(LOG_DIR)/honcho.log