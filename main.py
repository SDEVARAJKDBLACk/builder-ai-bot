# ==============================
# AI DATA ENTRY - AUTOMATED DATA WORKER
# SINGLE FILE ENTERPRISE SYSTEM
# ==============================

import flet as ft
import threading, os, re, json, time
from datetime import datetime
import pandas as pd

# Online AI
import openai

# File processing
from PIL import Image
import pytesseract
import docx2txt
import PyPDF2

# ==============================
# CONFIG
# ==============================

APP_TITLE = "AI Data Entry - Automated Data Worker"
HISTORY_FILE = "history.json"
OPENAI_MODEL = "gpt-4o-mini"

CORE_FIELDS = [
    "name","age","gender","phone","email","address","city","state","pincode",
    "country","product","amount","date","company","id","account","bank",
    "ifsc","dob","notes"
]

# ==============================
# AI ENGINE
# ==============================

class AIEngine:
    def __init__(self, api_key=None):
        self.api_key = api_key
        if api_key:
            openai.api_key = api_key

    def online_ai_parse(self, text):
        try:
            prompt = f"""
Extract structured fields from this raw data.
Detect unlimited fields.
Return JSON only.

Text:
{text}
"""
            res = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=[{"role":"user","content":prompt}],
                temperature=0.2
            )
            data = res.choices[0].message.content
            return json.loads(data)
        except:
            return self.offline_parse(text)

    def offline_parse(self, text):
        fields = {}

        # basic patterns
        patterns = {
            "phone": r"\b\d{10}\b",
            "pincode": r"\b\d{6}\b",
            "amount": r"\b\d{3,7}\b",
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        }

        for k,p in patterns.items():
            m = re.search(p, text)
            if m:
                fields[k] = m.group()

        tokens = re.split("[,|\n]", text)
        for t in tokens:
            t = t.strip()
            if t and t.lower() not in fields.values():
                fields[f"field_{len(fields)+1}"] = t

        return fields

# ==============================
# FILE ENGINE
# ==============================

class FileEngine:
    def read_file(self, path):
        ext = path.lower()
        if ext.endswith(".txt"):
            return open(path,"r",encoding="utf-8",errors="ignore").read()

        if ext.endswith(".docx"):
            return docx2txt.process(path)

        if ext.endswith(".pdf"):
            text=""
            with open(path,"rb") as f:
                r=PyPDF2.PdfReader(f)
                for p in r.pages:
                    text+=p.extract_text()+"\n"
            return text

        if ext.endswith((".png",".jpg",".jpeg")):
            img = Image.open(path)
            return pytesseract.image_to_string(img)

        return ""

# ==============================
# HISTORY ENGINE
# ==============================

class HistoryEngine:
    def __init__(self):
        if not os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE,"w") as f:
                json.dump([],f)

    def save(self,data):
        with open(HISTORY_FILE,"r") as f:
            h=json.load(f)
        h.append({"time":str(datetime.now()),"data":data})
        with open(HISTORY_FILE,"w") as f:
            json.dump(h,f,indent=2)

    def load(self):
        with open(HISTORY_FILE,"r") as f:
            return json.load(f)

# ==============================
# UI
# ==============================

def main(page: ft.Page):
    page.title = APP_TITLE
    page.window_width = 1200
    page.window_height = 750
    page.theme_mode = ft.ThemeMode.LIGHT

    ai = AIEngine(api_key=os.getenv("OPENAI_API_KEY"))
    file_engine = FileEngine()
    history_engine = HistoryEngine()

    input_box = ft.TextField(
        label="Enter any data / Paste text / Raw data",
        multiline=True,
        min_lines=6,
        expand=True
    )

    field_list = ft.ListView(expand=True, spacing=5)
    history_list = ft.ListView(expand=True, spacing=5)

    status = ft.Text("Ready")

    def analyze_data(e):
        text = input_box.value
        if not text:
            status.value="No input data"
            page.update()
            return

        status.value="Analyzing..."
        page.update()

        def task():
            data = ai.online_ai_parse(text)
            field_list.controls.clear()

            for k,v in data.items():
                field_list.controls.append(ft.Text(f"{k} : {v}"))

            history_engine.save(data)
            status.value="Analysis completed successfully"
            page.update()

        threading.Thread(target=task).start()

    def export_excel(e):
        rows=[]
        for c in field_list.controls:
            k,v = c.value.split(" : ",1)
            rows.append({"Field":k,"Value":v})

        if rows:
            df=pd.DataFrame(rows)
            df.to_excel("export.xlsx",index=False)
            status.value="Excel export successful"
        else:
            status.value="No data to export"
        page.update()

    def load_history(e):
        history_list.controls.clear()
        for h in history_engine.load():
            history_list.controls.append(ft.Text(str(h)))
        page.update()

    file_picker = ft.FilePicker()

    def pick_file(e):
        file_picker.pick_files()

    def file_result(e: ft.FilePickerResultEvent):
        if e.files:
            path = e.files[0].path
            text = file_engine.read_file(path)
            input_box.value = text
            page.update()

    file_picker.on_result = file_result
    page.overlay.append(file_picker)

    page.add(
        ft.Row([
            ft.Column([
                input_box,
                ft.Row([
                    ft.ElevatedButton("Analyze Data", on_click=analyze_data),
                    ft.ElevatedButton("Upload File", on_click=pick_file),
                    ft.ElevatedButton("Export Excel", on_click=export_excel),
                    ft.ElevatedButton("History", on_click=load_history),
                ]),
                status,
                ft.Text("powered by KD", size=10)
            ], expand=True),

            ft.VerticalDivider(),

            ft.Column([
                ft.Text("Detected Fields", weight="bold"),
                field_list,
                ft.Divider(),
                ft.Text("History", weight="bold"),
                history_list
            ], expand=True)
        ])
    )

ft.app(target=main)
