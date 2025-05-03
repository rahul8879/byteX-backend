import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database URL from environment variables
# DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL = "sqlite:///./rbyte_ai.db"

def check_database_tables():
    """Check all tables in the database and their record counts"""
    if not DATABASE_URL:
        logger.error("DATABASE_URL environment variable not found")
        return {"error": "DATABASE_URL not found"}
    
    try:
        # Create engine and session
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Get list of all tables
        tables_query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = db.execute(tables_query).fetchall()
        
        results = {}
        
        # Get count for each table
        for table in tables:
            table_name = table[0]
            count_query = text(f"SELECT COUNT(*) FROM {table_name}")
            count = db.execute(count_query).scalar()
            
            # Get sample records if count > 0
            sample = []
            if count > 0:
                sample_query = text(f"SELECT * FROM {table_name} LIMIT 2")
                sample_records = db.execute(sample_query).fetchall()
                for record in sample_records:
                    sample.append(dict(record._mapping))
            
            results[table_name] = {
                "count": count,
                "sample": sample
            }
        
        return results
    
    except Exception as e:
        logger.error(f"Error checking database tables: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    results = check_database_tables()
    print(results)
