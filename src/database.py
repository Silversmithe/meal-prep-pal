
import sqlite3
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

    def open(self) -> int:
        """
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
            return Database.Error.ERR_GENERIC
        
        self.connection_is_open = True
        return Database.Error.ERR_SUCCESS

    def close(self) -> int:
        """
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
    
    def write_recipe(self, paprika_recipe: RecipeObject):
        pass

    def read_recipe(self) -> RecipeObject:
        pass

##########################
## IN-FILE UNIT TESTING ##
##########################
## Run Tests if the config is 
if mpp_utils.APP__CONFIG__UNIT_TEST == True:
    """
    Test normal usage
    """
    def test0() -> bool:
        status = True
        database = Database()
        database.open()
        database.close()
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
