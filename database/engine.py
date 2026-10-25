from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import os

engine = create_async_engine(f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}", echo=True)

# Фабрика сессий
session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

class Base(DeclarativeBase):
    pass