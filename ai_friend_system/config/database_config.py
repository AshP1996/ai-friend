# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
# from sqlalchemy.orm import declarative_base
# from pathlib import Path

# Base = declarative_base()

# class DatabaseConfig:
#     def __init__(self):
#         self.engine = None
#         self.async_session = None
        
#     def initialize(self, db_path: Path):
#         database_url = f"sqlite+aiosqlite:///{db_path}"
#         self.engine = create_async_engine(
#             database_url,
#             echo=False,
#             future=True
#         )
#         self.async_session = async_sessionmaker(
#             self.engine,
#             class_=AsyncSession,
#             expire_on_commit=False
#         )
    
#     async def get_session(self) -> AsyncSession:
#         async with self.async_session() as session:
#             yield session
    
#     async def create_tables(self):
#         async with self.engine.begin() as conn:
#             await conn.run_sync(Base.metadata.create_all)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from pathlib import Path

Base = declarative_base()


class DatabaseConfig:
    def __init__(self):
        self.engine = None
        self.async_session = None

    def initialize(self, db_path: Path):
        # Build SQLite URL
        database_url = f"sqlite+aiosqlite:///{db_path}"

        # Create async engine
        self.engine = create_async_engine(
            database_url,
            echo=False,
            future=True,
            pool_pre_ping=True  # prevents "connection lost" errors
        )

        # Create sessionmaker
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    # Generator function to return async DB session
    async def get_session(self):
        async with self.async_session() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    # Create all tables using metadata
    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
