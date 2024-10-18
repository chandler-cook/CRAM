import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from io import BytesIO

# Function to detect if a page needs rotation based on content width
def is_page_rotated(page):
    pix = page.get_pixmap()  # Convert page to an image
    img = Image.open(BytesIO(pix.tobytes("ppm")))

    # Perform OCR (Optical Character Recognition) to detect layout
    ocr_result = pytesseract.image_to_osd(img, output_type=pytesseract.Output.DICT)
    rotation = int(ocr_result.get('rotate', 0))
    
    # If the page is rotated, this value will be something other than 0
    return rotation != 0

# Function to rotate the entire PDF based on content layout
def rotate_pdf_pages(pdf_path, output_path):
    document = fitz.open(pdf_path)
    
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        if is_page_rotated(page):
            print(f"Rotating page {page_num + 1}")
            page.set_rotation(90)  # Rotate page by 90 degrees
    
    # Save the modified PDF
    document.save(output_path)
    document.close()

# Main code to process the PDF
pdf_path = 'path/to/your/pdf/file'  # Replace with the path to your PDF file
output_path = 'path/to/output/file'  # Replace with the desired output path

rotate_pdf_pages(pdf_path, output_path)
