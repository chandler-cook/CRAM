# pip install pymupdf pillow pytesseract pdfplumber

import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

# Function to check if a page needs rotation
def is_page_rotated(page):
    # Convert the page into an image
    pix = page.get_pixmap()
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    
    # Perform OCR to detect orientation
    try:
        ocr_result = pytesseract.image_to_osd(img)
        if "Rotate: 90" in ocr_result or "Rotate: 270" in ocr_result:
            return True
    except Exception as e:
        print(f"Error detecting rotation: {e}")
        return False
    return False

# Function to rotate pages in the PDF
def rotate_pdf_pages(pdf_path, output_path):
    doc = fitz.open(pdf_path)
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        
        if is_page_rotated(page):
            page.set_rotation(90)  # Rotate the page clockwise
            print(f"Rotating page {page_num + 1}")
    
    # Save the rotated PDF
    doc.save(output_path)
    doc.close()
    print(f"Saved rotated PDF as {output_path}")

# Specify input and output PDF file paths
pdf_path = '/mnt/data/Challenge_Smaller_System_Under_Evaluation_Rev_0.1.pdf'
output_path = 'rotated_output.pdf'

# Rotate and save the PDF
rotate_pdf_pages(pdf_path, output_path)
