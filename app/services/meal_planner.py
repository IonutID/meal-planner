from sqlalchemy.orm import Session
from typing import List, Dict
import random

from app.models import models
from app.schemas import schemas

def generate_meal_plan(
    meal_plan_id: int,
    daily_calories: float,
    daily_protein: float,
    min_carbs: float,
    max_carbs: float,
    min_fat: float,
    max_fat: float,
    error_margin: float,
    max_repeating_days: int,
    allow_cheat_meal: bool,
    db: Session
) -> List[Dict]:
    """Generate a meal plan for a week with specific nutritional requirements."""
    # Get all recipes from the database
    all_recipes = db.query(models.Recipe).all()
    
    # Categorize recipes by meal type
    # This would normally be based on a field in your database
    # For now, let's use a simple heuristic: calories and time of day
    breakfast_recipes = [r for r in all_recipes if r.calories < daily_calories * 0.3]
    lunch_recipes = [r for r in all_recipes if r.calories >= daily_calories * 0.25 and r.calories <= daily_calories * 0.4]
    dinner_recipes = [r for r in all_recipes if r.calories >= daily_calories * 0.2 and r.calories <= daily_calories * 0.35]
    snack_recipes = [r for r in all_recipes if r.calories < daily_calories * 0.15]
    
    # If not enough recipes in each category, add more from general pool
    if len(breakfast_recipes) < 7:
        breakfast_recipes.extend(random.sample(all_recipes, min(7 - len(breakfast_recipes), len(all_recipes))))
    if len(lunch_recipes) < 7:
        lunch_recipes.extend(random.sample(all_recipes, min(7 - len(lunch_recipes), len(all_recipes))))
    if len(dinner_recipes) < 7:
        dinner_recipes.extend(random.sample(all_recipes, min(7 - len(dinner_recipes), len(all_recipes))))
    if len(snack_recipes) < 7:
        snack_recipes.extend(random.sample(all_recipes, min(7 - len(snack_recipes), len(all_recipes))))
    
    # Calculate calorie targets with error margin
    min_calories = daily_calories * (1 - error_margin)
    max_calories = daily_calories * (1 + error_margin)
    min_protein = daily_protein * (1 - error_margin)
    
    # Create pattern of repeating days based on max_repeating_days
    day_patterns = []
    if max_repeating_days == 1:
        # No repeating days - every day is different
        day_patterns = [[1], [2], [3], [4], [5], [6], [7]]
    elif max_repeating_days == 2:
        # Repeat Mon/Tue, Wed/Thu, Fri/Sat, Sunday unique
        day_patterns = [[1, 2], [3, 4], [5, 6], [7]]
    elif max_repeating_days == 3:
        # Repeat Mon/Tue/Wed, Thu/Fri/Sat, Sunday unique
        day_patterns = [[1, 2, 3], [4, 5, 6], [7]]
    
    # Generate meal plan assignments
    meal_plan_recipes = []
    
    # Create sets to track which recipes are used on which days
    used_recipes = {
        "breakfast": set(),
        "lunch": set(),
        "dinner": set(),
        "snack": set()
    }
    
    # Handle the special case for cheat meal
    cheat_meal_recipe = None
    if allow_cheat_meal:
        # Select a recipe for cheat meal that's higher in calories
        cheat_candidates = [r for r in all_recipes if r.calories > daily_calories * 0.4]
        if cheat_candidates:
            cheat_meal_recipe = random.choice(cheat_candidates)
        else:
            cheat_meal_recipe = random.choice(all_recipes)  # Fallback
    
    # Process each day pattern (group of repeating days)
    for pattern in day_patterns:
        # Choose recipes for this pattern
        selected_breakfast = random.choice([r for r in breakfast_recipes if r.id not in used_recipes["breakfast"]])
        selected_lunch = random.choice([r for r in lunch_recipes if r.id not in used_recipes["lunch"]])
        selected_dinner = random.choice([r for r in dinner_recipes if r.id not in used_recipes["dinner"]])
        selected_snack = random.choice([r for r in snack_recipes if r.id not in used_recipes["snack"]])
        
        used_recipes["breakfast"].add(selected_breakfast.id)
        used_recipes["lunch"].add(selected_lunch.id)
        used_recipes["dinner"].add(selected_dinner.id)
        used_recipes["snack"].add(selected_snack.id)
        
        # Special case: if this pattern includes Sunday (day 7) and cheat meal is allowed
        if 7 in pattern and allow_cheat_meal and cheat_meal_recipe:
            for day in pattern:
                if day == 7:  # Sunday
                    # Add breakfast, cheat meal for lunch, dinner and snack
                    meal_plan_recipes.append({
                        "recipe_id": selected_breakfast.id,
                        "day": day,
                        "meal_type": "breakfast"
                    })
                    meal_plan_recipes.append({
                        "recipe_id": cheat_meal_recipe.id,
                        "day": day,
                        "meal_type": "lunch"
                    })
                    meal_plan_recipes.append({
                        "recipe_id": selected_dinner.id,
                        "day": day,
                        "meal_type": "dinner"
                    })
                    meal_plan_recipes.append({
                        "recipe_id": selected_snack.id,
                        "day": day,
                        "meal_type": "snack"
                    })
                else:
                    # Regular day meals
                    meal_plan_recipes.append({
                        "recipe_id": selected_breakfast.id,
                        "day": day,
                        "meal_type": "breakfast"
                    })
                    meal_plan_recipes.append({
                        "recipe_id": selected_lunch.id,
                        "day": day,
                        "meal_type": "lunch"
                    })
                    meal_plan_recipes.append({
                        "recipe_id": selected_dinner.id,
                        "day": day,
                        "meal_type": "dinner"
                    })
                    meal_plan_recipes.append({
                        "recipe_id": selected_snack.id,
                        "day": day,
                        "meal_type": "snack"
                    })
        else:
            # Regular days without cheat meal
            for day in pattern:
                meal_plan_recipes.append({
                    "recipe_id": selected_breakfast.id,
                    "day": day,
                    "meal_type": "breakfast"
                })
                meal_plan_recipes.append({
                    "recipe_id": selected_lunch.id,
                    "day": day,
                    "meal_type": "lunch"
                })
                meal_plan_recipes.append({
                    "recipe_id": selected_dinner.id,
                    "day": day,
                    "meal_type": "dinner"
                })
                meal_plan_recipes.append({
                    "recipe_id": selected_snack.id,
                    "day": day,
                    "meal_type": "snack"
                })
    
    return meal_plan_recipes
