import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def semantic_extract(text):
    prompt = f"""
    Extract structured fields from this input.
    Return JSON only.

    Input:
    {text}

    Output format:
    {{
      "Name": "",
      "Phone": "",
      "Email": "",
      "City": "",
      "Product": "",
      "Amount": "",
      "AnyNewField": ""
    }}
    """

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0
    )

    content = res.choices[0].message.content
    return eval(content)
