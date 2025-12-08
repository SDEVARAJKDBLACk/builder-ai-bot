#!/usr/bin/env python3
# ai_data_entry_app.py
# AI Data Entry local app (PySimpleGUI)

import re
from datetime import datetime
import os
import pandas as pd
from dateutil import parser as dateparser
import PySimpleGUI as sg

FIELDS = [
    "Date", "Name", "Age", "Gender", "Phone", "Email", "Street", "City",
    "State", "Pincode", "Country", "Company", "Product/Service",
    "Order Amount", "ID Number", "Notes"
]
DEFAULT_SAVE_DIR = os.path.join(os.path.expanduser("~"), "Documents", "AI_Data_Entries")
os.makedirs(DEFAULT_SAVE_DIR, exist_ok=True)

def find_phone(text):
    m = re.search(r"(?:\+?\d{1,3}[\s\-]?)?(\d{10}|\d{9}|\d{8})", text)
    return m.group(0).strip() if m else ""

def find_email(text):
    m = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return m.group(0).strip() if m else ""

def find_amount(text):
    m = re.search(r"(?:₹|Rs|INR|\$)?\s*([0-9]{1,3}(?:[,\.][0-9]{3})*(?:\.\d+)?|[0-9]+(?:\.\d+)?)", text)
    return m.group(1).replace(",", "") if m else ""

def find_name(text):
    m = re.search(r"(?:Name|name)[:\-\s]\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)", text)
    if m:
        return m.group(1).strip()
    m2 = re.search(r"^([A-Z][a-z]+(?:\s[A-Z][a-z]+){0,2})", text.strip())
    return m2.group(1).strip() if m2 else ""

def find_age(text):
    m = re.search(r"\b(Age|age)[:\-\s]?\s*(\d{1,3})\b", text)
    if m:
        return m.group(2)
    m2 = re.search(r"\b(\d{2})\s*(?:years|yrs|y/o|yo)\b", text.lower())
    return m2.group(1) if m2 else ""

def find_gender(text):
    t = text.lower()
    if re.search(r"\bmale\b", t): return "Male"
    if re.search(r"\bfemale\b", t): return "Female"
    if re.search(r"\btrans\b", t): return "Trans"
    return ""

def find_pincode(text):
    m = re.search(r"\b(\d{5,6})\b", text)
    return m.group(1) if m else ""

def find_company(text):
    m = re.search(r"(?:Company|company|Co\.|Ltd|Pvt|Corporation|Inc|LLP|LLC)\s*[:\-]?\s*([A-Z][A-Za-z0-9 &]*)", text)
    if m:
        return m.group(1).strip()
    m2 = re.search(r"(?:from|at)\s+([A-Z][A-Za-z0-9 &]{2,})", text)
    return m2.group(1).strip() if m2 else ""

def find_address_terms(text):
    city = ""
    m = re.search(r"(?:city|City|from|at)\s+([A-Za-z ]{3,30})", text)
    if m:
        city = m.group(1).strip()
    return city

def find_date(text):
    try:
        dt = dateparser.parse(text, fuzzy=True, default=datetime.now())
        return dt.date().isoformat()
    except Exception:
        return ""

def extract_all(text):
    d = {k: "" for k in FIELDS}
    d["Date"] = datetime.now().date().isoformat()
    d["Name"] = find_name(text)
    d["Age"] = find_age(text)
    d["Gender"] = find_gender(text)
    d["Phone"] = find_phone(text)
    d["Email"] = find_email(text)
    d["Street"] = ""
    d["City"] = find_address_terms(text)
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

def open_file(path):
    try:
        if os.name == "nt":
            os.startfile(path)
        else:
            print("Open file:", path)
    except Exception as e:
        print("Unable to open file:", str(e))

def make_window(save_dir):
    sg.theme('DarkBlue3')
    layout = [
        [sg.Text("AI Data Entry Employee", font=("Helvetica", 16))],
        [sg.Text("Paste raw text (any format):")],
        [sg.Multiline(key="-RAW-", size=(80,10), tooltip="Paste messages, notes, orders, etc.")],
        [sg.Button("Parse", size=(10,1)), sg.Button("Save to Excel", size=(15,1)), sg.Button("Open Today's File", size=(15,1)), sg.Button("Exit")],
        [sg.Text("CSV Preview (first line):")],
        [sg.Multiline(key="-CSV-", size=(80,4), disabled=True)],
        [sg.Text("Save folder:"), sg.Input(save_dir, key="-FOLDER-", size=(60,1)), sg.FolderBrowse(target="-FOLDER-")],
        [sg.Text("", key="-STATUS-", size=(80,1))]
    ]
    return sg.Window("AI Data Entry Employee", layout, finalize=True)

def main():
    save_dir = DEFAULT_SAVE_DIR
    window = make_window(save_dir)
    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Exit"):
            break
        if event == "Parse":
            raw = values["-RAW-"].strip()
            if not raw:
                window["-STATUS-"].update("Please paste raw text first.")
                continue
            parsed = extract_all(raw)
            csv_row = ",".join([str(parsed.get(f, "")) for f in FIELDS])
            window["-CSV-"].update(csv_row + "\nData ready to save.")
            window["-STATUS-"].update("Parsed successfully. Preview shown. Click Save to append to Excel.")
        if event == "Save to Excel":
            raw = values["-RAW-"].strip()
            folder = values["-FOLDER-"] or save_dir
            os.makedirs(folder, exist_ok=True)
            if not raw:
                window["-STATUS-"].update("Please paste raw text first.")
                continue
            parsed = extract_all(raw)
            path = append_to_daily_excel(parsed, save_dir=folder)
            window["-STATUS-"].update(f"Saved to {path}")
            window["-CSV-"].update("")
            window["-RAW-"].update("")
        if event == "Open Today's File":
            folder = values["-FOLDER-"] or save_dir
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"AI_Data_{date_str}.xlsx"
            path = os.path.join(folder, filename)
            if os.path.exists(path):
                open_file(path)
            else:
                window["-STATUS-"].update("No file exists for today yet.")
    window.close()

if __name__ == "__main__":
    main()
