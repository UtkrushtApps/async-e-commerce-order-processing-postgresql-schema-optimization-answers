from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql+asyncpg://postgres:password@localhost:5432/ecommerce')

engine = create_async_engine(
    DATABASE_URL, echo=False, future=True
)

async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)
