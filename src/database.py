
import sqlite3
import json
from enum import Enum

# App packages
import mpp_utils
from data.recipe import RecipeObject


"""
Database Object

Maintains information and control over the 
database interface.
"""
class Database (object):

    DATABASE_PATH = "./datastore/mpp.db"

    class Error (Enum):
        ERR_SUCCESS = 0,
        ERR_GENERIC = 1,
        ERR_CONNECTION_NOT_OPEN = 2,
        ERR_CONNECTION_ALREADY_OPEN = 3,
        ERR_OPERATION_FAILED = 4,

    def __init__(self) -> None:
        self.connection_is_open = False
        self.connection = None
        self.cursor = None

    def __open(self) -> int:
        """
        Handled internally to make sure database operations are handled correctly.

        @retval True: open was successfull
        @retval False: failed to open the database
        """
        if self.connection_is_open is True:
            print("connection is already open")
            return Database.Error.ERR_CONNECTION_ALREADY_OPEN
        
        try:
            self.connection = sqlite3.connect(Database.DATABASE_PATH)
            self.cursor = self.connection.cursor()
        except:
            self.connection_is_open = False
            self.cursor = None
            return Database.Error.ERR_GENERIC
        
        self.connection_is_open = True
        return Database.Error.ERR_SUCCESS

    def __close(self) -> int:
        """
        Handled internally to make sure database operations are handled correctly.

        @retval True: open was successfull
        @retval False: close was not successful
        """
        if self.connection_is_open is False:
            print("connection is already closed")
            return Database.Error.ERR_CONNECTION_NOT_OPEN
        
        if type(self.connection) is not sqlite3.Connection:
            print("invalid database connection")
            return Database.Error.ERR_GENERIC 
        
        if self.cursor is None:
            print("invalid database cursor (Nones)")
            return Database.Error.ERR_GENERIC

        if type(self.cursor) is not sqlite3.Cursor:
            print("invalid database cursor")
            return Database.Error.ERR_GENERIC
        
        try:
            self.cursor = None
            self.connection.close()
            self.connection_is_open = False
        except:
            print("failed to close the database connction")
            return Database.Error.ERR_OPERATION_FAILED

        return Database.Error.ERR_SUCCESS
    
    def write_recipe(self, paprika_recipe: RecipeObject) -> int:
        result = Database.Error.ERR_GENERIC

        # Open and close the DB connection per read/write
        # FAIL if either open or close fails

        # get a cursor
        status = self.__open()
        if status != Database.Error.ERR_SUCCESS:
            return status
        
        recipe_uid = paprika_recipe.load("uid")
        recipe_in_database = False

        # load the data
        recipe_dict = paprika_recipe.as_dict()
        data = (
            recipe_dict["rating"],
            recipe_dict["photo_hash"],
            recipe_dict["on_favorites"],
            recipe_dict["photo"],
            recipe_dict["scale"],
            recipe_dict["ingredients"],
            recipe_dict["is_pinned"],
            recipe_dict["source"],
            recipe_dict["total_time"],
            recipe_dict["hash"],
            recipe_dict["description"],
            recipe_dict["source_url"],
            recipe_dict["difficulty"],
            recipe_dict["on_grocery_list"],
            recipe_dict["in_trash"],
            recipe_dict["directions"],
            json.dumps(recipe_dict["categories"]),
            recipe_dict["photo_url"],
            recipe_dict["cook_time"],
            recipe_dict["name"],
            recipe_dict["created"],
            recipe_dict["notes"],
            recipe_dict["photo_large"],
            recipe_dict["image_url"],
            recipe_dict["prep_time"],
            recipe_dict["servings"],
            recipe_dict["nutritional_info"]
        )

        # check if the recipe exists
        result = self.cursor.execute("SELECT * FROM RECIPE_TABLE WHERE uid='{}'".format(recipe_uid))
        row = result.fetchone()

        if row is not None:
            recipe_in_database = True
        else:
            recipe_in_database = False

        if recipe_in_database is True:
            # if it exists, we alter
            self.cursor.execute("""
                UPDATE RECIPE_TABLE 
                    SET rating = ?,
                        photo_hash = ?,
                        on_favorites = ?,
                        photo = ?,
                        scale = ?,
                        ingredients = ?,
                        is_pinned = ?,
                        source = ?,
                        total_time = ?,
                        hash = ?,
                        description = ?,
                        source_url = ?,
                        difficulty = ?,
                        on_grocery_list = ?,
                        in_trash = ?,
                        directions = ?,
                        categories = ?,
                        photo_url = ?,
                        cook_time = ?,
                        name = ?,
                        created = ?,
                        notes = ?,
                        photo_large = ?,
                        image_url = ?,
                        prep_time = ?,
                        servings = ?,
                        nutritional_info = ?
                        WHERE uid = '{recipe_uid}'
            """, data)
        else:
            # if it doenst exist, lets add
            self.cursor.execute(f"""
                INSERT INTO RECIPE_TABLE VALUES (
                    '{recipe_uid}',?,?,?,?,?,?,?,?,?,
                    ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
                )
            """, data)

        # commit the transaction to solidify the write
        self.connection.commit()

        status = self.__close()
        if status != Database.Error.ERR_SUCCESS:
            return status

        result = Database.Error.ERR_SUCCESS
        return result

    def read_recipe(self, uid) -> RecipeObject:
        """
        @retval RecipeObject: if the recipe with the uid is found
        @retval None: if the recipe is NOT found
        """
        paprika_recipe = RecipeObject()

        # Open and close the DB connection per read/write
        # FAIL if either open or close fails

        # get a cursor
        status = self.__open()
        if status != Database.Error.ERR_SUCCESS:
            return None
        
        result = self.cursor.execute("SELECT * FROM RECIPE_TABLE WHERE uid='{}'".format(uid))
        row = result.fetchone()

        # if nothing was found, return none
        if row is None:
            return None
        
        # fill in the paprika recipe otherwise
        paprika_recipe.init(
            uid=row[0],
            rating=row[1],
            photo_hash=row[2],
            on_favorites=bool(row[3]),
            photo=row[4],
            scale=row[5],
            ingredients=row[6],
            is_pinned=bool(row[7]),
            source=row[8],
            total_time=row[9],
            hash=row[10],
            description=row[11],
            source_url=row[12],
            difficulty=row[13],
            on_grocery_list=bool(row[14]),
            in_trash=bool(row[15]),
            directions=row[16],
            categories=json.loads(row[17]),
            photo_url=row[18],
            cook_time=row[19],
            name=row[20],
            created=row[21],
            notes=row[22],
            photo_large=row[23],
            image_url=row[24],
            prep_time=row[25],
            servings=row[26],
            nutritional_info=row[27]
        )

        status = self.__close()
        if status != Database.Error.ERR_SUCCESS:
            return None

        return paprika_recipe

##########################
## IN-FILE UNIT TESTING ##
##########################
## Run Tests if the config is 
if mpp_utils.APP__CONFIG__UNIT_TEST == True:
    # fake/test recipe
    uid = "647A8FCA-615C-4849-A692-94407600AB7A"
    new_uid = "fancy-uid"
    """
    Test normal usage
    """
    def test0() -> bool:
        status = True
        database = Database()

        # write recipe
        new_recipe = RecipeObject()
        new_recipe.store(key="uid", value="fancy-uid")
        new_recipe.store(key="name", value="God-Tier Recipe")
        new_recipe.store(key="created", value="beginning of time")
        database.write_recipe(paprika_recipe=new_recipe)

        # read recipe
        recipe = database.read_recipe(uid=new_uid)

        print("Read Paprika Recipe")
        print(recipe)

        print("on_grocery_list: {}".format(recipe.load("on_grocery_list")))
        try:
            print("bad_key: {}".format(recipe.load("bad_key")))
        except KeyError:
            status = status and True
        except Exception:
            status = False

        status = status and (database.connection_is_open == False)
        return status

    TestList = [test0]
    SuccessCount = 0

    for test in TestList:
        print("Running: {}".format(test.__name__))
        status = test()
        print("Test Result: {}".format(status))
        if status is True:
            SuccessCount += 1

    print("Passed {}/{} Tests".format(SuccessCount, len(TestList)))
