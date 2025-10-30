import json, os, time

CACHE_DIR = "data"
CACHE_EXPIRY_HOURS = 6  # refresh every 6 hours

os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_path(city: str) -> str:
    """Return full cache file path for a given city."""
    return os.path.join(CACHE_DIR, f"{city.lower()}_cache.json")


def is_cache_valid(path: str) -> bool:
    """Check if cache exists and is still valid."""
    if not os.path.exists(path):
        return False
    age_hours = (time.time() - os.path.getmtime(path)) / 3600
    return age_hours < CACHE_EXPIRY_HOURS


def load_cache(city: str):
    """Load cached data if valid."""
    path = get_cache_path(city)
    if is_cache_valid(path):
        with open(path, "r") as f:
            return json.load(f)
    return None


def save_cache(city: str, data):
    """Save JSON data to cache."""
    path = get_cache_path(city)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
