##
## This agent is a thread that manages storing and updating the 
## paprika recipies
##
## Reference: 
## - https://github.com/phha/pap2mealie
## - https://gist.github.com/mattdsteele/7386ec363badfdeaad05a418b9a1f30a

# pip install httplib2
from enum import Enum
import requests
import threading
import gzip

# App packages
import mpp_utils
from app import AppSurface
from data.recipe import RecipeObject
from database import Database


"""
Object that holds authentication information that is provided
by the user for this session. 
NOTE: Authorization information should never be stored
"""
class AuthenticationObject (object):

    def __init__(self, uname, pword) -> None:
        self.auth_info = (uname, pword)

    def set_username(self, uname):
        self.auth_info[0] = uname

    def set_password(self, pword):
        self.auth_info[1] = pword

    def __str__(self) -> str:
        return "Auth. Object: (user: {}, pass: {})".format(self.auth_info[0], self.auth_info[1])

"""
Object holds information about the Paprika3 HTTP Interface.
The recipe agent can reference parts of the API from here.
"""
class Paprika3 (object):

    ## REFERENCE TO INSTANCE
    _instance=None

    ##
    ## API DEFINITIONS
    API__VERSION             = "v1"
    API__BASE                = "https://www.paprikaapp.com/api/{}".format(API__VERSION)
    ## API ALL ITEMS
    API__SYNC_ALL_RECIPIES   = "{}/sync/recipes".format(API__BASE)
    API__SYNC_BOOKMARKS      = "{}/sync/bookmarks".format(API__BASE)
    API__SYNC_ALL_GROCERIES  = "{}/sync/groceries".format(API__BASE)
    API__SYNC_ALL_CATEGORIES = "{}/sync/categories".format(API__BASE)
    API__SYNC_ALL_MEALS      = "{}/sync/meals".format(API__BASE)
    ## SYNC SINGLE ITEMS
    API__SYNC_RECIPE         = "{}/sync/recipe".format(API__BASE)

    # Construction
    def __new__(cls):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance
    
    # Initialize the constructor
    def __init__(self) -> None:
        pass

    def add(self, api, item) -> str:
        """
        The goal is to make sure there is always a forwards slash at the end
        of the link. I think this is how we can garuntee GET and POST statements
        will go through.
        """
        formatted_str = ""
        # last character of api is '/'
        if api[len(api)-1] == "/":
            formatted_str = "{}{}/".format(api, item)
        else:
            formatted_str = "{}/{}/".format(api, item)
        return formatted_str

"""
Recipe Agent Object

Responsible for managing the interface and information from Paprika3.
The idea would be that the app server starts the recipe agent with a
specific task in mind, that the recipe agent would go and do.
The commands in mind are:

Recipe Sync/Update
- Pull recipes from Paprika3 Cloud -> local Paprika3 Storage
- Update recipes local Paprika3 storage -> Paprika3 Cloud

To Dos:
- Grocery Sync/Update
- Meal Sync/Update
"""
class RecipeAgent(threading.Thread):

    PaprikaObj=None

    # Error codes
    class Error(Enum):
        ERR_SUCCESS = 0,
        ERR_GENERIC = 1,
        ERR_REQUEST_FAIL = 2,
        ERR_INVALID_PARAMS = 3,
        ERR_INALID_SURFACE = 4

    # Commands to the recipe agent
    class Command(Enum):
        CMD_PULL_RECIPES = 0,
        CMD_PUSH_RECIPES = 1,
    
    def __init__(self, app_surface: AppSurface, auth: AuthenticationObject, cmd) -> None:
        super().__init__(group=None, target=None, name=None, args=(), kwargs={}, daemon=None)
        self.app_surface = app_surface
        self.authentication = auth
        self.command = cmd
        self.status = RecipeAgent.Error.ERR_GENERIC
        self.database = Database()

        if RecipeAgent.PaprikaObj is None:
            RecipeAgent.PaprikaObj = Paprika3()
        # sanity checks
        if type(auth) is not AuthenticationObject:
            self.authentication = None
        if type(cmd) is not RecipeAgent.Command:
            self.command = None

    ## HELPER FUNCTIONS
    # performs the actual http operation
    def __make_http_request(self, command, request_url, data=None, debug=False):
        """
        @retval None: if the request does not work as intended
        @retval Dict: a dictionary object of the recipe
        """
        result = None

        if debug is True:
            mpp_utils.dbgPrint("Request Sent: {}".format(request_url))

        try:
            if command == RecipeAgent.Command.CMD_PULL_RECIPES:
                result = requests.get(request_url, auth=self.authentication.auth_info)
            elif command == RecipeAgent.Command.CMD_PUSH_RECIPES:
                # If pushing data, there needs to be data to push
                if data is None:
                    return None
                # send the request
                result = requests.post(request_url, auth=self.authentication.auth_info, files={"data": data})
            else:
                pass

            if result is None:
                return None
            else:
                # raises an exception when an error happens
                result.raise_for_status()

        except Exception as e:
            mpp_utils.dbgPrint("__make_http_request: an exception occured while submitting the request")
            mpp_utils.dbgPrint("__make_http_request: {}".format(e))
            return None

        
        # information on debug
        if debug is True:
            mpp_utils.dbgPrint("Request Response")
            mpp_utils.dbgPrint("Status({}) - {}".format(result.status_code, result.reason))
            mpp_utils.dbgPrint("Reponse Content: {}".format(result.json()))
        
        return result.json()

    # Pulls a single recipe, and all of its details
    def __api_pull_recipe(self, recipe_uid: str):
        """
        Pulls a single recipe from paprika

        @retval None: if the request does not work as intended
        @retval Dict: a dictionary object of the recipe
        """
        result = None

        request_url = RecipeAgent.PaprikaObj.add(RecipeAgent.PaprikaObj.API__SYNC_RECIPE, recipe_uid)
        result = self.__make_http_request(command=RecipeAgent.Command.CMD_PULL_RECIPES, request_url=request_url, debug=False)
        
        return result
    
    # Pushes a single recipe, and all of its details
    def __api_push_recipe(self, recipe_uid: str, paprika_recipe: RecipeObject):
        """
        Uploads data fora single recipe  back to paprika

        @retval None: if the request does not work as intended
        @retval Dict: a dictionary object of the recipe
        """
        result = None

        # calculating the hash
        paprika_recipe.calculate_hash_sha256()

        # compress using gzip
        packaged_data = gzip.compress(paprika_recipe.as_json().encode(encoding="utf-8"))

        request_url = RecipeAgent.PaprikaObj.add(RecipeAgent.PaprikaObj.API__SYNC_RECIPE, recipe_uid)
        result = self.__make_http_request(command=RecipeAgent.Command.CMD_PUSH_RECIPES, request_url=request_url, data=packaged_data, debug=False)

        return result
    
    ## DIAGNOSTIC FUNCTION
    def test_pull(self):
        """
        @retval RecipeAgent.Error.ERR_REQUEST_FAIL: test failed
        @retval RecipeAgent.Error.ERR_REQUEST_FAIL: test succeeded
        """
        result = None

        request_url = RecipeAgent.PaprikaObj.API__SYNC_ALL_RECIPIES
        result = self.__make_http_request(command=RecipeAgent.Command.CMD_PULL_RECIPES, request_url=request_url)

        if result is None:
            return RecipeAgent.Error.ERR_REQUEST_FAIL
        
        # Iterate through each recipe and store into the local datastore
        uid_list = result['result']
        mpp_utils.dbgPrint("UID Count: {}".format(len(uid_list)))

        for uid in uid_list:
            mpp_utils.dbgPrint("UID: {}".format(uid))

        if result is None:
            print("Result FAILED")
            return RecipeAgent.Error.ERR_REQUEST_FAIL
        
        return RecipeAgent.Error.ERR_SUCCESS

    def test_push(self):
        """
        @retval RecipeAgent.Error.ERR_REQUEST_FAIL: test failed
        @retval RecipeAgent.Error.ERR_REQUEST_FAIL: test succeeded
        """
        # Get the recipes from the Database/Datastore
        # the UID of the fake recipe
        uid = "647A8FCA-615C-4849-A692-94407600AB7A"
        # create a fake recipe
        paprika_recipe = RecipeObject()
        paprika_recipe.init(
            uid=uid,
            name="Fake Recipe",
            directions="Gather up all the bullshit and throw it out",
            servings="2 servings",
            rating=4,
            difficulty="Easy",
            ingredients="1 cup bullshit\n1 cup help me!",
            notes="Generated with Meal Prep Pal",
            created="2018-03-26 09:00:02",
            image_url="",
            on_favorites=0,
            cook_time="",
            prep_time="10 minutes",
            source="www.fakeotherwebsite.com",
            source_url="",
            photo_hash="",
            photo="",
            nutritional_info="100 BILLION Calories",
            scale="",
            is_pinned=False,
            categories=[],
            hash="162e5ad0134e9398b98057aea951304780d0396582238320c28b34a7c35f841e",
            description="",
            total_time="",
            on_grocery_list=False,
            in_trash=False,
            photo_url="",
            photo_large=""
        )

        ### Lets try to push the recipe back!
        result = self.__api_push_recipe(recipe_uid=uid, paprika_recipe=paprika_recipe)

        if result is None:
            print("Result FAILED")
            return RecipeAgent.Error.ERR_REQUEST_FAIL
        
        return RecipeAgent.Error.ERR_SUCCESS
        
    ## CORE COMMAND FUNCTIONS
    def __api_pull_recipes(self, loadbar=False, debug=False) -> int:
        """
        @retval RecipeAgent.Error.ERR_SUCCESS: recipes are pulled as expected
        @retval RecipeAgent.Error.ERR_REQUEST_FAIL: Unable to pull recipes
        """
        # stats
        total_recipes = 0
        current_recipe_count = 0
        unable_to_store = 0
        successfully_stored = 0

        # pull all recipies to get the UIDs
        req1_result = None
        request_url = RecipeAgent.PaprikaObj.API__SYNC_ALL_RECIPIES
        req1_result = self.__make_http_request(command=RecipeAgent.Command.CMD_PULL_RECIPES, request_url=request_url)

        if req1_result is None:
            return RecipeAgent.Error.ERR_REQUEST_FAIL
        
        recipe_list = req1_result['result']
        total_recipes = len(recipe_list)
        mpp_utils.dbgPrint("Recipe Count: {}".format(total_recipes))

        # ITERATE THROUGH EACH RECIPE
        for recipe in recipe_list:
            # gather stats
            current_recipe_count += 1

            # creating a loading bar
            if loadbar is True:
                percent = int((current_recipe_count/total_recipes)*100.0)
                residual = 100 - percent
                print("[{}{}] ({}%)".format('='*percent,' '*residual, percent), end='\r')

            # recipe is an object with hash & uid
            uid = recipe['uid']
            reqx_result = self.__api_pull_recipe(recipe_uid=uid)

            # only do things if the uid result is not none
            if reqx_result is None:
                continue

            # load into paprika object
            jsonobject = reqx_result['result']
            paprika_recipe = RecipeObject()
            paprika_recipe.init_from_jsonobj(jsonobj=jsonobject)

            if debug is True:
                mpp_utils.dbgPrint("Pull UID: {}".format(recipe))
                mpp_utils.dbgPrint(paprika_recipe)

            # STORE INTO DATABASE
            if self.database.write_recipe(paprika_recipe=paprika_recipe) != Database.Error.ERR_SUCCESS:
                if debug is True:
                    mpp_utils.dbgPrint("Unable to store into database")
                unable_to_store += 1
            else:
                successfully_stored += 1
                
        if unable_to_store > successfully_stored:
            if debug is True:
                mpp_utils.dbgPrint("Failed when storing a majority of the recipes")
            return RecipeAgent.Error.ERR_REQUEST_FAIL

        # iterate through each UID and pull each recipe and all of its contents
        # store it in the database
        return RecipeAgent.Error.ERR_SUCCESS
    
    def __api_push_recipes(self, debug=False) -> int:
        """
        @retval RecipeAgent.Error.ERR_SUCCESS: recipes are pushed as expected
        @retval RecipeAgent.Error.ERR_REQUEST_FAIL: Unable to push recipes
        """
        uid_list = self.database.pull_recipe_list()

        # get all of the recipes from the database
        if uid_list is None:
            mpp_utils.dbgPrint("Unable to pull recipes")
            return RecipeAgent.Error.ERR_REQUEST_FAIL

        # iterate through each recipe in the database
        for element in uid_list:
            # uid is first and only element in tuple
            # based on behavior of "pull_recipe_list"
            uid = element[0]
            mpp_utils.dbgPrint('UID: {}'.format(uid))
            # construct the recipe object
            recipe = self.database.read_recipe(uid=uid)

            # skip if recipe is found
            if recipe is None:
                mpp_utils.dbgPrint("no recipe found")
                continue

            # skip if recipe has not been modified
            if not recipe.metadata_is_modified:
                mpp_utils.dbgPrint("recipe not modified")
                continue

            # push the recipe back to the paprika server
            self.__api_push_recipe(recipe_uid=uid, paprika_recipe=recipe)
                
        return RecipeAgent.Error.ERR_SUCCESS

    ## THREAD RUN DEFINITION
    def run(self) -> None:
        mpp_utils.dbgPrint("Running Recipe Agent")
        mpp_utils.dbgPrint("Command: {}".format(self.command))

        # check the surface
        if (type(self.app_surface) is not AppSurface) or (self.app_surface is None):
            self.status = RecipeAgent.Error.ERR_INVALID_SURFACE
            # set surface
            self.app_surface.surface_lock.acquire()
            self.app_surface.b_recipe_agent_running = False
            self.app_surface.surface_lock.release()
            return
        
        # set surface
        self.app_surface.surface_lock.acquire()
        self.app_surface.b_recipe_agent_running = True
        self.app_surface.surface_lock.release()

        status_code = RecipeAgent.Error.ERR_SUCCESS
        if self.command == RecipeAgent.Command.CMD_PULL_RECIPES:
            status_code = self.__api_pull_recipes(loadbar=False, debug=False)

        elif self.command == RecipeAgent.Command.CMD_PUSH_RECIPES:
            status_code = self.__api_push_recipes()

        # error handling
        if status_code is not RecipeAgent.Error.ERR_SUCCESS:
            mpp_utils.dbgPrint("Unable to complete command.")
            mpp_utils.dbgPrint("Error: {}".format(status_code))
        
        # set surface
        self.app_surface.surface_lock.acquire()
        self.app_surface.b_recipe_agent_running = False
        self.app_surface.surface_lock.release()

        # set the thread status
        self.status = status_code

##########################
## IN-FILE UNIT TESTING ##
##########################
## Run Tests if the config is 
if mpp_utils.APP__CONFIG__RECIPE_AGENT__UNIT_TEST == True:
    USER = input("Username: ")
    PASSWORD = input("Password: ")

    """
    Test Successfull single pull/push
    """
    def test0() -> bool:
        recipe_agent = RecipeAgent(cmd=RecipeAgent.Command.CMD_PULL_RECIPES, 
                                   app_surface=None,
                                   auth=AuthenticationObject(uname=USER, pword=PASSWORD))
        recipe_agent.test_pull()
        recipe_agent.test_push()
        return True

    """
    Test invalid credentials
    """
    def test1() -> bool:
        BAD_USER="fakeuser"
        BAD_PASSWORD="fakepass"
        recipe_agent = RecipeAgent(cmd=RecipeAgent.Command.CMD_PULL_RECIPES,
                                   app_surface=None,
                                   auth=AuthenticationObject(uname=BAD_USER, pword=BAD_PASSWORD))
        recipe_agent.start()
        recipe_agent.join()

        # Pass if this fails
        if recipe_agent.status is not RecipeAgent.Error.ERR_SUCCESS:
            return True
        else:
            return False

    """
    Test Successfull command to pull & store all recipes
    """
    def test2() -> bool:
        recipe_agent = RecipeAgent(cmd=RecipeAgent.Command.CMD_PULL_RECIPES,
                                   app_surface=None,
                                   auth=AuthenticationObject(uname=USER, pword=PASSWORD))
        recipe_agent.start()
        recipe_agent.join()

        if recipe_agent.status == RecipeAgent.Error.ERR_SUCCESS:
            return True
        else:
            return False
        
    """
    Test Successfull command to load all recipes from the database & push
    """
    def test3() -> bool:
        recipe_agent = RecipeAgent(cmd=RecipeAgent.Command.CMD_PUSH_RECIPES, 
                                   app_surface=None,
                                   auth=AuthenticationObject(uname=USER, pword=PASSWORD))
        recipe_agent.start()
        recipe_agent.join()

        if recipe_agent.status == RecipeAgent.Error.ERR_SUCCESS:
            return True
        else:
            return False

    TestList = [test3]
    SuccessCount = 0

    for test in TestList:
        print("Running: {}".format(test.__name__))
        status = test()
        print("Test Result: {}".format(status))
        if status is True:
            SuccessCount += 1

    print("Passed {}/{} Tests".format(SuccessCount, len(TestList)))
