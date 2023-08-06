## CONFIGURATIONS
APP__CONFIG__DEBUG_PRINT = True
APP__CONFIG__RECIPE_AGENT__UNIT_TEST = False
APP__CONFIG__DATABASE__UNIT_TEST = False
APP__CONFIG__NUTRITION_AGENT__UNIT_TEST = False
APP__CONFIG__MEAL_SCHEDULER_AGENT__UNIT_TEST = False

## Utility Functions
"""
Wrapper around print to only print when configured
"""
def dbgPrint(message):
    if APP__CONFIG__DEBUG_PRINT == True:
        print("[DEBUG] {}".format(message))