"""
Reddit Scraper Module for CityEatsInsight

This module handles fetching food-related posts and comments from city-specific
subreddits. It filters posts by relevance and recency to provide fresh, 
high-quality food recommendations.

Key Features:
- Time-based filtering (last 6 months only)
- Keyword-based food relevance detection
- Comment extraction and filtering
- Error handling for non-existent subreddits
"""

import os
import re
import time
from datetime import datetime, timedelta
import praw
from praw.exceptions import PRAWException
from prawcore.exceptions import NotFound, ResponseException
from dotenv import load_dotenv

# ========================= CONFIGURATION =========================

# Load environment variables from .env file
load_dotenv()

# Initialize Reddit API client with credentials
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("USER_AGENT")
)

# Time filter: Only fetch posts from the last 6 months for fresh recommendations
MONTHS_TO_SEARCH = 6
SECONDS_IN_MONTH = 30 * 24 * 60 * 60  # Approximate seconds in a month

# ========================= SEARCH KEYWORDS =========================

# Reddit search query for finding food-related posts
# Uses Reddit's search syntax to match post titles
POST_QUERY = (
    '(title:"best restaurant" OR title:"food recommendation" OR title:"must try food" '
    'OR title:"food places" OR title:"local food" OR title:"good food" '
    'OR title:"where to eat" OR title:"recommend food" OR title:"street food")'
)

# Keywords to identify food recommendation posts
# These are used for additional filtering beyond the search query
POST_KEYWORDS = [
    "must try", "recommend food", "suggest", "food places", "food spots",
    "best places for food", "any recommendations", "where to eat", "what to eat",
    "best restaurants", "local food", "food recommendations", "food guide",
    "good food", "top 10 food", "hidden gems food", "cheap eats", "affordable food",
    "famous food", "popular restaurants", "must visit restaurants", "street food",
    "breakfast places", "lunch spots", "dinner places", "foodie", "famous food"
]

# Keywords to identify food-related comments
# Used to filter out irrelevant comments from posts
FOOD_KEYWORDS = [
    "biryani", "chicken", "mutton", "pizza", "burger", "cafe", "restaurant",
    "hotel", "thali", "coffee", "chai", "dosa", "tandoori", "roll", "shawarma",
    "juice", "sandwich", "snack", "pasta", "paneer", "roti", "rice", "dal"
]

# ========================= FILTER FUNCTIONS =========================

def is_food_post_related(text: str) -> bool:
    """
    Check if a Reddit post is about food or restaurant recommendations.
    
    Uses keyword matching with word boundaries to avoid false positives.
    For example, "best" won't match "bestow", only standalone "best".
    
    Args:
        text: Combined post title and body text
        
    Returns:
        bool: True if the post contains food-related keywords
        
    Example:
        >>> is_food_post_related("What are the best restaurants in town?")
        True
        >>> is_food_post_related("Best places to visit")
        False
    """
    text_lower = text.lower()
    # Use regex word boundaries (\b) to match whole words only
    return any(re.search(rf"\b{re.escape(keyword)}\b", text_lower) for keyword in POST_KEYWORDS)


def is_food_comment(text: str) -> bool:
    """
    Check if a comment discusses food, dishes, or restaurants.
    
    Filters comments to keep only those mentioning specific food items
    or restaurant-related terms.
    
    Args:
        text: Comment body text
        
    Returns:
        bool: True if the comment mentions food-related keywords
        
    Example:
        >>> is_food_comment("Try the biryani at Paradise!")
        True
        >>> is_food_comment("I agree with you")
        False
    """
    text_lower = text.lower()
    # Use regex word boundaries to match whole words only
    return any(re.search(rf"\b{re.escape(keyword)}\b", text_lower) for keyword in FOOD_KEYWORDS)


def is_recent_post(post, months: int = MONTHS_TO_SEARCH) -> bool:
    """
    Check if a Reddit post was created within the specified time period.
    
    This ensures we only return fresh, recent food recommendations rather
    than outdated information from years ago.
    
    Args:
        post: PRAW submission object
        months: Number of months to look back (default: 6)
        
    Returns:
        bool: True if post is within the time window
        
    Example:
        Post from 2 months ago -> True
        Post from 2 years ago -> False
    """
    # Get current time and calculate cutoff timestamp
    current_time = time.time()
    cutoff_time = current_time - (months * SECONDS_IN_MONTH)
    
    # Reddit posts have a 'created_utc' timestamp
    return post.created_utc >= cutoff_time



# ========================= MAIN SCRAPER FUNCTION =========================

def get_city_posts(city: str, count: int):
    """
    Fetch recent food-related Reddit posts from a city's subreddit.
    
    This is the main entry point for the scraper. It searches a city's subreddit
    for food-related posts, filters them by relevance and recency, extracts
    top comments, and returns structured data for AI analysis.
    
    Workflow:
    1. Access the city's subreddit (e.g., r/hyderabad)
    2. Search for food-related posts using keywords
    3. Filter posts by time (last 6 months only)
    4. Extract and filter relevant comments from each post
    5. Return structured data with posts, comments, and metadata
    
    Args:
        city: Name of the city (used as subreddit name)
        count: Running count of posts processed (for tracking)
        
    Returns:
        tuple: (data, count) where:
            - data: List of post dictionaries or error dict
            - count: Updated count of posts processed
            
    Example Response:
        [
            {
                "title": "Best biryani places in Hyderabad?",
                "url": "https://reddit.com/r/hyderabad/...",
                "score": 245,
                "comments_text": "Try Paradise biryani...\nBawarchi is amazing..."
            },
            ...
        ]
        
    Error Response:
        {
            "error": "Subreddit r/xyz does not exist..."
        }
    """
    subreddit_name = city.lower()
    data = []

    try:
        # Step 1: Access the subreddit
        # This will raise NotFound exception if subreddit doesn't exist
        subreddit = reddit.subreddit(subreddit_name)
        
        # Verify subreddit exists by accessing its ID
        # This triggers an API call that will fail for non-existent subreddits
        _ = subreddit.id

        # Step 2: Search for food-related posts
        # Using 'all' time filter first, then we'll filter by date manually
        # sort='relevance' gives us the most relevant posts first
        posts_found = 0
        
        for post in subreddit.search(POST_QUERY, limit=50, sort="relevance", time_filter="all"):
            # Filter 1: Check if post is recent (last 6 months)
            if not is_recent_post(post):
                continue  # Skip old posts
            
            # Filter 2: Combine title and body text for relevance checking
            full_text = (post.title + " " + getattr(post, "selftext", "")).strip()
            
            # Filter 3: Check if post is actually about food recommendations
            if not is_food_post_related(full_text):
                continue  # Skip non-food posts
            
            # Post passed all filters - create data structure
            post_data = {
                "title": post.title,
                "url": f"https://reddit.com{post.permalink}",
                "score": post.score,  # Reddit upvotes
                "comments_text": ""
            }
            posts_found += 1

            # Step 3: Extract comments from the post
            # replace_more(limit=0) prevents fetching "load more comments" threads
            # This speeds up the scraping significantly
            post.comments.replace_more(limit=0)
            
            # Sort comments by score (upvotes) to get the most helpful ones first
            # Limit to top 20 comments to avoid processing too much data
            comments = sorted(post.comments.list(), key=lambda c: c.score, reverse=True)[:20]

            # Step 4: Filter comments to keep only food-related ones
            relevant_comments = [
                c.body.strip() for c in comments
                # Filter out very short comments (less than 5 words)
                # and comments that don't mention food
                if len(c.body.strip().split()) > 5 and is_food_comment(c.body)
            ]

            # Step 5: Combine filtered comments into one text block
            # Limit to top 10 comments to keep data manageable for AI processing
            if relevant_comments:
                post_data["comments_text"] = "\n".join(relevant_comments[:10])
                data.append(post_data)
            
            # Stop after finding enough posts to avoid excessive API calls
            if len(data) >= 10:
                break

        # Update the running count of posts processed
        count += posts_found
        
        # Check if we found any relevant data
        if not data:
            return {
                "error": f"No recent food-related posts found for r/{subreddit_name}. "
                         f"Try a different city or check if the subreddit is active."
            }, count

    except NotFound:
        # Subreddit doesn't exist
        return {
            "error": f"Subreddit r/{subreddit_name} does not exist. "
                     f"Please check the city name and try again."
        }, count
        
    except ResponseException as e:
        # Reddit API returned an error (rate limit, server error, etc.)
        return {
            "error": f"Reddit API error: {str(e)}. Please try again later."
        }, count
        
    except PRAWException as e:
        # General PRAW library error
        return {
            "error": f"Error accessing Reddit: {str(e)}"
        }, count
        
    except Exception as e:
        # Catch-all for unexpected errors
        return {
            "error": f"Unexpected error: {str(e)}"
        }, count
    
    return data, count

