from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# We use the 'postgresql+asyncpg' driver string
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite+aiosqlite:///./nebulax.db"
)

# The Async Engine
engine = create_async_engine(DATABASE_URL, echo=True)

# The Session Factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

# Dependency Injection for FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()