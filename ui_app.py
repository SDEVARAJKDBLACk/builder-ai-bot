
import flet as ft
import requests

API_URL = "http://127.0.0.1:8000/process"

def main(page: ft.Page):
    page.title = "AI Data Entry – Automated Data Worker"

    input_box = ft.TextField(label="Enter Data", multiline=True, height=200)
    output = ft.Text()

    def submit(e):
        try:
            r = requests.post(API_URL, json={"text": input_box.value})
            output.value = str(r.json())
        except Exception as ex:
            output.value = str(ex)
        page.update()

    page.add(input_box, ft.ElevatedButton("Process", on_click=submit), output)

ft.app(target=main)
