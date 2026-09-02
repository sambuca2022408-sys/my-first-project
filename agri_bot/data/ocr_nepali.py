import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import os

# Set Tesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_pdf(pdf_path, output_file="output_nepali.txt"):
    doc = fitz.open(pdf_path)
    all_text = []
    
    print(f"Total pages: {len(doc)}")
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        
        # Nepali + English OCR
        text = pytesseract.image_to_string(img, lang='nep+eng')
        all_text.append(f"\n--- Page {page_num + 1} ---\n")
        all_text.append(text)
        print(f"Page {page_num + 1} done")
    
    # Save to txt file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(all_text))
    
    print(f"DONE! Check {output_file}")

if __name__ == "__main__":
    pdf_file = r"Norms Book 2080_1709448574.pdf"
    extract_text_from_pdf(pdf_file)