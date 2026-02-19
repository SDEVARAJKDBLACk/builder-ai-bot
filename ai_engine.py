import requests, json
from config import OPENAI_API_KEY, MODEL

URL = "https://api.openai.com/v1/chat/completions"

def analyze_text(text):
    prompt = f"""
Extract structured fields from this unstructured text.
Return ONLY valid JSON. No explanation.

Text:
{text}
"""
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "AI data extraction engine"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0
    }

    r = requests.post(URL, headers=headers, json=payload, timeout=60)
    data = r.json()

    try:
        out = data["choices"][0]["message"]["content"]
        return json.loads(out)
    except:
        return {}
