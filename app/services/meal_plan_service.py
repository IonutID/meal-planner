from sqlalchemy.orm import Session
from collections import defaultdict
from app.models.models import MealPlan, Recipe, Ingredient, meal_plan_recipe, recipe_ingredient
from app.schemas.schemas import GroceryList, GroceryItem
from sqlalchemy import select, join

def generate_grocery_list(db: Session, meal_plan: MealPlan) -> GroceryList:
    # Get all recipes in this meal plan
    query = select([Recipe, meal_plan_recipe.c.day, meal_plan_recipe.c.meal_type]).select_from(
        join(Recipe, meal_plan_recipe, Recipe.id == meal_plan_recipe.c.recipe_id)
    ).where(meal_plan_recipe.c.meal_plan_id == meal_plan.id)
    
    result = db.execute(query).fetchall()
    
    # Build grocery list
    ingredients_needed = defaultdict(lambda: defaultdict(float))
    
    for row in result:
        recipe, day, meal_type = row
        
        # Get ingredients for this recipe
        ingredient_query = select([
            Ingredient.id,
            Ingredient.name,
            recipe_ingredient.c.amount,
            recipe_ingredient.c.unit
        ]).select_from(
            join(Ingredient, recipe_ingredient, Ingredient.id == recipe_ingredient.c.ingredient_id)
        ).where(recipe_ingredient.c.recipe_id == recipe.id)
        
        ingredients = db.execute(ingredient_query).fetchall()
        
        # Scale by number of people and add to tracking
        for ingredient in ingredients:
            ingredient_id, ingredient_name, amount, unit = ingredient
            
            # Scale by number of people
            scaled_amount = amount * meal_plan.num_people / recipe.servings
            
            # Add to tracking
            ingredients_needed[ingredient_name][unit] += scaled_amount
    
    # Convert to output format
    grocery_items = []
    for ingredient_name, units in ingredients_needed.items():
        for unit, amount in units.items():
            grocery_items.append(
                GroceryItem(
                    ingredient_name=ingredient_name,
                    total_amount=amount,
                    unit=unit
                )
            )
    
    return GroceryList(
        meal_plan_id=meal_plan.id,
        items=grocery_items
    )

def generate_meal_plan():
    # Implementation of the meal plan generation logic
    pass
