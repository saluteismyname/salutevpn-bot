from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from database.models import Base

engine = create_async_engine('sqlite+aiosqlite:///database.db', echo=True)

# Фабрика сессий
session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)