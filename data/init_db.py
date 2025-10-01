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
        (1, "Chicken Teriyaki Bowl", "lunch", "Step 1: Cut 1 lb chicken breast into bite-sized pieces. Step 2: In a bowl, mix 1/4 cup soy sauce, 2 tbsp honey, 1 tbsp rice vinegar, 1 tsp ginger, and 2 cloves minced garlic. Step 3: Marinate chicken in sauce for 30 minutes. Step 4: Heat 1 tbsp oil in a large skillet over medium-high heat. Step 5: Cook chicken for 6-8 minutes until golden brown and cooked through. Step 6: Meanwhile, steam 2 cups broccoli and carrots for 5 minutes. Step 7: Cook 2 cups jasmine rice according to package directions. Step 8: Serve chicken over rice with steamed vegetables. Step 9: Drizzle remaining teriyaki sauce on top.", 450, 35, 45, 12),
        (2, "Miso Soup", "appetizer", "Step 1: Bring 4 cups water to a gentle simmer in a medium pot. Step 2: Cut 4 oz tofu into small cubes. Step 3: In a small bowl, whisk 3 tbsp miso paste with 1/2 cup of the hot water until smooth. Step 4: Add miso mixture back to the pot. Step 5: Add tofu cubes and 2 tbsp wakame seaweed. Step 6: Simmer for 2-3 minutes (do not boil). Step 7: Remove from heat and stir in 2 chopped green onions. Step 8: Serve immediately in small bowls.", 80, 6, 8, 3),
        (3, "Green Tea", "drink", "Step 1: Heat water to 175°F (80°C) - do not use boiling water. Step 2: Measure 1 tsp loose green tea leaves or 1 tea bag per cup. Step 3: Pour hot water over tea leaves in a teapot or cup. Step 4: Steep for 2-3 minutes for delicate flavor, or up to 5 minutes for stronger taste. Step 5: Remove tea leaves or tea bag. Step 6: Serve immediately. Optional: Add honey to taste.", 2, 0, 0, 0),
        (4, "Vegetable Fried Rice", "dinner", "Step 1: Cook 2 cups rice and let cool completely (preferably day-old rice). Step 2: Heat 2 tbsp oil in a large wok or skillet over high heat. Step 3: Add 1 diced onion and cook for 2 minutes. Step 4: Add 2 minced garlic cloves and cook 30 seconds. Step 5: Add 1 cup mixed vegetables (carrots, peas, broccoli) and stir-fry 3-4 minutes. Step 6: Push vegetables to one side, scramble 2 beaten eggs on the other side. Step 7: Add rice and toss everything together. Step 8: Stir in 3 tbsp soy sauce and 1 tsp sesame oil. Step 9: Cook 2-3 minutes more, tossing constantly. Step 10: Garnish with sliced green onions.", 320, 8, 58, 8),
        (5, "Mango Sticky Rice", "dessert", "Step 1: Soak 1 cup glutinous rice in water for at least 4 hours or overnight. Step 2: Drain and steam rice in a steamer lined with cheesecloth for 25-30 minutes. Step 3: In a saucepan, heat 1 cup coconut milk with 1/3 cup sugar and 1/2 tsp salt until sugar dissolves. Step 4: Reserve 1/4 cup coconut sauce for serving. Step 5: Mix remaining sauce with hot rice and let stand 10 minutes. Step 6: Slice 2 ripe mangoes. Step 7: Serve rice with mango slices and reserved coconut sauce. Step 8: Sprinkle with toasted sesame seeds if desired.", 280, 4, 52, 8),
        
        # African recipes  
        (6, "Jollof Rice", "dinner", "Step 1: Heat 3 tbsp oil in a large pot over medium heat. Step 2: Add 1 large diced onion and cook until soft, 5 minutes. Step 3: Add 3 minced garlic cloves, 1 diced bell pepper, and cook 3 minutes. Step 4: Stir in 2 tbsp tomato paste and cook 2 minutes. Step 5: Add 1 can diced tomatoes, 2 tsp paprika, 1 tsp thyme, 1 bay leaf, salt and pepper. Step 6: Add 2 cups jasmine rice and stir to coat. Step 7: Pour in 3 cups chicken broth and bring to boil. Step 8: Reduce heat, cover and simmer 18-20 minutes. Step 9: Let stand 5 minutes, then fluff with fork. Step 10: Remove bay leaf and serve hot.", 380, 12, 62, 10),
        (7, "Plantain Chips", "appetizer", "Step 1: Select 2-3 green plantains that are firm. Step 2: Peel plantains and slice into thin rounds (1/8 inch thick). Step 3: Heat 2 cups vegetable oil to 350°F in a deep pan. Step 4: Fry plantain slices in batches for 2-3 minutes until golden. Step 5: Remove with slotted spoon and drain on paper towels. Step 6: Immediately season with salt while hot. Step 7: Let cool completely before serving. Step 8: Store in airtight container for up to 3 days.", 150, 2, 35, 5),
        (8, "Hibiscus Tea", "drink", "Step 1: Rinse 1/2 cup dried hibiscus flowers in cold water. Step 2: Bring 4 cups water to boil in a pot. Step 3: Remove from heat and add hibiscus flowers. Step 4: Cover and steep for 15-20 minutes for strong flavor. Step 5: Strain through fine mesh strainer, pressing flowers to extract liquid. Step 6: Add honey or sugar to taste while tea is warm. Step 7: Serve hot or chill for iced tea. Step 8: Garnish with lime slices if desired.", 25, 0, 6, 0),
        (9, "Coconut Rice Pudding", "dessert", "Step 1: Rinse 1 cup jasmine rice until water runs clear. Step 2: In a heavy-bottomed pot, combine rice with 2 cups water. Step 3: Bring to boil, then reduce heat and simmer covered for 15 minutes. Step 4: Add 1 can coconut milk, 1/2 cup sugar, and 1/2 tsp salt. Step 5: Simmer uncovered, stirring frequently, for 20-25 minutes until creamy. Step 6: Stir in 1 tsp vanilla extract. Step 7: Serve warm or chilled. Step 8: Garnish with toasted coconut flakes and cinnamon.", 220, 4, 42, 6),
        (10, "Spiced Lentil Stew", "lunch", "Step 1: Rinse 1 cup red lentils and set aside. Step 2: Heat 2 tbsp oil in large pot over medium heat. Step 3: Add 1 diced onion and cook until soft, 5 minutes. Step 4: Add 3 minced garlic cloves, 1 tbsp ginger, 2 tsp turmeric, 1 tsp cumin. Cook 1 minute. Step 5: Add 1 can diced tomatoes and cook 5 minutes. Step 6: Add lentils and 4 cups vegetable broth. Step 7: Bring to boil, reduce heat and simmer 20 minutes until lentils are tender. Step 8: Season with salt, pepper, and lemon juice. Step 9: Garnish with fresh cilantro.", 290, 18, 45, 4),
        
        # Hispanic recipes
        (11, "Black Bean Tacos", "lunch", "Step 1: Heat 1 tbsp oil in pan over medium heat. Step 2: Add 1 diced onion and cook 3 minutes. Step 3: Add 2 minced garlic cloves, 1 tsp cumin, 1/2 tsp chili powder. Cook 1 minute. Step 4: Add 2 cans drained black beans, 1/4 cup water. Step 5: Simmer 10 minutes, mashing some beans for texture. Step 6: Season with salt, pepper, and lime juice. Step 7: Warm 8 corn tortillas in dry skillet or microwave. Step 8: Fill tortillas with bean mixture. Step 9: Top with shredded cheese, salsa, cilantro, and diced onion. Step 10: Serve with lime wedges.", 340, 15, 48, 12),
        (12, "Guacamole", "appetizer", "Step 1: Cut 3 ripe avocados in half and remove pits. Step 2: Scoop avocado flesh into a mixing bowl. Step 3: Add juice of 1 lime immediately to prevent browning. Step 4: Add 1/4 cup finely diced red onion. Step 5: Add 2 tbsp chopped fresh cilantro. Step 6: Add 1-2 minced jalapeño peppers (remove seeds for less heat). Step 7: Add 1/2 tsp salt and 1/4 tsp black pepper. Step 8: Mash with fork, leaving some chunky texture. Step 9: Taste and adjust seasoning. Step 10: Serve immediately with tortilla chips.", 160, 3, 8, 15),
        (13, "Horchata", "drink", "Step 1: Soak 1 cup long-grain rice in 3 cups warm water for 1 hour. Step 2: Add 1 cinnamon stick to soaking rice. Step 3: Pour rice, water, and cinnamon into blender. Step 4: Blend on high for 60 seconds until smooth. Step 5: Strain mixture through fine mesh strainer into pitcher. Step 6: Add 1 cup milk, 1/2 cup sweetened condensed milk, 1 tsp vanilla. Step 7: Stir in 1/2 tsp ground cinnamon. Step 8: Chill for at least 2 hours. Step 9: Stir before serving over ice. Step 10: Dust with extra cinnamon.", 180, 3, 28, 6),
        (14, "Tres Leches Cake", "dessert", "Step 1: Preheat oven to 350°F. Grease 9x13 pan. Step 2: Beat 5 egg yolks with 3/4 cup sugar until fluffy. Step 3: Add 1/3 cup milk, 1 tsp vanilla, and 1 cup flour. Mix until smooth. Step 4: Beat 5 egg whites to stiff peaks, fold into batter. Step 5: Pour into pan and bake 25-30 minutes. Step 6: Mix 1 can evaporated milk, 1 can condensed milk, 1/2 cup heavy cream. Step 7: Poke holes all over warm cake with fork. Step 8: Pour milk mixture over cake slowly. Step 9: Refrigerate 4 hours or overnight. Step 10: Top with whipped cream before serving.", 320, 6, 45, 14),
        (15, "Chicken Enchiladas", "dinner", "Step 1: Cook 2 lbs chicken breast in seasoned water until tender, then shred. Step 2: Heat 2 tbsp oil in pan, sauté 1 diced onion until soft. Step 3: Mix chicken with onion, 1 cup shredded cheese, salt and pepper. Step 4: Warm 12 corn tortillas to make pliable. Step 5: Fill each tortilla with chicken mixture and roll tightly. Step 6: Place seam-side down in greased baking dish. Step 7: Cover with 2 cups enchilada sauce and 1 cup cheese. Step 8: Bake at 375°F for 20 minutes until bubbly. Step 9: Garnish with cilantro and sour cream. Step 10: Serve hot with rice and beans.", 420, 28, 35, 18),
        
        # Caucasian recipes
        (16, "Caesar Salad", "lunch", "Step 1: Wash and chop 1 large head romaine lettuce into bite-sized pieces. Step 2: Make dressing: whisk 2 egg yolks, 2 tbsp lemon juice, 1 tbsp Dijon mustard. Step 3: Slowly drizzle in 1/2 cup olive oil while whisking. Step 4: Add 2 minced garlic cloves, 2 tbsp grated Parmesan, salt and pepper. Step 5: For croutons: cube 4 slices bread, toss with olive oil, bake at 400°F for 10 minutes. Step 6: Toss lettuce with dressing until well coated. Step 7: Add croutons and 1/4 cup Parmesan cheese. Step 8: Toss gently and serve immediately. Step 9: Garnish with extra Parmesan and black pepper.", 280, 8, 15, 22),
        (17, "Garlic Bread", "appetizer", "Step 1: Preheat oven to 425°F. Step 2: Slice 1 French baguette in half lengthwise. Step 3: Soften 1/2 cup butter at room temperature. Step 4: Mince 4 cloves garlic very finely. Step 5: Mix butter with garlic, 2 tbsp chopped parsley, salt and pepper. Step 6: Spread garlic butter evenly on cut sides of bread. Step 7: Place on baking sheet cut-side up. Step 8: Bake 10-12 minutes until golden brown and crispy. Step 9: Cut into slices and serve immediately while hot.", 220, 6, 28, 12),
        (18, "Iced Coffee", "drink", "Step 1: Brew 1 cup strong coffee using 2 tbsp ground coffee. Step 2: Let coffee cool to room temperature, about 30 minutes. Step 3: Pour coffee into refrigerator and chill for 2 hours. Step 4: Fill tall glass with ice cubes. Step 5: Pour chilled coffee over ice, filling glass 3/4 full. Step 6: Add 2-4 tbsp milk or cream to taste. Step 7: Stir gently to combine. Step 8: Sweeten with sugar or syrup if desired. Step 9: Serve with straw and enjoy immediately.", 50, 2, 8, 1),
        (19, "Apple Pie", "dessert", "Step 1: Make pastry: mix 2 cups flour, 1 tsp salt, cut in 2/3 cup shortening until crumbly. Step 2: Add 6-7 tbsp cold water, form into 2 disks, chill 1 hour. Step 3: Peel and slice 6 cups apples thinly. Step 4: Mix apples with 3/4 cup sugar, 2 tbsp flour, 1 tsp cinnamon, 1/4 tsp nutmeg. Step 5: Roll out bottom crust, place in 9-inch pie pan. Step 6: Add apple filling and dot with 2 tbsp butter. Step 7: Roll out top crust, place over filling, seal edges. Step 8: Cut vents in top crust. Step 9: Bake at 425°F for 45-50 minutes until golden. Step 10: Cool before serving.", 350, 4, 52, 16),
        (20, "Grilled Salmon", "dinner", "Step 1: Let 4 salmon fillets come to room temperature, 15 minutes. Step 2: Preheat grill to medium-high heat. Step 3: Mix 2 tbsp olive oil, 2 tbsp lemon juice, 2 tsp dried herbs, salt and pepper. Step 4: Brush salmon with oil mixture on both sides. Step 5: Clean and oil grill grates well. Step 6: Place salmon skin-side down on grill. Step 7: Cook 4-5 minutes without moving. Step 8: Flip carefully and cook 3-4 minutes more. Step 9: Fish should flake easily when done. Step 10: Serve immediately with lemon wedges.", 380, 42, 2, 18),
        
        # Middle Eastern recipes
        (21, "Hummus", "appetizer", "Step 1: Drain and rinse 2 cans chickpeas, reserve 1/2 cup liquid. Step 2: Remove skins from chickpeas by rubbing in towel (optional for smoother texture). Step 3: Add chickpeas to food processor with 1/4 cup lemon juice. Step 4: Process 1 minute until crumbly. Step 5: Add 1/4 cup tahini, 1 small garlic clove, 1/2 tsp salt. Step 6: Process 1 minute, scrape sides. Step 7: With processor running, slowly add 2-3 tbsp ice water until creamy. Step 8: Taste and adjust lemon, salt, or garlic. Step 9: Serve drizzled with olive oil, paprika, and pine nuts. Step 10: Accompany with pita bread and vegetables.", 180, 8, 20, 10),
        (22, "Chicken Shawarma", "lunch", "Step 1: Slice 2 lbs chicken thighs into strips. Step 2: Make marinade: mix 1/4 cup olive oil, 2 tbsp lemon juice, 2 tsp turmeric, 2 tsp cumin, 1 tsp paprika, 1 tsp coriander, 4 minced garlic cloves, salt and pepper. Step 3: Marinate chicken 2-4 hours or overnight. Step 4: Preheat oven to 425°F. Step 5: Spread chicken on sheet pan in single layer. Step 6: Roast 25-30 minutes until golden and cooked through. Step 7: Let rest 5 minutes, then slice thinly. Step 8: Warm pita bread and fill with chicken. Step 9: Add cucumbers, tomatoes, red onion, and tahini sauce. Step 10: Wrap tightly and serve immediately.", 400, 35, 15, 22),
        (23, "Turkish Tea", "drink", "Step 1: Fill bottom pot of Turkish tea set with water and bring to boil. Step 2: Add 3-4 tbsp loose black tea to top pot. Step 3: When water boils, pour small amount over tea leaves. Step 4: Place tea pot on top of water pot and simmer 10-15 minutes. Step 5: Tea should be dark and concentrated. Step 6: Pour small amount of concentrate into tulip-shaped glass. Step 7: Dilute with hot water to desired strength. Step 8: Serve with sugar cubes on side. Step 9: Traditional to drink from small glasses. Step 10: Refill concentrate pot as needed.", 10, 0, 2, 0),
        (24, "Baklava", "dessert", "Step 1: Thaw 1 lb phyllo dough and keep covered with damp towel. Step 2: Mix 3 cups chopped walnuts, 1 tsp cinnamon, 1/4 cup sugar. Step 3: Melt 1 cup butter. Step 4: Brush 9x13 pan with butter, layer 8 phyllo sheets, brushing each with butter. Step 5: Sprinkle 1/3 nut mixture over phyllo. Step 6: Layer 5 more phyllo sheets with butter, add nuts, repeat. Step 7: Top with 8 phyllo sheets, brushing each. Step 8: Cut into diamond shapes before baking. Step 9: Bake at 350°F for 45 minutes until golden. Step 10: Make syrup: boil 1 cup honey, 1/2 cup water, 1 tbsp lemon juice. Pour over hot baklava and cool completely.", 280, 6, 32, 16),
        (25, "Lamb Pilaf", "dinner", "Step 1: Cut 1 lb lamb into cubes and season with salt and pepper. Step 2: Heat 3 tbsp oil in heavy pot over medium-high heat. Step 3: Brown lamb pieces on all sides, about 8 minutes total. Step 4: Add 1 diced onion and cook until soft, 5 minutes. Step 5: Add 2 cups basmati rice and stir to coat with oil. Step 6: Add 3 cups beef broth, 1 tsp allspice, 1/2 tsp cinnamon, bay leaf. Step 7: Bring to boil, then reduce heat to low. Step 8: Cover and simmer 18-20 minutes until rice is tender. Step 9: Let stand 10 minutes, then fluff with fork. Step 10: Garnish with toasted almonds and fresh herbs.", 450, 25, 48, 18),
        
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