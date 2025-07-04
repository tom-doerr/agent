from sqlalchemy import create_engine, Column, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/preferences.db")

# Create async engine
engine = create_async_engine(
    DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://"),
    echo=True if os.getenv("TESTING") else False
)

# Create session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


class ImageRecord(Base):
    __tablename__ = "images"
    
    id = Column(String, primary_key=True)
    url = Column(String, nullable=False)
    prompt = Column(Text, nullable=False)
    provider = Column(String, nullable=False)
    latent_vector = Column(JSON, nullable=False)  # Store as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    meta_data = Column(JSON, default={})


class PreferenceRecord(Base):
    __tablename__ = "preferences"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, default="default")
    image_id = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    feedback_type = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class ComparisonRecord(Base):
    __tablename__ = "comparisons"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, default="default")
    winner_id = Column(String, nullable=False)
    loser_id = Column(String, nullable=False)
    comparison_type = Column(String, default="a_b_test")
    timestamp = Column(DateTime, default=datetime.utcnow)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session