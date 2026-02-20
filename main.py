import flet as ft
import google.generativeai as genai
import json
import pandas as pd
import os
from dotenv import load_dotenv

# Load API Key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def analyze_with_ai(text):
    prompt = f"""
You are an AI data extraction engine.

Extract structured fields from the unstructured text.
Auto-detect fields like:
name, age, gender, phone, alternate_phone, email, address, city, state, country, pincode,
company, role, qualification, dob, id_number, reference_name, notes, custom_fields.

Return ONLY valid JSON.
No explanation.
No markdown.
Only JSON.

Input:
{text}
"""

    response = model.generate_content(prompt)
    raw = response.text.strip()

    # Clean code block if Gemini adds it
    if raw.startswith("```"):
        raw = raw.replace("```json", "").replace("```", "").strip()

    return json.loads(raw)

def main(page: ft.Page):
    page.title = "AI Data Entry – Smart Automated Data Worker"
    page.window_width = 1000
    page.window_height = 750
    page.scroll = ft.ScrollMode.AUTO

    input_box = ft.TextField(
        multiline=True,
        min_lines=10,
        max_lines=12,
        expand=True,
        label="Enter raw text / notes / messages / content",
    )

    output_box = ft.TextField(
        multiline=True,
        min_lines=10,
        max_lines=12,
        expand=True,
        label="Analyzed Output (JSON)",
        read_only=True,
    )

    extracted_data = {}

    def analyze_click(e):
        nonlocal extracted_data
        try:
            text = input_box.value.strip()
            if not text:
                output_box.value = "Please enter data"
                page.update()
                return

            result = analyze_with_ai(text)
            extracted_data = result
            output_box.value = json.dumps(result, indent=4)
        except Exception as err:
            output_box.value = f"AI Error:\n{str(err)}"

        page.update()

    def save_excel(e):
        try:
            if not extracted_data:
                output_box.value = "No analyzed data to save"
                page.update()
                return

            df = pd.DataFrame([extracted_data])
            df.to_excel("ai_data_output.xlsx", index=False)
            output_box.value = "Saved to ai_data_output.xlsx successfully"
        except Exception as err:
            output_box.value = f"Excel Error:\n{str(err)}"

        page.update()

    header = ft.Text(
        "AI Data Entry – Smart Automated Data Worker",
        size=26,
        weight=ft.FontWeight.BOLD,
    )

    analyze_btn = ft.ElevatedButton("Analyze Data", on_click=analyze_click)
    save_btn = ft.ElevatedButton("Save to Excel", on_click=save_excel)

    page.add(
        ft.Column(
            [
                header,
                ft.Container(height=10),
                input_box,
                ft.Container(height=10),
                ft.Row([analyze_btn, save_btn]),
                ft.Container(height=15),
                ft.Text("Analyzed Output", size=20, weight=ft.FontWeight.BOLD),
                output_box,
                ft.Container(height=10),
                ft.Text("Powered by KD | Publisher: Deva", size=12),
            ],
            expand=True,
        )
    )

ft.app(target=main)
