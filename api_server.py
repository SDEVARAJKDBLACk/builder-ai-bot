
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import openai, os
import pytesseract
from PIL import Image
import io

openai.api_key = os.getenv("OPENAI_API_KEY")
app = FastAPI()

class Data(BaseModel):
    text: str

@app.post("/analyze")
def analyze(data: Data):
    prompt = f"""You are an AI data extraction engine.
Detect unlimited fields, ensure 20 core fields if available,
return pure JSON only.
Input:
{data.text}
"""
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}]
        )
        content = resp.choices[0].message.content
        return {"fields": {"AI_Output": content}}
    except Exception as e:
        return {"fields": {"error": str(e)}}

@app.post("/ocr")
async def ocr(file: UploadFile = File(...)):
    img = Image.open(io.BytesIO(await file.read()))
    text = pytesseract.image_to_string(img)
    return {"text": text}
