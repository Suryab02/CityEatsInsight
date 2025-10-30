import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def analyze_text_with_gemini(text: str, city: str):
    """Use Gemini Flash AI to summarize all food-related posts for a city."""
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""
    You are analyzing Reddit discussions about FOOD and RESTAURANTS in Indian cities for a city food dashboard.

    Your job is to extract useful, structured insights from the provided text.

    Return ONLY valid JSON with these specific fields and structure:
    {{
        "city_overview": "A 1-2 sentence high-level summary of {city}'s food discussion focus (e.g., 'Discussions focus on finding budget-friendly biryani and late-night food.').",
        "top_recommendations": [
            {{
                "category": "Biryani / Non-Veg" | "Cafe for Work" | "Budget Food" | "Fine Dining" | "Street Food" | "Pure Veg" | "Desserts" | "Fast Food" | "Beach View Cafe",
                "restaurant_name": "The single most recommended or discussed place for this category.",
                "popular_dish": "The specific dish or item mentioned (e.g., 'Chicken Biryani', 'Dosa', 'Pour Over Coffee').",
                "reason": "Why it is recommended (e.g., 'Best flavor', 'Good Wi-Fi', 'Affordable', 'Excellent view')."
            }}
        ],
        "major_complaints": [
            {{
                "restaurant_name": "The restaurant with the most serious or repeated complaint (e.g., food poisoning, poor quality, high price for value).",
                "issue": "A brief description of the complaint.",
                "sentiment": "Negative"
            }}
        ]
    }}

    Analyze the provided text and populate the fields.
    If a category or complaint is not present, omit that array element.
    Do not use phrases like 'users said' or 'the post describes'.

    Text:
    {text[:10000]}  # cap to 10K chars to save tokens
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return {"error": str(e)}