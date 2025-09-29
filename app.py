#!/usr/bin/env python3
"""
Flask Meal Planning Application
Generates meal plans based on fridge ingredients, dietary preferences, and cultural background.
"""

import sqlite3
import json
import random
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_file, session
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'your-secret-key-here')

DATABASE = 'data/meal_planner.db'

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_recipes_by_filters(ingredients=None, dietary_prefs=None, race=None, meal_type=None):
    """Get recipes filtered by various criteria"""
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
    
    query += " ORDER BY r.title"
    
    try:
        recipes = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(recipe) for recipe in recipes]
    except Exception as e:
        print(f"Error getting recipes: {e}")
        conn.close()
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
        conn.close()
        return [dict(ing) for ing in ingredients]
    except Exception as e:
        print(f"Error getting ingredients for recipe {recipe_id}: {e}")
        conn.close()
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
            conn.close()
            return recipe_dict
        conn.close()
        return None
    except Exception as e:
        print(f"Error getting recipe {recipe_id}: {e}")
        conn.close()
        return None

def generate_meal_plan(days, ingredients=None, dietary_prefs=None, race=None):
    """Generate a meal plan for the specified number of days"""
    meal_types = ['breakfast', 'lunch', 'dinner', 'appetizer', 'dessert', 'drink']
    meal_plan = {}
    
    for day in range(1, days + 1):
        day_key = f"Day {day}"
        meal_plan[day_key] = {}
        
        for meal_type in meal_types:
            recipes = get_recipes_by_filters(
                ingredients=ingredients,
                dietary_prefs=dietary_prefs,
                race=race,
                meal_type=meal_type
            )
            
            if recipes:
                # Select a random recipe from available options
                selected_recipe = random.choice(recipes)
                meal_plan[day_key][meal_type] = selected_recipe
            else:
                # Fallback: get any recipe of this meal type
                fallback_recipes = get_recipes_by_filters(meal_type=meal_type)
                if fallback_recipes:
                    meal_plan[day_key][meal_type] = random.choice(fallback_recipes)
    
    return meal_plan

def calculate_missing_ingredients(meal_plan, user_ingredients):
    """Calculate ingredients needed for the meal plan that user doesn't have"""
    if not user_ingredients:
        user_ingredients = []
    
    user_ingredients_lower = [ing.strip().lower() for ing in user_ingredients]
    needed_ingredients = {}
    
    for day, meals in meal_plan.items():
        for meal_type, recipe in meals.items():
            if recipe:
                recipe_ingredients = get_recipe_ingredients(recipe['id'])
                for ingredient in recipe_ingredients:
                    ing_name = ingredient['name'].lower()
                    category = ingredient['category']
                    
                    # Check if user has this ingredient (or substitution)
                    has_ingredient = any(user_ing in ing_name or ing_name in user_ing 
                                       for user_ing in user_ingredients_lower)
                    
                    if not has_ingredient:
                        if category not in needed_ingredients:
                            needed_ingredients[category] = set()
                        needed_ingredients[category].add(ingredient['name'])
    
    # Convert sets to lists for JSON serialization
    for category in needed_ingredients:
        needed_ingredients[category] = list(needed_ingredients[category])
    
    return needed_ingredients

@app.route('/')
def index():
    """Home page with meal planning form"""
    return render_template('index.html')

@app.route('/generate_plan', methods=['POST'])
def generate_plan():
    """Generate meal plan based on user input"""
    try:
        # Get form data
        ingredients_input = request.form.get('ingredients', '').strip()
        days = int(request.form.get('days', '7'))
        dietary_prefs = request.form.getlist('dietary_prefs')
        race = request.form.get('race')
        
        # Parse ingredients
        ingredients = None
        if ingredients_input:
            ingredients = [ing.strip() for ing in ingredients_input.split(',') if ing.strip()]
        
        # Generate meal plan
        meal_plan = generate_meal_plan(days, ingredients, dietary_prefs, race)
        
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
    
    except Exception as e:
        print(f"Error generating meal plan: {e}")
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

@app.route('/export_pdf')
def export_pdf():
    """Generate and download PDF of current meal plan"""
    if 'current_meal_plan' not in session:
        return "No meal plan to export", 400
    
    try:
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph("Meal Plan", title_style))
        story.append(Spacer(1, 20))
        
        # Metadata
        metadata = session.get('plan_metadata', {})
        info_style = styles['Normal']
        story.append(Paragraph(f"<b>Duration:</b> {metadata.get('days', 'N/A')} days", info_style))
        story.append(Paragraph(f"<b>Dietary Preferences:</b> {', '.join(metadata.get('dietary_prefs', []))}", info_style))
        story.append(Paragraph(f"<b>Cultural Preference:</b> {metadata.get('race', 'N/A')}", info_style))
        story.append(Paragraph(f"<b>Generated:</b> {metadata.get('generated_at', 'N/A')}", info_style))
        story.append(Spacer(1, 20))
        
        # Meal plan
        meal_plan = session['current_meal_plan']
        for day, meals in meal_plan.items():
            # Day header
            day_style = ParagraphStyle(
                'DayHeader',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=10
            )
            story.append(Paragraph(day, day_style))
            
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
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
            story.append(Spacer(1, 20))
        
        # Shopping list
        shopping_list = session.get('current_shopping_list', {})
        if shopping_list:
            story.append(Paragraph("Shopping List", styles['Heading2']))
            story.append(Spacer(1, 10))
            
            for category, ingredients in shopping_list.items():
                if ingredients:
                    story.append(Paragraph(f"<b>{category.title()}:</b>", styles['Normal']))
                    for ingredient in ingredients:
                        story.append(Paragraph(f"• {ingredient}", styles['Normal']))
                    story.append(Spacer(1, 10))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"meal_plan_{datetime.now().strftime('%Y%m%d')}.pdf",
            mimetype='application/pdf'
        )
    
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
        
        response = app.response_class(
            response=json.dumps(export_data, indent=2),
            status=200,
            mimetype='application/json'
        )
        response.headers['Content-Disposition'] = f'attachment; filename=meal_plan_{datetime.now().strftime("%Y%m%d")}.json'
        return response
    
    except Exception as e:
        print(f"Error exporting JSON: {e}")
        return "Error exporting JSON", 500

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