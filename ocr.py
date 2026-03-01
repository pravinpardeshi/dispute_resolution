
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

def extract_text_from_pdf(pdf_path: str):
    images = convert_from_path(pdf_path)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img)
    return text
