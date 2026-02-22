import flet as ft
import os
import json
import pandas as pd
import pytesseract
from PIL import Image
import docx
import PyPDF2
import google.generativeai as genai
from datetime import datetime
import asyncio
import spacy
import en_core_web_sm
import sys

# 1. EXE kulla model path-ah kandupidikka indha logic venum
def get_model_path():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        # EXE kulla spaCy model indha folder-la thaan bundle aagi irukkum
        return os.path.join(base_path, "en_core_web_sm")
    return "en_core_web_sm"

# 2. Offline NLP Setup - Indha oru block mattum podhum
nlp = None
try:
    # First, internal bundle-la irundhu load panna try pannum
    model_path = get_model_path()
    nlp = spacy.load(model_path)
except Exception:
    try:
        # Fallback: direct import load
        nlp = en_core_web_sm.load()
    except Exception as e:
        print(f"NLP Model loading failed: {e}")

# 3. Gemini API Setup
API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

CORE_FIELDS = [
    "name", "age", "gender", "phone", "alternate_phone", "email", 
    "address", "city", "state", "country", "pincode", "dob", 
    "company", "designation", "qualification", "id_number", 
    "reference_name", "notes", "source", "custom_field"
]

class AIDataEntryProcessor:
    def __init__(self):
        self.history = []
        
    def extract_text(self, file_path, source_type):
        text = ""
        try:
            if source_type == "pdf":
                reader = PyPDF2.PdfReader(file_path)
                text = " ".join([page.extract_text() or "" for page in reader.pages])
            elif source_type == "docx":
                doc = docx.Document(file_path)
                text = " ".join([p.text for p in doc.paragraphs])
            elif source_type == "image":
                text = pytesseract.image_to_string(Image.open(file_path))
            elif source_type == "text":
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            else:
                text = file_path
        except Exception as e:
            text = f"Error reading file: {e}"
        return text

    def analyze_with_gemini(self, raw_text):
        prompt = (
            f"Extract the following fields from the text: {', '.join(CORE_FIELDS)}. "
            f"If a field is missing, use 'N/A'. Return only a valid JSON object.\n\n"
            f"Text: {raw_text}"
        )
        try:
            response = model.generate_content(prompt)
            # Remove markdown code blocks if AI adds them
            clean_json = response.text.strip().replace("```json", "").replace("```", "")
            data = json.loads(clean_json)
            return data
        except Exception as e:
            return {"error": f"AI Analysis failed: {e}"}

async def main(page: ft.Page):
    page.title = "AI Data Entry Automation Bot"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 800
    page.window_height = 600
    
    processor = AIDataEntryProcessor()
    all_extracted_data = []

    # UI Components
    status_text = ft.Text("Ready", color="blue")
    results_list = ft.Column(scroll="always", expand=True)

    async def on_file_result(e: ft.FilePickerResultEvent):
        if not e.files:
            return
        
        status_text.value = "Processing files... Please wait."
        status_text.color = "orange"
        await page.update_async()

        for picked_file in e.files:
            file_ext = os.path.splitext(picked_file.path)[1].lower()
            
            # Determine source type
            if file_ext == ".pdf": stype = "pdf"
            elif file_ext == ".docx": stype = "docx"
            elif file_ext in [".png", ".jpg", ".jpeg"]: stype = "image"
            else: stype = "text"

            # Process
            raw_content = processor.extract_text(picked_file.path, stype)
            ai_data = processor.analyze_with_gemini(raw_content)
            
            all_extracted_data.append(ai_data)
            
            # Show in UI
            name = ai_data.get("name", "Unknown")
            results_list.controls.append(
                ft.ListTile(
                    title=ft.Text(f"Processed: {name}"),
                    subtitle=ft.Text(f"Email: {ai_data.get('email', 'N/A')}"),
                    leading=ft.Icon(ft.icons.CHECK_CIRCLE, color="green")
                )
            )
        
        status_text.value = f"Finished processing {len(e.files)} files."
        status_text.color = "green"
        await page.update_async()

    def export_data(e):
        if not all_extracted_data:
            status_text.value = "No data to export!"
            status_text.color = "red"
            page.update()
            return
        
        df = pd.DataFrame(all_extracted_data)
        df.to_excel("Exported_Data.xlsx", index=False)
        status_text.value = "Data exported to Exported_Data.xlsx"
        page.update()

    file_picker = ft.FilePicker(on_result=on_file_result)
    page.overlay.append(file_picker)

    # Layout
    page.add(
        ft.Row([
            ft.Text("AI Builder Bot", size=30, weight="bold"),
            ft.Icon(ft.icons.AUTO_AWESOME, color="amber")
        ], alignment="center"),
        ft.Divider(),
        ft.Row([
            ft.ElevatedButton(
                "Upload Documents", 
                icon=ft.icons.UPLOAD_FILE, 
                on_click=lambda _: file_picker.pick_files(allow_multiple=True)
            ),
            ft.ElevatedButton(
                "Export to Excel", 
                icon=ft.icons.DOWNLOAD, 
                on_click=export_data
            )
        ], alignment="center"),
        status_text,
        ft.Text("Results:", weight="bold"),
        results_list
    )

if __name__ == "__main__":
    ft.app(target=main)
