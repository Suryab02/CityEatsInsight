"""
CityEatsInsight Backend API

FastAPI-based REST API that provides food insights from Reddit discussions.
Fetches and analyzes city-specific food recommendations using Reddit data
and AI-powered summarization.

Endpoints:
- GET /health - Health check
- GET / - API info
- GET /city/{name} - Raw Reddit posts for a city
- GET /insights/{city} - AI-analyzed food insights
- GET /city_suggestions/{query} - City autocomplete suggestions
"""

import json
import re
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from reddit_scraper import get_city_posts
from nlp_analyzer import analyze_comment
from nlp_filter import aggregate_data, clean_gemini_output
from google_genai import analyze_text_with_gemini
from cache_manager import load_cache, save_cache

# ========================= APP INITIALIZATION =========================

app = FastAPI(title="CityEatsInsight API")

# ========================= CORS CONFIGURATION =========================

# Get frontend URL from environment variable or default to local development
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")

# Allowed origins for CORS (Cross-Origin Resource Sharing)
# This enables the frontend to make API calls from different domains
FRONTEND_ORIGINS = [
    "http://localhost:5173",  # Vite default port
    "http://localhost:5174",  # Vite alternate port
    "http://localhost:3000",  # React/Next.js default port
    FRONTEND_URL,  # Custom frontend URL from environment
    "https://city-eats-insight.vercel.app",  # Production frontend
    "https://cityeatsinsight-frontend.vercel.app"  # Alternate production URL
]


# ========================= MIDDLEWARE =========================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all API responses.
    
    Headers added:
    - X-Frame-Options: Prevents clickjacking attacks
    - X-Content-Type-Options: Prevents MIME-sniffing
    - Strict-Transport-Security: Enforces HTTPS
    - Referrer-Policy: Controls referrer information
    """
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
        return response


app.add_middleware(SecurityHeadersMiddleware)


# CORS Setup (must be after security middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ========================= API ENDPOINTS =========================

@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        dict: Status information
    """
    return {"status": "ok", "service": "CityEatsInsight Backend"}


@app.get("/")
def home():
    """
    Root endpoint providing API information.
    
    Returns:
        dict: Welcome message and version info
    """
    return {"message": "CityEatsInsight backend is running!", "version": "1.0"}


@app.get("/city/{name}")
def get_city_data(name: str):
    """
    Get raw Reddit posts for a specific city without AI analysis.
    
    This endpoint fetches food-related posts from the city's subreddit
    but doesn't perform AI summarization. Useful for debugging or
    getting raw data.
    
    Args:
        name: City name (used as subreddit name)
        
    Returns:
        dict: {
            "city": "city_name",
            "posts": [...],
            "count": number_of_posts
        }
    """
    try:
        count = 0
        # Fetch posts from Reddit scraper
        result, count = get_city_posts(name, count)
        
        # Handle error responses from scraper
        if isinstance(result, dict) and "error" in result:
            return {"city": name, "posts": [], "count": count, "error": result["error"]}
        
        return {"city": name, "posts": result, "count": count}
    except Exception as e:
        return {"city": name, "posts": [], "count": 0, "error": str(e)}


@app.get("/insights/{city}")
def analyze_city(city: str):
    """
    Get AI-generated food insights for a city.
    
    This is the main endpoint that:
    1. Fetches recent Reddit posts about food in the city
    2. Analyzes posts with Google Gemini AI
    3. Returns structured insights (recommendations, complaints, overview)
    4. Caches results for 6 hours to improve performance
    
    The endpoint uses a fallback mechanism:
    - Primary: Google Gemini AI for rich insights
    - Fallback: Simple NLP analyzer if Gemini fails/quota exceeded
    
    Args:
        city: Name of the city to analyze
        
    Returns:
        dict: {
            "city": "city_name",
            "insights": [
                {
                    "title": "Post title",
                    "url": "Reddit URL",
                    "score": upvotes,
                    "summary": {
                        "city_overview": "...",
                        "top_recommendations": [...],
                        "major_complaints": [...]
                    }
                },
                ...
            ],
            "count": number_of_posts_processed
        }
    """
    try:
        count = 0
        # Step 1: Fetch raw posts from Reddit
        raw_posts, count = get_city_posts(city, count)
        
        # Handle error responses from scraper
        if isinstance(raw_posts, dict) and "error" in raw_posts:
            return {"city": city, "insights": [], "count": count, "error": raw_posts["error"]}
        
        posts = raw_posts if isinstance(raw_posts, list) else []

        if not posts:
            return {"city": city, "insights": [], "count": count, "error": "No food-related posts found for this city"}

        # Step 2: Analyze top posts with AI
        insights = []
        for post in posts[:5]:  # Limit to top 5 posts to save API quota
            # Combine title and comments for comprehensive analysis
            combined_text = f"{post.get('title', '')}\n{post.get('comments_text', '')}".strip()
            if not combined_text:
                continue
            
            ai_summary = None
            try:
                # Try Gemini AI first
                ai_raw = analyze_text_with_gemini(combined_text, city)
                ai_summary = clean_gemini_output(ai_raw)
                
                # Check if Gemini returned an error (like quota exceeded)
                if isinstance(ai_summary, dict) and "error" in ai_summary:
                    # Use fallback analyzer
                    from simple_analyzer import extract_simple_insights
                    ai_summary = extract_simple_insights(combined_text, city)
                    
            except Exception as e:
                # Use fallback analyzer on any exception
                try:
                    from simple_analyzer import extract_simple_insights
                    ai_summary = extract_simple_insights(combined_text, city)
                except:
                    ai_summary = {"error": f"AI summarization failed: {str(e)}"}

            insights.append({
                "title": post.get("title"),
                "url": post.get("url"),
                "score": post.get("score"),
                "summary": ai_summary
            })

        # Step 3: Cache results for future requests
        result = {"city": city, "insights": insights, "count": count}
        save_cache(city, result)
        return result

    except Exception as e:
        return {"city": city, "insights": [], "count": 0, "error": str(e)}


# ========================= CITY SUGGESTIONS =========================

def load_cities():
    """
    Load list of cities from JSON file for autocomplete suggestions.
    
    Tries multiple possible paths to find cities.json:
    - data/cities.json (local development)
    - ./data/cities.json (relative path)
    - /app/data/cities.json (Docker/production)
    
    Returns:
        list: List of city names, or empty list if file not found
    """
    try:
        # Try multiple possible paths
        paths = [
            "data/cities.json",
            "./data/cities.json",
            "/app/data/cities.json"
        ]
        for path in paths:
            if os.path.exists(path):
                with open(path, "r") as f:
                    return json.load(f)
        
        # Return empty list if file not found
        print("Warning: cities.json not found")
        return []
    except Exception as e:
        print(f"Error loading cities.json: {e}")
        return []


# Load cities list on startup
CITIES = load_cities()


@app.get("/city_suggestions/{query}")
def city_suggestions(query: str):
    """
    Get city name suggestions for autocomplete.
    
    Provides smart city suggestions based on user input:
    1. First tries exact prefix matching (e.g., "hyd" -> "Hyderabad")
    2. Falls back to substring matching if no prefix matches
    3. Returns up to 30 suggestions
    
    Args:
        query: User's search query (partial city name)
        
    Returns:
        dict: {
            "results": ["City1", "City2", ...]
        }
        
    Example:
        GET /city_suggestions/hyd
        -> {"results": ["Hyderabad", "Ahmedabad", ...]}
    """
    if not CITIES:
        return {"results": []}
    
    query = query.lower().strip()
    
    # If query is empty, return popular cities
    if not query:
        return {"results": CITIES[:30]}
    
    # First try exact prefix match (faster and more relevant)
    matches = [city for city in CITIES if city.lower().startswith(query)]
    
    # If no matches, try substring match (more flexible)
    if not matches:
        matches = [city for city in CITIES if query in city.lower()]
    
    # Return up to 30 suggestions
    return {"results": matches[:30]}


# Vercel handler for serverless deployment
# No need to run uvicorn directly on Vercel
if __name__ == "__main__":
    # This runs locally only
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True  # Only for local development
    )