"""
NLP Filter Module for CityEatsInsight

This module handles data aggregation and AI output cleaning for the application.
It processes analyzed comments to generate restaurant insights and cleans
Gemini AI responses to extract structured JSON data.

Key Features:
- Aggregate restaurant mentions and sentiment from comments
- Clean and parse Gemini AI JSON responses
- Handle malformed JSON with fallback strategies
- Generate restaurant summaries with food associations
"""

from collections import defaultdict
import json
import os
import re


# ========================= DATA AGGREGATION =========================

def aggregate_data(city, analyzed_comments):
    """
    Aggregate analyzed comments to generate restaurant insights.
    
    This function processes a list of analyzed comments to:
    1. Count restaurant mentions
    2. Track positive/negative sentiment
    3. Associate foods with each restaurant
    4. Generate summary descriptions
    
    Args:
        city: Name of the city being analyzed
        analyzed_comments: List of comment analysis dicts from nlp_analyzer
        
    Returns:
        list: Restaurant insights with structure:
            [
                {
                    "name": "Restaurant Name",
                    "mentions": 5,
                    "positive": 4,
                    "negative": 1,
                    "foods": ["biryani", "chicken"],
                    "summary": "Mostly positive, popular for biryani, chicken."
                },
                ...
            ]
            
    Side Effect:
        Saves results to data/{city}.json file
        
    Example:
        >>> comments = [
        ...     {"restaurants": ["Paradise"], "sentiment": 0.8, "foods": ["biryani"]},
        ...     {"restaurants": ["Paradise"], "sentiment": 0.6, "foods": ["chicken"]}
        ... ]
        >>> aggregate_data("hyderabad", comments)
        [{'name': 'Paradise', 'mentions': 2, 'positive': 2, 'negative': 0, ...}]
    """
    # Use defaultdict to automatically initialize restaurant entries
    results = defaultdict(lambda: {"mentions": 0, "positive": 0, "negative": 0, "foods": set()})

    # Process each analyzed comment
    for c in analyzed_comments:
        for r in c["restaurants"]:
            # Increment mention count
            results[r]["mentions"] += 1
            
            # Track sentiment
            if c["sentiment"] > 0:
                results[r]["positive"] += 1
            elif c["sentiment"] < 0:
                results[r]["negative"] += 1
            
            # Add associated foods (using set to avoid duplicates)
            results[r]["foods"].update(c["foods"])

    # Convert to output format
    output = []
    for name, info in results.items():
        # Generate summary based on sentiment ratio
        summary = "Mostly positive" if info["positive"] > info["negative"] else "Mixed reviews"
        
        # Create restaurant entry
        output.append({
            "name": name,
            "mentions": info["mentions"],
            "positive": info["positive"],
            "negative": info["negative"],
            "foods": list(info["foods"]),  # Convert set to list for JSON serialization
            "summary": f"{summary}, popular for {', '.join(info['foods']) if info['foods'] else 'varied dishes'}."
        })

    # Save to file for caching/debugging
    os.makedirs("data", exist_ok=True)
    with open(f"data/{city.lower()}.json", "w") as f:
        json.dump(output, f, indent=2)

    return output


# ========================= AI OUTPUT CLEANING =========================

def clean_gemini_output(raw_text):
    """
    Clean and parse Gemini AI output to extract structured JSON data.
    
    Gemini sometimes returns JSON wrapped in markdown code blocks or with
    escaped characters. This function handles various output formats and
    extracts valid JSON.
    
    Handles:
    - Markdown code fences (```json ... ```)
    - Escaped newlines and quotes
    - Single quotes instead of double quotes
    - Already-parsed dict objects
    - List responses (joins them)
    
    Args:
        raw_text: Raw output from Gemini AI (string, dict, or list)
        
    Returns:
        dict: Parsed JSON data with structure:
            {
                "city_overview": "...",
                "top_recommendations": [...],
                "major_complaints": [...]
            }
            
        Or error dict if parsing fails:
            {
                "error": "Error description",
                "raw": "original text"
            }
            
    Example:
        >>> raw = '```json\\n{"city_overview": "Great food"}\\n```'
        >>> clean_gemini_output(raw)
        {'city_overview': 'Great food'}
        
        >>> clean_gemini_output({"already": "parsed"})
        {'already': 'parsed'}
    """
    # Handle empty responses
    if not raw_text:
        return {"error": "Empty AI response"}

    # 🧩 Handle non-string inputs gracefully
    if isinstance(raw_text, dict):
        # Already parsed JSON - return as is
        return raw_text
    elif isinstance(raw_text, list):
        # Join list elements if Gemini returned list of chunks
        raw_text = " ".join(map(str, raw_text))
    else:
        # Ensure it's a string
        raw_text = str(raw_text)

    # 🧼 Remove markdown fences and language hints
    # Pattern: ```json ... ``` or ``` ... ```
    text = raw_text.strip()
    text = re.sub(r"^```json\s*|\s*```$", "", text.strip())

    # 🧹 Clean escaped characters
    # Replace escaped newlines and quotes with actual characters
    text = text.replace("\\n", "\n").replace('\\"', '"').strip()

    # 🎯 Find the first valid JSON object in the text
    # This handles cases where there's extra text before/after the JSON
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return {"error": "No valid JSON found", "raw": raw_text}

    json_str = match.group(0)

    # 🧠 Try to parse JSON
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        try:
            # Fallback: replace single quotes with double quotes
            # Some AI models use single quotes which isn't valid JSON
            fixed = json_str.replace("'", '"')
            data = json.loads(fixed)
        except Exception as e:
            return {"error": f"JSON parse failed: {e}", "raw": raw_text}

    return data


