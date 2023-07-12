##
## This agent is a thread that updates nutritional information
## of the recipes
##

# python builtin
from enum import Enum
import threading
from typing import Any

# user defined
import time
import mpp_utils
from app import AppSurface
from database import Database

# for testing purposes
from recipe_agent import *

"""
Nutritional Agent Object

Calculates the nutritional information
"""
class NutritionAgent(threading.Thread):

    # Error codes
    class Error(Enum):
        ERR_SUCCESS = 0,
        ERR_GENERIC = 1,
        ERR_INVALID_SURFACE = 2

    def __init__(self, app_surface: AppSurface) -> None:
        super().__init__(group=None, target=None, name=None, args=(), kwargs={}, daemon=None)
        self.database = Database()
        self.app_surface = app_surface
        self.status = NutritionAgent.Error.ERR_GENERIC

    def run(self) -> None:
        mpp_utils.dbgPrint("Running Nutritional Agent")

        # confirm that the app surface is real
        if (type(self.app_surface) is not AppSurface) or (self.app_surface is None):
            self.status = NutritionAgent.Error.ERR_INVALID_SURFACE
            return
        
        # set surface
        self.app_surface.surface_lock.acquire()
        self.app_surface.b_nutrition_agent_running = True
        self.app_surface.surface_lock.release()
        
        # iterate while there are new recipes still being added
        # AKA nutritional agent is running
        while self.app_surface.b_recipe_agent_running:
            mpp_utils.dbgPrint("Recipe Agent is still running... Nutritional Agent SCAN")
            time.sleep(60)
            # iterate through all the recipes at the time
            # calculate the nutritional info for each one
        else:
            mpp_utils.dbgPrint("Nutritional Agent FINAL PASS")
            pass
        
        mpp_utils.dbgPrint("Nutritional Agent COMPLETED")

        # set surface
        self.app_surface.surface_lock.acquire()
        self.app_surface.b_nutrition_agent_running = False
        self.app_surface.surface_lock.release()

        self.status = NutritionAgent.Error.ERR_SUCCESS


##########################
## IN-FILE UNIT TESTING ##
##########################
## Run Tests if the config is 
if mpp_utils.APP__CONFIG__NUTRITION_AGENT__UNIT_TEST == True:
    USER = input("Username: ")
    PASSWORD = input("Password: ")

    """
    Testing Nutrition agent & recipe agent together
    """
    def test0() -> bool:
        surface = AppSurface()
        recipe_agent = RecipeAgent(app_surface=surface,
                                   auth=AuthenticationObject(uname=USER, pword=PASSWORD),
                                   cmd=RecipeAgent.Command.CMD_PULL_RECIPES)
        nutrition_agent = NutritionAgent(app_surface=surface)
        recipe_agent.start()
        nutrition_agent.start()
        # waiting for threads to finish
        recipe_agent.join()
        nutrition_agent.join()

        return True

    TestList = [test0]
    SuccessCount = 0

    for test in TestList:
        print("Running: {}".format(test.__name__))
        status = test()
        print("Test Result: {}".format(status))
        if status is True:
            SuccessCount += 1

    print("Passed {}/{} Tests".format(SuccessCount, len(TestList)))
