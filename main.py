import flet as ft
import re
import json
import os
import threading
import time
from datetime import datetime
from collections import defaultdict
import pandas as pd

# =========================
# GLOBAL MEMORY SYSTEM
# =========================
HISTORY = []
LEARNED_FIELDS = {}
AUTO_FIELDS = set()

BASE_FIELDS = [
    "name","age","gender","phone","email","city","state","country","pincode",
    "product","amount","price","company","date","time","id","address",
    "dob","account","order"
]

SYNONYMS = {
    "mobile":"phone",
    "ph":"phone",
    "amt":"amount",
    "cost":"amount",
    "dob":"dob",
    "mail":"email",
    "location":"city"
}

SPELLING = {
    "amout":"amount",
    "phon":"phone",
    "naem":"name",
    "adress":"address"
}

# =========================
# AI CORE ENGINE
# =========================
def normalize_word(word):
    word = word.lower().strip()
    if word in SPELLING:
        word = SPELLING[word]
    if word in SYNONYMS:
        word = SYNONYMS[word]
    return word

def detect_patterns(text):
    data = defaultdict(list)

    patterns = {
        "phone": r"\b\d{10}\b",
        "pincode": r"\b\d{6}\b",
        "email": r"\b[\w\.-]+@[\w\.-]+\.\w+\b",
        "amount": r"\b\d+(?:\.\d+)?\b",
        "date": r"\b\d{2}[/-]\d{2}[/-]\d{4}\b",
        "time": r"\b\d{2}:\d{2}\b"
    }

    for field, pattern in patterns.items():
        matches = re.findall(pattern, text)
        if matches:
            data[field].extend(matches)

    words = re.split(r"[,\s\n]+", text)

    names = []
    for i in range(len(words)-1):
        if words[i].istitle() and words[i+1].istitle():
            names.append(words[i]+" "+words[i+1])
        elif words[i].istitle():
            names.append(words[i])

    if names:
        data["name"].extend(list(set(names)))

    return data

# =========================
# FIELD LEARNING ENGINE
# =========================
def learn_fields(data):
    for k in data:
        if k not in BASE_FIELDS:
            AUTO_FIELDS.add(k)
            LEARNED_FIELDS[k] = LEARNED_FIELDS.get(k,0)+1

# =========================
# AI ANALYSIS ENGINE
# =========================
def analyze_text(text):
    results = defaultdict(list)

    text = text.replace("\n"," ").replace("\t"," ")
    pattern_data = detect_patterns(text)

    for k,v in pattern_data.items():
        results[k].extend(v)

    tokens = re.split(r"[,\s]+", text)

    for token in tokens:
        w = normalize_word(token)
        if w in BASE_FIELDS:
            results[w].append(token)

    learn_fields(results)

    return results

# =========================
# EXPORT ENGINE
# =========================
def export_excel(data):
    flat = {}
    for k,v in data.items():
        flat[k] = ", ".join(list(set(v)))
    df = pd.DataFrame([flat])
    filename = f"ai_data_{int(time.time())}.xlsx"
    df.to_excel(filename,index=False)
    return filename

# =========================
# UI ENGINE (FLET)
# =========================
def main(page: ft.Page):
    page.title = "AI Data Entry – Automated Data Worker"
    page.window_width = 1100
    page.window_height = 750
    page.theme_mode = ft.ThemeMode.LIGHT

    input_box = ft.TextField(
        label="Enter Any Data / Paste Text / Raw Data",
        multiline=True,
        height=180,
        expand=True
    )

    output = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    history_panel = ft.Column(scroll=ft.ScrollMode.AUTO)

    status_text = ft.Text("", size=12)

    def update_history(data):
        HISTORY.insert(0,data)
        if len(HISTORY)>10:
            HISTORY.pop()

        history_panel.controls.clear()
        for i,h in enumerate(HISTORY):
            history_panel.controls.append(
                ft.Text(f"{i+1}. {list(h.keys())}")
            )
        page.update()

    def analyze_click(e):
        text = input_box.value
        if not text.strip():
            return

        result = analyze_text(text)
        output.controls.clear()

        for k,v in result.items():
            output.controls.append(
                ft.Text(f"{k.upper()} : {list(set(v))}")
            )

        update_history(result)
        status_text.value = "✅ Data analysis successfully"
        page.update()

    def export_click(e):
        if not HISTORY:
            status_text.value = "❌ No data to export"
            page.update()
            return

        file = export_excel(HISTORY[0])
        status_text.value = f"✅ Excel exported: {file}"
        page.update()

    analyze_btn = ft.ElevatedButton("Analyze Data", on_click=analyze_click)
    export_btn = ft.ElevatedButton("Export Excel", on_click=export_click)

    page.add(
        ft.Row([
            ft.Column([
                ft.Text("AI Data Entry – Automated Data Worker", size=22, weight="bold"),
                input_box,
                ft.Row([analyze_btn, export_btn]),
                status_text,
                ft.Divider(),
                ft.Text("Detected Fields"),
                output
            ], expand=True),
            ft.VerticalDivider(),
            ft.Column([
                ft.Text("History (Last 10)", size=16, weight="bold"),
                history_panel
            ], width=300)
        ]),
        ft.Container(
            content=ft.Text("powered by KD", size=10),
            alignment=ft.alignment.center
        )
    )

ft.app(target=main)
