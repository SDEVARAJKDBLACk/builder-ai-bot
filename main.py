import flet as ft
import os
import re
import pandas as pd
from datetime import datetime

# ---------- NLP ----------
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = None

# ---------- VOICE ----------
try:
    import speech_recognition as sr
except:
    sr = None


# ---------- SAVE LOCATION ----------
BASE_DIR = os.path.join(os.path.expanduser("~"), "AI_Data_Entry_Output")
os.makedirs(BASE_DIR, exist_ok=True)
EXCEL_FILE = os.path.join(BASE_DIR, "ai_data_entry.xlsx")


# ---------- DATA EXTRACTION ----------
def extract_data(text: str):
    data = {}

    # 1️⃣ KEY : VALUE parsing (MAIN FIX)
    for line in text.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()

    # 2️⃣ REGEX fallback
    patterns = {
        "Email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "Phone": r"\b\d{10}\b",
        "Pincode": r"\b\d{6}\b",
        "Amount": r"\b\d+(\.\d{1,2})?\b",
    }

    for key, pattern in patterns.items():
        match = re.findall(pattern, text)
        if match and key not in data:
            data[key] = match[0]

    # 3️⃣ NLP enrichment (supporting role)
    if nlp:
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ not in data:
                data[ent.label_] = ent.text

    data["Saved_Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return data


# ---------- SAVE TO EXCEL ----------
def save_to_excel(record: dict):
    df_new = pd.DataFrame([record])

    if os.path.exists(EXCEL_FILE):
        df_old = pd.read_excel(EXCEL_FILE)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new

    df.to_excel(EXCEL_FILE, index=False)


# ---------- UI ----------
def main(page: ft.Page):
    page.title = "AI Data Entry Pro"
    page.window_width = 960
    page.window_height = 680

    analyzed_record = {}

    input_box = ft.TextField(
        label="Enter raw text / notes / phrases",
        multiline=True,
        min_lines=6,
        expand=True
    )

    status = ft.Text()
    table = ft.DataTable(columns=[], rows=[])

    # ---------- BUTTONS ----------
    def analyze_data(e):
        nonlocal analyzed_record
        text = input_box.value.strip()

        if not text:
            status.value = "Please enter data"
            page.update()
            return

        analyzed_record = extract_data(text)

        table.columns = [
            ft.DataColumn(ft.Text(k)) for k in analyzed_record.keys()
        ]
        table.rows = [
            ft.DataRow(
                cells=[ft.DataCell(ft.Text(str(v))) for v in analyzed_record.values()]
            )
        ]

        status.value = "Data analyzed successfully"
        page.update()

    def save_excel_btn(e):
        if not analyzed_record:
            status.value = "Analyze data first"
            page.update()
            return

        save_to_excel(analyzed_record)
        status.value = "Data saved to Excel successfully"
        page.update()

    def voice_input(e):
        if not sr:
            status.value = "Speech module not available"
            page.update()
            return

        try:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                status.value = "Listening..."
                page.update()
                audio = r.listen(source)

            text = r.recognize_google(audio)
            input_box.value += "\n" + text
            status.value = "Voice input added"
        except Exception:
            status.value = "Voice recognition failed"

        page.update()

    # ---------- LAYOUT ----------
    page.add(
        ft.Column(
            expand=True,
            controls=[
                ft.Text(
                    "AI Data Entry – Smart Automated Data Worker",
                    size=22,
                    weight="bold"
                ),
                input_box,

                ft.Row(
                    controls=[
                        ft.ElevatedButton("Analyze Data", on_click=analyze_data),
                        ft.ElevatedButton("Save to Excel", on_click=save_excel_btn),
                        ft.ElevatedButton("🎤 Voice Input", on_click=voice_input),
                    ]
                ),

                ft.Text("Analyzed Output", size=18, weight="bold"),
                table,
                status,
                ft.Divider(),
                ft.Text("Powered by KD | Publisher: Deva", italic=True),
            ]
        )
    )


ft.app(target=main)
