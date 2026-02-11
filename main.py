import flet as ft
import os, sys, json, re
from dotenv import load_dotenv
import pandas as pd
from openai import OpenAI
import pdfplumber
from docx import Document
from PIL import Image
import pytesseract

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    print("❌ OPENAI_API_KEY not set")
    sys.exit()

client = OpenAI(api_key=API_KEY)

HISTORY_FILE = "history.json"

FIELDS = [
    "name","age","gender","phone","email","address","city","pincode",
    "product","price","amount","salary","company","date","id_number",
    "account","bank","website","notes","other"
]

def ai_extract(text):
    prompt = f"""
Extract structured fields from this text.
Detect ALL possible fields automatically.
Return JSON only.

Text:
{text}
"""
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}]
    )
    return json.loads(res.choices[0].message.content)

def read_file(path):
    if path.endswith(".pdf"):
        text=""
        with pdfplumber.open(path) as pdf:
            for p in pdf.pages:
                text+=p.extract_text() or ""
        return text
    elif path.endswith(".docx"):
        doc=Document(path)
        return "\n".join([p.text for p in doc.paragraphs])
    elif path.endswith((".png",".jpg",".jpeg")):
        return pytesseract.image_to_string(Image.open(path))
    else:
        with open(path,"r",encoding="utf-8",errors="ignore") as f:
            return f.read()

def save_history(data):
    hist=[]
    if os.path.exists(HISTORY_FILE):
        hist=json.load(open(HISTORY_FILE))
    hist.insert(0,data)
    hist=hist[:10]
    json.dump(hist,open(HISTORY_FILE,"w"),indent=2)

def main(page: ft.Page):
    page.title="AI Data Entry"
    page.theme_mode="dark"

    input_box = ft.TextField(label="Enter or paste text / upload file", multiline=True, min_lines=6, expand=True)

    result_table = ft.DataTable(columns=[
        ft.DataColumn(ft.Text("Field")),
        ft.DataColumn(ft.Text("Value"))
    ], rows=[])

    def analyze(e):
        text=input_box.value
        if not text.strip():
            page.snack_bar=ft.SnackBar(ft.Text("Enter some text"))
            page.snack_bar.open=True
            page.update()
            return
        data=ai_extract(text)
        save_history(data)
        rows=[]
        for k,v in data.items():
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(k))),
                ft.DataCell(ft.Text(str(v)))
            ]))
        result_table.rows=rows
        page.snack_bar=ft.SnackBar(ft.Text("✅ Data analysis successfully"))
        page.snack_bar.open=True
        page.update()

    def export_excel(e):
        rows=[]
        for r in result_table.rows:
            rows.append({
                "field": r.cells[0].content.value,
                "value": r.cells[1].content.value
            })
        df=pd.DataFrame(rows)
        df.to_excel("output.xlsx",index=False)
        page.snack_bar=ft.SnackBar(ft.Text("✅ Excel exported successfully"))
        page.snack_bar.open=True
        page.update()

    def pick_file(e: ft.FilePickerResultEvent):
        if e.files:
            text=read_file(e.files[0].path)
            input_box.value=text
            page.update()

    file_picker=ft.FilePicker(on_result=pick_file)
    page.overlay.append(file_picker)

    page.add(
        ft.Text("AI Data Entry System",size=28,weight="bold"),
        input_box,
        ft.Row([
            ft.ElevatedButton("Analyze",on_click=analyze),
            ft.ElevatedButton("Export Excel",on_click=export_excel),
            ft.ElevatedButton("Upload File",on_click=lambda e: file_picker.pick_files())
        ]),
        result_table,
        ft.Text("Powered by KD",size=10,opacity=0.5)
    )

ft.app(target=main)
