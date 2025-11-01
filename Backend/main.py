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


app = FastAPI(title="CityEatsInsight API")

# Get frontend URL from environment or default to local
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")

FRONTEND_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    FRONTEND_URL,
    "https://city-eats-insight.vercel.app",
    "https://cityeatsinsight-frontend.vercel.app"  # Update with your actual frontend URL
]


# Security headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
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


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "CityEatsInsight Backend"}


@app.get("/")
def home():
    return {"message": "CityEatsInsight backend is running!", "version": "1.0"}


@app.get("/city/{name}")
def get_city_data(name: str):
    """Get raw posts for a specific city"""
    try:
        posts = get_city_posts(name)
        return {"city": name, "posts": posts}
    except Exception as e:
        return {"city": name, "posts": [], "error": str(e)}


@app.get("/insights/{city}")
def analyze_city(city: str):
    """Get AI-generated insights for a city"""
    try:
        # Check cache first
        cached = load_cache(city)
        if cached:
            return {"cached": True, **cached}

        # Get raw posts
        raw_posts = get_city_posts(city)
        if isinstance(raw_posts, dict):
            posts = raw_posts.get("data", [])
        elif isinstance(raw_posts, list):
            posts = raw_posts
        else:
            posts = []

        if not posts:
            return {"city": city, "insights": [], "error": "No posts found"}

        # Analyze top posts
        insights = []
        for post in posts[:3]:
            combined_text = f"{post.get('title', '')}\n{post.get('comments_text', '')}".strip()
            if not combined_text:
                continue
            try:
                ai_raw = analyze_text_with_gemini(combined_text, city)
                ai_summary = clean_gemini_output(ai_raw)
            except Exception as e:
                ai_summary = {"error": f"AI summarization failed: {str(e)}"}

            insights.append({
                "title": post.get("title"),
                "url": post.get("url"),
                "score": post.get("score"),
                "summary": ai_summary
            })

        result = {"city": city, "insights": insights}
        save_cache(city, result)
        return result

    except Exception as e:
        return {"city": city, "insights": [], "error": str(e)}


# ---- City Suggestions ----
def load_cities():
    """Load cities from JSON file with error handling"""
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


CITIES = load_cities()


@app.get("/city_suggestions/{query}")
def city_suggestions(query: str):
    """Get city suggestions based on query"""
    if not CITIES:
        return {"results": []}
    
    query = query.lower().strip()
    if not query:
        return {"results": CITIES[:30]}
    
    # First try exact prefix match
    matches = [city for city in CITIES if city.lower().startswith(query)]
    
    # If no matches, try substring match
    if not matches:
        matches = [city for city in CITIES if query in city.lower()]
    
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