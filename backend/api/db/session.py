from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from backend.api.config.settings import get_settings


settings = get_settings()

DATABASE_URL = (
    f"postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}"
    f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
)

engine = create_async_engine(DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = sessionmaker(  # type: ignore[call-overload]
    bind=engine,  # type: ignore[call-overload]
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_session() -> AsyncSession:  # type: ignore[call-overload]
    async with AsyncSessionLocal() as session:  # type: ignore[call-overload]
        yield session  # type: ignore[call-overload]
