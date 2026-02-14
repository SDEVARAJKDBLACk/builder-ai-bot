import flet as ft
import re, os, json
from datetime import datetime
import pandas as pd

# ---------- SAFE IMPORTS ----------
def safe_import(name):
    try:
        return __import__(name)
    except:
        return None

ai_engine = safe_import("ai_engine")
file_engine = safe_import("file_engine")
learning_engine = safe_import("learning_engine")

# ---------- CORE FIELDS ----------
CORE_FIELDS = [
    "Name","Age","Gender","Phone","Email","Address","City","State","Pincode","Country",
    "Product","Category","Company","Amount","Price","Salary","Date","OrderID","AccountNumber","Notes"
]

history_data = []
dynamic_fields = set()

# ---------- BASIC PRE-PARSER ----------
def basic_extract(text):
    data = {}
    patterns = {
        "Phone": r"\b\d{10}\b",
        "Email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}",
        "Pincode": r"\b\d{6}\b",
        "Amount": r"\b\d+(?:\.\d{1,2})?\b",
        "Date": r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"
    }
    for k,p in patterns.items():
        m = re.findall(p,text)
        if m: data[k] = ", ".join(m)
    return data

# ---------- AI PIPELINE ----------
def ai_pipeline(text):
    data = {}

    # Layer 1: Basic extraction
    data.update(basic_extract(text))

    # Layer 2: AI semantic extraction
    if ai_engine:
        try:
            ai_data = ai_engine.semantic_extract(text)
            for k,v in ai_data.items():
                data[k] = v
        except:
            pass

    # Layer 3: Learning system
    if learning_engine:
        try:
            learning_engine.learn_fields(data)
        except:
            pass

    # Dynamic fields
    for k in data.keys():
        if k not in CORE_FIELDS:
            dynamic_fields.add(k)

    return data

# ---------- UI ----------
def main(page: ft.Page):
    page.title = "AI Data Entry – Automated Data Worker"
    page.scroll = ft.ScrollMode.AUTO

    input_box = ft.TextField(label="Enter / Paste Text or Upload File Content", multiline=True, min_lines=6)

    status = ft.Text("Status: Ready", color="green")

    history_list = ft.ListView(expand=True)

    table = ft.DataTable(columns=[], rows=[])

    def rebuild_columns():
        all_fields = CORE_FIELDS + list(dynamic_fields)
        table.columns = [ft.DataColumn(ft.Text(f)) for f in all_fields]

    def add_row(data):
        all_fields = CORE_FIELDS + list(dynamic_fields)
        cells = [ft.DataCell(ft.Text(str(data.get(f,"")))) for f in all_fields]
        table.rows.append(ft.DataRow(cells=cells))

    def analyze(e):
        text = input_box.value.strip()
        if not text:
            status.value = "Status: No input"
            page.update()
            return

        result = ai_pipeline(text)
        history_data.append(result)

        rebuild_columns()
        add_row(result)

        history_list.controls.insert(0, ft.Text(json.dumps(result, ensure_ascii=False)))
        if len(history_list.controls) > 10:
            history_list.controls.pop()

        status.value = "Status: Data analysis successfully"
        page.update()

    def export_excel(e):
        if not history_data:
            status.value = "Status: No data"
            page.update()
            return

        all_fields = CORE_FIELDS + list(dynamic_fields)
        df = pd.DataFrame(history_data)
        df = df.reindex(columns=all_fields)
        fname = f"ai_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(fname, index=False)

        status.value = f"Status: Excel export successful ({fname})"
        page.update()

    page.add(
        ft.Text("AI Data Entry – Automated Data Worker", size=22, weight="bold"),
        input_box,
        ft.Row([
            ft.ElevatedButton("Analyze Data", on_click=analyze),
            ft.ElevatedButton("Export Excel", on_click=export_excel)
        ]),
        ft.Text("Extracted Data"),
        table,
        ft.Text("History (Last 10)"),
        history_list,
        status,
        ft.Text("Powered by KD", size=10, opacity=0.6)
    )

ft.app(target=main)
