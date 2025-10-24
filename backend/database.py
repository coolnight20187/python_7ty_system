"""
Database configuration and connection
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from models.base import Base

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://ty7user:ty7password@localhost:5432/ty7_db"
)

# For development with SQLite
SQLITE_URL = "sqlite:///./ty7_system.db"

# Use SQLite for development if PostgreSQL is not available
try:
    engine = create_engine(DATABASE_URL, echo=True)
    # Test connection
    with engine.connect() as conn:
        conn.execute("SELECT 1")
    print("✅ Connected to PostgreSQL")
except Exception as e:
    print(f"⚠️ PostgreSQL connection failed: {e}")
    print("🔄 Falling back to SQLite")
    engine = create_engine(
        SQLITE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=True
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

def init_database():
    """Initialize database with tables and seed data"""
    create_tables()
    print("🚀 Database initialized successfully")