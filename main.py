
import flet as ft
import re
import pandas as pd
from datetime import datetime
import os
import speech_recognition as sr

# NLP
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = None

APP_TITLE = "AI Data Entry – Smart Automated Data Worker"
PUBLISHER = "Deva"
EXCEL_FILE = "ai_data_entry_output.xlsx"


# ---------------- DATA EXTRACTION ----------------
def extract_data(text: str):
    data = {}

    lines = [l.strip() for l in text.splitlines() if l.strip()]

    for line in lines:
        low = line.lower()

        if "name" in low:
            data["Name"] = line.split(":")[-1].strip()

        elif "age" in low:
            n = re.findall(r"\d+", line)
            if n:
                data["Age"] = n[0]

        elif "gender" in low:
            data["Gender"] = line.split(":")[-1].strip()

        elif "product" in low:
            data["Product"] = line.split(":")[-1].strip()

        elif "amount" in low or "price" in low:
            a = re.findall(r"\d+(\.\d{1,2})?", line)
            if a:
                data["Amount"] = a[0][0] if isinstance(a[0], tuple) else a[0]

        elif "city" in low:
            data["City"] = line.split(":")[-1].strip()

        elif "pincode" in low:
            p = re.findall(r"\d{6}", line)
            if p:
                data["Pincode"] = p[0]

    email = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    phone = re.findall(r"\b\d{10}\b", text)

    if email:
        data["Email"] = email[0]
    if phone:
        data["Phone"] = phone[0]

    if nlp:
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON" and "Name" not in data:
                data["Name"] = ent.text
            elif ent.label_ == "GPE" and "City" not in data:
                data["City"] = ent.text

    data["Saved_Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return data


# ---------------- FLET APP ----------------
def main(page: ft.Page):
    page.title = APP_TITLE
    page.window_width = 1100
    page.window_height = 700
    page.theme_mode = ft.ThemeMode.DARK

    analyzed_data = {}

    input_box = ft.TextField(
        label="Enter raw data / notes / voice input",
        multiline=True,
        min_lines=6,
        expand=True,
    )

    table = ft.DataTable(columns=[], rows=[])

    status = ft.Text("Ready", size=12)

    # ---- BUTTON FUNCTIONS ----
    def analyze_click(e):
        nonlocal analyzed_data
        raw = input_box.value.strip()
        if not raw:
            status.value = "Please enter some data"
            page.update()
            return

        analyzed_data = extract_data(raw)

        table.columns = [
            ft.DataColumn(ft.Text(k)) for k in analyzed_data.keys()
        ]
        table.rows = [
            ft.DataRow(cells=[ft.DataCell(ft.Text(str(v))) for v in analyzed_data.values()])
        ]

        status.value = "Data analyzed successfully"
        page.update()

    def save_excel_click(e):
        if not analyzed_data:
            status.value = "Analyze data first"
            page.update()
            return

        df = pd.DataFrame([analyzed_data])
        if os.path.exists(EXCEL_FILE):
            old = pd.read_excel(EXCEL_FILE)
            df = pd.concat([old, df], ignore_index=True)

        df.to_excel(EXCEL_FILE, index=False)
        status.value = "Data saved to Excel"
        page.update()

    def voice_input_click(e):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            status.value = "Listening..."
            page.update()
            try:
                audio = r.listen(source)
                text = r.recognize_google(audio)
                input_box.value += text + "\n"
                status.value = "Voice input added"
            except:
                status.value = "Voice input failed"
        page.update()

    # ---- UI ----
    page.add(
        ft.Column(
            [
                ft.Text(APP_TITLE, size=22, weight="bold"),
                ft.Text(f"Publisher: {PUBLISHER}", size=12),
                input_box,
                ft.Row(
                    [
                        ft.ElevatedButton("Analyze Data", on_click=analyze_click),
                        ft.ElevatedButton("Save to Excel", on_click=save_excel_click),
                        ft.ElevatedButton("Voice Input", on_click=voice_input_click),
                    ]
                ),
                table,
                status,
                ft.Text("Powered by KD", size=11),
            ],
            expand=True,
        )
    )


ft.app(target=main)
