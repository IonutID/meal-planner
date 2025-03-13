from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Table, Date
from sqlalchemy.orm import relationship
from app.db.base import Base  # Import from base.py instead

# Association table for recipe-ingredient relationship
recipe_ingredient = Table(
    'recipe_ingredient',
    Base.metadata,
    Column('recipe_id', Integer, ForeignKey('recipes.id'), primary_key=True),
    Column('ingredient_id', Integer, ForeignKey('ingredients.id'), primary_key=True),
    Column('amount', Float),
    Column('unit', String),
)

# Association table for meal plan-recipe relationship
meal_plan_recipe = Table(
    'meal_plan_recipe',
    Base.metadata,
    Column('meal_plan_id', Integer, ForeignKey('meal_plans.id'), primary_key=True),
    Column('recipe_id', Integer, ForeignKey('recipes.id'), primary_key=True),
    Column('day', Integer),
    Column('meal_type', String),  # breakfast, lunch, dinner, snack
)

class Recipe(Base):
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    instructions = Column(String)
    prep_time = Column(Integer)  # in minutes
    cook_time = Column(Integer)  # in minutes
    servings = Column(Integer)
    
    # Nutritional values per serving
    calories = Column(Float)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)
    
    # Relationships
    ingredients = relationship("Ingredient", secondary=recipe_ingredient, back_populates="recipes")
    meal_plans = relationship("MealPlan", secondary=meal_plan_recipe, back_populates="recipes")

class Ingredient(Base):
    __tablename__ = "ingredients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    calories_per_100g = Column(Float)
    protein_per_100g = Column(Float)
    carbs_per_100g = Column(Float)
    fat_per_100g = Column(Float)
    
    # Relationships
    recipes = relationship("Recipe", secondary=recipe_ingredient, back_populates="ingredients")

class MealPlan(Base):
    __tablename__ = "meal_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    daily_calories = Column(Float)
    daily_protein = Column(Float)
    min_carbs = Column(Float)
    max_carbs = Column(Float)
    min_fat = Column(Float)
    max_fat = Column(Float)
    num_people = Column(Integer)
    days = Column(Integer)
    error_margin = Column(Float, default=0.1)
    max_repeating_days = Column(Integer, default=2)
    allow_cheat_meal = Column(Boolean, default=False)
    
    # Relationships
    recipes = relationship("Recipe", secondary=meal_plan_recipe, back_populates="meal_plans")
