import json, re, os , uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from reddit_scraper import get_city_posts
from nlp_analyzer import analyze_comment
from nlp_filter import aggregate_data, clean_gemini_output
from google_genai import analyze_text_with_gemini
from cache_manager import load_cache, save_cache


app = FastAPI(title="CityEatsInsight API")


FRONTEND_ORIGINS = [
    "http://localhost:5173",
    "https://city-eats-insight.vercel.app"
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

@app.get("/health")
def health_check():
    return {"status": "ok"}

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "CityEatsInsight backend is running!"}


@app.get("/city/{name}")
def get_city_data(name: str):
    posts = get_city_posts(name)
    return {"city": name, "posts": posts}


@app.get("/insights/{city}")
def analyze_city(city: str):
    cached = load_cache(city)
    if cached:
        return cached

    raw_posts = get_city_posts(city)
    if isinstance(raw_posts, dict):
        posts = raw_posts.get("data", [])
    elif isinstance(raw_posts, list):
        posts = raw_posts
    else:
        posts = []

    if not posts:
        return {"city": city, "insights": [], "error": "No posts found"}

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


# ---- City Suggestions ----
with open("data/cities.json", "r") as f:
    CITIES = json.load(f)

@app.get("/city_suggestions/{query}")
def city_suggestions(query: str):
    query = query.lower()
    matches = [city for city in CITIES if city.lower().startswith(query)]
    if not matches:
        matches = [city for city in CITIES if query in city.lower()]
    return {"results": matches[:30]}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Railway provides PORT automatically
    uvicorn.run("main:app", host="0.0.0.0", port=port)