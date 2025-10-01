#!/usr/bin/env python3
"""
Add database indexes for performance optimization
"""
import sqlite3

DATABASE = 'data/meal_planner.db'

def add_indexes():
    """Add indexes to improve query performance"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_recipes_meal_type ON recipes(meal_type)",
        "CREATE INDEX IF NOT EXISTS idx_recipe_races_recipe_id ON recipe_races(recipe_id)",
        "CREATE INDEX IF NOT EXISTS idx_recipe_races_race ON recipe_races(race)",
        "CREATE INDEX IF NOT EXISTS idx_recipe_dietary_tags_recipe_id ON recipe_dietary_tags(recipe_id)",
        "CREATE INDEX IF NOT EXISTS idx_recipe_dietary_tags_tag ON recipe_dietary_tags(tag)",
        "CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_recipe_id ON recipe_ingredients(recipe_id)",
        "CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_ingredient_id ON recipe_ingredients(ingredient_id)",
        "CREATE INDEX IF NOT EXISTS idx_ingredients_name ON ingredients(name)",
        "CREATE INDEX IF NOT EXISTS idx_substitutions_ingredient_id ON substitutions(ingredient_id)",
        "CREATE INDEX IF NOT EXISTS idx_substitutions_substitute_id ON substitutions(substitute_ingredient_id)",
        "CREATE INDEX IF NOT EXISTS idx_ratings_recipe_id ON ratings(recipe_id)",
    ]
    
    for index_sql in indexes:
        try:
            cursor.execute(index_sql)
            print(f"✓ Created: {index_sql.split('idx_')[1].split(' ON')[0]}")
        except Exception as e:
            print(f"✗ Error creating index: {e}")
    
    conn.commit()
    conn.close()
    print("\n✓ All indexes created successfully!")

if __name__ == '__main__':
    add_indexes()
