
from flet import *
import requests

def main(page: Page):
    page.title = "AI Data Entry - Automated Data Worker (Phase 3)"
    input_box = TextField(label="Enter any data / paste text / raw data", multiline=True, expand=True)
    history = Column(scroll=True)
    output = Column(scroll=True)

    def analyze(e):
        try:
            r = requests.post("http://127.0.0.1:8000/analyze", json={"text": input_box.value})
            data = r.json()
            output.controls.clear()
            history.controls.append(Text(input_box.value[:60]))
            for k,v in data.get("fields", {}).items():
                output.controls.append(Text(f"{k} : {v}"))
            page.snack_bar = SnackBar(Text("AI analysis completed"))
            page.snack_bar.open = True
            page.update()
        except Exception as ex:
            output.controls.append(Text(f"Error: {ex}"))
            page.update()

    page.add(
        Column([
            input_box,
            ElevatedButton("Analyze", on_click=analyze),
            Text("History"),
            history,
            Text("Detected Fields"),
            output,
            Text("Powered by KD", size=10)
        ])
    )

app(target=main)
