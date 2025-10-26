web: uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
frontend: cd frontend && npm run dev
extractor: PYTHONUNBUFFERED=1 python -m backend.workers.extractor.main
renderer: PYTHONUNBUFFERED=1 python -m backend.workers.renderer.main