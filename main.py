import flet as ft
import re
import pandas as pd
import os
from datetime import datetime

# Optional AI features (safe import)
try:
    import speech_recognition as sr
except:
    sr = None

try:
    import pytesseract
    from PIL import Image
except:
    pytesseract = None

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = None


EXCEL_FILE = "ai_data_entry.xlsx"


# ---------------- AI EXTRACTION ----------------
def extract_entities(text: str):
    data = {}

    # Regex patterns
    patterns = {
        "Email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "Phone": r"\b\d{10}\b",
        "Pincode": r"\b\d{6}\b",
        "Amount": r"\b\d+(\.\d{1,2})?\b",
    }

    for key, pattern in patterns.items():
        found = re.findall(pattern, text)
        if found:
            data[key] = ", ".join(map(str, found))

    # spaCy NLP (dynamic fields)
    if nlp:
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ not in data:
                data[ent.label_] = ent.text

    data["Raw_Input"] = text
    data["Date_Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return data


# ---------------- EXCEL SAVE (APPEND FIXED) ----------------
def save_to_excel(data: dict):
    df_new = pd.DataFrame([data])

    if os.path.exists(EXCEL_FILE):
        df_old = pd.read_excel(EXCEL_FILE)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new

    df.to_excel(EXCEL_FILE, index=False)


# ---------------- UI APP ----------------
def main(page: ft.Page):
    page.title = "AI Data Entry Pro"
    page.window_width = 950
    page.window_height = 650

    input_box = ft.TextField(
        label="Enter raw data (text / notes / phrases)",
        multiline=True,
        min_lines=5,
        expand=True
    )

    status = ft.Text()

    table = ft.DataTable(columns=[], rows=[])

    # -------- BUTTON ACTIONS --------
    def analyze_text(e):
        text = input_box.value.strip()
        if not text:
            status.value = "Enter some data first"
            page.update()
            return

        data = extract_entities(text)

        table.columns = [ft.DataColumn(ft.Text(k)) for k in data.keys()]
        table.rows = [
            ft.DataRow(
                cells=[ft.DataCell(ft.Text(str(v))) for v in data.values()]
            )
        ]

        save_to_excel(data)
        status.value = "✅ Data analyzed & saved to Excel"
        page.update()

    def voice_input(e):
        if not sr:
            status.value = "Speech module not installed"
            page.update()
            return

        r = sr.Recognizer()
        with sr.Microphone() as source:
            status.value = " Listening..."
            page.update()
            audio = r.listen(source)

        try:
            text = r.recognize_google(audio)
            input_box.value += "\n" + text
            status.value = "Voice input added"
        except:
            status.value = "Voice recognition failed"

        page.update()

    def image_input(e):
        if not pytesseract:
            status.value = "OCR not installed"
            page.update()
            return

        file_picker.pick_files(allow_multiple=False)

    def on_file_selected(e: ft.FilePickerResultEvent):
        if not e.files:
            return
        img_path = e.files[0].path
        text = pytesseract.image_to_string(Image.open(img_path))
        input_box.value += "\n" + text
        status.value = "Image text extracted"
        page.update()

    file_picker = ft.FilePicker(on_result=on_file_selected)
    page.overlay.append(file_picker)

    # -------- UI LAYOUT --------
    page.add(
        ft.Column(
            expand=True,
            controls=[
                ft.Text("AI Data Entry – Smart Automated Data Worker",
                        size=22, weight="bold"),
                input_box,
                ft.Row(
                    controls=[
                        ft.ElevatedButton("Analyze & Save Excel", on_click=analyze_text),
                        ft.ElevatedButton(" Voice Input", on_click=voice_input),
                        ft.ElevatedButton(" Image OCR", on_click=image_input),
                    ]
                ),
                table,
                status,
                ft.Divider(),
                ft.Text("Powered by KD", italic=True),
            ]
        )
    )


# -------- SAFE ENTRY POINT --------
ft.app(target=main)

