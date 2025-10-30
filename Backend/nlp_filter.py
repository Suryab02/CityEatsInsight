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
    """
    Cleans Gemini output like:
    ```json
    {
        "city_overview": "...",
        "top_recommendations": [...],
        "major_complaints": [...]
    }
    ```
    and returns a parsed Python dict.
    """
    if not raw_text:
        return {"error": "Empty AI response"}

    # Remove markdown fences and language hints
    text = raw_text.strip()
    text = re.sub(r"^```json\s*|\s*```$", "", text.strip())

    # Extract the inner JSON (handles escaped \n)
    text = text.replace("\\n", "\n").replace("\\\"", "\"").strip()

    # Try to find the first valid JSON object
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return {"error": "No valid JSON found", "raw": raw_text}

    json_str = match.group(0)

    try:
        # Parse to Python dict
        data = json.loads(json_str)
    except json.JSONDecodeError:
        # Attempt light cleaning
        fixed = json_str.replace("'", '"')
        data = json.loads(fixed)

    # Return the clean structure
    return data

