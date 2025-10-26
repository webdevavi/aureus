web: uvicorn backend.api.main:app --port 8000 --reload
frontend: cd frontend && npm run dev
extractor: PYTHONUNBUFFERED=1 python -m backend.workers.extractor.main
renderer: PYTHONUNBUFFERED=1 python -m backend.workers.renderer.main