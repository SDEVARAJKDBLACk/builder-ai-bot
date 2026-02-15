import flet as ft
import pandas as pd
from datetime import datetime

# ==============================
# AI Data Entry – Automated Data Worker
# STABLE CORE VERSION
# ==============================

HISTORY = []

class CoreEngine:
    def __init__(self):
        self.history = []

    def simple_field_detect(self, text: str):
        words = text.replace(",", " ").replace("\n", " ").split()
        fields = []

        for w in words:
            if len(w) > 2 and w.isalpha():
                fields.append(w.capitalize())

        return list(set(fields))

    def export_excel(self, data_dict: dict):
        df = pd.DataFrame([data_dict])
        filename = f"ai_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(filename, index=False)
        return filename


engine = CoreEngine()

def main(page: ft.Page):
    page.title = "AI Data Entry – Automated Data Worker"
    page.window_width = 1200
    page.window_height = 750

    title = ft.Text("AI Data Entry – Automated Data Worker", size=24, weight="bold")

    input_box = ft.TextField(
        label="Paste any data / text here",
        multiline=True,
        height=200,
        expand=True
    )

    detected_fields_view = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    history_view = ft.Column(scroll=ft.ScrollMode.AUTO, height=150)

    status_text = ft.Text("")

    def analyze_data(e):
        detected_fields_view.controls.clear()
        text = input_box.value

        if not text.strip():
            status_text.value = "❌ No input data"
            page.update()
            return

        fields = engine.simple_field_detect(text)

        for f in fields:
            detected_fields_view.controls.append(ft.TextField(label=f))

        HISTORY.insert(0, fields)
        if len(HISTORY) > 10:
            HISTORY.pop()

        history_view.controls.clear()
        for i, h in enumerate(HISTORY):
            history_view.controls.append(ft.Text(f"{i+1}. {h}"))

        status_text.value = "✅ Data analyzed"
        page.update()

    def export_excel(e):
        data = {}
        for c in detected_fields_view.controls:
            data[c.label] = c.value

        if not data:
            status_text.value = "❌ No data to export"
            page.update()
            return

        file = engine.export_excel(data)
        status_text.value = f"✅ Excel exported: {file}"
        page.update()

    def clear_all(e):
        input_box.value = ""
        detected_fields_view.controls.clear()
        status_text.value = "🧹 Cleared"
        page.update()

    analyze_btn = ft.ElevatedButton("Analyze", on_click=analyze_data)
    export_btn = ft.ElevatedButton("Export Excel", on_click=export_excel)
    clear_btn = ft.ElevatedButton("Clear", on_click=clear_all)

    page.add(
        ft.Column([
            title,
            input_box,
            ft.Row([analyze_btn, export_btn, clear_btn]),
            status_text,
            ft.Divider(),
            ft.Text("Detected Fields", size=16, weight="bold"),
            detected_fields_view,
            ft.Divider(),
            ft.Text("History (Last 10)", size=16, weight="bold"),
            history_view
        ], expand=True)
    )

# 🔥 IMPORTANT FIX:
# Use WEB_BROWSER mode to avoid flet_desktop crash
ft.app(target=main, view=ft.WEB_BROWSER)
