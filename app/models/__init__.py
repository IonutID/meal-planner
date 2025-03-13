# Package initialization

# Define the modules explicitly to be accessible as recipes and meal_plans
import sys
import os
from importlib.util import spec_from_file_location, module_from_spec

# Get the directory where this __init__.py is located
package_dir = os.path.dirname(__file__)

# Define the recipe module
recipe_path = os.path.join(package_dir, 'recipe.py')
recipe_spec = spec_from_file_location("recipe", recipe_path)
recipes = module_from_spec(recipe_spec)
recipe_spec.loader.exec_module(recipes)

# Define the meal_plan module
meal_plan_path = os.path.join(package_dir, 'meal_plan.py')
meal_plan_spec = spec_from_file_location("meal_plan", meal_plan_path)
meal_plans = module_from_spec(meal_plan_spec)
meal_plan_spec.loader.exec_module(meal_plans)

# Import classes for direct access
from .recipe import *
from .meal_plans import *
