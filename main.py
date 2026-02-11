 
# SINGLE EXE AI DATA ENTRY APP
import flet as ft
import openai, os, json
import pandas as pd
import tempfile, pdfplumber
from docx import Document
from PIL import Image
import pytesseract
from datetime import datetime

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise Exception("OPENAI_API_KEY not set in environment")
openai.api_key = OPENAI_API_KEY

SYSTEM_PROMPT = """
You are an AI data extraction engine.
Extract structured fields from any text.
Return JSON only.
Support multiple values per field.
Detect unknown fields too.
"""

history = []

def ai_extract(text):
    res = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"system","content":SYSTEM_PROMPT},
            {"role":"user","content":text}
        ],
        temperature=0
    )
    content = res["choices"][0]["message"]["content"]
    data = json.loads(content)
    norm = {}
    for k,v in data.items():
        norm[k] = v if isinstance(v,list) else [v]
    return norm

def extract_text_file(path):
    if path.endswith(".txt"):
        return open(path,encoding="utf-8",errors="ignore").read()
    if path.endswith(".pdf"):
        t=""
        with pdfplumber.open(path) as pdf:
            for p in pdf.pages:
                t+= (p.extract_text() or "")+"\n"
        return t
    if path.endswith(".docx"):
        d=Document(path)
        return "\n".join(p.text for p in d.paragraphs)
    return ""

def extract_text_image(path):
    return pytesseract.image_to_string(Image.open(path))

def main(page: ft.Page):
    page.title="AI Data Entry – The Automated Data Worker"
    extracted={}

    input_box=ft.TextField(label="Enter or paste input",multiline=True,min_lines=8,expand=True)
    output=ft.Column(scroll="auto")
    history_col=ft.Column(height=150,scroll="auto")

    def render():
        output.controls.clear()
        for f,vals in extracted.items():
            output.controls.append(ft.Text(f,weight="bold"))
            for v in vals:
                output.controls.append(ft.Text(f"• {v}"))
            output.controls.append(ft.Divider())
        page.update()

    def analyze_text(text):
        nonlocal extracted
        extracted=ai_extract(text)
        render()
        history.append({"time":datetime.now().strftime("%H:%M:%S"),"text":text,"data":extracted})
        if len(history)>10: history.pop(0)
        history_col.controls.clear()
        for h in history[::-1]:
            history_col.controls.append(ft.Text(f"{h['time']} - {h['text'][:40]}"))
        page.snack_bar=ft.SnackBar(ft.Text("Data analysis successfully completed"))
        page.snack_bar.open=True
        page.update()

    def analyze_click(e):
        if input_box.value.strip():
            analyze_text(input_box.value)

    def export_excel(e):
        if not extracted: return
        rows=[]
        for f,vals in extracted.items():
            for v in vals:
                rows.append({"Field":f,"Value":v})
        df=pd.DataFrame(rows)
        path=os.path.join(tempfile.gettempdir(),"ai_data.xlsx")
        df.to_excel(path,index=False)
        page.snack_bar=ft.SnackBar(ft.Text("Excel export successful"))
        page.snack_bar.open=True
        page.update()

    def pick_file(e: ft.FilePickerResultEvent):
        if not e.files: return
        path=e.files[0].path
        if path.lower().endswith((".png",".jpg",".jpeg")):
            text=extract_text_image(path)
        else:
            text=extract_text_file(path)
        input_box.value=text
        analyze_text(text)

    picker=ft.FilePicker(on_result=pick_file)
    page.overlay.append(picker)

    page.add(ft.Column([
        input_box,
        ft.Row([
            ft.ElevatedButton("Analyze Data",on_click=analyze_click),
            ft.ElevatedButton("Upload File",on_click=lambda _:picker.pick_files(allow_multiple=False)),
            ft.ElevatedButton("Export Excel",on_click=export_excel),
        ]),
        ft.Text("Extracted Fields",weight="bold"),
        output,
        ft.Text("History (Last 10)",weight="bold"),
        history_col,
        ft.Container(ft.Text("Powered by KD",size=10),alignment=ft.alignment.center)
    ],expand=True))

ft.app(target=main)
