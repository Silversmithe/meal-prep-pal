--
-- References root: https://www.sqlite.org/doclist.html

-- Create the recipe table
-- Ref. https://www.sqlite.org/lang_createtable.html
-- IDs are created from the recipe object
CREATE TABLE IF NOT EXISTS RECIPE_TABLE (
    uid             TEXT    UNIQUE NOT NULL,
    rating          INT     DEFAULT 0,
    photo_hash      TEXT    DEFAULT "",
    on_favorites    INT     DEFAULT 0, -- False
    photo           TEXT    DEFAULT "",
    scale           TEXT    DEFAULT "",
    ingredients     TEXT    DEFAULT "",
    is_pinned       INT     DEFAULT 0, -- False
    source          TEXT    DEFAULT "",
    total_time      TEXT    DEFAULT "",
    hash            TEXT    DEFAULT "",
    description     TEXT    DEFAULT "",
    source_url      TEXT    DEFAULT "",
    difficulty      TEXT    DEFAULT "",
    on_grocery_list INT     DEFAULT 0, -- False
    in_trash        INT     DEFAULT 0, -- False
    directions      TEXT    DEFAULT "",
    categories      TEXT    DEFAULT "", -- JSON list of categories
    photo_url       TEXT    DEFAULT "", -- Originally None
    cook_time       TEXT    DEFAULT "",
    name            TEXT    DEFAULT "",
    created         TEXT    DEFAULT "",
    notes           TEXT    DEFAULT "",
    photo_large     TEXT    DEFAULT "", -- Originally None
    image_url       TEXT    DEFAULT "",
    prep_time       TEXT    DEFAULT "",
    servings        TEXT    DEFAULT "",
    nutritional_info TEXT    DEFAULT "",
    -- Metadata for database management
    -- NOT a part of the recipe
    b_has_nutritional_info  INT    DEFAULT 0, -- False
    b_recipe_modified       INT    DEFAULT 0  -- False    
);

-- Create the meals table
-- Meals are one or more recipes
CREATE TABLE IF NOT EXISTS MEAL_TABLE (
    -- locally created ID
    id TEXT NOT NULL
);

-- Insert some fake values in
-- Ref. https://www.sqlite.org/lang_insert.html
-- Ref. https://www.sqlite.org/lang_delete.html
-- Ref. https://www.sqlite.org/lang_update.html
-- INSERT INTO RECIPE_TABLE (uid,name) VALUES ("647A8FCA-615C-4849-A692-94407600AB7A", "meh");
-- INSERT INTO RECIPE_TABLE (uid,name) VALUES ("0", "Test Recipe 1"),("1", "Test Recipe 2");