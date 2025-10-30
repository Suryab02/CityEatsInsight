from collections import defaultdict
import json, os
import re

def aggregate_data(city, analyzed_comments):
    results = defaultdict(lambda: {"mentions": 0, "positive": 0, "negative": 0, "foods": set()})

    for c in analyzed_comments:
        for r in c["restaurants"]:
            results[r]["mentions"] += 1
            if c["sentiment"] > 0:
                results[r]["positive"] += 1
            elif c["sentiment"] < 0:
                results[r]["negative"] += 1
            results[r]["foods"].update(c["foods"])

    output = []
    for name, info in results.items():
        summary = "Mostly positive" if info["positive"] > info["negative"] else "Mixed reviews"
        output.append({
            "name": name,
            "mentions": info["mentions"],
            "positive": info["positive"],
            "negative": info["negative"],
            "foods": list(info["foods"]),
            "summary": f"{summary}, popular for {', '.join(info['foods']) if info['foods'] else 'varied dishes'}."
        })

    os.makedirs("data", exist_ok=True)
    with open(f"data/{city.lower()}.json", "w") as f:
        json.dump(output, f, indent=2)

    return output

def clean_gemini_output(raw_text: str):
    """Extracts and normalizes Gemini JSON output."""
    if not raw_text:
        return {}

    # Step 1: Extract JSON-like part from markdown or text
    match = re.search(r"\{[\s\S]*\}", raw_text)
    if not match:
        return {"error": "Invalid AI output"}

    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        # Attempt to fix minor JSON errors (quotes, etc.)
        cleaned = match.group(0).replace("'", '"')
        try:
            data = json.loads(cleaned)
        except Exception:
            return {"error": "Failed to parse AI JSON"}

    # Step 2: Normalize key names
    normalized = {
        "intent": data.get("intent", "unknown"),
        "restaurant_names": data.get("restaurant_names", []),
        "popular_foods": data.get("popular_foods", []),
        "overall_sentiment": data.get("overall_sentiment", "neutral"),
        "summary": data.get("summary", "")
    }

    # Step 3: Fix capitalization for restaurant & food names
    normalized["restaurant_names"] = [
        r.title().strip() for r in normalized["restaurant_names"]
    ]
    normalized["popular_foods"] = [
        f.title().strip() for f in normalized["popular_foods"]
    ]

    return normalized
