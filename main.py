import flet as ft
import pandas as pd
import spacy
import speech_recognition as sr
import subprocess
import sys
import re
from datetime import datetime

# ---------- SAFE spaCy loader ----------
def load_spacy_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        subprocess.check_call(
            [sys.executable, "-m", "spacy", "download", "en_core_web_sm"]
        )
        return spacy.load("en_core_web_sm")

nlp = load_spacy_model()
# --------------------------------------


def extract_dynamic_ai(text: str) -> dict:
    data = {}

    # 1️⃣ Key-Value detection (best for notes, invoices)
    lines = text.splitlines()
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip().title()
            value = value.strip()
            if key and value:
                data[key] = value

    # 2️⃣ NLP entity detection (fallback)
    doc = nlp(text)

    for ent in doc.ents:
        label_map = {
            "PERSON": "Name",
            "GPE": "City",
            "ORG": "Organization",
            "DATE": "Date",
            "MONEY": "Amount",
            "QUANTITY": "Quantity",
        }

        field = label_map.get(ent.label_)
        if field and field not in data:
            data[field] = ent.text

    # 3️⃣ Regex-based smart detection
    patterns = {
        "Phone": r"\b\d{10}\b",
        "Email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "Pincode": r"\b\d{6}\b",
    }

    for field, pattern in patterns.items():
        match = re.search(pattern, text)
        if match and field not in data:
            data[field] = match.group()

    # 4️⃣ Always add timestamp
    data["Captured On"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return data


def get_voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        return r.recognize_google(audio)
    except Exception:
        return ""


def main(page: ft.Page):
    page.title = "AI Data Entry Pro"
    page.window_width = 900
    page.window_height = 650
    page.padding = 20

    input_box = ft.TextField(
        label="Enter any raw data (notes / invoice / message / voice)",
        multiline=True,
        min_lines=6,
        expand=True,
    )

    table = ft.DataTable(columns=[], rows=[])
    status = ft.Text()
    extracted = {}

    def analyze(e):
        nonlocal extracted
        if not input_box.value.strip():
            status.value = "Please enter input"
            status.color = ft.Colors.RED
            page.update()
            return

        extracted = extract_dynamic_ai(input_box.value)

        table.columns.clear()
        table.rows.clear()

        # Dynamic table creation
        for key in extracted.keys():
            table.columns.append(ft.DataColumn(ft.Text(key)))

        table.rows.append(
            ft.DataRow(
                cells=[ft.DataCell(ft.Text(v)) for v in extracted.values()]
            )
        )

        status.value = "AI dynamically created fields successfully"
        status.color = ft.Colors.GREEN
        page.update()

    def voice(e):
        status.value = "Listening..."
        status.color = ft.Colors.BLUE
        page.update()

        text = get_voice_input()
        if text:
            input_box.value = text
            status.value = "Voice input captured"
            status.color = ft.Colors.GREEN
        else:
            status.value = "Voice recognition failed"
            status.color = ft.Colors.RED

        page.update()

    def export_excel(e):
        if not extracted:
            status.value = "No data to export"
            status.color = ft.Colors.RED
            page.update()
            return

        df = pd.DataFrame([extracted])
        filename = f"AI_Dynamic_Data_{datetime.now().strftime('%H%M%S')}.xlsx"
        df.to_excel(filename, index=False)

        status.value = f"Excel saved: {filename}"
        status.color = ft.Colors.GREEN
        page.update()

    page.add(
        ft.Column(
            [
                ft.Text(
                    "AI Data Entry Pro – Smart Automated Data Worker",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                ),
                input_box,
                ft.Row(
                    [
                        ft.ElevatedButton("Analyze with AI", on_click=analyze),
                        ft.OutlinedButton("Voice Input 🎤", on_click=voice),
                        ft.FilledButton("Export to Excel", on_click=export_excel),
                    ]
                ),
                ft.Divider(),
                ft.Text("Dynamic Extracted Data", size=18),
                table,
                ft.Divider(),
                status,
                ft.Text(
                    "Powered by KD",
                    size=12,
                    italic=True,
                    color=ft.Colors.GREY,
                ),
            ],
            expand=True,
        )
    )


ft.app(target=main)
