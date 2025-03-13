# This file redirects imports to the appropriate modules

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database connection configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./meal_planner.db"
# For PostgreSQL use: SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Database initialization function moved from db_init.py
def init_db():
    # Import models here to ensure they're registered with Base before creating tables
    from app.models import recipes, meal_plans  # Adjust imports based on your actual model modules
    
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully")

# Dependency for getting DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Re-export necessary database components
# This allows any file that previously imported from app.database to continue working

# Find all Pydantic models with Config classes like:
class SomeRecipeSchema(BaseModel):
    # ...existing code...
    
    class Config:
        from_attributes = True  # Changed from orm_mode = True
# ...existing code...