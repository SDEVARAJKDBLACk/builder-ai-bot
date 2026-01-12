# ==========================================================
# AI Data Entry – Automated Data Worker
# Single File Production Version (2025)
# ==========================================================

import flet as ft
import re
import os
import pandas as pd
from datetime import datetime

# ---------- AI / NLP ----------
import spacy
nlp = spacy.load("en_core_web_sm")

# ---------- OCR ----------
import easyocr
ocr_reader = easyocr.Reader(['en'], gpu=False)

# ---------- Voice ----------
import whisper
whisper_model = whisper.load_model("base")

# ---------- File Paths ----------
EXCEL_FILE = "ai_data_entry.xlsx"
TRAIN_FILE = "training_data.csv"

# ==========================================================
# SMART DATA EXTRACTION
# ==========================================================
def extract_entities(text: str):
    doc = nlp(text)

    data = {
        "Name": "",
        "Age": "",
        "Gender": "",
        "Phone": "",
        "Address": "",
        "Products": "",
        "Amount": "",
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # spaCy entities
    for ent in doc.ents:
        if ent.label_ == "PERSON" and not data["Name"]:
            data["Name"] = ent.text
        if ent.label_ in ["GPE", "LOC"] and not data["Address"]:
            data["Address"] = ent.text

    # Regex extraction
    phone = re.search(r"\b\d{10}\b", text)
    if phone:
        data["Phone"] = phone.group()

    age = re.search(r"\b(age|aged)\s+(\d{1,3})", text, re.I)
    if age:
        data["Age"] = age.group(2)

    gender = re.search(r"\b(male|female|other)\b", text, re.I)
    if gender:
        data["Gender"] = gender.group(1).capitalize()

    amount = re.search(r"\b(amount|total|price)\s+(\d+)", text, re.I)
    if amount:
        data["Amount"] = amount.group(2)

    product = re.search(r"\b(bought|purchased|products?)\s+(.+)", text, re.I)
    if product:
        data["Products"] = product.group(2)

    return data

# ==========================================================
# SAVE TO EXCEL
# ==========================================================
def save_to_excel(data):
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
    else:
        df = pd.DataFrame(columns=data.keys())

    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)

# ==========================================================
# AUTO LEARNING DATASET
# ==========================================================
def save_training(raw_text, extracted):
    row = {"raw_text": raw_text, **extracted}
    df = pd.DataFrame([row])

    if os.path.exists(TRAIN_FILE):
        df.to_csv(TRAIN_FILE, mode="a", header=False, index=False)
    else:
        df.to_csv(TRAIN_FILE, index=False)

# ==========================================================
# VOICE INPUT
# ==========================================================
def voice_to_text():
    # expects voice.wav recorded externally or via future enhancement
    if not os.path.exists("voice.wav"):
        return "Voice file not found (voice.wav)"
    result = whisper_model.transcribe("voice.wav")
    return result["text"]

# ==========================================================
# OCR IMAGE INPUT
# ==========================================================
def image_to_text(path):
    result = ocr_reader.readtext(path, detail=0)
    return " ".join(result)

# ==========================================================
# GUI APPLICATION
# ==========================================================
def main(page: ft.Page):
    page.title = "AI Data Entry – Automated Data Worker"
    page.window_width = 900
    page.window_height = 700
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    raw_input = ft.TextField(
        label="Raw Input (Text / Voice / OCR)",
        multiline=True,
        min_lines=8,
        expand=True
    )

    output_box = ft.Text(selectable=True)

    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)

    def analyze_and_save(e):
        extracted = extract_entities(raw_input.value)
        save_to_excel(extracted)
        save_training(raw_input.value, extracted)

        output_box.value = "\n".join(
            [f"{k}: {v}" for k, v in extracted.items()]
        )
        page.update()

    def voice_input(e):
        raw_input.value += "\n" + voice_to_text()
        page.update()

    def pick_image(e):
        def on_result(r: ft.FilePickerResultEvent):
            if r.files:
                text = image_to_text(r.files[0].path)
                raw_input.value += "\n" + text
                page.update()

        file_picker.on_result = on_result
        file_picker.pick_files(allow_multiple=False)

    page.add(
        ft.Text("AI Data Entry – Automated Data Worker", size=24, weight="bold"),
        ft.Text("2025 Smart Automated Data Extraction System", size=14),
        ft.Divider(),
        raw_input,
        ft.Row([
            ft.ElevatedButton("🎙 Voice Input", on_click=voice_input),
            ft.ElevatedButton("📷 OCR Image", on_click=pick_image),
            ft.ElevatedButton("🧠 Analyze & Save", on_click=analyze_and_save)
        ]),
        ft.Divider(),
        ft.Text("Extracted Structured Data:", size=18),
        output_box
    )

ft.app(target=main)
