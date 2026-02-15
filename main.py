import flet as ft
import sys
import os
import pandas as pd
from datetime import datetime

# SAFE EXIT
def safe_exit():
    sys.exit()

# -------- CORE DATA ENGINE ----------
class DataEngine:
    def __init__(self):
        self.history = []

    def detect_fields(self, text):
        base_fields = [
            "Name","Age","Gender","Phone","Email","Address",
            "DOB","ID","Amount","Date","Company","City",
            "State","Country","Zip","Account","IFSC","PAN",
            "Aadhar","Remarks"
        ]

        detected = []
        for f in base_fields:
            if f.lower() in text.lower():
                detected.append(f)

        # unlimited dynamic detection
        words = text.split()
        for w in words:
            if w.istitle() and w not in detected:
                detected.append(w)

        return list(set(detected))

    def export_excel(self, data):
        df = pd.DataFrame(data)
        filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(filename, index=False)
        return filename


engine = DataEngine()

# -------- UI LAYER ----------
def main(page: ft.Page):
    page.title = "AI Data Entry System"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1200
    page.window_height = 750

    title = ft.Text("AI DATA ENTRY APPLICATION", size=24, weight="bold")

    input_box = ft.TextField(
        label="Paste text / extracted content here",
        multiline=True,
        height=200
    )

    fields_view = ft.Column(scroll="auto")

    history_view = ft.Column(scroll="auto", height=150)

    def detect_click(e):
        fields_view.controls.clear()
        text = input_box.value
        fields = engine.detect_fields(text)

        for f in fields:
            fields_view.controls.append(
                ft.TextField(label=f)
            )

        engine.history.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "fields": fields
        })

        history_view.controls.append(
            ft.Text(f"[{engine.history[-1]['time']}] {fields}")
        )

        page.update()

    def export_click(e):
        data = {}
        for c in fields_view.controls:
            data[c.label] = c.value

        file = engine.export_excel([data])
        page.snack_bar = ft.SnackBar(ft.Text(f"Excel Exported: {file}"))
        page.snack_bar.open = True
        page.update()

    detect_btn = ft.ElevatedButton("Detect Fields", on_click=detect_click)
    export_btn = ft.ElevatedButton("Export Excel", on_click=export_click)

    layout = ft.Column([
        title,
        input_box,
        ft.Row([detect_btn, export_btn]),
        ft.Text("Detected Fields:"),
        fields_view,
        ft.Text("History:"),
        history_view
    ])

    page.add(layout)

ft.app(target=main)
