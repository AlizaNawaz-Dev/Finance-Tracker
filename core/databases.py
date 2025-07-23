from .config import settings
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from sqlalchemy.orm import sessionmaker,declarative_base


SQLALCHEMY_DATABASE_URL=f'postgresql+asyncpg://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

engine=create_async_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal=sessionmaker(bind=engine,class_=AsyncSession,expire_on_commit=False,autoflush=False,)

async def get_db():
    async with SessionLocal() as session:
        yield session
   
Base=declarative_base()