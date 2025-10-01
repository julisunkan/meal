#!/usr/bin/env python3
"""
Database initialization script for the meal planning application.
Creates tables and populates with diverse sample data.
"""

import sqlite3
import os

def create_connection(db_file):
    """Create a database connection to SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(f"Error creating connection: {e}")
    return conn

def create_tables(conn):
    """Create all necessary tables"""
    
    # Recipes table
    recipes_table = """
    CREATE TABLE IF NOT EXISTS recipes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        meal_type TEXT NOT NULL,
        instructions TEXT NOT NULL,
        calories INTEGER NOT NULL,
        protein REAL NOT NULL,
        carbs REAL NOT NULL,
        fat REAL NOT NULL
    );
    """
    
    # Ingredients table  
    ingredients_table = """
    CREATE TABLE IF NOT EXISTS ingredients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        category TEXT NOT NULL
    );
    """
    
    # Recipe ingredients junction table
    recipe_ingredients_table = """
    CREATE TABLE IF NOT EXISTS recipe_ingredients (
        recipe_id INTEGER NOT NULL,
        ingredient_id INTEGER NOT NULL,
        FOREIGN KEY (recipe_id) REFERENCES recipes (id),
        FOREIGN KEY (ingredient_id) REFERENCES ingredients (id),
        PRIMARY KEY (recipe_id, ingredient_id)
    );
    """
    
    # Recipe dietary tags
    recipe_dietary_tags_table = """
    CREATE TABLE IF NOT EXISTS recipe_dietary_tags (
        recipe_id INTEGER NOT NULL,
        tag TEXT NOT NULL,
        FOREIGN KEY (recipe_id) REFERENCES recipes (id),
        PRIMARY KEY (recipe_id, tag)
    );
    """
    
    # Recipe races/ethnicities
    recipe_races_table = """
    CREATE TABLE IF NOT EXISTS recipe_races (
        recipe_id INTEGER NOT NULL,
        race TEXT NOT NULL,
        FOREIGN KEY (recipe_id) REFERENCES recipes (id),
        PRIMARY KEY (recipe_id, race)
    );
    """
    
    # Ingredient substitutions
    substitutions_table = """
    CREATE TABLE IF NOT EXISTS substitutions (
        ingredient_id INTEGER NOT NULL,
        substitute_ingredient_id INTEGER NOT NULL,
        FOREIGN KEY (ingredient_id) REFERENCES ingredients (id),
        FOREIGN KEY (substitute_ingredient_id) REFERENCES ingredients (id),
        PRIMARY KEY (ingredient_id, substitute_ingredient_id)
    );
    """
    
    # Recipe ratings
    ratings_table = """
    CREATE TABLE IF NOT EXISTS ratings (
        recipe_id INTEGER NOT NULL,
        rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
        FOREIGN KEY (recipe_id) REFERENCES recipes (id),
        PRIMARY KEY (recipe_id)
    );
    """
    
    try:
        cursor = conn.cursor()
        cursor.execute(recipes_table)
        cursor.execute(ingredients_table)
        cursor.execute(recipe_ingredients_table)
        cursor.execute(recipe_dietary_tags_table)
        cursor.execute(recipe_races_table)
        cursor.execute(substitutions_table)
        cursor.execute(ratings_table)
        conn.commit()
        print("All tables created successfully")
    except sqlite3.Error as e:
        print(f"Error creating tables: {e}")

def populate_ingredients(conn):
    """Populate ingredients table with diverse ingredients"""
    
    ingredients = [
        # Proteins
        ('chicken breast', 'protein'), ('beef', 'protein'), ('salmon', 'protein'), 
        ('tofu', 'protein'), ('eggs', 'protein'), ('black beans', 'protein'),
        ('lentils', 'protein'), ('chickpeas', 'protein'), ('pork', 'protein'),
        ('shrimp', 'protein'), ('tempeh', 'protein'), ('quinoa', 'protein'),
        
        # Vegetables
        ('onion', 'vegetable'), ('garlic', 'vegetable'), ('tomato', 'vegetable'),
        ('bell pepper', 'vegetable'), ('carrot', 'vegetable'), ('broccoli', 'vegetable'),
        ('spinach', 'vegetable'), ('mushroom', 'vegetable'), ('zucchini', 'vegetable'),
        ('cucumber', 'vegetable'), ('lettuce', 'vegetable'), ('corn', 'vegetable'),
        ('potato', 'vegetable'), ('sweet potato', 'vegetable'), ('cabbage', 'vegetable'),
        ('ginger', 'vegetable'), ('cilantro', 'vegetable'), ('bok choy', 'vegetable'),
        
        # Grains
        ('rice', 'grain'), ('pasta', 'grain'), ('bread', 'grain'), ('oats', 'grain'),
        ('flour', 'grain'), ('couscous', 'grain'), ('bulgur', 'grain'),
        ('jasmine rice', 'grain'), ('basmati rice', 'grain'), ('tortillas', 'grain'),
        
        # Dairy
        ('milk', 'dairy'), ('cheese', 'dairy'), ('yogurt', 'dairy'), ('butter', 'dairy'),
        ('cream cheese', 'dairy'), ('sour cream', 'dairy'), ('mozzarella', 'dairy'),
        ('coconut milk', 'dairy'), ('almond milk', 'dairy'),
        
        # Spices & Seasonings
        ('salt', 'spice'), ('pepper', 'spice'), ('cumin', 'spice'), ('paprika', 'spice'),
        ('turmeric', 'spice'), ('curry powder', 'spice'), ('soy sauce', 'spice'),
        ('olive oil', 'spice'), ('sesame oil', 'spice'), ('vinegar', 'spice'),
        ('lime', 'spice'), ('lemon', 'spice'), ('chili powder', 'spice'),
        ('oregano', 'spice'), ('basil', 'spice'), ('thyme', 'spice'),
        ('cinnamon', 'spice'), ('vanilla', 'spice'), ('garam masala', 'spice'),
        ('miso paste', 'spice'), ('fish sauce', 'spice'), ('harissa', 'spice'),
        
        # Fruits
        ('apple', 'fruit'), ('banana', 'fruit'), ('orange', 'fruit'), ('berries', 'fruit'),
        ('mango', 'fruit'), ('avocado', 'fruit'), ('pineapple', 'fruit'),
        ('coconut', 'fruit'), ('dates', 'fruit'), ('pomegranate', 'fruit'),
        
        # Beverages
        ('tea', 'beverage'), ('coffee', 'beverage'), ('green tea', 'beverage'),
        ('orange juice', 'beverage'), ('coconut water', 'beverage'),
        ('mango lassi', 'beverage'), ('hibiscus tea', 'beverage'),
        
        # Nuts & Seeds
        ('almonds', 'nuts'), ('walnuts', 'nuts'), ('sesame seeds', 'nuts'),
        ('peanuts', 'nuts'), ('cashews', 'nuts'), ('pine nuts', 'nuts'),
        
        # Other
        ('honey', 'sweetener'), ('sugar', 'sweetener'), ('maple syrup', 'sweetener'),
        ('vegetable broth', 'broth'), ('chicken broth', 'broth'), ('wine', 'alcohol')
    ]
    
    try:
        cursor = conn.cursor()
        cursor.executemany("INSERT OR IGNORE INTO ingredients (name, category) VALUES (?, ?)", ingredients)
        conn.commit()
        print(f"Inserted {len(ingredients)} ingredients")
    except sqlite3.Error as e:
        print(f"Error inserting ingredients: {e}")

def populate_recipes(conn):
    """Populate recipes with diverse cultural dishes"""
    
    recipes = [
        # Asian recipes
        (1, "Chicken Teriyaki Bowl", "lunch", "Marinate chicken in teriyaki sauce. Grill chicken and serve over rice with steamed vegetables.", 450, 35, 45, 12),
        (2, "Miso Soup", "appetizer", "Heat water, add miso paste, tofu, and seaweed. Simmer for 5 minutes.", 80, 6, 8, 3),
        (3, "Green Tea", "drink", "Steep green tea leaves in hot water for 3-5 minutes.", 2, 0, 0, 0),
        (4, "Vegetable Fried Rice", "dinner", "Stir-fry rice with mixed vegetables, soy sauce, and sesame oil.", 320, 8, 58, 8),
        (5, "Mango Sticky Rice", "dessert", "Cook sticky rice with coconut milk, serve with fresh mango slices.", 280, 4, 52, 8),
        
        # African recipes  
        (6, "Jollof Rice", "dinner", "Cook rice with tomatoes, onions, peppers, and spices until fragrant and flavorful.", 380, 12, 62, 10),
        (7, "Plantain Chips", "appetizer", "Slice plantains thin and fry until crispy. Season with salt.", 150, 2, 35, 5),
        (8, "Hibiscus Tea", "drink", "Steep dried hibiscus flowers in hot water. Add honey to taste.", 25, 0, 6, 0),
        (9, "Coconut Rice Pudding", "dessert", "Cook rice with coconut milk and sugar until creamy.", 220, 4, 42, 6),
        (10, "Spiced Lentil Stew", "lunch", "Cook lentils with onions, tomatoes, and African spices.", 290, 18, 45, 4),
        
        # Hispanic recipes
        (11, "Black Bean Tacos", "lunch", "Warm tortillas, fill with seasoned black beans, cheese, and salsa.", 340, 15, 48, 12),
        (12, "Guacamole", "appetizer", "Mash avocados with lime, onion, cilantro, and salt.", 160, 3, 8, 15),
        (13, "Horchata", "drink", "Blend rice, cinnamon, vanilla, and milk. Strain and chill.", 180, 3, 28, 6),
        (14, "Tres Leches Cake", "dessert", "Sponge cake soaked in three types of milk.", 320, 6, 45, 14),
        (15, "Chicken Enchiladas", "dinner", "Roll chicken in tortillas, top with sauce and cheese, bake.", 420, 28, 35, 18),
        
        # Caucasian recipes
        (16, "Caesar Salad", "lunch", "Toss romaine lettuce with Caesar dressing, croutons, and parmesan.", 280, 8, 15, 22),
        (17, "Garlic Bread", "appetizer", "Spread garlic butter on bread, bake until golden.", 220, 6, 28, 12),
        (18, "Iced Coffee", "drink", "Brew strong coffee, chill, serve over ice with milk.", 50, 2, 8, 1),
        (19, "Apple Pie", "dessert", "Bake spiced apples in pastry crust until golden.", 350, 4, 52, 16),
        (20, "Grilled Salmon", "dinner", "Season salmon with herbs, grill until flaky.", 380, 42, 2, 18),
        
        # Middle Eastern recipes
        (21, "Hummus", "appetizer", "Blend chickpeas, tahini, lemon, and garlic until smooth.", 180, 8, 20, 10),
        (22, "Chicken Shawarma", "lunch", "Marinate chicken in Middle Eastern spices, roast and slice.", 400, 35, 15, 22),
        (23, "Turkish Tea", "drink", "Brew strong black tea in traditional tea glasses.", 10, 0, 2, 0),
        (24, "Baklava", "dessert", "Layer phyllo with nuts and honey syrup.", 280, 6, 32, 16),
        (25, "Lamb Pilaf", "dinner", "Cook rice with lamb, onions, and Middle Eastern spices.", 450, 25, 48, 18),
        
        # Breakfast items across cultures
        (26, "Congee", "breakfast", "Cook rice in broth until porridge-like. Top with ginger and green onions.", 200, 6, 38, 2),
        (27, "Injera with Lentils", "breakfast", "Serve spongy Ethiopian bread with spiced lentils.", 250, 12, 45, 3),
        (28, "Breakfast Burrito", "breakfast", "Scrambled eggs with beans, cheese, and salsa in tortilla.", 380, 18, 32, 20),
        (29, "English Breakfast", "breakfast", "Eggs, beans, toast, and grilled tomatoes.", 420, 22, 35, 24),
        (30, "Turkish Breakfast", "breakfast", "Cheese, olives, bread, tomatoes, and tea.", 350, 15, 30, 20),
        
        # More drinks
        (31, "Mango Lassi", "drink", "Blend mango, yogurt, and cardamom until smooth.", 150, 4, 28, 3),
        (32, "Mint Tea", "drink", "Steep mint leaves in hot water with sugar.", 30, 0, 8, 0),
        (33, "Fresh Orange Juice", "drink", "Squeeze fresh oranges, strain pulp if desired.", 110, 2, 26, 0),
        
        # More appetizers
        (34, "Spring Rolls", "appetizer", "Wrap vegetables in rice paper, serve with dipping sauce.", 120, 4, 22, 2),
        (35, "Stuffed Dates", "appetizer", "Fill dates with nuts and cream cheese.", 180, 4, 28, 8),
        (36, "Bruschetta", "appetizer", "Top toasted bread with tomatoes, basil, and garlic.", 140, 4, 20, 6),
        
        # More desserts
        (37, "Mochi Ice Cream", "dessert", "Wrap ice cream in sweet rice dough.", 160, 3, 28, 6),
        (38, "Flan", "dessert", "Caramel custard dessert.", 240, 6, 35, 9),
        (39, "Tiramisu", "dessert", "Coffee-soaked ladyfingers with mascarpone.", 300, 8, 32, 18),
        
        # Additional Asian recipes
        (40, "Ramen Noodle Soup", "lunch", "Cook ramen noodles in rich broth with vegetables and egg.", 420, 18, 52, 14),
        (41, "Korean Bibimbap", "dinner", "Serve rice with seasoned vegetables, meat, and fried egg.", 480, 22, 68, 16),
        (42, "Pad Thai", "lunch", "Stir-fry rice noodles with shrimp, tofu, and tamarind sauce.", 390, 16, 58, 12),
        (43, "Japanese Pancakes", "breakfast", "Fluffy pancakes served with syrup and butter.", 320, 8, 45, 12),
        (44, "Thai Tom Yum Soup", "appetizer", "Spicy and sour soup with lemongrass and lime leaves.", 85, 6, 12, 2),
        (45, "Matcha Latte", "drink", "Whisk matcha powder with steamed milk and sweetener.", 120, 4, 18, 4),
        (46, "Vietnamese Spring Rolls", "appetizer", "Fresh rolls with vegetables, herbs, and dipping sauce.", 140, 5, 25, 3),
        (47, "Chinese Congee", "breakfast", "Rice porridge cooked until creamy, topped with ginger.", 180, 6, 35, 2),
        (48, "Thai Mango Salad", "lunch", "Shredded green mango with lime, chili, and peanuts.", 160, 4, 28, 6),
        (49, "Korean Kimchi", "appetizer", "Fermented cabbage with garlic, ginger, and chili.", 25, 2, 5, 0),
        
        # Additional African recipes
        (50, "Moroccan Tagine", "dinner", "Slow-cooked stew with meat, vegetables, and preserved lemons.", 350, 28, 25, 18),
        (51, "Ethiopian Injera", "breakfast", "Spongy flatbread made from teff flour.", 220, 8, 42, 2),
        (52, "West African Fufu", "dinner", "Pounded yam or cassava served with soup.", 280, 4, 68, 1),
        (53, "South African Bobotie", "lunch", "Spiced meat casserole topped with egg custard.", 410, 25, 15, 28),
        (54, "Moroccan Mint Tea", "drink", "Green tea brewed with fresh mint and sugar.", 35, 0, 9, 0),
        (55, "Nigerian Suya", "appetizer", "Grilled spiced meat skewers.", 250, 20, 5, 16),
        (56, "Ethiopian Doro Wat", "dinner", "Spicy chicken stew with berbere spice blend.", 380, 32, 18, 22),
        (57, "African Peanut Soup", "lunch", "Creamy soup with peanuts, vegetables, and meat.", 320, 14, 22, 20),
        (58, "Malva Pudding", "dessert", "Sweet sponge cake with apricot jam and custard.", 290, 5, 48, 12),
        (59, "Biltong", "appetizer", "Dried and seasoned meat strips.", 180, 30, 2, 6),
        
        # Additional Hispanic recipes
        (60, "Paella Valenciana", "dinner", "Spanish rice dish with saffron, chicken, and seafood.", 450, 35, 45, 18),
        (61, "Churros", "dessert", "Fried dough pastry dusted with cinnamon sugar.", 280, 4, 35, 15),
        (62, "Ceviche", "lunch", "Raw fish marinated in citrus juice with onions and peppers.", 180, 25, 8, 2),
        (63, "Empanadas", "appetizer", "Baked pastries filled with meat, cheese, or vegetables.", 220, 10, 25, 12),
        (64, "Mexican Hot Chocolate", "drink", "Rich chocolate drink with cinnamon and chili.", 200, 6, 32, 8),
        (65, "Arroz con Leche", "dessert", "Creamy rice pudding with cinnamon and vanilla.", 240, 6, 45, 6),
        (66, "Mole Poblano", "dinner", "Complex sauce with chocolate and chili over chicken.", 480, 38, 25, 28),
        (67, "Gazpacho", "appetizer", "Cold soup made with tomatoes, peppers, and cucumbers.", 90, 3, 18, 2),
        (68, "Frijoles Refritos", "lunch", "Refried beans with onions and spices.", 180, 12, 28, 4),
        (69, "Dulce de Leche", "dessert", "Sweet caramel sauce made from milk and sugar.", 320, 8, 52, 12),
        
        # Additional Caucasian recipes
        (70, "Beef Wellington", "dinner", "Beef tenderloin wrapped in pastry with mushroom duxelles.", 580, 42, 35, 32),
        (71, "French Croissant", "breakfast", "Buttery, flaky pastry perfect for breakfast.", 350, 8, 32, 22),
        (72, "Italian Minestrone", "lunch", "Hearty vegetable soup with pasta and beans.", 220, 10, 35, 6),
        (73, "German Sauerbraten", "dinner", "Marinated pot roast with sweet and sour sauce.", 420, 38, 18, 22),
        (74, "French Onion Soup", "appetizer", "Rich soup with caramelized onions and cheese.", 280, 12, 25, 16),
        (75, "Espresso", "drink", "Strong Italian coffee served in small portions.", 5, 0, 1, 0),
        (76, "British Shepherd's Pie", "dinner", "Ground lamb with vegetables topped with mashed potatoes.", 380, 22, 35, 18),
        (77, "Italian Gelato", "dessert", "Dense, creamy Italian ice cream.", 180, 4, 25, 8),
        (78, "German Pretzel", "appetizer", "Twisted bread with coarse salt.", 250, 8, 48, 4),
        (79, "French Ratatouille", "lunch", "Vegetable stew with eggplant, zucchini, and tomatoes.", 140, 5, 25, 4),
        
        # Additional Middle Eastern recipes
        (80, "Turkish Baklava", "dessert", "Layered pastry with nuts and honey syrup.", 320, 6, 35, 18),
        (81, "Lebanese Fattoush", "lunch", "Salad with mixed greens, vegetables, and crispy pita.", 180, 6, 25, 8),
        (82, "Persian Kebab", "dinner", "Grilled meat skewers with saffron rice.", 420, 35, 32, 18),
        (83, "Turkish Coffee", "drink", "Strong coffee brewed in special pot with cardamom.", 12, 0, 2, 0),
        (84, "Baba Ganoush", "appetizer", "Roasted eggplant dip with tahini and garlic.", 120, 4, 12, 8),
        (85, "Lebanese Kibbeh", "lunch", "Fried bulgur shells stuffed with spiced meat.", 280, 16, 25, 14),
        (86, "Middle Eastern Rice Pilaf", "dinner", "Fragrant rice with almonds and raisins.", 320, 8, 58, 8),
        (87, "Turkish Delight", "dessert", "Gel confection with rose water and nuts.", 180, 2, 42, 2),
        (88, "Moroccan Couscous", "lunch", "Steamed semolina with vegetables and meat.", 350, 18, 52, 8),
        (89, "Persian Doogh", "drink", "Yogurt drink with mint and salt.", 85, 4, 12, 2),
        
        # More breakfast options
        (90, "American Pancakes", "breakfast", "Fluffy pancakes with maple syrup and butter.", 380, 8, 52, 16),
        (91, "English Muffin", "breakfast", "Toasted muffin with butter and jam.", 180, 6, 28, 5),
        (92, "Spanish Tortilla", "breakfast", "Potato and egg omelet served at room temperature.", 290, 15, 22, 18),
        (93, "French Crepes", "breakfast", "Thin pancakes with various sweet or savory fillings.", 220, 6, 32, 8),
        (94, "Mexican Breakfast Burrito", "breakfast", "Tortilla filled with eggs, beans, and salsa.", 420, 20, 38, 22),
        (95, "Asian Rice Porridge", "breakfast", "Creamy rice with ginger and green onions.", 160, 5, 32, 2),
        (96, "African Porridge", "breakfast", "Millet or sorghum porridge with milk and honey.", 180, 6, 35, 3),
        (97, "Middle Eastern Manakish", "breakfast", "Flatbread topped with za'atar and olive oil.", 220, 6, 35, 8),
        (98, "German Muesli", "breakfast", "Oats with nuts, fruits, and yogurt.", 240, 8, 38, 8),
        (99, "Italian Cornetto", "breakfast", "Sweet pastry similar to croissant.", 280, 6, 35, 14),
        
        # More drinks
        (100, "Chai Tea Latte", "drink", "Spiced tea with steamed milk.", 150, 4, 25, 5),
        (101, "Fresh Orange Juice", "drink", "Freshly squeezed orange juice.", 110, 2, 26, 0),
        (102, "Coconut Water", "drink", "Natural coconut water.", 45, 1, 9, 0),
        (103, "Smoothie Bowl", "drink", "Thick fruit smoothie topped with granola.", 280, 8, 52, 6),
        (104, "Lemonade", "drink", "Fresh lemon juice with sugar and water.", 90, 0, 24, 0),
        (105, "Kombucha", "drink", "Fermented tea with probiotics.", 30, 0, 7, 0)
    ]
    
    try:
        cursor = conn.cursor()
        for recipe in recipes:
            cursor.execute("""
                INSERT OR IGNORE INTO recipes (id, title, meal_type, instructions, calories, protein, carbs, fat) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, recipe)
        conn.commit()
        print(f"Inserted {len(recipes)} recipes")
    except sqlite3.Error as e:
        print(f"Error inserting recipes: {e}")

def populate_recipe_ingredients(conn):
    """Link recipes to their ingredients"""
    
    recipe_ingredients = [
        # Chicken Teriyaki Bowl (1)
        (1, 1), (1, 30), (1, 31), (1, 17), (1, 18),  # chicken, rice, soy sauce, broccoli, carrot
        
        # Miso Soup (2)  
        (2, 45), (2, 5),  # miso paste, tofu
        
        # Green Tea (3)
        (3, 57),  # green tea
        
        # Vegetable Fried Rice (4)
        (4, 30), (4, 13), (4, 14), (4, 17), (4, 31), (4, 32),  # rice, onion, garlic, broccoli, soy sauce, sesame oil
        
        # Mango Sticky Rice (5)
        (5, 30), (5, 28), (5, 55),  # rice, coconut milk, mango
        
        # Jollof Rice (6)
        (6, 30), (6, 15), (6, 13), (6, 14), (6, 38),  # rice, tomato, onion, garlic, paprika
        
        # Plantain Chips (7)
        (7, 56), (7, 37),  # plantain, salt
        
        # Hibiscus Tea (8)
        (8, 61), (8, 67),  # hibiscus tea, honey
        
        # Coconut Rice Pudding (9)
        (9, 30), (9, 28), (9, 68),  # rice, coconut milk, sugar
        
        # Spiced Lentil Stew (10)
        (10, 7), (10, 13), (10, 15), (10, 39),  # lentils, onion, tomato, turmeric
        
        # Black Bean Tacos (11)
        (11, 35), (11, 6), (11, 26),  # tortillas, black beans, cheese
        
        # Guacamole (12)
        (12, 56), (12, 34), (12, 13), (12, 17),  # avocado, lime, onion, cilantro
        
        # Horchata (13)
        (13, 30), (13, 47), (13, 49), (13, 25),  # rice, cinnamon, vanilla, milk
        
        # Tres Leches Cake (14)
        (14, 33), (14, 25), (14, 27), (14, 29),  # flour, milk, cream cheese, butter
        
        # Chicken Enchiladas (15)
        (15, 1), (15, 35), (15, 26),  # chicken, tortillas, cheese
        
        # Caesar Salad (16)
        (16, 21), (16, 26),  # lettuce, cheese
        
        # Garlic Bread (17)
        (17, 31), (17, 14), (17, 29),  # bread, garlic, butter
        
        # Iced Coffee (18)
        (18, 58), (18, 25),  # coffee, milk
        
        # Apple Pie (19)
        (19, 51), (19, 33), (19, 47),  # apple, flour, cinnamon
        
        # Grilled Salmon (20)
        (20, 3), (20, 45),  # salmon, oregano
        
        # Hummus (21)
        (21, 8), (21, 34), (21, 14),  # chickpeas, lemon, garlic
        
        # Chicken Shawarma (22)
        (22, 1), (22, 39), (22, 40),  # chicken, turmeric, cumin
        
        # Turkish Tea (23)
        (23, 57),  # tea
        
        # Baklava (24)
        (24, 65), (24, 67),  # nuts, honey
        
        # Lamb Pilaf (25)
        (25, 9), (25, 30), (25, 13),  # lamb, rice, onion
        
        # Congee (26)
        (26, 30), (26, 70), (26, 16),  # rice, broth, ginger
        
        # Injera with Lentils (27)
        (27, 33), (27, 7),  # flour, lentils
        
        # Breakfast Burrito (28)
        (28, 5), (28, 6), (28, 26), (28, 35),  # eggs, black beans, cheese, tortillas
        
        # English Breakfast (29)
        (29, 5), (29, 6), (29, 31), (29, 15),  # eggs, beans, bread, tomato
        
        # Turkish Breakfast (30)
        (30, 26), (30, 31), (30, 15),  # cheese, bread, tomato
        
        # Mango Lassi (31)
        (31, 55), (31, 27),  # mango, yogurt
        
        # Mint Tea (32)
        (32, 57), (32, 68),  # tea, sugar
        
        # Fresh Orange Juice (33)
        (33, 53),  # orange
        
        # Spring Rolls (34)
        (34, 17), (34, 18), (34, 19),  # vegetables
        
        # Stuffed Dates (35)
        (35, 56), (35, 65), (35, 29),  # dates, nuts, cream cheese
        
        # Bruschetta (36)
        (36, 31), (36, 15), (36, 45), (36, 14),  # bread, tomato, basil, garlic
        
        # Mochi Ice Cream (37)
        (37, 30), (37, 68),  # rice, sugar
        
        # Flan (38)
        (38, 5), (38, 25), (38, 68),  # eggs, milk, sugar
        
        # Tiramisu (39)
        (39, 58), (39, 29)  # coffee, cream cheese
    ]
    
    try:
        cursor = conn.cursor()
        cursor.executemany("INSERT OR IGNORE INTO recipe_ingredients (recipe_id, ingredient_id) VALUES (?, ?)", recipe_ingredients)
        conn.commit()
        print(f"Inserted {len(recipe_ingredients)} recipe-ingredient relationships")
    except sqlite3.Error as e:
        print(f"Error inserting recipe ingredients: {e}")

def populate_dietary_tags(conn):
    """Add dietary preference tags to recipes"""
    
    dietary_tags = [
        # Vegan recipes
        (3, 'vegan'), (4, 'vegan'), (7, 'vegan'), (8, 'vegan'), (10, 'vegan'),
        (12, 'vegan'), (21, 'vegan'), (26, 'vegan'), (32, 'vegan'), (33, 'vegan'),
        (34, 'vegan'),
        
        # Vegetarian recipes  
        (2, 'vegetarian'), (3, 'vegetarian'), (4, 'vegetarian'), (5, 'vegetarian'),
        (7, 'vegetarian'), (8, 'vegetarian'), (9, 'vegetarian'), (10, 'vegetarian'),
        (12, 'vegetarian'), (13, 'vegetarian'), (14, 'vegetarian'), (17, 'vegetarian'),
        (18, 'vegetarian'), (19, 'vegetarian'), (21, 'vegetarian'), (23, 'vegetarian'),
        (24, 'vegetarian'), (26, 'vegetarian'), (27, 'vegetarian'), (31, 'vegetarian'),
        (32, 'vegetarian'), (33, 'vegetarian'), (34, 'vegetarian'), (35, 'vegetarian'),
        (36, 'vegetarian'), (37, 'vegetarian'), (38, 'vegetarian'), (39, 'vegetarian'),
        
        # Gluten-free recipes
        (2, 'gluten-free'), (3, 'gluten-free'), (6, 'gluten-free'), (7, 'gluten-free'),
        (8, 'gluten-free'), (9, 'gluten-free'), (10, 'gluten-free'), (12, 'gluten-free'),
        (13, 'gluten-free'), (18, 'gluten-free'), (20, 'gluten-free'), (21, 'gluten-free'),
        (22, 'gluten-free'), (23, 'gluten-free'), (25, 'gluten-free'), (26, 'gluten-free'),
        (31, 'gluten-free'), (32, 'gluten-free'), (33, 'gluten-free'), (34, 'gluten-free'),
        (35, 'gluten-free'), (37, 'gluten-free'), (38, 'gluten-free')
    ]
    
    try:
        cursor = conn.cursor()
        cursor.executemany("INSERT OR IGNORE INTO recipe_dietary_tags (recipe_id, tag) VALUES (?, ?)", dietary_tags)
        conn.commit()
        print(f"Inserted {len(dietary_tags)} dietary tags")
    except sqlite3.Error as e:
        print(f"Error inserting dietary tags: {e}")

def populate_race_tags(conn):
    """Add cultural/ethnic tags to recipes"""
    
    race_tags = [
        # Asian recipes
        (1, 'Asian'), (2, 'Asian'), (3, 'Asian'), (4, 'Asian'), (5, 'Asian'),
        (26, 'Asian'), (34, 'Asian'), (37, 'Asian'),
        
        # African recipes
        (6, 'African'), (7, 'African'), (8, 'African'), (9, 'African'), (10, 'African'),
        (27, 'African'),
        
        # Hispanic recipes
        (11, 'Hispanic'), (12, 'Hispanic'), (13, 'Hispanic'), (14, 'Hispanic'), (15, 'Hispanic'),
        (28, 'Hispanic'), (38, 'Hispanic'),
        
        # Caucasian recipes
        (16, 'Caucasian'), (17, 'Caucasian'), (18, 'Caucasian'), (19, 'Caucasian'), (20, 'Caucasian'),
        (29, 'Caucasian'), (36, 'Caucasian'), (39, 'Caucasian'),
        
        # Middle Eastern recipes
        (21, 'Middle Eastern'), (22, 'Middle Eastern'), (23, 'Middle Eastern'), (24, 'Middle Eastern'), (25, 'Middle Eastern'),
        (30, 'Middle Eastern'), (31, 'Middle Eastern'), (32, 'Middle Eastern'), (35, 'Middle Eastern'),
        
        # Universal recipes (can appear in multiple cultures)
        (33, 'Caucasian'), (33, 'Hispanic'), (33, 'Asian'),  # Orange juice
    ]
    
    try:
        cursor = conn.cursor()
        cursor.executemany("INSERT OR IGNORE INTO recipe_races (recipe_id, race) VALUES (?, ?)", race_tags)
        conn.commit()
        print(f"Inserted {len(race_tags)} race tags")
    except sqlite3.Error as e:
        print(f"Error inserting race tags: {e}")

def populate_substitutions(conn):
    """Add ingredient substitutions"""
    
    substitutions = [
        # Protein substitutions
        (1, 5),   # chicken -> eggs
        (1, 4),   # chicken -> tofu
        (3, 10),  # salmon -> shrimp
        (4, 2),   # tofu -> beef
        (6, 8),   # black beans -> chickpeas
        (7, 6),   # lentils -> black beans
        
        # Dairy substitutions
        (25, 28), # milk -> coconut milk
        (25, 29), # milk -> almond milk
        (26, 27), # cheese -> yogurt
        (29, 25), # butter -> coconut oil (represented as coconut milk)
        
        # Grain substitutions
        (30, 32), # rice -> quinoa
        (31, 34), # pasta -> couscous
        (32, 35), # bread -> tortillas
        (33, 30), # oats -> rice
        
        # Spice substitutions
        (40, 39), # cumin -> turmeric
        (38, 43), # paprika -> chili powder
        (47, 68), # cinnamon -> sugar (for sweetness)
        
        # Vegetable substitutions
        (13, 16), # onion -> ginger
        (15, 19), # tomato -> mushroom
        (16, 14), # bell pepper -> garlic
        (18, 19), # carrot -> mushroom
        (20, 17)  # spinach -> broccoli
    ]
    
    try:
        cursor = conn.cursor()
        cursor.executemany("INSERT OR IGNORE INTO substitutions (ingredient_id, substitute_ingredient_id) VALUES (?, ?)", substitutions)
        conn.commit()
        print(f"Inserted {len(substitutions)} substitutions")
    except sqlite3.Error as e:
        print(f"Error inserting substitutions: {e}")

def populate_ratings(conn):
    """Add sample ratings to recipes"""
    
    ratings = [
        (1, 4), (2, 5), (3, 4), (4, 5), (5, 4), (6, 5), (7, 3), (8, 4), (9, 4), (10, 5),
        (11, 4), (12, 5), (13, 4), (14, 5), (15, 4), (16, 4), (17, 3), (18, 4), (19, 5), (20, 5),
        (21, 5), (22, 4), (23, 4), (24, 5), (25, 4), (26, 4), (27, 4), (28, 4), (29, 4), (30, 4),
        (31, 5), (32, 4), (33, 4), (34, 4), (35, 4), (36, 4), (37, 5), (38, 5), (39, 5)
    ]
    
    try:
        cursor = conn.cursor()
        cursor.executemany("INSERT OR IGNORE INTO ratings (recipe_id, rating) VALUES (?, ?)", ratings)
        conn.commit()
        print(f"Inserted {len(ratings)} ratings")
    except sqlite3.Error as e:
        print(f"Error inserting ratings: {e}")

def initialize_database():
    """Main function to initialize the database"""
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Database file path
    database = "data/meal_planner.db"
    
    # Create connection
    conn = create_connection(database)
    
    if conn is not None:
        print("Creating tables...")
        create_tables(conn)
        
        print("Populating ingredients...")
        populate_ingredients(conn)
        
        print("Populating recipes...")
        populate_recipes(conn)
        
        print("Linking recipes to ingredients...")
        populate_recipe_ingredients(conn)
        
        print("Adding dietary tags...")
        populate_dietary_tags(conn)
        
        print("Adding cultural tags...")
        populate_race_tags(conn)
        
        print("Adding substitutions...")
        populate_substitutions(conn)
        
        print("Adding ratings...")
        populate_ratings(conn)
        
        conn.close()
        print(f"Database initialization complete! Database saved as {database}")
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    initialize_database()