# app.py
# AI Data Entry Employee - Flet Modern UI (White + Green theme)
# Title shown: "AI Data Entry Employee  — Powered by KD"

import flet as ft
import re
import os
import pandas as pd
from datetime import datetime

APP_TITLE = "AI Data Entry Employee  — Powered by KD"

FIELDS = [
    "Date","Name","Age","Gender","Phone","Email","Street","City",
    "State","Pincode","Country","Company","Product/Service",
    "Order Amount","ID Number","Notes"
]

DEFAULT_SAVE_DIR = os.path.join(os.path.expanduser("~"), "Documents", "AI_Data_Entries")
os.makedirs(DEFAULT_SAVE_DIR, exist_ok=True)

# --- Simple extraction heuristics ---
def find_phone(text):
    m = re.search(r"(?:\+?\d{1,3}[\s\-]?)?(\d{10}|\d{9}|\d{8})", text)
    return m.group(0).strip() if m else ""

def find_email(text):
    m = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return m.group(0).strip() if m else ""

def find_amount(text):
    m = re.search(r"(?:₹|Rs|INR|\$)?\s*([0-9]{1,3}(?:[,\.][0-9]{3})*(?:\.\d+)?|[0-9]+(?:\.\d+)?)", text)
    return m.group(1).replace(",","") if m else ""

def find_name(text):
    m = re.search(r"(?:Name|name)[:\-\s]\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)", text)
    if m: return m.group(1).strip()
    m2 = re.search(r"([A-Z][a-z]+(?:\s[A-Z][a-z]+){0,2})", text.strip())
    return m2.group(1).strip() if m2 else ""

def find_age(text):
    m = re.search(r"\b(?:Age|age)[:\-\s]?(\d{1,3})\b", text)
    if m: return m.group(1)
    m2 = re.search(r"\b(\d{2})\s*(?:years|yrs|y/o|yo)\b", text.lower())
    return m2.group(1) if m2 else ""

def find_gender(text):
    t = text.lower()
    if "male" in t: return "Male"
    if "female" in t: return "Female"
    if "trans" in t: return "Trans"
    return ""

def find_city(text):
    m = re.search(r"(?:city|City|from|at)\s+([A-Za-z ]{3,30})", text)
    return m.group(1).strip() if m else ""

def find_pincode(text):
    m = re.search(r"\b(\d{5,6})\b", text)
    return m.group(1) if m else ""

def find_company(text):
    m = re.search(r"(?:Company|company|Co\.|Ltd|Pvt|Inc|LLP|LLC)[:\-\s]*([A-Z][A-Za-z0-9 &]*)", text)
    return m.group(1).strip() if m else ""

def extract_all(text):
    d = {k: "" for k in FIELDS}
    d["Date"] = datetime.now().date().isoformat()
    d["Name"] = find_name(text)
    d["Age"] = find_age(text)
    d["Gender"] = find_gender(text)
    d["Phone"] = find_phone(text)
    d["Email"] = find_email(text)
    d["Street"] = ""
    d["City"] = find_city(text)
    d["State"] = ""
    d["Pincode"] = find_pincode(text)
    d["Country"] = ""
    d["Company"] = find_company(text)
    d["Product/Service"] = ""
    d["Order Amount"] = find_amount(text)
    d["ID Number"] = ""
    d["Notes"] = text.strip()
    return d

def append_to_daily_excel(row_dict, save_dir=DEFAULT_SAVE_DIR):
    os.makedirs(save_dir, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"AI_Data_{date_str}.xlsx"
    path = os.path.join(save_dir, filename)
    df_new = pd.DataFrame([row_dict], columns=FIELDS)
    if os.path.exists(path):
        try:
            df_old = pd.read_excel(path, engine="openpyxl")
            df = pd.concat([df_old, df_new], ignore_index=True)
        except Exception:
            df = df_new
    else:
        df = df_new
    df.to_excel(path, index=False, engine="openpyxl")
    return path

# --- Flet UI (white bg, green rounded buttons) ---
def main(page: ft.Page):
    page.title = APP_TITLE
    page.window_width = 980
    page.window_height = 720
    page.bgcolor = "white"
    green = "#16a34a"

    raw_input = ft.TextField(label="Paste raw text here", multiline=True, height=180, expand=True)
    preview = ft.TextField(label="CSV Preview (read-only)", multiline=True, height=120, expand=True, disabled=True)
    status = ft.Text(value="Ready", color="black")

    def do_parse(e):
        txt = raw_input.value or ""
        if not txt.strip():
            status.value = "Please enter raw text first."
            page.update()
            return
        parsed = extract_all(txt)
        page.client_storage.set("parsed", parsed)
        csv_row = ",".join([str(parsed.get(f,"")) for f in FIELDS])
        preview.value = csv_row
        status.value = "Parsed successfully."
        page.update()

    def do_save(e):
        parsed = page.client_storage.get("parsed")
        if not parsed:
            status.value = "Nothing parsed. Click Parse first."
            page.update()
            return
        folder = folder_input.value or DEFAULT_SAVE_DIR
        os.makedirs(folder, exist_ok=True)
        path = append_to_daily_excel(parsed, save_dir=folder)
        status.value = f"Saved to {path}"
        raw_input.value = ""
        preview.value = ""
        page.client_storage.remove("parsed")
        page.update()

    def do_open(e):
        folder = folder_input.value or DEFAULT_SAVE_DIR
        filename = f"AI_Data_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
        full = os.path.join(folder, filename)
        if os.path.exists(full):
            if os.name == "nt":
                os.startfile(full)
            else:
                os.system(f'xdg-open "{full}"')
            status.value = f"Opened {full}"
        else:
            status.value = "Today's file not found."
        page.update()

    folder_input = ft.TextField(label="Save folder (optional)", value=DEFAULT_SAVE_DIR, expand=True)

    btn_parse = ft.ElevatedButton("Parse", on_click=do_parse, bgcolor=green, color="white",
                                 style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)))
    btn_save = ft.ElevatedButton("Save to Excel", on_click=do_save, bgcolor=green, color="white",
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)))
    btn_open = ft.ElevatedButton("Open Today's File", on_click=do_open, bgcolor=green, color="white",
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)))
    btn_exit = ft.ElevatedButton("Exit", on_click=lambda e: page.window_close(), bgcolor="#ef4444", color="white",
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)))

    header = ft.Row([ft.Text(APP_TITLE, size=18, weight="bold"), ft.Spacer(), btn_exit], alignment="center")

    page.add(
        header,
        ft.Column([
            raw_input,
            ft.Row([btn_parse, ft.Container(width=12), btn_save, ft.Container(width=12), btn_open]),
            preview,
            folder_input,
            ft.Row([status])
        ], spacing=12)
    )

if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER)
                  
