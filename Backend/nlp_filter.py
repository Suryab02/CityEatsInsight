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


import json
import re

def clean_gemini_output(raw_text):
    """
    Cleans Gemini output like:
    ```json
    {
        "city_overview": "...",
        "top_recommendations": [...],
        "major_complaints": [...]
    }
    ```
    Returns a parsed Python dict safely, handling both dict and string responses.
    """
    if not raw_text:
        return {"error": "Empty AI response"}

    # 🧩 Handle non-string inputs gracefully
    if isinstance(raw_text, dict):
        # Already parsed JSON
        return raw_text
    elif isinstance(raw_text, list):
        # Join list elements if Gemini returned list of chunks
        raw_text = " ".join(map(str, raw_text))
    else:
        # Ensure it's a string
        raw_text = str(raw_text)

    # 🧼 Remove markdown fences and language hints
    text = raw_text.strip()
    text = re.sub(r"^```json\s*|\s*```$", "", text.strip())

    # 🧹 Clean escaped characters
    text = text.replace("\\n", "\n").replace('\\"', '"').strip()

    # 🎯 Find the first valid JSON object in the text
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
            fixed = json_str.replace("'", '"')
            data = json.loads(fixed)
        except Exception as e:
            return {"error": f"JSON parse failed: {e}", "raw": raw_text}

    return data

