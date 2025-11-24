from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, mapped_column, Mapped
from sqlalchemy import Integer, String, Boolean, Text, Float
from sqlalchemy import Column

DATABASE_URL = "sqlite+aiosqlite:///./db.sqlite3"

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    tg_id = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=True)
    balance = Column(Float, default=0.0)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner_tg = Column(Integer, nullable=True)  # telegram id of owner; nullable for public

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
