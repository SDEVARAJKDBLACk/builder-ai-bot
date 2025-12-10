import flet as ft
import pandas as pd
import os
from datetime import datetime
import re

FIELDS = [
    "Date", "Name", "Age", "Gender", "Phone", "Email", "City",
    "Pincode", "Company", "Order Amount", "Notes"
]

SAVE_DIR = os.path.join(os.path.expanduser("~"), "Documents", "AI_Data_Entries")
os.makedirs(SAVE_DIR, exist_ok=True)

# ---------------------- Extractors -------------------------

def find_name(t):
    m = re.search(r"(?:name[:\-]?\s*)([A-Za-z ]+)", t, re.I)
    return m.group(1).strip().title() if m else ""

def find_age(t):
    m = re.search(r"(\d{1,2})\s*(yrs|years|age)", t, re.I)
    return m.group(1) if m else ""

def find_gender(t):
    t = t.lower()
    if "male" in t: return "Male"
    if "female" in t: return "Female"
    return ""

def find_phone(t):
    m = re.search(r"\b\d{10}\b", t)
    return m.group(0) if m else ""

def find_email(t):
    m = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}", t)
    return m.group(0) if m else ""

def find_city(t):
    m = re.search(r"(?:city|from)\s+([A-Za-z ]+)", t, re.I)
    return m.group(1).strip().title() if m else ""

def find_pincode(t):
    m = re.search(r"\b\d{6}\b", t)
    return m.group(0) if m else ""

def find_company(t):
    m = re.search(r"company[:\-]?\s*([A-Za-z0-9 &]+)", t, re.I)
    return m.group(1).strip().title() if m else ""

def find_amount(t):
    m = re.search(r"(₹|Rs|INR)?\s*([0-9]+\.?[0-9]*)", t)
    return m.group(2) if m else ""

def extract_all(text):
    return {
        "Date": datetime.now().date().isoformat(),
        "Name": find_name(text),
        "Age": find_age(text),
        "Gender": find_gender(text),
        "Phone": find_phone(text),
        "Email": find_email(text),
        "City": find_city(text),
        "Pincode": find_pincode(text),
        "Company": find_company(text),
        "Order Amount": find_amount(text),
        "Notes": text.strip()
    }

def save_to_excel(row):
    today = datetime.now().strftime("%Y-%m-%d")
    file = os.path.join(SAVE_DIR, f"AI_Data_{today}.xlsx")

    df_new = pd.DataFrame([row], columns=FIELDS)

    if os.path.exists(file):
        df_old = pd.read_excel(file)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new

    df.to_excel(file, index=False)
    return file

# ---------------------- UI -------------------------

def main(page: ft.Page):
    page.title = "AI Data Entry Employee — Powered by KD"
    page.horizontal_alignment = "center"
    page.scroll = "AUTO"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 450
    page.window_height = 700

    raw = ft.TextField(label="Paste raw text here", multiline=True, min_lines=8, width=400)
    preview = ft.Text("", size=14, selectable=True)

    def parse_data(e):
        if not raw.value.strip():
            preview.value = "⚠ Please enter some text."
            page.update()
            return

        data = extract_all(raw.value)

        preview.value = "\n".join([f"{k}: {v}" for k, v in data.items()])
        page.update()

    def save_data(e):
        if not raw.value.strip():
            preview.value = "⚠ Nothing to save."
            page.update()
            return

        data = extract_all(raw.value)
        path = save_to_excel(data)

        preview.value = f"✔ Saved Successfully!\n{path}"
        raw.value = ""
        page.update()

    parse_btn = ft.FilledButton(
        text="Parse Text",
        bgcolor="#2ecc71",
        color="white",
        on_click=parse_data
    )

    save_btn = ft.FilledButton(
        text="Save to Excel",
        bgcolor="#27ae60",
        color="white",
        on_click=save_data
    )

    page.add(
        ft.Text("AI Data Entry Employee — Powered by KD", size=20, weight=ft.FontWeight.BOLD, color="#2ecc71"),
        raw,
        parse_btn,
        save_btn,
        preview
    )

ft.app(target=main)
