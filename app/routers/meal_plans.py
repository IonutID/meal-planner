from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime, timedelta
import calendar

from app.db.database import get_db
from app.models import models
from app.schemas import schemas
from app.services.meal_planner import generate_meal_plan

router = APIRouter(
    prefix="/meal-plans",
    tags=["meal-plans"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.MealPlanResponse)
def create_meal_plan(meal_plan: schemas.MealPlanCreate, db: Session = Depends(get_db)):
    # Create the meal plan in the database
    db_meal_plan = models.MealPlan(
        name=meal_plan.name,
        daily_calories=meal_plan.daily_calories,
        daily_protein=meal_plan.daily_protein,
        min_carbs=meal_plan.min_carbs,
        max_carbs=meal_plan.max_carbs,
        min_fat=meal_plan.min_fat,
        max_fat=meal_plan.max_fat,
        num_people=meal_plan.num_people,
        error_margin=meal_plan.error_margin,
        max_repeating_days=meal_plan.max_repeating_days,
        allow_cheat_meal=meal_plan.allow_cheat_meal
    )
    db.add(db_meal_plan)
    db.commit()
    db.refresh(db_meal_plan)
    
    # Generate the meal plan recipes
    meal_plan_recipes = generate_meal_plan(
        db_meal_plan.id,
        db_meal_plan.daily_calories,
        db_meal_plan.daily_protein,
        db_meal_plan.min_carbs,
        db_meal_plan.max_carbs,
        db_meal_plan.min_fat,
        db_meal_plan.max_fat,
        db_meal_plan.error_margin,
        db_meal_plan.max_repeating_days,
        db_meal_plan.allow_cheat_meal,
        db
    )
    
    # Add all recipe assignments to the database
    for recipe_assignment in meal_plan_recipes:
        db_meal_plan_recipe = models.MealPlanRecipe(
            meal_plan_id=db_meal_plan.id,
            recipe_id=recipe_assignment["recipe_id"],
            day=recipe_assignment["day"],
            meal_type=recipe_assignment["meal_type"]
        )
        db.add(db_meal_plan_recipe)
    
    db.commit()
    
    # Format the response
    return get_formatted_meal_plan(db_meal_plan.id, db)

@router.get("/{meal_plan_id}", response_model=schemas.MealPlanResponse)
def read_meal_plan(meal_plan_id: int, db: Session = Depends(get_db)):
    meal_plan = db.query(models.MealPlan).filter(models.MealPlan.id == meal_plan_id).first()
    if meal_plan is None:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    
    return get_formatted_meal_plan(meal_plan_id, db)

@router.get("/", response_model=List[schemas.MealPlanResponse])
def read_meal_plans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    meal_plans = db.query(models.MealPlan).offset(skip).limit(limit).all()
    return [get_formatted_meal_plan(meal_plan.id, db) for meal_plan in meal_plans]

def get_formatted_meal_plan(meal_plan_id: int, db: Session):
    meal_plan = db.query(models.MealPlan).filter(models.MealPlan.id == meal_plan_id).first()
    
    # Get all assigned recipes
    recipe_assignments = db.query(
        models.MealPlanRecipe, 
        models.Recipe
    ).join(
        models.Recipe, 
        models.MealPlanRecipe.recipe_id == models.Recipe.id
    ).filter(
        models.MealPlanRecipe.meal_plan_id == meal_plan_id
    ).all()
    
    # Organize recipes by day and meal type
    days = []
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    total_plan_calories = 0
    total_plan_protein = 0
    total_plan_carbs = 0
    total_plan_fat = 0
    
    for day_num in range(1, 8):  # Monday (1) to Sunday (7)
        day_meals = {
            "day": day_num,
            "day_name": day_names[day_num - 1],
            "breakfast": None,
            "lunch": None,
            "dinner": None,
            "snack": None,
            "total_calories": 0,
            "total_protein": 0,
            "total_carbs": 0,
            "total_fat": 0,
        }
        
        # Find recipes for this day
        day_recipes = [(assignment, recipe) for assignment, recipe in recipe_assignments if assignment.day == day_num]
        
        for assignment, recipe in day_recipes:
            # Add recipe details to the appropriate meal type
            recipe_details = {
                "id": recipe.id,
                "name": recipe.name,
                "calories": recipe.calories,
                "protein": recipe.protein,
                "carbs": recipe.carbs,
                "fat": recipe.fat,
            }
            
            # Update day's meal
            day_meals[assignment.meal_type] = recipe_details
            
            # Update day's nutritional totals
            day_meals["total_calories"] += recipe.calories
            day_meals["total_protein"] += recipe.protein
            day_meals["total_carbs"] += recipe.carbs
            day_meals["total_fat"] += recipe.fat
        
        # Update plan totals
        total_plan_calories += day_meals["total_calories"]
        total_plan_protein += day_meals["total_protein"]
        total_plan_carbs += day_meals["total_carbs"]
        total_plan_fat += day_meals["total_fat"]
        
        days.append(day_meals)
    
    # Create the response
    return {
        "id": meal_plan.id,
        "name": meal_plan.name,
        "daily_calories": meal_plan.daily_calories,
        "daily_protein": meal_plan.daily_protein,
        "min_carbs": meal_plan.min_carbs,
        "max_carbs": meal_plan.max_carbs,
        "min_fat": meal_plan.min_fat,
        "max_fat": meal_plan.max_fat,
        "num_people": meal_plan.num_people,
        "error_margin": meal_plan.error_margin,
        "max_repeating_days": meal_plan.max_repeating_days,
        "allow_cheat_meal": meal_plan.allow_cheat_meal,
        "days": days,
        "total_calories": total_plan_calories,
        "total_protein": total_plan_protein,
        "total_carbs": total_plan_carbs,
        "total_fat": total_plan_fat
    }

@router.get("/{meal_plan_id}/grocery-list", response_model=schemas.GroceryList)
def get_grocery_list(meal_plan_id: int, db: Session = Depends(get_db)):
    # Check if meal plan exists
    meal_plan = db.query(models.MealPlan).filter(models.MealPlan.id == meal_plan_id).first()
    if meal_plan is None:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    
    # Get all recipes in the meal plan
    recipe_assignments = db.query(models.MealPlanRecipe).filter(
        models.MealPlanRecipe.meal_plan_id == meal_plan_id
    ).all()
    
    recipe_ids = [assignment.recipe_id for assignment in recipe_assignments]
    
    # Get all ingredients for these recipes
    ingredients = {}
    
    for recipe_id in recipe_ids:
        recipe_ingredients = db.query(
            models.recipe_ingredient.c.ingredient_id,
            models.recipe_ingredient.c.amount,
            models.recipe_ingredient.c.unit,
            models.Ingredient.name
        ).join(
            models.Ingredient,
            models.recipe_ingredient.c.ingredient_id == models.Ingredient.id
        ).filter(
            models.recipe_ingredient.c.recipe_id == recipe_id
        ).all()
        
        for ing_id, amount, unit, name in recipe_ingredients:
            key = f"{ing_id}:{unit}"
            if key not in ingredients:
                ingredients[key] = {
                    "ingredient_name": name,
                    "total_amount": 0,
                    "unit": unit
                }
            # Scale by number of people
            ingredients[key]["total_amount"] += amount * meal_plan.num_people
    
    return {
        "meal_plan_id": meal_plan_id,
        "items": list(ingredients.values())
    }
