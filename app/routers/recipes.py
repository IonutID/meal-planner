from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models import models
from app.schemas import schemas
from app.utils.db_utils import retry_on_db_lock

router = APIRouter(
    prefix="/recipes",
    tags=["recipes"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.RecipeResponse)
def create_recipe(recipe: schemas.RecipeCreate, db: Session = Depends(get_db)):
    db_recipe = models.Recipe(
        name=recipe.name,
        description=recipe.description,
        instructions=recipe.instructions,
        prep_time=recipe.prep_time,
        cook_time=recipe.cook_time,
        servings=recipe.servings,
        calories=recipe.calories,
        protein=recipe.protein,
        carbs=recipe.carbs,
        fat=recipe.fat
    )
    db.add(db_recipe)
    db.commit()
    
    # Add ingredients to recipe
    for ingredient_data in recipe.ingredients:
        ingredient = db.query(models.Ingredient).filter(models.Ingredient.id == ingredient_data.ingredient_id).first()
        if not ingredient:
            db.rollback()
            raise HTTPException(status_code=404, detail=f"Ingredient with id {ingredient_data.ingredient_id} not found")
        
        db.execute(
            models.recipe_ingredient.insert().values(
                recipe_id=db_recipe.id,
                ingredient_id=ingredient_data.ingredient_id,
                amount=ingredient_data.amount,
                unit=ingredient_data.unit
            )
        )
    
    db.commit()
    db.refresh(db_recipe)
    return format_recipe_response(db_recipe, db)

@router.get("/", response_model=List[schemas.RecipeResponse])
def read_recipes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    recipes = db.query(models.Recipe).offset(skip).limit(limit).all()
    return [format_recipe_response(recipe, db) for recipe in recipes]

@router.get("/{recipe_id}", response_model=schemas.RecipeResponse)
def read_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return format_recipe_response(recipe, db)

def format_recipe_response(recipe, db):
    # Get ingredients with their details
    ingredients_query = db.query(
        models.recipe_ingredient.c.ingredient_id,
        models.Ingredient.name,
        models.recipe_ingredient.c.amount,
        models.recipe_ingredient.c.unit
    ).join(
        models.Ingredient,
        models.recipe_ingredient.c.ingredient_id == models.Ingredient.id
    ).filter(
        models.recipe_ingredient.c.recipe_id == recipe.id
    ).all()
    
    # Create the response object
    return {
        "id": recipe.id,
        "name": recipe.name,
        "description": recipe.description,
        "instructions": recipe.instructions,
        "prep_time": recipe.prep_time,
        "cook_time": recipe.cook_time,
        "servings": recipe.servings,
        "calories": recipe.calories,
        "protein": recipe.protein,
        "carbs": recipe.carbs,
        "fat": recipe.fat,
        "ingredients": [
            {
                "ingredient_id": ing_id,
                "ingredient_name": name,
                "amount": amount,
                "unit": unit
            } for ing_id, name, amount, unit in ingredients_query
        ]
    }

@router.post("/ingredients/", response_model=schemas.Ingredient)
@retry_on_db_lock(max_retries=5)
def create_ingredient(ingredient: schemas.IngredientCreate, db: Session = Depends(get_db)):
    db_ingredient = models.Ingredient(
        name=ingredient.name,
        calories_per_100g=ingredient.calories_per_100g,
        protein_per_100g=ingredient.protein_per_100g,
        carbs_per_100g=ingredient.carbs_per_100g,
        fat_per_100g=ingredient.fat_per_100g
    )
    db.add(db_ingredient)
    try:
        db.commit()
        db.refresh(db_ingredient)
    except Exception as e:
        db.rollback()
        raise
    return db_ingredient

@router.get("/ingredients/", response_model=List[schemas.Ingredient])
def read_ingredients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    ingredients = db.query(models.Ingredient).offset(skip).limit(limit).all()
    return ingredients
