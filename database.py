from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os


# SQLite database URL — use DATABASE_URL env var if set (required on Azure Functions
# where the app directory is read-only; set DATABASE_URL=sqlite:////tmp/rbyte_ai.db
# in Application Settings, or point to an Azure SQL connection string).
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./rbyte_ai.db")

# Create SQLAlchemy engine
_connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=_connect_args
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()
