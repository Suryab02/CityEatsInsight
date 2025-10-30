from fastapi import FastAPI
from reddit_scraper import get_city_posts
from nlp_analyzer import analyze_comment
from nlp_filter import aggregate_data,clean_gemini_output
from google_genai import analyze_text_with_gemini
from cache_manager import load_cache,save_cache

app = FastAPI()


@app.get("/")
def home():
    return {"message": "CityEatsInsight backend is running!"}


@app.get("/city/{name}")
def get_city_data(name: str):
    """Fetch raw posts + comments (for debugging / inspection)"""
    posts = get_city_posts(name)
    return {"city": name, "posts": posts}


@app.get("/insights/{city}")
def analyze_city(city: str):
    """
    Analyze Reddit food posts from a given city and return AI-generated insights.
    Combines filtered comments and post title for Gemini summarization.
    """
    cached = load_cache(city)
    if cached:
        return cached
    
    posts = get_city_posts(city)
    insights = []

    for post in posts[:3]:  # limit to 5 for performance
        combined_text = f"{post['title']}\n{post['comments_text']}".strip()
        if not combined_text:
            continue

        ai_raw = analyze_text_with_gemini(combined_text , city)
        ai_summary = clean_gemini_output(ai_raw)

        insights.append({
            "title": post["title"],
            "url": post["url"],
            "score": post["score"],
            "summary": ai_summary
        })

        result = {"city": city, "insights": insights}

    # 💾 Save to cache
    save_cache(city, result)

    return result