from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List


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
    
    for recipe_assignment in meal_plan_recipes:
       db.execute(
            models.meal_plan_recipe.insert().values(
                meal_plan_id=db_meal_plan.id,
                recipe_id=recipe_assignment["recipe_id"],
                day=recipe_assignment["day"],
                meal_type=recipe_assignment["meal_type"]
            )
        )
    db.commit()
    
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
    # Get the meal plan
    meal_plan = db.query(models.MealPlan).filter(models.MealPlan.id == meal_plan_id).first()
    
    if not meal_plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    
    # Get recipe assignments using the association table
    recipe_assignments = db.query(
        models.meal_plan_recipe.c.day,
        models.meal_plan_recipe.c.meal_type,
        models.Recipe
    ).join(
        models.Recipe, 
        models.meal_plan_recipe.c.recipe_id == models.Recipe.id
    ).filter(
        models.meal_plan_recipe.c.meal_plan_id == meal_plan_id
    ).all()
    
    # Format meal plan response
    meals = []
    total_calories = 0.0
    total_protein = 0.0
    total_carbs = 0.0
    total_fat = 0.0
    days_set = set()
    day_stats = {}
    day_meals = {}
    
    # Helper function to get day name
    def get_day_name(day_number):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return days[(day_number - 1) % 7]
    
    # Process all recipe assignments
    for day, meal_type, recipe in recipe_assignments:
        # Create meal entry for the response list
        meal_entry = {
            "day": day,
            "meal_type": meal_type,
            "recipe_id": recipe.id,
            "recipe_name": recipe.name,
            "calories": recipe.calories,
            "protein": recipe.protein,
            "carbs": recipe.carbs,
            "fat": recipe.fat,
            "servings": recipe.servings
        }
        meals.append(meal_entry)
        
        # Track nutritional info per day
        if day not in day_stats:
            day_stats[day] = {
                "day": day,
                "day_name": get_day_name(day),
                "total_calories": 0.0,
                "total_protein": 0.0,
                "total_carbs": 0.0,
                "total_fat": 0.0
            }
            day_meals[day] = {
                "breakfast": None,
                "lunch": None,
                "dinner": None,
                "snack": None
            }
        
        # Add meal to the appropriate meal type for this day
        day_meals[day][meal_type] = meal_entry
        
        days_set.add(day)
        day_stats[day]["total_calories"] += recipe.calories
        day_stats[day]["total_protein"] += recipe.protein
        day_stats[day]["total_carbs"] += recipe.carbs
        day_stats[day]["total_fat"] += recipe.fat
        
        # Track overall totals
        total_calories += recipe.calories
        total_protein += recipe.protein
        total_carbs += recipe.carbs
        total_fat += recipe.fat
    
    # Format days as a list of objects
    days = []
    for day_number in sorted(days_set):
        day_data = day_stats[day_number].copy()
        # Add meal type fields
        day_data.update(day_meals[day_number])
        days.append(day_data)
    
    # Return formatted response
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
        "meals": meals,
        "days": days,
        "total_calories": total_calories,
        "total_protein": total_protein,
        "total_carbs": total_carbs,
        "total_fat": total_fat
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
