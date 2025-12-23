import flet as ft
import os
import re
import pandas as pd
from datetime import datetime

# ---------- SAFE NLP LOAD ----------
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = None

# ---------- SAFE VOICE LOAD ----------
try:
    import speech_recognition as sr
except:
    sr = None


# ---------- SAVE LOCATION (VERY IMPORTANT) ----------
SAVE_DIR = os.path.join(os.path.expanduser("~"), "AI_Data_Entry_Output")
os.makedirs(SAVE_DIR, exist_ok=True)
EXCEL_FILE = os.path.join(SAVE_DIR, "ai_data_entry.xlsx")


# ---------- AI EXTRACTION ----------
def extract_data(text: str):
    result = {}

    regex_patterns = {
        "Email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "Phone": r"\b\d{10}\b",
        "Pincode": r"\b\d{6}\b",
        "Amount": r"\b\d+(\.\d{1,2})?\b",
    }

    for key, pattern in regex_patterns.items():
        found = re.findall(pattern, text)
        if found:
            result[key] = ", ".join(map(str, found))

    if nlp:
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ not in result:
                result[ent.label_] = ent.text

    result["Raw_Input"] = text
    result["Saved_Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return result


# ---------- EXCEL SAVE (100% WORKING) ----------
def save_excel(data: dict):
    df_new = pd.DataFrame([data])

    if os.path.exists(EXCEL_FILE):
        df_old = pd.read_excel(EXCEL_FILE)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new

    df.to_excel(EXCEL_FILE, index=False)


# ---------- UI ----------
def main(page: ft.Page):
    page.title = "AI Data Entry Pro"
    page.window_width = 950
    page.window_height = 680

    analyzed_data = {}

    input_box = ft.TextField(
        label="Enter raw text / notes / phrases",
        multiline=True,
        min_lines=5,
        expand=True
    )

    status = ft.Text()
    table = ft.DataTable(columns=[], rows=[])

    # ---------- BUTTON FUNCTIONS ----------
    def analyze_only(e):
        nonlocal analyzed_data
        text = input_box.value.strip()

        if not text:
            status.value = "❌ Please enter some data"
            page.update()
            return

        analyzed_data = extract_data(text)

        table.columns = [ft.DataColumn(ft.Text(k)) for k in analyzed_data.keys()]
        table.rows = [
            ft.DataRow(
                cells=[ft.DataCell(ft.Text(str(v))) for v in analyzed_data.values()]
            )
        ]

        status.value = "Data analyzed successfully"
        page.update()

    def save_only(e):
        if not analyzed_data:
            status.value = " Analyze data"
            page.update()
            return

        save_excel(analyzed_data)
        status.value = f" Saved to Excel: {EXCEL_FILE}"
        page.update()

    def voice_input(e):
        if not sr:
            status.value = "Speech module not installed"
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
            status.value = " Voice input added"
        except Exception as ex:
            status.value = f"Voice error: {ex}"

        page.update()

    # ---------- UI LAYOUT ----------
    page.add(
        ft.Column(
            expand=True,
            controls=[
                ft.Text("AI Data Entry – Smart Automated Data Worker",
                        size=22, weight="bold"),
                input_box,

                ft.Row(
                    controls=[
                        ft.ElevatedButton("Analyze Data", on_click=analyze_only),
                        ft.ElevatedButton("Save to Excel", on_click=save_only),
                        ft.ElevatedButton(" Voice Input", on_click=voice_input),
                    ]
                ),

                ft.Text("Analyzed Output", size=18, weight="bold"),
                table,
                status,
                ft.Divider(),
                ft.Text("Powered by KD", italic=True),
                ft.Text(f"Excel save path: {EXCEL_FILE}", size=12)
            ]
        )
    )


ft.app(target=main)
