SHELL := /bin/bash
LOG_DIR := logs
PM2_CONFIG := pm2.config.js

api:
	uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload

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
	@echo "Starting all services with Honcho (development mode)..."
	mkdir -p $(LOG_DIR)
	honcho start

prod:
	@echo "Starting Aureus in production mode with PM2..."
	mkdir -p $(LOG_DIR)
	pm2 start $(PM2_CONFIG)
	pm2 save
	@echo "All processes started. Use 'make logs' or 'make stop' for management."

stop:
	@echo "Stopping all Aureus PM2 processes..."
	pm2 stop all || true
	pm2 delete all || true
	@echo "All processes stopped."

restart:
	@echo "Restarting all PM2 processes..."
	pm2 restart all --update-env

logs:
	@echo "Following all PM2 logs..."
	pm2 logs

status:
	@echo "Process status:"
	pm2 status

view-log:
	@echo "Showing Honcho development log..."
	tail -f $(LOG_DIR)/honcho.log || true

clean:
	@echo "Cleaning logs..."
	rm -rf $(LOG_DIR) && mkdir -p $(LOG_DIR)

.PHONY: api frontend extractor renderer dev prod stop restart logs status view-log clean