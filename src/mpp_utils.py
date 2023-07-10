## CONFIGURATIONS
APP__CONFIG__DEBUG_PRINT = True
APP__CONFIG__RECIPE_AGENT__UNIT_TEST = True
APP__CONFIG__DATABASE__UNIT_TEST = False

## Utility Functions
"""
Wrapper around print to only print when configured
"""
def dbgPrint(message):
    if APP__CONFIG__DEBUG_PRINT is True:
        print("[DEBUG] {}".format(message))