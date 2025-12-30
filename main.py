import flet as ft
import re
import pandas as pd
from datetime import datetime
import os

# -------- OPTIONAL AI LIBS --------
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = None

try:
    import speech_recognition as sr
except:
    sr = None

try:
    from PIL import Image
    import pytesseract
except:
    pytesseract = None


EXCEL_FILE = "ai_data_entry_output.xlsx"


# -------- DATA EXTRACTION --------
def extract_data(text):
    data = {}
    lines = text.splitlines()

    for line in lines:
        l = line.lower()

        if "name" in l:
            data["Name"] = line.split(":")[-1].strip()

        elif "age" in l:
            m = re.findall(r"\d+", line)
            if m:
                data["Age"] = m[0]

        elif "gender" in l:
            data["Gender"] = line.split(":")[-1].strip()

        elif "product" in l or "item" in l:
            data["Product"] = line.split(":")[-1].strip()

        elif "amount" in l or "price" in l:
            m = re.findall(r"\d+", line)
            if m:
                data["Amount"] = m[0]

        elif "city" in l:
            data["City"] = line.split(":")[-1].strip()

        elif "pincode" in l:
            m = re.findall(r"\d{6}", line)
            if m:
                data["Pincode"] = m[0]

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
            if ent.label_ == "GPE" and "City" not in data:
                data["City"] = ent.text

    data["Saved_Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data["Raw_Input"] = text
    return data


# -------- SAVE EXCEL --------
def save_excel(data):
    df_new = pd.DataFrame([data])
    if os.path.exists(EXCEL_FILE):
        df_old = pd.read_excel(EXCEL_FILE)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_excel(EXCEL_FILE, index=False)


# -------- UI --------
def main(page: ft.Page):
    page.title = "AI Data Entry – Smart Automated Data Worker"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 900
    page.window_height = 650

    analyzed = {}

    input_box = ft.TextField(
        label="Enter text / voice / OCR input",
        multiline=True,
        min_lines=7,
        expand=True
    )

    table = ft.DataTable(columns=[], rows=[])
    status = ft.Text("")

    # -------- BUTTON LOGIC --------
    def analyze(e):
        nonlocal analyzed
        table.columns.clear()
        table.rows.clear()

        analyzed = extract_data(input_box.value)

        if not analyzed:
            status.value = "No data found"
            page.update()
            return

        table.columns.extend(
            [ft.DataColumn(ft.Text(k)) for k in analyzed.keys()]
        )

        table.rows.append(
            ft.DataRow(cells=[ft.DataCell(ft.Text(str(v))) for v in analyzed.values()])
        )

        status.value = "Data analyzed successfully"
        page.update()

    def save(e):
        if not analyzed:
            status.value = "Analyze first"
            page.update()
            return
        save_excel(analyzed)
        status.value = "Saved to Excel successfully"
        page.update()

    def voice(e):
        if not sr:
            status.value = "Speech library not installed"
            page.update()
            return

        r = sr.Recognizer()
        with sr.Microphone() as source:
            status.value = "Listening..."
            page.update()
            audio = r.listen(source)

        try:
            text = r.recognize_google(audio)
            input_box.value += "\n" + text
            status.value = "Voice captured"
        except:
            status.value = "Voice recognition failed"

        page.update()

    def ocr(e):
        if not pytesseract:
            status.value = "OCR library not installed"
            page.update()
            return

        def file_picked(res):
            if not res.files:
                return
            img = Image.open(res.files[0].path)
            text = pytesseract.image_to_string(img)
            input_box.value += "\n" + text
            status.value = "OCR text extracted"
            page.update()

        page.overlay.append(
            ft.FilePicker(on_result=file_picked)
        )
        page.overlay[-1].pick_files(allow_multiple=False)

    # -------- BUTTONS --------
    buttons = ft.Row([
        ft.ElevatedButton("Analyze Data", on_click=analyze),
        ft.ElevatedButton("Save to Excel", on_click=save),
        ft.ElevatedButton("Voice Input", on_click=voice),
        ft.ElevatedButton("OCR Image", on_click=ocr),
    ])

    page.add(
        ft.Column([
            ft.Text("AI Data Entry – Smart Automated Data Worker", size=22, weight="bold"),
            input_box,
            buttons,
            ft.Text("Analyzed Output", size=16, weight="bold"),
            table,
            status,
            ft.Text("Powered by KD | Publisher: Deva", size=12, opacity=0.6)
        ], expand=True)
    )


ft.app(target=main)
