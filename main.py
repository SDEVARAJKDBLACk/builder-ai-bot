
import flet as ft
import re
import pandas as pd
from datetime import datetime

def extract_entities(text: str):
    data = {}

    patterns = {
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "phone": r"\b\d{10}\b",
        "pincode": r"\b\d{6}\b",
        "amount": r"\b\d+(\.\d{1,2})?\b",
    }

    for key, pattern in patterns.items():
        found = re.findall(pattern, text)
        if found:
            data[key] = ", ".join(found)

    names = []
    for word in text.split():
        if word.istitle() and len(word) > 3:
            names.append(word)

    if names:
        data["names"] = " ".join(names)

    return data


def main(page: ft.Page):
    page.title = "AI Data Entry Pro"
    page.window_width = 900
    page.window_height = 600

    input_box = ft.TextField(
        label="Enter raw input (text / notes / phrases)",
        multiline=True,
        min_lines=5,
        expand=True
    )

    table = ft.DataTable(columns=[], rows=[])
    status = ft.Text()

    def analyze(e):
        text = input_box.value.strip()
        if not text:
            status.value = "Please enter input"
            page.update()
            return

        data = extract_entities(text)
        if not data:
            status.value = "No structured data detected"
            page.update()
            return

        table.columns = [ft.DataColumn(ft.Text(k)) for k in data.keys()]
        table.rows = [
            ft.DataRow(
                cells=[ft.DataCell(ft.Text(v)) for v in data.values()]
            )
        ]

        status.value = "Data analyzed successfully"
        page.update()

    def export_excel(e):
        if not table.rows:
            status.value = "No data to export"
            page.update()
            return

        headers = [c.label.value for c in table.columns]
        values = [cell.content.value for cell in table.rows[0].cells]

        df = pd.DataFrame([values], columns=headers)
        filename = f"ai_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(filename, index=False)

        status.value = f"Excel saved: {filename}"
        page.update()

    page.add(
        ft.Column(
            expand=True,
            controls=[
                ft.Text("AI Data Entry – Smart Automated Data Worker", size=22, weight="bold"),
                input_box,
                ft.Row([
                    ft.ElevatedButton("Analyze", on_click=analyze),
                    ft.ElevatedButton("Export Excel", on_click=export_excel),
                ]),
                table,
                status,
                ft.Text("Powered by KD", italic=True),
            ]
        )
    )

# ✅ FIXED ENTRY POINT
ft.app(target=main)
