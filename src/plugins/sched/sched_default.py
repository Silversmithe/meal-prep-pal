
import random

# objects
from data.surface import AppSurface
from data.plan import MealPlan

# actors
from database import *
from recipe_agent import *
from nutritional_agent import *
from meal_scheduler_agent import *


"""
Creates a meal plan
"""
def create_schedule(app_surface: AppSurface, recipe_agent: RecipeAgent, database: Database, start_day: str, end_day: str) -> MealPlan:
    # define the schedule
    # do a basic mealplan
    plan = MealPlan(start_day=start_day, end_day=end_day)

    uid_list = database.pull_recipe_list()
    uid_count = len(uid_list)

    # iterate through each day
    for day in plan.meal_plan.keys():
        # iterate through each meal
        day_elt = plan.meal_plan[day]
        for meal in day_elt.day_plan.keys():
            generate_meal = True
            while generate_meal is True:
                # generate uid
                uid_num = random.randrange(start=0, stop=uid_count)
                uid = uid_list[uid_num][0]
                # only store if not duplicate
                recipe = database.read_recipe(uid=uid)
                # store in meal
                day_elt.day_plan[meal] = recipe


    # print the mealplan
    return plan

"""
Update a single meal in schedule
"""
def update_schedule_meal(app_surface: AppSurface, recipe_agent: RecipeAgent, database: Database, day_key, meal_key, recipe: RecipeObject) -> None:
    # if there is no recipe, select a random one
    if recipe is None:
        uid_list = database.pull_recipe_list()
        uid_count = len(uid_list)
        uid_num = random.randrange(start=0, stop=uid_count)
        uid = uid_list[uid_num]

        # SCHEDULING
        new_recipe = database.read_recipe(uid=uid[0])

        # ASSIGN
        app_surface.current_mealplan.meal_plan[day_key].day_plan[meal_key] = new_recipe
    else:
        # if there is a recipe just replace
        app_surface.current_mealplan.meal_plan[day_key].day_plan[meal_key] = recipe