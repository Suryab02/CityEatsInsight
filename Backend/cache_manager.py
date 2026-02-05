"""
Cache Manager Module for CityEatsInsight

This module handles caching of Reddit data and AI-generated insights to improve
performance and reduce API calls. It implements a time-based cache expiry system.

Key Features:
- Automatic cache directory creation
- Time-based cache expiry (6 hours by default)
- Vercel serverless compatibility (uses /tmp on Vercel)
- JSON-based storage for easy debugging

Cache Strategy:
- Each city's data is cached separately
- Cache expires after CACHE_EXPIRY_HOURS
- Stale cache is automatically refreshed on next request
"""

import tempfile
import json
import os
import time

# ========================= CONFIGURATION =========================

# Cache directory location
# On Vercel (serverless), use /tmp directory (ephemeral but fast)
# On local/traditional servers, use 'data/' directory (persistent)
if os.environ.get("VERCEL"):
    CACHE_DIR = os.path.join(tempfile.gettempdir(), "city_eats_cache")
else:
    CACHE_DIR = "data"

# Cache expiry time in hours
# After this time, cached data is considered stale and will be refreshed
CACHE_EXPIRY_HOURS = 6

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)


# ========================= CACHE FUNCTIONS =========================

def get_cache_path(city: str) -> str:
    """
    Generate the full file path for a city's cache file.
    
    Cache files are named: {city_name}_cache.json
    Example: hyderabad_cache.json, bangalore_cache.json
    
    Args:
        city: Name of the city (case-insensitive)
        
    Returns:
        str: Absolute path to the cache file
        
    Example:
        >>> get_cache_path("Hyderabad")
        '/path/to/data/hyderabad_cache.json'
    """
    return os.path.join(CACHE_DIR, f"{city.lower()}_cache.json")


def is_cache_valid(path: str) -> bool:
    """
    Check if a cache file exists and is still fresh (not expired).
    
    A cache is considered valid if:
    1. The file exists
    2. The file was modified less than CACHE_EXPIRY_HOURS ago
    
    Args:
        path: Full path to the cache file
        
    Returns:
        bool: True if cache is valid and can be used, False otherwise
        
    Example:
        Cache created 2 hours ago -> True (still valid)
        Cache created 8 hours ago -> False (expired)
    """
    # Check if file exists
    if not os.path.exists(path):
        return False
    
    # Calculate how old the cache is in hours
    file_modified_time = os.path.getmtime(path)
    current_time = time.time()
    age_hours = (current_time - file_modified_time) / 3600
    
    # Cache is valid if it's younger than expiry time
    return age_hours < CACHE_EXPIRY_HOURS


def load_cache(city: str):
    """
    Load cached data for a city if it exists and is still valid.
    
    This function checks if cached data exists and is fresh before loading it.
    If cache is stale or doesn't exist, returns None to trigger a fresh fetch.
    
    Args:
        city: Name of the city
        
    Returns:
        dict or None: Cached data if valid, None if cache is stale/missing
        
    Example:
        >>> data = load_cache("hyderabad")
        >>> if data:
        ...     print("Using cached data")
        ... else:
        ...     print("Need to fetch fresh data")
    """
    path = get_cache_path(city)
    
    # Only load if cache is valid
    if is_cache_valid(path):
        with open(path, "r") as f:
            return json.load(f)
    
    return None


def save_cache(city: str, data):
    """
    Save data to cache for a specific city.
    
    Overwrites existing cache file if it exists. The file's modification
    time is automatically updated, which is used for expiry checking.
    
    Args:
        city: Name of the city
        data: Dictionary or list to cache (must be JSON-serializable)
        
    Example:
        >>> insights = {"city": "Hyderabad", "insights": [...]}
        >>> save_cache("hyderabad", insights)
    """
    path = get_cache_path(city)
    
    # Write data with pretty formatting for easier debugging
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


