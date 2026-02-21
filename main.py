import flet as ft
import os
import json
import spacy
import pandas as pd
import pytesseract
from PIL import Image
import docx
import PyPDF2
import google.generativeai as genai
from datetime import datetime
import asyncio # For async operations in Flet

# --- CONFIGURATION (Move to a separate config.py or .env in production) ---
# Tesseract path (Windows users - uncomment and set if not in PATH)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Gemini API Setup
# genai.configure(api_key="YOUR_GEMINI_API_KEY") # Replace with your actual key
# Using a placeholder for now, make sure to replace it
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")) 
model = genai.GenerativeModel('gemini-1.5-flash')

# Offline NLP Setup
try:
    nlp = spacy.load("en_core_web_sm")
except:
    # Ensure spaCy model is downloaded if not present
    print("Downloading spaCy model 'en_core_web_sm'...")
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# --- CORE AI DATA ENTRY LOGIC ---
CORE_FIELDS = [
    "name", "age", "gender", "phone", "alternate_phone", "email", 
    "address", "city", "state", "country", "pincode", "dob", 
    "company", "designation", "qualification", "id_number", 
    "reference_name", "notes", "source", "custom_field"
]

class AIDataEntryProcessor:
    def __init__(self):
        self.history = [] # For learning loop or history tracking
        
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
            else: # For direct user input
                text = file_path # In this case, file_path is the raw text itself
        except Exception as e:
            print(f"Error extracting text from {file_path}: {e}")
            text = f"Error during text extraction: {e}"
        return text

    def analyze_with_gemini(self, raw_text, source_type):
        prompt = f"""
        Act as an Advanced Data Entry Specialist. Extract information from the provided text.
        
        RULES:
        1. Extract exactly these fields: {', '.join(CORE_FIELDS)}.
        2. If a field is not found or not applicable, return "N/A" for that field's value.
        3. 'source' should be '{source_type}'.
        4. If you find extra important data not explicitly covered by the core fields, include it as key-value pairs within the 'custom_field' dictionary. If no custom fields are found, set 'custom_field' to "N/A".
        5. Output MUST be a valid JSON object only. Do NOT include any introductory or concluding text outside the JSON.
        
        TEXT TO ANALYZE:
        {raw_text}
        """
        
        try:
            response = model.generate_content(prompt)
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            
            # Simple validation to ensure it's a JSON
            data = json.loads(clean_json)
            
            # Ensure all CORE_FIELDS are present, add N/A if missing
            for field in CORE_FIELDS:
                if field not in data:
                    data[field] = "N/A"
            
            self.history.append({"text": raw_text, "result": data})
            return data
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print(f"Raw response from Gemini: {response.text}")
            return {"error": "Failed to parse AI response", "details": response.text}
        except Exception as e:
            print(f"Error during Gemini analysis: {e}")
            return {"error": f"AI analysis failed: {e}"}

    def export_to_excel(self, data_list, filename="extracted_data.xlsx"):
        if not data_list:
            return False, "No data to export."
        try:
            df = pd.DataFrame(data_list)
            df.to_excel(filename, index=False)
            return True, f"Data exported to {filename}"
        except Exception as e:
            return False, f"Error exporting to Excel: {e}"

# --- FLET UI APPLICATION ---
async def main(page: ft.Page):
    page.title = "AI Data Entry Automation (Flet)"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_width = 800
    page.window_height = 700
    page.window_resizable = True

    processor = AIDataEntryProcessor()
    extracted_data_list = [] # To store all extracted data for Excel export

    # UI Elements
    file_picker = ft.FilePicker(on_result=lambda e: asyncio.run(on_file_picked(e)))
    page.overlay.append(file_picker)

    output_text = ft.Column(scroll=ft.ScrollMode.ADAPTIVE)
    progress_bar = ft.ProgressBar(width=400, visible=False)
    status_message = ft.Text("")

    async def process_file(file_path, source_type):
        status_message.value = f"Processing {os.path.basename(file_path)}..."
        progress_bar.visible = True
        await page.update_async()

        text = processor.extract_text(file_path, source_type)
        if "Error" in text:
            output_text.controls.append(ft.Text(f"Error: {text}", color=ft.colors.RED_500))
            output_text.controls.append(ft.Divider())
            status_message.value = "Error during text extraction."
            progress_bar.visible = False
            await page.update_async()
            return
        
        # Display raw text if it's not too long
        output_text.controls.append(
            ft.ExpansionTile(
                title=ft.Text(f"Raw Text from {os.path.basename(file_path)} ({source_type})"),
                controls=[
                    ft.Container(
                        ft.Text(text[:1000] + "..." if len(text) > 1000 else text, size=12, selectable=True),
                        padding=10,
                        border_radius=5,
                        border=ft.border.all(1, ft.colors.BLUE_GREY_100),
                        width=page.window_width * 0.9,
                        height=150,
                        scroll=ft.ScrollMode.ADAPTIVE
                    )
                ]
            )
        )

        analysis_result = processor.analyze_with_gemini(text, source_type)

        if "error" in analysis_result:
            output_text.controls.append(ft.Text(f"AI Error: {analysis_result['error']}", color=ft.colors.RED_500))
            if "details" in analysis_result:
                output_text.controls.append(ft.Text(f"Details: {analysis_result['details']}", color=ft.colors.RED_300))
            output_text.controls.append(ft.Divider())
        else:
            extracted_data_list.append(analysis_result)
            output_text.controls.append(
                ft.ExpansionTile(
                    title=ft.Text(f"Extracted Data from {os.path.basename(file_path)}"),
                    controls=[
                        ft.Column([
                            ft.Text(f"{k}: {v}", selectable=True) 
                            for k, v in analysis_result.items()
                        ])
                    ]
                )
            )
            output_text.controls.append(ft.Divider())
        
        status_message.value = f"Finished processing {os.path.basename(file_path)}."
        progress_bar.visible = False
        await page.update_async()

    async def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files:
            for f in e.files:
                file_path = f.path
                file_extension = os.path.splitext(file_path)[1].lower()
                source_type = "text"
                if file_extension == ".pdf":
                    source_type = "pdf"
                elif file_extension == ".docx":
                    source_type = "docx"
                elif file_extension in [".png", ".jpg", ".jpeg"]:
                    source_type = "image"
                
                await process_file(file_path, source_type)
        else:
            status_message.value = "No file selected."
            await page.update_async()

    async def upload_file_button_clicked(e):
        await file_picker.pick_files_async(
            allow_multiple=True,
            allowed_extensions=["txt", "pdf", "docx", "png", "jpg", "jpeg"]
        )
    
    user_input_field = ft.TextField(
        label="Enter raw text here for analysis",
        multiline=True,
        min_lines=3,
        max_lines=10,
        width=page.window_width * 0.9,
    )

    async def process_user_input(e):
        raw_text = user_input_field.value.strip()
        if not raw_text:
            status_message.value = "Please enter some text."
            await page.update_async()
            return
        
        status_message.value = "Processing user input..."
        progress_bar.visible = True
        await page.update_async()

        analysis_result = processor.analyze_with_gemini(raw_text, "user_input")
        
        if "error" in analysis_result:
            output_text.controls.append(ft.Text(f"AI Error: {analysis_result['error']}", color=ft.colors.RED_500))
            if "details" in analysis_result:
                output_text.controls.append(ft.Text(f"Details: {analysis_result['details']}", color=ft.colors.RED_300))
            output_text.controls.append(ft.Divider())
        else:
            extracted_data_list.append(analysis_result)
            output_text.controls.append(
                ft.ExpansionTile(
                    title=ft.Text(f"Extracted Data from User Input"),
                    controls=[
                        ft.Column([
                            ft.Text(f"{k}: {v}", selectable=True) 
                            for k, v in analysis_result.items()
                        ])
                    ]
                )
            )
            output_text.controls.append(ft.Divider())
        
        user_input_field.value = "" # Clear after processing
        status_message.value = "Finished processing user input."
        progress_bar.visible = False
        await page.update_async()

    async def export_excel_button_clicked(e):
        if not extracted_data_list:
            status_message.value = "No data to export to Excel."
            await page.update_async()
            return

        success, msg = processor.export_to_excel(extracted_data_list, "extracted_ai_data.xlsx")
        status_message.value = msg
        if success:
            status_message.color = ft.colors.GREEN_500
        else:
            status_message.color = ft.colors.RED_500
        await page.update_async()
        

    page.add(
        ft.AppBar(
            title=ft.Text("AI Data Entry Automation"),
            center_title=True,
            bgcolor=ft.colors.BLUE_GREY_700,
            color=ft.colors.WHITE
        ),
        ft.Container(
            content=ft.Column(
                [
                    ft.Text("Upload files (PDF, Word, Image, Text) or enter raw text:", size=16),
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "Upload Files",
                                icon=ft.icons.UPLOAD_FILE,
                                on_click=upload_file_button_clicked,
                            ),
                            ft.ElevatedButton(
                                "Export All to Excel",
                                icon=ft.icons.DOWNLOAD,
                                on_click=export_excel_button_clicked,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Divider(),
                    user_input_field,
                    ft.ElevatedButton(
                        "Analyze Entered Text",
                        icon=ft.icons.ANALYTICS,
                        on_click=process_user_input,
                    ),
                    ft.Divider(),
                    progress_bar,
                    status_message,
                    ft.Text("Extraction Results:", size=16),
                    ft.Container(
                        output_text,
                        border=ft.border.all(1, ft.colors.BLUE_GREY_200),
                        border_radius=5,
                        padding=10,
                        height=300,
                        expand=True,
                        scroll=ft.ScrollMode.ADAPTIVE
                    )
                ]
            ),
            padding=20,
            expand=True
        )
    )
    # Initial page update
    await page.update_async()


if __name__ == "__main__":
    ft.app(target=main)

