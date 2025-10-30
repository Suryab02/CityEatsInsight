import os
import re
import praw
from dotenv import load_dotenv

# ------------------------- Setup -------------------------
load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("USER_AGENT")
)

# ------------------------- Keywords -------------------------
POST_QUERY = (
    '(title:"best restaurant" OR title:"food recommendation" OR title:"must try" '
    'OR title:"food places" OR title:"local food" OR title:"good food" '
    'OR title:"where to eat" OR title:"recommend" OR title:"cafe" OR title:"street food")'
)

POST_KEYWORDS = [
    "must try", "recommend", "suggest", "food places", "food spots",
    "best places", "any recommendations", "where to eat", "what to eat",
    "best restaurants", "local food", "food recommendations", "food guide",
    "good food", "top 10 food", "hidden gems", "cheap eats", "affordable food",
    "famous food", "popular restaurants", "must visit restaurants", "street food",
    "breakfast places", "lunch spots", "dinner places", "foodie"
]

FOOD_KEYWORDS = [
    "biryani", "chicken", "mutton", "pizza", "burger", "cafe", "restaurant",
    "hotel", "thali", "coffee", "chai", "dosa", "tandoori", "roll", "shawarma",
    "juice", "sandwich", "snack", "pasta", "paneer", "roti", "rice", "dal"
]

# ------------------------- Filters -------------------------
def is_food_post_related(text: str) -> bool:
    """Detect if a Reddit post is about food or restaurant recommendations."""
    text_lower = text.lower()
    return any(re.search(rf"\b{re.escape(keyword)}\b", text_lower) for keyword in POST_KEYWORDS)


def is_food_comment(text: str) -> bool:
    """Detect if a comment is talking about food, dishes, or restaurants."""
    text_lower = text.lower()
    return any(re.search(rf"\b{re.escape(keyword)}\b", text_lower) for keyword in FOOD_KEYWORDS)


# ------------------------- Main Function -------------------------
def get_city_posts(city: str):
    """
    Fetch Reddit posts about food in a given city subreddit.
    Filters posts and comments to keep only food-related ones.
    Returns structured data for AI summarization.
    """
    subreddit_name = city.lower()
    data = []

    try:
        subreddit = reddit.subreddit(subreddit_name)

        # Step 1: Search for food-related posts
        for post in subreddit.search(POST_QUERY, limit=40, sort="new"):
            full_text = (post.title + " " + getattr(post, "selftext", "")).strip()
            if not is_food_post_related(full_text):
                continue

            post_data = {
                "title": post.title,
                "url": f"https://reddit.com{post.permalink}",
                "score": post.score,
                "comments_text": ""
            }

            # Step 2: Fetch comments and filter only food-related ones
            post.comments.replace_more(limit=0)
            comments = sorted(post.comments.list(), key=lambda c: c.score, reverse=True)[:30]

            relevant_comments = [
                c.body.strip() for c in comments
                if len(c.body.strip().split()) > 5 and is_food_comment(c.body)
            ]

            # Step 3: Combine filtered comments into one text for AI
            if relevant_comments:
                post_data["comments_text"] = "\n".join(relevant_comments)
                data.append(post_data)

    except Exception as e:
        return {"error": str(e)}

    return data
