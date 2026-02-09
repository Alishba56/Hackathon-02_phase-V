from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.pool import QueuePool
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("NEON_DB_URL")

if not DATABASE_URL:
    raise ValueError("NEON_DB_URL environment variable is not set")

# Create engine with connection pooling for Neon PostgreSQL
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging during development
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using them
    poolclass=QueuePool
)


def get_session():
    """Dependency function for per-request database sessions"""
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    """Create all database tables on startup"""
    SQLModel.metadata.create_all(engine)
