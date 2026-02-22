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
import spacy # Added missing import

# Gemini API Setup
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")) 
model = genai.GenerativeModel('gemini-1.5-flash')

# Offline NLP Setup Fix - Supports EXE bundling
nlp = None
try:
    # Try loading directly if bundled
    import en_core_web_sm
    nlp = en_core_web_sm.load()
except ImportError:
    # Fallback for local development
    try:
        nlp = spacy.load("en_core_web_sm")
    except:
        print("NLP Model not found. Basic extraction will continue.")

# ... (Rest of your AIDataEntryProcessor class and Flet UI code remains the same as your original file)

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
            text = f"Error: {e}"
        return text

    def analyze_with_gemini(self, raw_text, source_type):
        prompt = f"Extract fields {CORE_FIELDS} from this text: {raw_text}. Return ONLY JSON."
        try:
            response = model.generate_content(prompt)
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            for field in CORE_FIELDS:
                if field not in data: data[field] = "N/A"
            return data
        except Exception as e:
            return {"error": f"AI analysis failed: {e}"}

    def export_to_excel(self, data_list, filename="extracted_data.xlsx"):
        try:
            df = pd.DataFrame(data_list)
            df.to_excel(filename, index=False)
            return True, f"Saved to {filename}"
        except Exception as e:
            return False, f"Excel Error: {e}"

async def main(page: ft.Page):
    page.title = "AI Data Entry Automation"
    page.scroll = "adaptive"
    processor = AIDataEntryProcessor()
    extracted_data_list = []

    status_message = ft.Text("")
    output_text = ft.Column()

    async def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files:
            status_message.value = "Processing..."
            await page.update_async()
            for f in e.files:
                ext = os.path.splitext(f.path)[1].lower()
                stype = "image" if ext in [".png", ".jpg", ".jpeg"] else "text"
                if ext == ".pdf": stype = "pdf"
                elif ext == ".docx": stype = "docx"
                
                txt = processor.extract_text(f.path, stype)
                res = processor.analyze_with_gemini(txt, stype)
                extracted_data_list.append(res)
                output_text.controls.append(ft.Text(f"Extracted: {res.get('name', 'Unknown')}", color="green"))
            status_message.value = "Done!"
            await page.update_async()

    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)

    page.add(
        ft.ElevatedButton("Select Files", icon=ft.icons.UPLOAD_FILE, on_click=lambda _: file_picker.pick_files(allow_multiple=True)),
        status_message,
        output_text
    )

if __name__ == "__main__":
    ft.app(target=main)
