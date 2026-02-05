"""
NLP Analyzer Module for CityEatsInsight

This module performs natural language processing on Reddit comments to extract
food-related insights, sentiment analysis, and entity recognition.

Key Features:
- Sentiment analysis using TextBlob
- Restaurant and food item entity extraction
- Relevance filtering for food-related content
- Named entity recognition with regex patterns

Used as a fallback when AI summarization is unavailable or for basic analysis.
"""

import re
from textblob import TextBlob

# ========================= KEYWORD LISTS =========================

# Keywords that suggest a restaurant mention in text
RESTAURANT_HINTS = ["restaurant", "hotel", "mess", "biryani", "cafe", "place"]

# Common food items to extract from text
FOOD_HINTS = ["biryani", "chicken", "mutton", "dosa", "pizza", "pasta", "coffee", "burger"]

# Comprehensive list of food-related keywords for relevance detection
RELEVANT_FOOD_KEYWORDS = [
    "biryani", "chicken", "curry", "roll", "cafe", "restaurant",
    "pizza", "thali", "shawarma", "momos", "tandoori", "paneer",
    "chai", "coffee", "dosa", "ice cream", "snack", "tiffin"
]

# Phrases that indicate a recommendation
RECOMMENDATION_PHRASES = [
    "must try", "go to", "you should try", "i recommend", "best place",
    "really good", "worth it", "amazing", "loved the", "try their"
]


# ========================= ENTITY EXTRACTION =========================

def extract_entities(text: str):
    """
    Extract restaurant names and food items from text using pattern matching.
    
    Uses regex to find capitalized phrases (likely restaurant names) and
    matches against known food keywords.
    
    Args:
        text: Comment or post text to analyze
        
    Returns:
        tuple: (restaurants, foods) where:
            - restaurants: List of potential restaurant names
            - foods: List of food items mentioned
            
    Example:
        >>> extract_entities("Try the biryani at Paradise Restaurant")
        (['Paradise Restaurant'], ['biryani'])
    """
    restaurants, foods = [], []
    
    # Extract capitalized phrases (potential restaurant names)
    # Pattern: One or more capitalized words (e.g., "Paradise Restaurant")
    for match in re.findall(r"\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\b", text):
        # Only consider it a restaurant if restaurant-related words are nearby
        if any(h in text.lower() for h in RESTAURANT_HINTS):
            restaurants.append(match.strip())

    # Extract food items by matching against known food keywords
    for food in FOOD_HINTS:
        if food in text.lower():
            foods.append(food)

    # Remove duplicates and return
    return list(set(restaurants)), list(set(foods))


# ========================= SENTIMENT ANALYSIS =========================

def sentiment_label(score):
    """
    Convert a numerical sentiment score to a human-readable label.
    
    Sentiment scores range from -1 (very negative) to +1 (very positive).
    We use thresholds to categorize into positive/negative/neutral.
    
    Args:
        score: Float between -1 and 1 from TextBlob sentiment analysis
        
    Returns:
        str: "positive", "negative", or "neutral"
        
    Example:
        >>> sentiment_label(0.5)
        'positive'
        >>> sentiment_label(-0.3)
        'negative'
        >>> sentiment_label(0.1)
        'neutral'
    """
    if score > 0.2:
        return "positive"
    elif score < -0.2:
        return "negative"
    else:
        return "neutral"


def analyze_comment(comment: str):
    """
    Perform comprehensive NLP analysis on a Reddit comment.
    
    This function:
    1. Checks if the comment is food-related
    2. Performs sentiment analysis
    3. Extracts restaurant names and food items
    4. Returns structured data for aggregation
    
    Args:
        comment: Text of the Reddit comment
        
    Returns:
        dict: Analysis results with keys:
            - text: Original comment text
            - sentiment: Numerical score (-1 to 1)
            - sentiment_label: "positive", "negative", or "neutral"
            - restaurants: List of restaurant names found
            - foods: List of food items found
            - relevant: Boolean indicating if comment is food-related
            
    Example:
        >>> analyze_comment("Paradise biryani is amazing!")
        {
            'text': 'Paradise biryani is amazing!',
            'sentiment': 0.8,
            'sentiment_label': 'positive',
            'restaurants': ['Paradise'],
            'foods': ['biryani'],
            'relevant': True
        }
    """
    # Handle empty comments
    if not comment.strip():
        return {
            "text": "",
            "sentiment": 0.0,
            "sentiment_label": "neutral",
            "restaurants": [],
            "foods": [],
            "relevant": False
        }

    # Filter out non-food comments early to save processing
    if not is_relevant_comment(comment):
        return {
            "text": comment,
            "sentiment": 0.0,
            "sentiment_label": "neutral",
            "restaurants": [],
            "foods": [],
            "relevant": False
        }

    # Perform sentiment analysis using TextBlob
    # polarity ranges from -1 (negative) to 1 (positive)
    sentiment = TextBlob(comment).sentiment.polarity
    
    # Extract entities (restaurants and foods)
    restaurants, foods = extract_entities(comment)

    return {
        "text": comment,
        "sentiment": sentiment,
        "sentiment_label": sentiment_label(sentiment),
        "restaurants": list({r.lower().strip() for r in restaurants}),  # Normalize to lowercase
        "foods": list({f.lower().strip() for f in foods}),  # Normalize to lowercase
        "relevant": True
    }


# ========================= RELEVANCE FILTERING =========================

def is_relevant_comment(comment: str) -> bool:
    """
    Check if a comment is about food, restaurants, or dining.
    
    Uses keyword matching to filter out off-topic comments like
    general chit-chat, politics, etc.
    
    Args:
        comment: Comment text to check
        
    Returns:
        bool: True if comment mentions food-related terms
        
    Example:
        >>> is_relevant_comment("The biryani here is great")
        True
        >>> is_relevant_comment("What's the weather like?")
        False
    """
    # List of food-related terms to check for
    FOOD_TERMS = [
        "biryani", "thali", "shawarma", "curry", "roll", "tandoori",
        "cafe", "restaurant", "dosa", "momos", "chicken", "paneer", 
        "food", "taste", "must try", "recommend", "best place"
    ]
    
    text = comment.lower()
    
    # Return True if any food term is found in the comment
    return any(word in text for word in FOOD_TERMS)

