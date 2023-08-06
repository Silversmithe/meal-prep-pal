##
## This consists of 3 things:
## - app server
## - terminal console

import random
import threading
from getpass import getpass

# objects
from data.surface import AppSurface
from data.plan import MealPlan

# actors
from database import *
from recipe_agent import *
from nutritional_agent import *
from meal_scheduler_agent import *

# schedulers
from plugins.sched import sched_default

## PRINT HELPER FUNCTIONS
def print_exception(msg=""):
    print("\n<<{}>>".format(msg))

def print_info(msg=""):
    print("[info] {}".format(msg))

## TERMINAL FUNCTIONS
def prompt(start=">>") -> str:
    print("{} ".format(start), end="")
    result = input()
    return result

# define the functions
def cmd_default_plan(app_surface: AppSurface, recipe_agent: RecipeAgent, database: Database) -> bool:

    user_start_day = prompt("Schedule start day?").lower()
    user_end_day = prompt("Schedule end day?").lower()

    # wait for this to be complete before scheduling meals
    if app_surface.b_recipe_agent_running == True:
        print("Wait for Paprika Sync to complete")
        recipe_agent.show_progress_status = True
        recipe_agent.join()

    meal_plan = sched_default.create_schedule(app_surface=app_surface,
                                              recipe_agent=recipe_agent,
                                              database=database,
                                              start_day=user_start_day,
                                              end_day=user_end_day)
    app_surface.current_mealplan = meal_plan

    return True

def cmd_default_plan_update(app_surface: AppSurface, recipe_agent: RecipeAgent, database: Database) -> bool:

    if app_surface.current_mealplan is not None:    
        day_of_week = prompt("Day of week: ")
        meal = prompt("Meal: ")

        # wait for this to be complete before scheduling meals
        if app_surface.b_recipe_agent_running == True:
            print("Wait for Paprika Sync to complete")
            recipe_agent.show_progress_status = True
            recipe_agent.join()

        sched_default.update_schedule_meal(app_surface=app_surface, 
                                           recipe_agent=recipe_agent,
                                           database=database,
                                           day_key=day_of_week,
                                           meal_key=meal,
                                           recipe=None)
        return True
    else:
        return False
    return True

def cmd_show_plan(app_surface: AppSurface, recipe_agent: RecipeAgent, database: Database) -> bool:
    if app_surface.current_mealplan is not None:
        print(app_surface.current_mealplan)
        return True
    else:
        return False
    
def cmd_sync_paprika(app_surface: AppSurface, recipe_agent: RecipeAgent, database: Database) -> bool:
    if app_surface.b_recipe_agent_running == True:
        return False
    
    print_info("Syncing with paprika ...")
    recipe_agent.command = RecipeAgent.Command.CMD_PULL_RECIPES
    recipe_agent.start()
    return True

def cmd_wait_for_paprika(app_surface: AppSurface, recipe_agent: RecipeAgent, database: Database) -> bool:
    if app_surface.b_recipe_agent_running == True:
        recipe_agent.show_progress_status = True
        recipe_agent.join()
        return True
    else:
        return False

def cmd_test_paprika(app_surface: AppSurface, recipe_agent: RecipeAgent, database: Database) -> bool:
    b_is_valid_connection = recipe_agent.test_pull()
    if b_is_valid_connection != RecipeAgent.Error.ERR_SUCCESS:
        print("Unable to connect to Paprika, likely invalid authentication")
        return False
    else:
        print("Test connection to Paprika SUCCESSFUL")
        return True
    
def cmd_quit(app_surface: AppSurface, recipe_agent: RecipeAgent, database: Database) -> bool:
    app_surface.surface_lock.acquire()
    app_surface.b_app_running = False
    app_surface.surface_lock.release()
    raise Exception

COMMAND_LIST = [
    cmd_default_plan,
    cmd_default_plan_update,
    cmd_show_plan,
    cmd_sync_paprika,
    cmd_wait_for_paprika,
    cmd_test_paprika,
    cmd_quit
]

def cmd_help():
    print('=' * 50)
    print("help:")
    for cmd in COMMAND_LIST:
        print("{}".format(cmd.__name__))
    print('=' * 50)

"""
Main Functions
"""
if __name__ == "__main__":
    # set configurations
    mpp_utils.APP__CONFIG__DEBUG_PRINT = False

    # show the title screen
    title = "Meal Prep Pal"
    version = 1.0
    print('=' * len(title))
    print(title)
    print("v{}".format(version))
    print('=' * len(title))

    # start the application
    try:
        # getting user information
        print("User: ", end="")
        username = input()
        password = getpass(prompt="Password: ")

        # setting up objects
        app_surface = AppSurface()
        app_surface.b_app_running = True # okay not to lock before other objects are set up

        user_auth = AuthenticationObject(uname=username, pword=password)
        databse = Database()
        recipe_agent = RecipeAgent(cmd=RecipeAgent.Command.CMD_PULL_RECIPES, 
                                    app_surface=app_surface,
                                    auth=user_auth,
                                    debug=False)
        
        # test connection
        b_is_valid_connection = recipe_agent.test_pull()
        if b_is_valid_connection != RecipeAgent.Error.ERR_SUCCESS:
            print("Unable to connect to Paprika, likely invalid authentication")
            raise Exception
        else:
            print("Test connection to Paprika SUCCESSFUL")

        # start the agents
        user_input = prompt("Do you want to start a sync with paprika? [y/n]")
        if user_input.lower() == "y":
            cmd_sync_paprika(app_surface=app_surface, recipe_agent=recipe_agent, database=databse)

        if mpp_utils.APP__CONFIG__DEBUG_PRINT is True:
            # wait for all agents to finish
            print_info("Waiting paprika sync to finish...")
            recipe_agent.join()

        # start the terminal
        while app_surface.b_app_running:
            # do whatever we want in the middle
            # ask for user informaition about the meal-plan
            user_input = prompt(start=">>")
            user_input = user_input.lower()
            print("User entered: {}".format(user_input))

            # do command processing here cuz im lazy
            if user_input == "help":
                cmd_help()
            # search for the command
            for cmd in COMMAND_LIST:
                if user_input == cmd.__name__:
                    b_success = cmd(app_surface=app_surface, recipe_agent=recipe_agent, database=databse)
                    if b_success == True:
                        print_info("Success")
                    else:
                        print_info("Failure")

        # wait for all agents to finish
        print_info("Waiting paprika sync to finish...")
        recipe_agent.join()
    
    except KeyboardInterrupt:
        print_exception("keyboard interrupt detected")
    except Exception as e:
        print_exception("unexpected exception occred")
        print(e)
    finally:
        # trigger shutdown
        app_surface.surface_lock.acquire()
        app_surface.b_app_running = False
        app_surface.surface_lock.release()

        print_info("closing mpp")
        exit()
