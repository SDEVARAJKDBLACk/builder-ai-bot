import flet as ft
import re
import pandas as pd
import spacy
import speech_recognition as sr
from datetime import datetime

# Load AI NLP model (offline)
nlp = spacy.load("en_core_web_sm")


def extract_data_ai(text: str) -> dict:
    doc = nlp(text)

    data = {
        "Name": "",
        "Phone": "",
        "Email": "",
        "Amount": "",
        "City": "",
        "Date": datetime.now().strftime("%Y-%m-%d"),
    }

    # AI-based entity extraction
    for ent in doc.ents:
        if ent.label_ == "PERSON" and not data["Name"]:
            data["Name"] = ent.text
        elif ent.label_ == "GPE" and not data["City"]:
            data["City"] = ent.text

    # Regex-based extraction
    phone = re.search(r"\b\d{10}\b", text)
    email = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    amount = re.search(r"(₹|rs\.?)\s?\d+", text, re.IGNORECASE)

    if phone:
        data["Phone"] = phone.group()
    if email:
        data["Email"] = email.group()
    if amount:
        data["Amount"] = amount.group()

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
        label="Enter raw input (text / notes / invoice / voice)",
        multiline=True,
        min_lines=6,
        max_lines=8,
        expand=True,
    )

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Field")),
            ft.DataColumn(ft.Text("Value")),
        ],
        rows=[],
    )

    status = ft.Text()
    extracted = {}

    def analyze(e):
        nonlocal extracted
        if not input_box.value.strip():
            status.value = "Input required"
            status.color = ft.Colors.RED
            page.update()
            return

        extracted = extract_data_ai(input_box.value)
        table.rows.clear()

        for k, v in extracted.items():
            table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(k)),
                        ft.DataCell(ft.Text(v)),
                    ]
                )
            )

        status.value = "AI analysis completed successfully"
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
        filename = f"AI_Data_Entry_{datetime.now().strftime('%H%M%S')}.xlsx"
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
                ft.Text("Extracted Data", size=18),
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
