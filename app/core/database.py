from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, Float, Integer, DateTime
from datetime import datetime
from app.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True
)

# Create async session factory
async_session = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Create base class for declarative models
Base = declarative_base()

# Database session dependency
async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Token model for database
class TokenModel(Base):
    __tablename__ = "tokens"
    
    token_address = Column(String, primary_key=True)
    token_name = Column(String, nullable=False)
    token_ticker = Column(String, nullable=False)
    price_sol = Column(Float, nullable=False)
    market_cap_sol = Column(Float, nullable=False)
    volume_sol = Column(Float, nullable=False)
    liquidity_sol = Column(Float, nullable=False)
    transaction_count = Column(Integer, nullable=False)
    price_1hr_change = Column(Float, nullable=False)
    protocol = Column(String, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Initialize database tables
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)