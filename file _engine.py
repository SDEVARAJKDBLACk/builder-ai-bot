def read_file(path):
    if path.endswith(".txt"):
        return open(path,encoding="utf-8").read()

    if path.endswith(".docx"):
        from docx import Document
        doc = Document(path)
        return "\n".join([p.text for p in doc.paragraphs])

    if path.endswith(".pdf"):
        import pdfplumber
        text=""
        with pdfplumber.open(path) as pdf:
            for p in pdf.pages:
                text+=p.extract_text()+"\n"
        return text

    if path.endswith((".png",".jpg",".jpeg")):
        import pytesseract
        from PIL import Image
        return pytesseract.image_to_string(Image.open(path))

    return ""
