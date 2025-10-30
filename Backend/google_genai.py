import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_text_with_gemini(text: str):
    """Use Gemini Flash AI to summarize food-related posts."""
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = f"""
    You are analyzing Reddit posts about food, restaurants, and cafes in Indian cities.

    Your goal is to extract structured insights for a dashboard.

    For the given Reddit post (and its top comments), return a JSON object with these fields:
    - intent: 'recommendation', 'review', 'complaint', 'question', or 'other'
    - restaurant_names: list of restaurant or cafe names mentioned
    - popular_foods: list of food or dish names mentioned
    - overall_sentiment: 'positive', 'negative', or 'neutral'
    - summary: 2–3 lines summarizing what the post and comments are about
    - key_finding: 1–2 sentence actionable takeaway written as a clear fact (avoid phrases like 'the post says' or 'the user is saying')

    Be concise, factual, and directly relevant to food or restaurant discussions.

    Text:
    {text}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return {"error": str(e)}
