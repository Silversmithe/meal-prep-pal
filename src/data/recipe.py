
import json
import gzip
import hashlib

# User packages
import mpp_utils


"""
Example Recipe

{'rating': 5, 'photo_hash': '', 'on_favorites': False, 'photo': '', 'uid': '647A8FCA-615C-4849-A692-94407600AB7A',
'scale': '', 'ingredients': '1 cup bullshit', 'is_pinned': False, 'source': 'www.fakewebsite.com', 'total_time': '',
'hash': '585217406a5a39310b7f4f4ca6b445554b2c8426f86890d91374da9683979bd8', 'description': '', 'source_url': '',
'difficulty': 'Easy', 'on_grocery_list': False, 'in_trash': False, 'directions': 'Do nothing and give up BLAH',
'categories': [], 'photo_url': None, 'cook_time': '', 'name': 'Fake Recipe (Updated)', 'created': '2018-03-26 09:00:02',
'notes': '', 'photo_large': None, 'image_url': '', 'prep_time': '', 'servings': '',
'nutritional_info': '100 BILLION Calories'}
"""

"""
Recipe Object

Container for storing all information about the recipe
"""
class RecipeObject (object):

    def __init__(self) -> None:
        self.__recipe_data = {
            "uid": str(),
            "rating": int(),
            "photo_hash": str(),
            "on_favorites": bool(),
            "photo": str(),
            "scale": str(),
            "ingredients": str(),
            "is_pinned": bool(),
            "source": str(),
            "total_time": str(),
            "hash": str(),
            "description": str(),
            "source_url": str(),
            "difficulty": str(),
            "on_grocery_list": bool(),
            "in_trash": bool(),
            "directions": str(),
            "categories": [], # Note: List of strings
            "photo_url": None,
            "cook_time": str(),
            "name": str(),
            "created": str(),
            "notes": str(),
            "photo_large": None,
            "image_url": str(),
            "prep_time": str(),
            "servings": str(),
            "nutritional_info": str()
        }

    def init(self,
        uid: str, rating: int, photo_hash: str, on_favorites: bool, photo: str, scale: str,
        ingredients: str, is_pinned: bool, source: str, total_time: str, hash: str, description: str,
        source_url: str, difficulty: str, on_grocery_list: bool, in_trash: bool, directions: str, 
        categories, photo_url, cook_time: str, name: str, created: str, notes: str, photo_large,
        image_url: str, prep_time: str, servings: str, nutritional_info: str
    ):
        self.__recipe_data['uid'] = uid
        self.__recipe_data['rating'] = rating
        self.__recipe_data['photo_hash'] = photo_hash
        self.__recipe_data['on_favorites'] = on_favorites
        self.__recipe_data['photo'] = photo
        self.__recipe_data['scale'] = scale
        self.__recipe_data['ingredients'] = ingredients
        self.__recipe_data['is_pinned'] = is_pinned
        self.__recipe_data['source'] = source
        self.__recipe_data['total_time'] = total_time
        self.__recipe_data['hash'] = hash
        self.__recipe_data['description'] = description
        self.__recipe_data['source_url'] = source_url
        self.__recipe_data['difficulty'] = difficulty
        self.__recipe_data['on_grocery_list'] = on_grocery_list
        self.__recipe_data['in_trash'] = in_trash
        self.__recipe_data['directions'] = directions
        self.__recipe_data['categories'] = categories
        self.__recipe_data['photo_url'] = photo_url
        self.__recipe_data['cook_time'] = cook_time
        self.__recipe_data['name'] = name
        self.__recipe_data['created'] = created
        self.__recipe_data['notes'] = notes
        self.__recipe_data['photo_large'] = photo_large
        self.__recipe_data['image_url'] = image_url
        self.__recipe_data['prep_time'] = prep_time
        self.__recipe_data['servings'] = servings
        self.__recipe_data['nutritional_info'] = nutritional_info

    def load(self, key):
        """
        Throws a KeyError exception if the key does not exist
        in the dictionary.

        @retval value: if key exists
        """
        result = None
        if key in self.__recipe_data:
            result = self.__recipe_data[key]
        else:
            raise KeyError
        
        return result
    
    def store(self, key, value):
        """
        A more constrained setting of dictionary values. They are 
        constrained to within the keys already established in the object.
        You cannot create any new keys! 

        Make sure the type of the value matches the current type stored.
        """
        if key in self.__recipe_data:
            if type(value) == type(self.__recipe_data[key]):
                self.__recipe_data[key] = value
            else:
                mpp_utils.dbgPrint("unable to store value, types dont match!")
        else:
            raise KeyError

    def as_dict(self) -> dict:
        return self.__recipe_data
    
    def as_json(self) -> str:
        """
        @retval None: if the conversion to JSON does not work
        @retval str: the json result
        """
        result = None
        try:
            result = json.dumps(self.__recipe_data, sort_keys=True)
        except Exception as e:
            mpp_utils.dbgPrint("[{}] error while converting recipe to json".format(self.__recipe_data["uid"]))
            mpp_utils.dbgPrint(e)

        return result
    
    def calculate_hash_sha256(self) -> None:
        """
        Calculate the SHA256 Hash of the Paprika Recipe
        """
        # ref. https://github.com/coddingtonbear/paprika-recipes/blob/master/paprika_recipes/recipe.py
        # create a copy of the recipe
        scratch_recipe = dict(self.__recipe_data)
        # remove hash field while calculating new hash value
        scratch_recipe.pop('hash', None)
        # get JSON and do utf-8 encoding
        scratch_recipe_json = json.dumps(scratch_recipe, sort_keys=True).encode(encoding="utf-8")
        calculated_hash = hashlib.sha256(scratch_recipe_json).hexdigest()
        # update the recipe
        self.__recipe_data["hash"] = calculated_hash

    def __str__(self) -> str:
        result = "Paprika Recipe <{}> ({})".format(self.__recipe_data["uid"], self.__recipe_data["name"])
        return result