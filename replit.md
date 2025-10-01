# Overview

This is a comprehensive Flask-based meal planning application that generates personalized meal plans based on user fridge ingredients, dietary preferences, and cultural backgrounds. The app creates complete meal plans covering all meal types (breakfast, lunch, dinner, appetizers, desserts, drinks) and provides advanced features like PDF export, shopping list generation, JSON import/export, and recipe rating system. The application requires no user authentication and focuses on providing quick, culturally-diverse meal planning solutions with an intuitive Bootstrap 5 interface.

## Key Features Implemented
- **Progressive Web App**: Installable PWA with offline support, service worker caching, and app icons
- **Mobile-First Design**: Colorful, vibrant UI with gradient backgrounds and mobile-app-style navigation
- **Cultural Diversity**: Recipes from Asian, African, Hispanic, Caucasian, and Middle Eastern cuisines
- **Smart Filtering**: Ingredient-based filtering with substitution support
- **Dietary Support**: Vegan, vegetarian, and gluten-free options
- **Complete Meal Planning**: Covers all meal types including drinks and appetizers
- **Shopping Lists**: Automatically generated categorized shopping lists for missing ingredients
- **Export Options**: PDF generation with ReportLab and JSON import/export functionality
- **Recipe Rating**: User rating system stored in SQLite
- **Bottom Navigation**: Mobile-app-style footer navigation for easy access

## Recent Changes

### October 1, 2025 - PWA & Mobile UI Update
- **Progressive Web App**: Full PWA implementation with manifest.json, service worker, and offline capabilities
- **PWA Icons**: Generated complete icon set (72px-512px) including maskable icons for Android/iOS
- **Mobile-First UI**: Transformed to colorful mobile-app design with gradient backgrounds
- **Bottom Navigation**: Added mobile-app-style bottom navigation bar
- **Colorful Design**: Implemented vibrant gradient themes and modern card-based layouts
- **Security Enhancement**: Fixed session secret key configuration

### September 29, 2025 - Initial Implementation
- **Database Setup**: Created SQLite database with 39 diverse recipes across all cultures and meal types
- **Flask Backend**: Implemented complete meal planning algorithm with ingredient filtering and substitutions
- **UI Templates**: Built responsive Bootstrap 5 templates with meal cards, nutrition display, and shopping lists
- **PDF Export**: Integrated ReportLab for comprehensive meal plan and shopping list PDFs
- **Rating System**: Added recipe rating functionality with AJAX updates
- **Workflow Configuration**: Set up Flask development server on port 5000

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Architecture
- **Framework**: Flask web framework with Python 3
- **Database**: SQLite with normalized schema including recipes, ingredients, dietary tags, cultural associations, and substitutions
- **PDF Generation**: ReportLab library for generating meal plan and shopping list PDFs
- **Session Management**: Flask sessions for temporary data storage without user authentication

## Frontend Architecture
- **Progressive Web App**: Service worker with cache-first strategy, manifest.json with app metadata
- **UI Framework**: Bootstrap 5 for responsive design with custom gradient themes
- **Icons**: Font Awesome 6 for consistent iconography; custom PWA icons (regular and maskable)
- **Templates**: Jinja2 templating with base template inheritance
- **Styling**: Mobile-first design with CSS gradients, rounded cards, and bottom navigation
- **PWA Features**: Installable on mobile/desktop, offline caching, app-like experience

## Database Schema
- **recipes**: Core recipe data with nutritional information
- **ingredients**: Ingredient catalog with categories
- **recipe_ingredients**: Many-to-many relationship between recipes and ingredients
- **recipe_dietary_tags**: Dietary preference associations (vegan, vegetarian, gluten-free)
- **recipe_races**: Cultural cuisine associations (Asian, African, Hispanic, Caucasian, Middle Eastern)
- **substitutions**: Ingredient substitution mapping for flexibility
- **ratings**: Optional recipe rating system

## Core Features Architecture
- **Meal Plan Generation**: Algorithm that respects ingredient availability, dietary restrictions, and cultural preferences
- **Shopping List**: Automatic generation of categorized missing ingredients
- **Export System**: JSON and PDF export capabilities for meal plans
- **Recipe Detail System**: Individual recipe pages with full nutritional and preparation information

## Data Processing Logic
- **Ingredient Filtering**: Optional ingredient-based filtering with substitution support
- **Cultural Cuisine Matching**: Recipe filtering based on selected ethnicity/culture
- **Dietary Restriction Handling**: Automatic filtering for dietary preferences
- **Nutrition Calculation**: Per-recipe and aggregate nutritional information display

# External Dependencies

## Python Libraries
- **Flask**: Web framework for routing, templating, and session management
- **SQLite3**: Built-in database connectivity (no external database server required)
- **ReportLab**: PDF generation for meal plans and shopping lists
- **JSON**: Built-in library for data export/import functionality

## Frontend Dependencies
- **Bootstrap 5**: CSS framework served via CDN for responsive UI components
- **Font Awesome 6**: Icon library served via CDN for visual elements

## File System Dependencies
- **Templates Directory**: Jinja2 HTML templates for page rendering
- **Static Directory**: CSS, JavaScript, and asset files
  - **Icons Directory**: Complete PWA icon set (16px-512px, maskable icons, Apple touch icons)
  - **manifest.json**: PWA configuration file
  - **service-worker.js**: Service worker for offline functionality
- **Data Directory**: SQLite database storage and initialization scripts

Note: The application is designed to be fully self-contained with minimal external dependencies, using SQLite for local data storage and CDN-hosted frontend libraries for easy deployment.