--
-- References root: https://www.sqlite.org/doclist.html

-- Create the recipe table
-- Ref. https://www.sqlite.org/lang_createtable.html
-- IDs are created from the recipe object
CREATE TABLE IF NOT EXISTS RECIPE_TABLE (
	uid TEXT NOT NULL,
    scale 
    name TEXT,
    description TEXT,
    ingredients TEXT,
    directions TEXT,
    notes TEXT,
    nutritional_info TEXT
);

-- Create the meals table
-- Meals are one or more recipes
CREATE TABLE IF NOT EXISTS MEAL_TABLE (
    -- locally created ID
    id TEXT NOT NULL
);

-- TEST DATA
-- Insert some fake values in
-- Ref. https://www.sqlite.org/lang_insert.html
-- Ref. https://www.sqlite.org/lang_delete.html
-- Ref. https://www.sqlite.org/lang_update.html
INSERT INTO RECIPE_TABLE VALUES ("Recipe 1",NULL), ("Recipe 2", NULL)