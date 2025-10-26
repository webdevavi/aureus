from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.config.settings import get_settings
from backend.api.routes.reports import router as reports_router
from backend.api.routes.report_files import router as report_files_router
from backend.api.db.models.report import Base
from backend.api.db.session import engine


app = FastAPI(title="Aureus API")

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print(f"API running in {settings.env} mode")


app.include_router(report_files_router)
app.include_router(reports_router)
