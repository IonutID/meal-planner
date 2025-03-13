from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel

from app.database import Base

# SQLAlchemy Model
class Recipe(Base):
    __tablename__ = "recipes"
    
    # Add extend_existing=True to fix the error
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    ingredients = Column(Text)
    instructions = Column(Text)
    
    # Relationship with MealPlan if exists
    # meal_plans = relationship("MealPlan", back_populates="recipes")

# Pydantic Models for API
class RecipeBase(BaseModel):
    name: str
    description: str
    ingredients: str
    instructions: str

class RecipeCreate(RecipeBase):
    pass

class RecipeUpdate(RecipeBase):
    pass

class RecipeInDBBase(RecipeBase):
    id: int

    class Config:
        from_attributes = True

class Recipe(RecipeInDBBase):
    pass

class RecipeInDB(RecipeInDBBase):
    pass
