from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

class IngredientBase(BaseModel):
    name: str
    calories_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float

class IngredientCreate(IngredientBase):
    pass

class Ingredient(IngredientBase):
    id: int
    
    class Config:
        orm_mode = True

class RecipeIngredient(BaseModel):
    ingredient_id: int
    amount: float
    unit: str

class RecipeBase(BaseModel):
    name: str
    description: Optional[str] = None
    instructions: str
    prep_time: int
    cook_time: int
    servings: int
    calories: float
    protein: float
    carbs: float
    fat: float

class RecipeCreate(RecipeBase):
    ingredients: List[RecipeIngredient]

class RecipeIngredientResponse(BaseModel):
    ingredient_id: int
    ingredient_name: str
    amount: float
    unit: str
    
    class Config:
        orm_mode = True

# Update RecipeResponse to include the detailed ingredients
class RecipeResponse(RecipeBase):
    id: int
    ingredients: List[RecipeIngredientResponse] = []
    
    class Config:
        orm_mode = True

class MealPlanBase(BaseModel):
    name: str
    daily_calories: float
    daily_protein: float
    min_carbs: float
    max_carbs: float
    min_fat: float
    max_fat: float
    num_people: int = Field(gt=0, description="Number of people this meal plan is for")
    error_margin: float = Field(default=0.1, ge=0, le=0.5, description="Error margin for daily calories and macros (0.1 = 10%)")
    max_repeating_days: int = Field(default=2, ge=1, le=3, description="Maximum number of days to repeat meal combinations")
    allow_cheat_meal: bool = Field(default=False, description="Whether to allow a cheat meal on Sunday lunch")

class MealTypeEnum(str, Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"

class MealPlanCreate(MealPlanBase):
    pass

class MealPlanRecipe(BaseModel):
    recipe_id: int
    day: int  # 1 = Monday, 2 = Tuesday, ..., 7 = Sunday
    meal_type: MealTypeEnum

class DayMeals(BaseModel):
    day: int  # 1 = Monday, 2 = Tuesday, ..., 7 = Sunday
    day_name: str
    breakfast: Optional[Dict] = None
    lunch: Optional[Dict] = None
    dinner: Optional[Dict] = None
    snack: Optional[Dict] = None
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float

class MealPlanResponse(MealPlanBase):
    id: int
    days: List[DayMeals]
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    
    class Config:
        orm_mode = True

class GroceryItem(BaseModel):
    ingredient_name: str
    total_amount: float
    unit: str

class GroceryList(BaseModel):
    meal_plan_id: int
    items: List[GroceryItem]
