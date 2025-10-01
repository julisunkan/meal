#!/usr/bin/env python3
"""
Flask Meal Planning Application
Generates meal plans based on fridge ingredients, dietary preferences, and cultural background.
"""

import sqlite3
import json
import random
import hashlib
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_file, session, g
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET')

DATABASE = 'data/meal_planner.db'

# Ensure database exists
def ensure_database_exists():
    """Create database if it doesn't exist"""
    import os
    if not os.path.exists(DATABASE):
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
        # Initialize database
        from data.init_db import initialize_database
        initialize_database()

# Initialize database on startup
ensure_database_exists()

def ensure_database_indexes():
    """Ensure all performance indexes exist on startup (idempotent)"""
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
        except Exception as e:
            print(f"Warning: Could not create index: {e}")
    
    conn.commit()
    conn.close()

# Ensure indexes exist on app startup
ensure_database_indexes()

@app.route('/service-worker.js')
def service_worker():
    """Serve the service worker"""
    return send_file('static/service-worker.js', mimetype='application/javascript')

@app.route('/favicon.ico')
def favicon():
    """Serve the favicon"""
    return send_file('static/icons/favicon-32.png', mimetype='image/png')

def get_db():
    """Get per-request database connection (reused across the request)"""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Close database connection at end of request"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def get_db_connection():
    """Legacy wrapper - uses get_db() for connection reuse"""
    return get_db()

def get_recipes_by_filters(ingredients=None, dietary_prefs=None, race=None, meal_type=None, skip_order=False):
    """Get recipes filtered by various criteria
    
    Args:
        skip_order: If True, skip ORDER BY for better performance (useful for meal plan generation)
    """
    conn = get_db_connection()
    
    # Base query
    query = """
    SELECT DISTINCT r.id, r.title, r.meal_type, r.instructions, 
           r.calories, r.protein, r.carbs, r.fat
    FROM recipes r
    """
    
    conditions = []
    params = []
    
    # Filter by race/ethnicity
    if race:
        query += " JOIN recipe_races rr ON r.id = rr.recipe_id"
        conditions.append("rr.race = ?")
        params.append(race)
    
    # Filter by dietary preferences
    if dietary_prefs:
        for i, pref in enumerate(dietary_prefs):
            alias = f"rdt{i}"
            query += f" JOIN recipe_dietary_tags {alias} ON r.id = {alias}.recipe_id"
            conditions.append(f"{alias}.tag = ?")
            params.append(pref)
    
    # Filter by meal type
    if meal_type:
        conditions.append("r.meal_type = ?")
        params.append(meal_type)
    
    # Filter by ingredients (if provided)
    if ingredients:
        ingredient_conditions = []
        for ingredient in ingredients:
            # Check for exact match or substitution
            subquery = """
            EXISTS (
                SELECT 1 FROM recipe_ingredients ri
                JOIN ingredients i ON ri.ingredient_id = i.id
                WHERE ri.recipe_id = r.id AND (
                    LOWER(i.name) LIKE LOWER(?) OR
                    i.id IN (
                        SELECT s.substitute_ingredient_id 
                        FROM substitutions s 
                        JOIN ingredients i2 ON s.ingredient_id = i2.id
                        WHERE LOWER(i2.name) LIKE LOWER(?)
                    )
                )
            )
            """
            ingredient_conditions.append(subquery)
            params.extend([f"%{ingredient.strip()}%", f"%{ingredient.strip()}%"])
        
        if ingredient_conditions:
            conditions.append(f"({' OR '.join(ingredient_conditions)})")
    
    # Add WHERE clause if there are conditions
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    # Only add ORDER BY if needed (skip for performance in meal plan generation)
    if not skip_order:
        query += " ORDER BY r.title"
    
    try:
        recipes = conn.execute(query, params).fetchall()
        return [dict(recipe) for recipe in recipes]
    except Exception as e:
        print(f"Error getting recipes: {e}")
        return []

def get_recipe_ingredients(recipe_id):
    """Get ingredients for a specific recipe"""
    conn = get_db_connection()
    try:
        ingredients = conn.execute("""
            SELECT i.name, i.category
            FROM ingredients i
            JOIN recipe_ingredients ri ON i.id = ri.ingredient_id
            WHERE ri.recipe_id = ?
            ORDER BY i.category, i.name
        """, (recipe_id,)).fetchall()
        return [dict(ing) for ing in ingredients]
    except Exception as e:
        print(f"Error getting ingredients for recipe {recipe_id}: {e}")
        return []

def get_recipe_by_id(recipe_id):
    """Get a single recipe by ID"""
    conn = get_db_connection()
    try:
        recipe = conn.execute("""
            SELECT r.*, 
                   GROUP_CONCAT(DISTINCT rdt.tag) as dietary_tags,
                   GROUP_CONCAT(DISTINCT rr.race) as races,
                   rt.rating
            FROM recipes r
            LEFT JOIN recipe_dietary_tags rdt ON r.id = rdt.recipe_id
            LEFT JOIN recipe_races rr ON r.id = rr.recipe_id
            LEFT JOIN ratings rt ON r.id = rt.recipe_id
            WHERE r.id = ?
            GROUP BY r.id
        """, (recipe_id,)).fetchone()
        
        if recipe:
            recipe_dict = dict(recipe)
            recipe_dict['ingredients'] = get_recipe_ingredients(recipe_id)
            recipe_dict['dietary_tags'] = recipe['dietary_tags'].split(',') if recipe['dietary_tags'] else []
            recipe_dict['races'] = recipe['races'].split(',') if recipe['races'] else []
            return recipe_dict
        return None
    except Exception as e:
        print(f"Error getting recipe {recipe_id}: {e}")
        return None

def generate_meal_plan(days, ingredients=None, dietary_prefs=None, race=None):
    """Generate a meal plan for the specified number of days (optimized with batched queries)"""
    meal_types = ['breakfast', 'lunch', 'dinner', 'appetizer', 'dessert', 'drink']
    meal_plan = {}
    
    # OPTIMIZATION: Pre-fetch all recipes by meal type in one batch per type (6 queries total max)
    # This replaces the N+1 query pattern (days * 6 queries)
    recipes_by_type = {}
    fallback_by_type = {}
    
    for meal_type in meal_types:
        # Primary filtered recipes
        recipes_by_type[meal_type] = get_recipes_by_filters(
            ingredients=ingredients,
            dietary_prefs=dietary_prefs,
            race=race,
            meal_type=meal_type,
            skip_order=True  # Skip ORDER BY for performance
        )
        
        # Fallback recipes (only meal type filter)
        fallback_by_type[meal_type] = get_recipes_by_filters(
            meal_type=meal_type,
            skip_order=True  # Skip ORDER BY for performance
        )
    
    # Track all used recipes globally - no recipe should appear twice
    used_recipe_ids = set()
    
    for day in range(1, days + 1):
        day_key = f"Day {day}"
        meal_plan[day_key] = {}
        
        for meal_type in meal_types:
            # Use pre-fetched recipes
            recipes = recipes_by_type[meal_type]
            
            if recipes:
                # Only select recipes that haven't been used before
                available_recipes = [r for r in recipes if r['id'] not in used_recipe_ids]
                
                if available_recipes:
                    selected_recipe = random.choice(available_recipes)
                    meal_plan[day_key][meal_type] = selected_recipe
                    used_recipe_ids.add(selected_recipe['id'])
                else:
                    # Try fallback (pre-fetched)
                    fallback_recipes = fallback_by_type[meal_type]
                    available_fallback = [r for r in fallback_recipes if r['id'] not in used_recipe_ids]
                    
                    if available_fallback:
                        selected_recipe = random.choice(available_fallback)
                        meal_plan[day_key][meal_type] = selected_recipe
                        used_recipe_ids.add(selected_recipe['id'])
            else:
                # Use fallback (pre-fetched)
                fallback_recipes = fallback_by_type[meal_type]
                available_fallback = [r for r in fallback_recipes if r['id'] not in used_recipe_ids]
                
                if available_fallback:
                    selected_recipe = random.choice(available_fallback)
                    meal_plan[day_key][meal_type] = selected_recipe
                    used_recipe_ids.add(selected_recipe['id'])
    
    return meal_plan

def calculate_missing_ingredients(meal_plan, user_ingredients):
    """Calculate ingredients needed for the meal plan that user doesn't have (optimized with batch query)"""
    if not user_ingredients:
        user_ingredients = []
    
    # Collect all recipe IDs from the meal plan
    recipe_ids = []
    for day, meals in meal_plan.items():
        for meal_type, recipe in meals.items():
            if recipe and recipe.get('id'):
                recipe_ids.append(recipe['id'])
    
    if not recipe_ids:
        return {}
    
    # OPTIMIZATION: Single batched query for all ingredients
    conn = get_db_connection()
    placeholders = ','.join('?' * len(recipe_ids))
    query = f"""
        SELECT i.name, i.category
        FROM ingredients i
        JOIN recipe_ingredients ri ON i.id = ri.ingredient_id
        WHERE ri.recipe_id IN ({placeholders})
        ORDER BY i.category, i.name
    """
    
    all_ingredients = conn.execute(query, recipe_ids).fetchall()
    
    # Pre-build set of user ingredients for faster lookup
    user_ingredients_set = set(ing.strip().lower() for ing in user_ingredients)
    needed_ingredients = {}
    
    for ingredient in all_ingredients:
        ing_name = ingredient['name']
        ing_name_lower = ing_name.lower()
        category = ingredient['category']
        
        # Check if user has this ingredient (exact or partial match)
        has_ingredient = False
        for user_ing in user_ingredients_set:
            if user_ing in ing_name_lower or ing_name_lower in user_ing:
                has_ingredient = True
                break
        
        if not has_ingredient:
            if category not in needed_ingredients:
                needed_ingredients[category] = set()
            needed_ingredients[category].add(ing_name)
    
    # Convert sets to lists for JSON serialization
    for category in needed_ingredients:
        needed_ingredients[category] = sorted(list(needed_ingredients[category]))
    
    return needed_ingredients

@app.route('/')
def index():
    """Home page with meal planning form"""
    return render_template('index.html')

@app.route('/generate_plan', methods=['POST'])
def generate_plan():
    """Generate meal plan based on user input"""
    try:
        # Ensure database exists
        ensure_database_exists()
        
        # Get form data
        ingredients_input = request.form.get('ingredients', '').strip()
        days = int(request.form.get('days', '7'))
        dietary_prefs = request.form.getlist('dietary_prefs')
        race = request.form.get('race')
        
        # Validate days input
        if days < 1 or days > 30:
            return render_template('index.html', error="Please enter between 1-30 days.")
        
        # Parse ingredients
        ingredients = None
        if ingredients_input:
            ingredients = [ing.strip() for ing in ingredients_input.split(',') if ing.strip()]
        
        # Generate meal plan
        meal_plan = generate_meal_plan(days, ingredients, dietary_prefs, race)
        
        # Check if meal plan was generated successfully
        if not meal_plan:
            return render_template('index.html', error="Could not generate meal plan. Please try different preferences.")
        
        # Calculate shopping list
        shopping_list = calculate_missing_ingredients(meal_plan, ingredients)
        
        # Store in session for PDF export
        session['current_meal_plan'] = meal_plan
        session['current_shopping_list'] = shopping_list
        session['plan_metadata'] = {
            'days': days,
            'ingredients': ingredients or [],
            'dietary_prefs': dietary_prefs,
            'race': race,
            'generated_at': datetime.now().isoformat()
        }
        
        return render_template('meal_plan.html', 
                             meal_plan=meal_plan, 
                             shopping_list=shopping_list,
                             metadata=session['plan_metadata'])
    
    except ValueError as e:
        print(f"Validation error: {e}")
        return render_template('index.html', error="Invalid input. Please check your entries.")
    except Exception as e:
        print(f"Error generating meal plan: {e}")
        import traceback
        traceback.print_exc()
        return render_template('index.html', error="Error generating meal plan. Please try again.")

@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    """Show detailed view of a recipe"""
    recipe = get_recipe_by_id(recipe_id)
    if recipe:
        return render_template('recipe_detail.html', recipe=recipe)
    else:
        return "Recipe not found", 404

@app.route('/rate_recipe/<int:recipe_id>', methods=['POST'])
def rate_recipe(recipe_id):
    """Update recipe rating"""
    try:
        rating = int(request.form.get('rating', '0'))
        if 1 <= rating <= 5:
            conn = get_db_connection()
            conn.execute("""
                INSERT OR REPLACE INTO ratings (recipe_id, rating) 
                VALUES (?, ?)
            """, (recipe_id, rating))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Rating saved!'})
        else:
            return jsonify({'success': False, 'message': 'Invalid rating'})
    except Exception as e:
        print(f"Error rating recipe: {e}")
        return jsonify({'success': False, 'message': 'Error saving rating'})

# OPTIMIZATION: Pre-create reusable PDF styles and server-side PDF cache (defined once, not per request)
_pdf_styles = None
_pdf_table_style = None
_pdf_cache = {}  # Server-side PDF cache (plan_hash -> pdf_bytes)
_pdf_cache_max_size = 50  # Limit cache size

def get_pdf_styles():
    """Get cached PDF styles (created once and reused)"""
    global _pdf_styles, _pdf_table_style
    if _pdf_styles is None:
        base_styles = getSampleStyleSheet()
        _pdf_styles = {
            'title': ParagraphStyle(
                'CustomTitle',
                parent=base_styles['Heading1'],
                fontSize=20,
                spaceAfter=30,
                alignment=1
            ),
            'day_header': ParagraphStyle(
                'DayHeader',
                parent=base_styles['Heading2'],
                fontSize=16,
                spaceAfter=10
            ),
            'normal': base_styles['Normal'],
            'heading2': base_styles['Heading2']
        }
        _pdf_table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
    return _pdf_styles, _pdf_table_style

@app.route('/export_pdf')
def export_pdf():
    """Generate and download PDF of current meal plan (optimized with server-side caching)"""
    if 'current_meal_plan' not in session:
        return "No meal plan to export", 400
    
    try:
        # OPTIMIZATION: Check if we have a cached PDF for this exact meal plan
        global _pdf_cache
        meal_plan = session['current_meal_plan']
        metadata = session.get('plan_metadata', {})
        
        # Create a hash of the meal plan for caching (server-side, not in session)
        plan_hash = hashlib.md5(json.dumps(meal_plan, sort_keys=True).encode()).hexdigest()
        
        if plan_hash in _pdf_cache:
            # Return cached PDF from server-side cache
            pdf_bytes = _pdf_cache[plan_hash]
            response = app.response_class(
                pdf_bytes,
                status=200,
                mimetype='application/pdf'
            )
            response.headers['Content-Disposition'] = f'attachment; filename="meal_plan_{datetime.now().strftime("%Y%m%d")}.pdf"'
            response.headers['Content-Length'] = len(pdf_bytes)
            response.headers['Cache-Control'] = 'no-cache'
            return response
        
        # Generate PDF (not cached)
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Get reusable styles
        styles, table_style = get_pdf_styles()
        
        # Title
        story.append(Paragraph("Meal Plan", styles['title']))
        story.append(Spacer(1, 20))
        
        # Metadata
        story.append(Paragraph(f"<b>Duration:</b> {metadata.get('days', 'N/A')} days", styles['normal']))
        story.append(Paragraph(f"<b>Dietary Preferences:</b> {', '.join(metadata.get('dietary_prefs', []))}", styles['normal']))
        story.append(Paragraph(f"<b>Cultural Preference:</b> {metadata.get('race', 'N/A')}", styles['normal']))
        story.append(Paragraph(f"<b>Generated:</b> {metadata.get('generated_at', 'N/A')}", styles['normal']))
        story.append(Spacer(1, 20))
        
        # Meal plan
        for day, meals in meal_plan.items():
            story.append(Paragraph(day, styles['day_header']))
            
            # Meals table
            meal_data = [['Meal Type', 'Recipe', 'Calories', 'Protein', 'Carbs', 'Fat']]
            for meal_type, recipe in meals.items():
                if recipe:
                    meal_data.append([
                        meal_type.title(),
                        recipe['title'],
                        f"{recipe['calories']}",
                        f"{recipe['protein']}g",
                        f"{recipe['carbs']}g",
                        f"{recipe['fat']}g"
                    ])
            
            table = Table(meal_data, colWidths=[1*inch, 2.5*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
            table.setStyle(table_style)
            story.append(table)
            story.append(Spacer(1, 20))
        
        # Shopping list
        shopping_list = session.get('current_shopping_list', {})
        if shopping_list:
            story.append(Paragraph("Shopping List", styles['heading2']))
            story.append(Spacer(1, 10))
            
            for category, ingredients in shopping_list.items():
                if ingredients:
                    story.append(Paragraph(f"<b>{category.title()}:</b>", styles['normal']))
                    for ingredient in ingredients:
                        story.append(Paragraph(f"• {ingredient}", styles['normal']))
                    story.append(Spacer(1, 10))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        pdf_bytes = buffer.getvalue()
        
        # Cache the PDF in server-side cache (for repeated downloads)
        _pdf_cache[plan_hash] = pdf_bytes
        
        # Limit cache size to prevent memory bloat
        if len(_pdf_cache) > _pdf_cache_max_size:
            # Remove oldest entry (simple FIFO, could use LRU)
            first_key = next(iter(_pdf_cache))
            del _pdf_cache[first_key]
        
        # Create response with proper headers for server-side download
        response = app.response_class(
            pdf_bytes,
            status=200,
            mimetype='application/pdf'
        )
        response.headers['Content-Disposition'] = f'attachment; filename="meal_plan_{datetime.now().strftime("%Y%m%d")}.pdf"'
        response.headers['Content-Length'] = len(pdf_bytes)
        response.headers['Cache-Control'] = 'no-cache'
        
        return response
    
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return "Error generating PDF", 500

@app.route('/export_json')
def export_json():
    """Export current meal plan as JSON"""
    if 'current_meal_plan' not in session:
        return "No meal plan to export", 400
    
    try:
        export_data = {
            'meal_plan': session['current_meal_plan'],
            'shopping_list': session.get('current_shopping_list', {}),
            'metadata': session.get('plan_metadata', {})
        }
        
        # Generate JSON content
        json_content = json.dumps(export_data, indent=2)
        
        # Create response with proper headers for server-side download
        response = app.response_class(
            json_content,
            status=200,
            mimetype='application/json'
        )
        response.headers['Content-Disposition'] = f'attachment; filename="meal_plan_{datetime.now().strftime("%Y%m%d")}.json"'
        response.headers['Content-Length'] = len(json_content.encode('utf-8'))
        response.headers['Cache-Control'] = 'no-cache'
        
        return response
    
    except Exception as e:
        print(f"Error exporting JSON: {e}")
        return "Error exporting JSON", 500

@app.route('/samples')
def samples():
    """Show sample meal plans across different cultures"""
    # Sample 30-day meal plans for different cultures
    sample_plans = {
        'Asian': {
            'title': 'Asian Fusion 30-Day Plan',
            'description': 'Explore diverse Asian cuisines with balanced nutrition',
            'highlights': ['Japanese breakfast bowls', 'Thai curry dinners', 'Korean BBQ', 'Chinese stir-fries'],
            'cultural_focus': 'Asian',
            'avg_calories': 1850,
            'preview_meals': [
                {'day': 1, 'breakfast': 'Miso Soup with Rice', 'lunch': 'Pad Thai', 'dinner': 'Teriyaki Salmon'},
                {'day': 2, 'breakfast': 'Congee with Vegetables', 'lunch': 'Korean Bibimbap', 'dinner': 'Sweet and Sour Pork'},
                {'day': 3, 'breakfast': 'Japanese Omelette', 'lunch': 'Ramen Bowl', 'dinner': 'Thai Green Curry'}
            ]
        },
        'Hispanic': {
            'title': 'Hispanic Heritage 30-Day Plan',
            'description': 'Celebrate Hispanic flavors with authentic recipes',
            'highlights': ['Mexican breakfasts', 'Spanish paellas', 'Argentinian grills', 'Cuban classics'],
            'cultural_focus': 'Hispanic',
            'avg_calories': 1900,
            'preview_meals': [
                {'day': 1, 'breakfast': 'Huevos Rancheros', 'lunch': 'Chicken Quesadilla', 'dinner': 'Beef Tacos'},
                {'day': 2, 'breakfast': 'Breakfast Burrito', 'lunch': 'Spanish Paella', 'dinner': 'Chiles Rellenos'},
                {'day': 3, 'breakfast': 'Pan Dulce', 'lunch': 'Cuban Sandwich', 'dinner': 'Arroz con Pollo'}
            ]
        },
        'African': {
            'title': 'African Diaspora 30-Day Plan',
            'description': 'Rich flavors from across the African continent',
            'highlights': ['Ethiopian injera', 'Moroccan tagines', 'West African stews', 'South African braai'],
            'cultural_focus': 'African',
            'avg_calories': 1800,
            'preview_meals': [
                {'day': 1, 'breakfast': 'Injera with Honey', 'lunch': 'Jollof Rice', 'dinner': 'Moroccan Tagine'},
                {'day': 2, 'breakfast': 'African Porridge', 'lunch': 'Bobotie', 'dinner': 'Ethiopian Doro Wat'},
                {'day': 3, 'breakfast': 'Mandazi', 'lunch': 'Thieboudienne', 'dinner': 'South African Potjiekos'}
            ]
        },
        'Middle Eastern': {
            'title': 'Middle Eastern 30-Day Plan',
            'description': 'Aromatic spices and ancient grain traditions',
            'highlights': ['Lebanese mezze', 'Persian rice dishes', 'Turkish delights', 'Israeli breakfast'],
            'cultural_focus': 'Middle Eastern',
            'avg_calories': 1750,
            'preview_meals': [
                {'day': 1, 'breakfast': 'Shakshuka', 'lunch': 'Hummus Bowl', 'dinner': 'Lamb Kebabs'},
                {'day': 2, 'breakfast': 'Labneh Toast', 'lunch': 'Falafel Wrap', 'dinner': 'Persian Rice'},
                {'day': 3, 'breakfast': 'Za\'atar Bread', 'lunch': 'Tabbouleh Salad', 'dinner': 'Turkish Kofta'}
            ]
        },
        'Caucasian': {
            'title': 'European Heritage 30-Day Plan',
            'description': 'Classic European comfort foods with modern twists',
            'highlights': ['Italian pasta', 'French cuisine', 'German hearty meals', 'British classics'],
            'cultural_focus': 'Caucasian',
            'avg_calories': 1950,
            'preview_meals': [
                {'day': 1, 'breakfast': 'French Toast', 'lunch': 'Caesar Salad', 'dinner': 'Spaghetti Carbonara'},
                {'day': 2, 'breakfast': 'English Breakfast', 'lunch': 'German Schnitzel', 'dinner': 'Beef Bourguignon'},
                {'day': 3, 'breakfast': 'Pancakes', 'lunch': 'Italian Risotto', 'dinner': 'Fish and Chips'}
            ]
        }
    }
    
    return render_template('samples.html', sample_plans=sample_plans)

@app.route('/generate_sample/<culture>')
def generate_sample(culture):
    """Generate a sample meal plan for a specific culture"""
    culture_map = {
        'asian': 'Asian',
        'hispanic': 'Hispanic', 
        'african': 'African',
        'middle-eastern': 'Middle Eastern',
        'caucasian': 'Caucasian'
    }
    
    race = culture_map.get(culture.lower())
    if not race:
        return "Culture not found", 404
    
    # Generate a 7-day meal plan for the specific culture
    meal_plan = generate_meal_plan(7, ingredients=None, dietary_prefs=None, race=race)
    
    # Calculate shopping list
    shopping_list = calculate_missing_ingredients(meal_plan, [])
    
    # Store in session for PDF export
    session['current_meal_plan'] = meal_plan
    session['current_shopping_list'] = shopping_list
    session['plan_metadata'] = {
        'days': 7,
        'ingredients': [],
        'dietary_prefs': [],
        'race': race,
        'generated_at': datetime.now().isoformat(),
        'sample_plan': True,
        'culture': culture.title()
    }
    
    return render_template('meal_plan.html', 
                         meal_plan=meal_plan, 
                         shopping_list=shopping_list,
                         metadata=session['plan_metadata'],
                         is_sample=True)

@app.route('/import_json', methods=['POST'])
def import_json():
    """Import meal plan from JSON file"""
    try:
        if 'json_file' not in request.files:
            return "No file uploaded", 400
        
        file = request.files['json_file']
        if file.filename == '':
            return "No file selected", 400
        
        if file and file.filename and file.filename.endswith('.json'):
            content = file.read().decode('utf-8')
            data = json.loads(content)
            
            # Validate structure
            if 'meal_plan' in data:
                session['current_meal_plan'] = data['meal_plan']
                session['current_shopping_list'] = data.get('shopping_list', {})
                session['plan_metadata'] = data.get('metadata', {})
                
                return render_template('meal_plan.html', 
                                     meal_plan=data['meal_plan'],
                                     shopping_list=data.get('shopping_list', {}),
                                     metadata=data.get('metadata', {}),
                                     success="Meal plan imported successfully!")
            else:
                return "Invalid JSON format", 400
        else:
            return "Please upload a JSON file", 400
    
    except Exception as e:
        print(f"Error importing JSON: {e}")
        return "Error importing meal plan", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)