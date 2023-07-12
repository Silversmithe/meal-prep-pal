##
## This consists of 3 things:
## - app server
## - terminal console

import threading


"""
App Surface Object

Used to share information between different threads
"""
class AppSurface (object):
    
    def __init__(self) -> None:
        self.surface_lock = threading.Lock()
        self.b_recipe_agent_running = False
        self.b_nutrition_agent_running = False