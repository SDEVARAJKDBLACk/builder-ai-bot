import re
import os
import pandas as pd
from datetime import datetime
from tkinter import *
from tkinter import messagebox, filedialog

FIELDS = [
    "Date","Name","Age","Gender","Phone","Email","Street","City",
    "State","Pincode","Country","Company",
    "Product/Service","Order Amount","ID Number","Notes"
]

SAVE_DIR = os.path.join(os.path.expanduser("~"), "Documents", "AI_Data_Entries")
os.makedirs(SAVE_DIR, exist_ok=True)

# ---------- SMART EXTRACTORS ----------

def find_age(text):
    m = re.search(r"\b(\d{1,3})\s*(years?|yrs?|y/o)?\b", text.lower())
    return m.group(1) if m else ""

def find_name(text):
    # labeled name
    m = re.search(r"(name)[:\- ]+([a-zA-Z]{3,})", text, re.I)
    if m:
        return m.group(2).title()

    # fallback: first alphabet-only word
    m2 = re.search(r"\b([A-Za-z]{3,})\b", text)
    return m2.group(1).title() if m2 else ""

def find_gender(text):
    t = text.lower()
    if "male" in t: return "Male"
    if "female" in t: return "Female"
    if "trans" in t: return "Trans"
    return ""

def find_phone(text):
    m = re.search(r"\b\d{10}\b", text)
    return m.group(0) if m else ""

def find_email(text):
    m = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}", text)
    return m.group(0) if m else ""

def find_amount(text):
    # ONLY detect amount if currency exists
    m = re.search(r"(₹|rs|inr|\$)\s*([0-9,.]+)", text.lower())
    return m.group(2).replace(",", "") if m else ""

# ---------- CORE PARSER ----------

def extract_data(text):
    data = {k:"" for k in FIELDS}
    data["Date"] = datetime.now().strftime("%Y-%m-%d")

    data["Age"] = find_age(text)
    if data["Age"]:
        text = re.sub(r"\b"+data["Age"]+r"\b", "", text)

    data["Name"] = find_name(text)
    data["Gender"] = find_gender(text)
    data["Phone"] = find_phone(text)
    data["Email"] = find_email(text)
    data["Order Amount"] = find_amount(text)
    data["Notes"] = text.strip()

    return data

# ---------- EXCEL SAVE ----------

def save_excel(row):
    file = os.path.join(SAVE_DIR, f"AI_Data_{datetime.now().date()}.xlsx")
    df_new = pd.DataFrame([row])

    if os.path.exists(file):
        df_old = pd.read_excel(file)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new

    df.to_excel(file, index=False)
    return file

# ---------- GUI ----------

def parse_text():
    global parsed
    raw = input_box.get("1.0", END).strip()
    if not raw:
        messagebox.showwarning("Warning","Enter text first")
        return
    parsed = extract_data(raw)
    preview.delete("1.0", END)
    preview.insert(END, ",".join(parsed[f] for f in FIELDS))

def save_data():
    if not parsed:
        return
    path = save_excel(parsed)
    messagebox.showinfo("Saved", f"Saved to:\n{path}")
    input_box.delete("1.0", END)
    preview.delete("1.0", END)

root = Tk()
root.title("AI Data Entry Employee")
root.geometry("900x550")

Label(root,text="AI Data Entry Employee",font=("Arial",18)).pack()

input_box = Text(root,height=8,width=100)
input_box.pack(pady=5)

Button(root,text="Parse",command=parse_text).pack()

preview = Text(root,height=4,width=100,bg="#EEE")
preview.pack(pady=5)

Button(root,text="Save to Excel",command=save_data).pack(pady=10)

parsed = {}
root.mainloop()
