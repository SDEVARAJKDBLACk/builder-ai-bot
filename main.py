import flet as ft import google.generativeai as genai import json import pandas as pd import os from dotenv import load_dotenv

================= ENV =================

load_dotenv() GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY) model = genai.GenerativeModel("gemini-1.5-flash")

================= AI ENGINE =================

def ai_analyze(text): prompt = f""" Extract structured data from the following unstructured input.

Rules:

Auto detect fields

Create meaningful field names

Max 20 fields

Output ONLY valid JSON

No explanation

No markdown

No formatting text


Input: {text} """ response = model.generate_content(prompt) return response.text.strip()

================= FLET UI =================

def main(page: ft.Page): page.title = "AI Data Entry – Gemini Smart Worker" page.theme_mode = ft.ThemeMode.LIGHT page.window_width = 1200 page.window_height = 800

structured_data = {}

title = ft.Text("AI Data Entry – Smart Automated Data Worker", size=26, weight=ft.FontWeight.BOLD)

input_box = ft.TextField(
    multiline=True,
    min_lines=6,
    max_lines=10,
    label="Enter Raw Data",
    expand=True,
)

output_box = ft.TextField(
    multiline=True,
    min_lines=10,
    max_lines=18,
    label="Analyzed Output",
    expand=True,
    read_only=True
)

status_text = ft.Text("Status: Idle", size=12)

def analyze_click(e):
    nonlocal structured_data
    raw_text = input_box.value
    if not raw_text:
        page.snack_bar = ft.SnackBar(ft.Text("Please enter data"))
        page.snack_bar.open = True
        page.update()
        return

    status_text.value = "Status: Analyzing..."
    page.update()

    try:
        ai_result = ai_analyze(raw_text)
        start = ai_result.find("{")
        end = ai_result.rfind("}") + 1
        clean_json = ai_result[start:end]
        structured_data = json.loads(clean_json)

        output = ""
        for k, v in structured_data.items():
            output += f"{k}: {v}\n"

        output_box.value = output
        status_text.value = "Status: Analysis completed"

    except Exception as err:
        output_box.value = f"AI Error: {str(err)}"
        status_text.value = "Status: Error"

    page.update()

def export_excel(e):
    if not structured_data:
        page.snack_bar = ft.SnackBar(ft.Text("No analyzed data"))
        page.snack_bar.open = True
        page.update()
        return

    df = pd.DataFrame([structured_data])
    file_name = "ai_data_output.xlsx"
    df.to_excel(file_name, index=False)

    page.snack_bar = ft.SnackBar(ft.Text(f"Excel saved: {file_name}"))
    page.snack_bar.open = True
    page.update()

analyze_btn = ft.ElevatedButton("Analyze Data", icon=ft.icons.AUTO_FIX_HIGH, on_click=analyze_click)
save_btn = ft.ElevatedButton("Save to Excel", icon=ft.icons.SAVE, on_click=export_excel)

btn_row = ft.Row([analyze_btn, save_btn], alignment=ft.MainAxisAlignment.CENTER)

layout = ft.Column([
    title,
    ft.Divider(),
    input_box,
    btn_row,
    ft.Divider(),
    output_box,
    status_text
], expand=True, spacing=15)

page.add(layout)

================= RUN =================

ft.app(target=main)
