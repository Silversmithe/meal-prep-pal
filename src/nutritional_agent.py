##
## This agent is a thread that updates nutritional information
## of the recipes
##

# python builtin
import re
from enum import Enum
import threading
import json
from typing import Any

# user defined
import time
import mpp_utils
from data.surface import AppSurface
from database import Database

# for testing purposes
from recipe_agent import *

"""
Edmam

Use Edmam Service to calculate nutritional value of the recipes
Ref. https://www.edamam.com/
"""
class EdmamService (object):

    def __init__(self) -> None:
        pass


"""
Nutritional Value
"""
class NutritionalInfo(object):

    def __init__(self) -> None:
        self.info = {
            "servings": float(),         # QUANTITY
            "calories": float(),         # KCAL
            "carbohydrates": float(),    # GRAMS
            "protein": float(),          # GRAMS
            "fat": float(),              # GRAMS
            "saturated-fat": float(),    # GRAMS 
            "cholesterol": float(),      # GRAMS 
            "sodium": float(),           # GRAMS 
            "potassium": float(),        # GRAMS 
            "fiber": float(),            # GRAMS 
            "sugar": float(),            # GRAMS 
            "calcium": float(),          # GRAMS 
            "iron": float()              # GRAMS 
        }

    def __str__(self):
        return str(self.info)
    
    
"""
Nutritional Agent Object

Calculates the nutritional information
"""
class NutritionAgent(threading.Thread):

    SIGNATURE = "@meal-prep-pal"

    # Error codes
    class Error(Enum):
        ERR_SUCCESS = 0,
        ERR_GENERIC = 1,
        ERR_INVALID_SURFACE = 2

    def __init__(self, app_surface: AppSurface, force_update=False) -> None:
        super().__init__(group=None, target=None, name=None, args=(), kwargs={}, daemon=None)
        self.database = Database()
        self.app_surface = app_surface
        self.status = NutritionAgent.Error.ERR_GENERIC
        self.force_update = force_update

    def __sign_recipe(self, recipe: RecipeObject) -> int:
        """
        Mark on the recipe that it was updated by Meal Prep Pal
        """
        notes = recipe.load(key="notes")
        updated_notes = notes
        if not NutritionAgent.SIGNATURE in notes:
            updated_notes = "{}\n{}".format(notes, NutritionAgent.SIGNATURE)
        recipe.store(key="notes", value=updated_notes)

    def __calculate_nutritional_info(self, paprika_recipe: RecipeObject, debug=False) -> int:
        """
        Calculate nutritional info
        """
        # function status
        status = NutritionAgent.Error.ERR_SUCCESS
        # stat info
        TotalIngredients = 0
        IngredientsFound = 0
        # nutritional info
        nutritional_info = NutritionalInfo()

        if debug is True:
            mpp_utils.dbgPrint(paprika_recipe)

        if paprika_recipe is None:
            return NutritionAgent.Error.ERR_GENERIC
        
        ## extract ingredients
        # load string
        ingredients_as_str = paprika_recipe.load(key="ingredients")
        # split by newline
        ingredient_list = ingredients_as_str.split('\n')
        TotalIngredients = len(ingredient_list)

        # iterate through the ingredients
        for element in ingredient_list:
            TotalIngredients += 1
            b_ingredient_found = False

            ##
            ## Check if ingredient is a recipe
            ##
            ## For simplicy we can just have them look at the 
            ## other recipe for simplicity and skip calculation
            ## if thats cool.
            ##
            ## Ingredient is recipe: (can have spaces)
            ## 2 tbsp [recipe:Persillade and something]
            # use regex to determine if ingredient is a recipe
            expression = '\[recipe\:(\w|\s|-)*\]'
            recipe_match = re.search(expression, element)
            if recipe_match is not None:
                b_ingredient_found = True
                IngredientsFound += 1
                continue

            # split by spaces
            ingredient = element.split(" ")
            ##
            ## INGREDIENT LOOKUP ALGORITHM
            ##
            ## Basically need to find items in the databse with 
            ## the highest 'similarity' to the ingredient.
            ##
            ## Then we pull the nutritional information, and 
            ## ensure it is the correct portion.
            pass

            # check if the ingredient is found
            if b_ingredient_found is True:
                IngredientsFound += 1 

        if debug is True:
            mpp_utils.dbgPrint("Found {}/{} ingredients".format(IngredientsFound, TotalIngredients))

        # store nutritional information in recipe
        paprika_recipe.store(key="nutritional_info", value=str(nutritional_info))

        # sign recipe
        # TODO: make sure this signature works! this is getting passed by value fyi
        self.__sign_recipe(recipe=paprika_recipe)

        # re-store in recipe

        return status

    def __recipe_update_pass(self, debug=False) -> int:
        """
        Iterate through all of the recipes. Update nutritional 
        information as necessary.
        """
        uid_list = self.database.pull_recipe_list()

        if uid_list is None:
            return NutritionAgent.Error.ERR_GENERIC
        
        if debug is True:
            mpp_utils.dbgPrint("Nutritional Agent Recipe (UPDATE PASS)")
            mpp_utils.dbgPrint("UIDs counted: {}".format(len(uid_list)))

        # iterate through uids
        for item in uid_list:
            uid = item[0]
            # calculate the nutritional information
            paprika_recipe = self.database.read_recipe(uid=uid)
            # check for force update & if recipe has nutritional info
            if (self.force_update is True) or (not paprika_recipe.metadata_has_nutritional_info):
                # outputting debug information
                if debug is True:
                    mpp_utils.dbgPrint("<uid: {}, force_update: {}, has nutritional info: {}".format(uid, self.force_update, paprika_recipe.metadata_has_nutritional_info))
                # calculate the hash value
                self.__calculate_nutritional_info(paprika_recipe=paprika_recipe, debug=debug)
                # print(paprika_recipe.load(key="nutritional_info"))
                ## Turn off DATABASE WRITE RIGHT NOW for DEVELEOPMENT REASONS
                # self.database.write_recipe(paprika_recipe=paprika_recipe)

        return NutritionAgent.Error.ERR_SUCCESS

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
            # only update recipes if there is not a force update
            # otherise for a force update, just wait for all the recipes to be added
            if self.force_update is False:
                # iterate through all the recipes at the time
                # calculate the nutritional info for each one
                self.__recipe_update_pass(debug=True)
            time.sleep(60)
        else:
            mpp_utils.dbgPrint("Nutritional Agent FINAL PASS")
            self.__recipe_update_pass(debug=True)
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
        nutrition_agent = NutritionAgent(app_surface=surface, force_update=False)
        recipe_agent.start()
        nutrition_agent.start()
        # waiting for threads to finish
        recipe_agent.join()
        nutrition_agent.join()

        return True
    
    """
    Test Regex
    """
    def test1() -> bool:
        ingredient = '2 tbsp [recipe:Persillade and raddishes]'
        ingredient2 = 'Lavender Coriander Chia Pudding|1 [recipe:3-Ingredient Chia Pudding]'
        expression = '\[recipe\:(\w|\s|-)*\]'
        recipe_match = re.search(expression, ingredient2)
        print(recipe_match)
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
