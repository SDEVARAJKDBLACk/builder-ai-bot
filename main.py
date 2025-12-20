import flet as ft
import re
import pandas as pd
from datetime import datetime

def extract_entities(text: str):
    data = {}

    patterns = {
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "phone": r"\b\d{10}\b",
        "amount": r"\b\d+(\.\d{1,2})?\b",
        "pincode": r"\b\d{6}\b"
    }

    for key, pattern in patterns.items():
        match = re.findall(pattern, text)
        if match:
            data[key] = ", ".join(match)

    words = text.split()
    for w in words:
        if w.istitle() and len(w) > 3:
            data.setdefault("names", "")
            data["names"] += w + " "

    return data


def main(page: ft.Page):
    page.title = "AI Data Entry Pro"
    page.window_width = 900
    page.window_height = 600
    page.theme_mode = ft.ThemeMode.LIGHT

    input_box = ft.TextField(
        label="Enter raw data (text / notes / phrases)",
        multiline=True,
        min_lines=5,
        expand=True
    )

    output_table = ft.DataTable(columns=[], rows=[])

    status = ft.Text()

    def analyze_data(e):
        raw_text = input_box.value.strip()
        if not raw_text:
            status.value = "Please enter some data"
            page.update()
            return

        extracted = extract_entities(raw_text)

        if not extracted:
            status.value = "No structured data detected"
            page.update()
            return

        columns = [ft.DataColumn(ft.Text(k)) for k in extracted.keys()]
        values = [ft.DataCell(ft.Text(v)) for v in extracted.values()]

        output_table.columns = columns
        output_table.rows = [ft.DataRow(cells=values)]

        status.value = "Data analyzed successfully"
        page.update()

    def export_excel(e):
        if not output_table.rows:
            status.value = "No data to export"
            page.update()
            return

        headers = [col.label.value for col in output_table.columns]
        values = [cell.content.value for cell in output_table.rows[0].cells]

        df = pd.DataFrame([values], columns=headers)
        filename = f"ai_data_entry_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(filename, index=False)

        status.value = f"Excel saved: {filename}"
        page.update()

    page.add(
        ft.Column(
            expand=True,
            controls=[
                ft.Text("AI Data Entry – Smart Automated Data Worker", size=22, weight="bold"),
                input_box,
                ft.Row(
                    controls=[
                        ft.ElevatedButton("Analyze Data", on_click=analyze_data),
                        ft.ElevatedButton("Export to Excel", on_click=export_excel),
                    ]
                ),
                output_table,
                status,
                ft.Text("Powered by KD", italic=True)
            ]
        )
    )

ft.app(target=main, view=ft.AppView.WINDOW)
