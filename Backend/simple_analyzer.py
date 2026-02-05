import re
from collections import Counter

def extract_simple_insights(text: str, city: str):
    """
    Fallback function when Gemini API is unavailable.
    Extracts basic insights from Reddit text using simple NLP.
    """
    text_lower = text.lower()
    
    # Common restaurant/food keywords
    restaurant_patterns = [
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:restaurant|cafe|hotel|biryani|kitchen|diner|eatery)\b',
        r'\b(?:at|from|try)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
    ]
    
    food_items = [
        'biryani', 'dosa', 'idli', 'vada', 'chicken', 'mutton', 'paneer',
        'pizza', 'burger', 'sandwich', 'coffee', 'chai', 'tea', 'juice',
        'thali', 'curry', 'rice', 'naan', 'roti', 'pasta', 'noodles'
    ]
    
    # Extract mentioned restaurants
    restaurants = []
    for pattern in restaurant_patterns:
        matches = re.findall(pattern, text)
        restaurants.extend(matches)
    
    # Count food mentions
    food_mentions = Counter()
    for food in food_items:
        count = len(re.findall(rf'\b{food}\b', text_lower))
        if count > 0:
            food_mentions[food] = count
    
    # Get top foods
    top_foods = food_mentions.most_common(5)
    
    # Create basic recommendations
    recommendations = []
    restaurant_counter = Counter(restaurants)
    for restaurant, count in restaurant_counter.most_common(3):
        if count >= 2:  # Only include if mentioned multiple times
            # Try to find associated food
            associated_food = "Various dishes"
            for food, _ in top_foods:
                if food in text_lower[max(0, text_lower.find(restaurant.lower())-100):text_lower.find(restaurant.lower())+100]:
                    associated_food = food.capitalize()
                    break
            
            recommendations.append({
                "category": "Popular Choice",
                "restaurant_name": restaurant,
                "popular_dish": associated_food,
                "reason": f"Frequently mentioned in discussions ({count} times)"
            })
    
    # If no restaurants found, create generic recommendations
    if not recommendations and top_foods:
        for food, count in top_foods[:3]:
            recommendations.append({
                "category": "Popular Dish",
                "restaurant_name": f"{city} Local Favorites",
                "popular_dish": food.capitalize(),
                "reason": f"Highly discussed ({count} mentions)"
            })
    
    return {
        "city_overview": f"Discussions in {city} focus on {', '.join([f[0] for f in top_foods[:3]])} and local dining experiences." if top_foods else f"General food discussions about {city}.",
        "top_recommendations": recommendations[:5],
        "major_complaints": []  # Simple extraction doesn't detect complaints reliably
    }
