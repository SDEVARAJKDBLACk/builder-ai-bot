main.py (FIXED VERSION - SYNTAX ERROR REMOVED)

import flet as ft import google.generativeai as genai import pandas as pd from dotenv import load_dotenv import os import json

Load API Key

load_dotenv() GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY) model = genai.GenerativeModel("gemini-pro")

---------- AI FUNCTION ----------

def ai_extract(text): prompt = f""" Extract structured fields from the following unstructured data. Auto-detect fields. Return JSON only.

Text:
{text}
"""
try:
    response = model.generate_content(prompt)
    raw = response.text
    start = raw.find("{")
    end = raw.rfind("}")
    json_data = raw[start:end+1]
    return json.loads(json_data)
except Exception as e:
    return {"error": str(e)}

---------- UI ----------

def main(page: ft.Page): page.title = "AI Data Entry - Gemini" page.window_width = 1000 page.window_height = 700

input_box = ft.TextField(
    multiline=True,
    min_lines=8,
    max_lines=12,
    expand=True,
    label="Paste unstructured data here"
)

output_box = ft.TextField(
    multiline=True,
    min_lines=10,
    max_lines=15,
    expand=True,
    label="Analyzed Output"
)

extracted_data = {}

def analyze(e):
    nonlocal extracted_data
    text = input_box.value
    if not text:
        output_box.value = "No input provided"
    else:
        data = ai_extract(text)
        extracted_data = data
        output_box.value = json.dumps(data, indent=4)
    page.update()

def save_excel(e):
    if not extracted_data:
        output_box.value = "No data to export"
    else:
        df = pd.DataFrame([extracted_data])
        df.to_excel("ai_data_output.xlsx", index=False)
        output_box.value = "Saved as ai_data_output.xlsx"
    page.update()

page.add(
    ft.Column([
        ft.Text("AI Data Entry - Smart Automated Data Worker", size=24, weight=ft.FontWeight.BOLD),
        input_box,
        ft.Row([
            ft.ElevatedButton("Analyze Data", on_click=analyze),
            ft.ElevatedButton("Save to Excel", on_click=save_excel)
        ]),
        ft.Text("Analyzed Output", size=20, weight=ft.FontWeight.BOLD),
        output_box,
    ], expand=True)
)

ft.app(target=main)
