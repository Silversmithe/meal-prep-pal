
from collections.abc import Callable, Iterable, Mapping
from enum import Enum

import threading
from typing import Any

# App packages
import mpp_utils
from data.surface import AppSurface
from data.recipe import RecipeObject
from data.surface import AppSurface
from database import Database


"""
Meal Scheduler Agent Object

Responsible for creating the meals for the week using 
different available scheduling policies.
"""
class MealSchedulerAgent(threading.Thread):

    def __init__(self, app_surface: AppSurface, policy="random") -> None:
        super().__init__(group=None, target=None, name=None, args=(), kwargs={}, daemon=None)

    def get_policies(self):
        """
        Return a list of the possible policies available
        """
        pass

##########################
## IN-FILE UNIT TESTING ##
##########################
## Run Tests if the config is 
if mpp_utils.APP__CONFIG__MEAL_SCHEDULER_AGENT__UNIT_TEST == True:
    """
    Test Successfull single pull/push
    """
    def test0() -> bool:
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