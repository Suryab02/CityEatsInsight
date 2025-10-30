import re
from textblob import TextBlob

RESTAURANT_HINTS = ["restaurant", "hotel", "mess", "biryani", "cafe", "place"]
FOOD_HINTS = ["biryani", "chicken", "mutton", "dosa", "pizza", "pasta", "coffee", "burger"]
RELEVANT_FOOD_KEYWORDS = [
    "biryani", "chicken", "curry", "roll", "cafe", "restaurant",
    "pizza", "thali", "shawarma", "momos", "tandoori", "paneer",
    "chai", "coffee", "dosa", "ice cream", "snack", "tiffin"
]

RECOMMENDATION_PHRASES = [
    "must try", "go to", "you should try", "i recommend", "best place",
    "really good", "worth it", "amazing", "loved the", "try their"
]

def extract_entities(text: str):
    restaurants, foods = [], []
    for match in re.findall(r"\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\b", text):
        if any(h in text.lower() for h in RESTAURANT_HINTS):
            restaurants.append(match.strip())

    for food in FOOD_HINTS:
        if food in text.lower():
            foods.append(food)

    return list(set(restaurants)), list(set(foods))


def analyze_comment(comment: str):
    if not comment.strip():
        return {"text": "", "sentiment": 0.0, "sentiment_label": "neutral", "restaurants": [], "foods": [], "relevant": False}

    # Filter out non-food comments
    if not is_relevant_comment(comment):
        return {"text": comment, "sentiment": 0.0, "sentiment_label": "neutral", "restaurants": [], "foods": [], "relevant": False}

    sentiment = TextBlob(comment).sentiment.polarity
    restaurants, foods = extract_entities(comment)

    return {
        "text": comment,
        "sentiment": sentiment,
        "sentiment_label": sentiment_label(sentiment),
        "restaurants": list({r.lower().strip() for r in restaurants}),
        "foods": list({f.lower().strip() for f in foods}),
        "relevant": True
    }

def is_relevant_comment(comment: str) -> bool:
    FOOD_TERMS = [
        "biryani", "thali", "shawarma", "curry", "roll", "tandoori",
        "cafe", "restaurant", "dosa", "momos", "chicken", "paneer", 
        "food", "taste", "must try", "recommend", "best place"
    ]
    text = comment.lower()
    return any(word in text for word in FOOD_TERMS)

def sentiment_label(score):
    if score > 0.2:
        return "positive"
    elif score < -0.2:
        return "negative"
    else:
        return "neutral"
