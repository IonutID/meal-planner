# Meal Planner API

A FastAPI application for planning meals and generating grocery lists based on nutritional requirements.

## Features

-   Create and manage recipes with ingredients and nutritional information
-   Generate meal plans based on caloric and macronutrient needs
-   Generate grocery lists for meal plans
-   Support for planning for multiple people

## Setup

1. Clone this repository
2. Create a virtual environment:
    ```
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3. Install dependencies:
    ```
    pip install -r requirements.txt
    ```
4. Run the application:
    ```
    python main.py
    ```

## API Endpoints

### Recipes

-   `GET /recipes/` - List all recipes
-   `POST /recipes/` - Create a new recipe
-   `GET /recipes/{recipe_id}` - Get details for a specific recipe
-   `POST /recipes/ingredients/` - Create a new ingredient
-   `GET /recipes/ingredients/` - List all ingredients

### Meal Plans

-   `GET /meal-plans/` - List all meal plans
-   `POST /meal-plans/` - Create a new meal plan
-   `GET /meal-plans/{meal_plan_id}` - Get details for a specific meal plan
-   `POST /meal-plans/{meal_plan_id}/generate` - Generate recipes for a meal plan
-   `GET /meal-plans/{meal_plan_id}/grocery-list` - Get the grocery list for a meal plan

## Example Usage

1. Create ingredients with nutritional values
2. Create recipes using those ingredients
3. Create a meal plan with your dietary requirements
4. Generate the meal plan to assign recipes to days/meals
5. Get the grocery list for shopping
