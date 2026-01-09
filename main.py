#!/usr/bin/env python3
# AI Data Entry Employee (Tkinter Version - Works 100% in EXE)

import re
import os
import pandas as pd
from datetime import datetime
from tkinter import *
from tkinter import messagebox, filedialog

FIELDS = [
    "Date", "Name", "Age", "Gender", "Phone", "Email", "Street", "City",
    "State", "Pincode", "Country", "Company", "Product/Service",
    "Order Amount", "ID Number", "Notes"
]

DEFAULT_SAVE_DIR = os.path.join(os.path.expanduser("~"), "Documents", "AI_Data_Entries")
os.makedirs(DEFAULT_SAVE_DIR, exist_ok=True)

def find_phone(t):  return (m.group(0).strip() if (m := re.search(r"(?:\+?\d{1,3}[\s\-]?)?(\d{10}|\d{9}|\d{8})", t)) else "")
def find_email(t):  return (m.group(0).strip() if (m := re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", t)) else "")
def find_amount(t): return (m.group(1).replace(",", "") if (m := re.search(r"(?:₹|Rs|INR|\$)?\s*([0-9]{1,3}(?:[,\.][0-9]{3})*(?:\.\d+)?|[0-9]+(?:\.\d+)?)", t)) else "")
def find_name(t):
    m = re.search(r"(?:Name|name)[:\-\s]\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)", t)
    if m: return m.group(1).strip()
    m2 = re.search(r"^([A-Z][a-z]+(?:\s[A-Z][a-z]+){0,2})", t.strip())
    return m2.group(1).strip() if m2 else ""
def find_age(t):
    if m := re.search(r"\b(Age|age)[\s:]*([0-9]{1,3})\b", t): return m.group(2)
    if m2 := re.search(r"\b(\d{2})\s*(years|yrs|y/o|yo)\b", t.lower()): return m2.group(1)
    return ""
def find_gender(t):
    t = t.lower()
    return "Male" if "male" in t else "Female" if "female" in t else "Trans" if "trans" in t else ""
def find_pincode(t): return (m.group(1) if (m := re.search(r"\b(\d{5,6})\b", t)) else "")
def find_company(t):
    m = re.search(r"(Company|Co\.|Pvt|Ltd|LLP|LLC|Corporation|Inc)\s*[:\-]?\s*([A-Z][A-Za-z0-9 &]*)", t)
    return m.group(2).strip() if m else ""
def find_city(t):
    m = re.search(r"(?:city|City|from|at)\s+([A-Za-z ]{3,30})", t)
    return m.group(1).strip() if m else ""

def extract(text):
    d = {k: "" for k in FIELDS}
    d["Date"] = datetime.now().date().isoformat()
    d["Name"] = find_name(text)
    d["Age"] = find_age(text)
    d["Gender"] = find_gender(text)
    d["Phone"] = find_phone(text)
    d["Email"] = find_email(text)
    d["City"] = find_city(text)
    d["Pincode"] = find_pincode(text)
    d["Company"] = find_company(text)
    d["Order Amount"] = find_amount(text)
    d["Notes"] = text.strip()
    return d

def save_excel(row, folder):
    filename = f"AI_Data_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    path = os.path.join(folder, filename)
    new_df = pd.DataFrame([row], columns=FIELDS)
    if os.path.exists(path):
        try:
            old_df = pd.read_excel(path, engine="openpyxl")
            df = pd.concat([old_df, new_df], ignore_index=True)
        except:
            df = new_df
    else:
        df = new_df
    df.to_excel(path, index=False, engine="openpyxl")
    return path

def parse_text():
    raw = input_box.get("1.0", END).strip()
    if not raw:
        messagebox.showwarning("Warning", "Paste text first!")
        return
    global parsed
    parsed = extract(raw)
    csv_preview = ",".join([str(parsed.get(f, "")) for f in FIELDS])
    preview_box.config(state="normal")
    preview_box.delete("1.0", END)
    preview_box.insert(END, csv_preview)
    preview_box.config(state="disabled")
    status_label.config(text="Parsed successfully.")

def save_data():
    if not parsed:
        messagebox.showwarning("Warning", "Parse text first!")
        return
    folder = folder_path.get()
    os.makedirs(folder, exist_ok=True)
    path = save_excel(parsed, folder)
    status_label.config(text=f"Saved to {path}")
    input_box.delete("1.0", END)
    preview_box.config(state="normal")
    preview_box.delete("1.0", END)
    preview_box.config(state="disabled")

def open_today():
    folder = folder_path.get()
    filename = f"AI_Data_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    path = os.path.join(folder, filename)
    if os.path.exists(path): os.startfile(path)
    else: status_label.config(text="Today's file not found.")

# GUI
root = Tk()
root.title("AI Data Entry Employee")
root.geometry("900x600")

Label(root, text="AI Data Entry Employee", font=("Arial", 18)).pack()

input_box = Text(root, height=10, width=100)
input_box.pack()

Button(root, text="Parse", command=parse_text).pack()

preview_box = Text(root, height=4, width=100, state="disabled", bg="#EDEDED")
preview_box.pack()

folder_path = StringVar(value=DEFAULT_SAVE_DIR)
Entry(root, textvariable=folder_path, width=70).pack(side=LEFT, padx=10)
Button(root, text="Browse", command=lambda: folder_path.set(filedialog.askdirectory())).pack(side=LEFT)

Button(root, text="Save to Excel", command=save_data).pack(pady=10)
Button(root, text="Open Today File", command=open_today).pack()

status_label = Label(root, text="", fg="blue")
status_label.pack(pady=10)

parsed = {}
root.mainloop()
