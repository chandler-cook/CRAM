# pip install pytesseract fitz Pillow
import fitz  # PyMuPDF
import pytesseract
from pytesseract import Output
from PIL import Image
import os

# Function to set a default DPI for the image before processing with Tesseract
def ensure_dpi(img):
    # Ensure the DPI is set to 300 for proper OCR
    img = img.convert('RGB')
    img.save("/tmp/temp_img.png", dpi=(300, 300))
    img = Image.open("/tmp/temp_img.png")
    return img

# Function to detect if a page needs to be rotated
def is_page_rotated(img):
    # Perform OCR to detect text orientation
    img = ensure_dpi(img)  # Ensure proper DPI
    ocr_result = pytesseract.image_to_osd(img, output_type=Output.DICT)
    rotation = ocr_result['rotate']
    return rotation

# Function to check if the page contains a table (heuristic based on visual layout)
def contains_table(page):
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    # Perform OCR to extract text data
    img = ensure_dpi(img)  # Ensure proper DPI
    ocr_data = pytesseract.image_to_data(img, output_type=Output.DICT)
    text_count = len(ocr_data['text'])
    
    # Heuristic: Check for table-like structures
    table_like_threshold = 0.6  # Adjust this threshold based on the document layout
    confidence_threshold = 60  # Confidence threshold for the OCR detection
    
    table_lines = sum([1 for conf in ocr_data['conf'] if int(conf) > confidence_threshold])
    
    if table_lines / text_count < table_like_threshold:
        return True
    return False

# Function to rotate pages in the PDF
def rotate_pdf_pages(pdf_path, output_path):
    # Open the PDF
    document = fitz.open(pdf_path)
    
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Detect if the page is rotated incorrectly
        rotation = is_page_rotated(img)
        
        # Check for table structures
        if contains_table(page) or rotation != 0:
            print(f"Rotating page {page_num+1} by {rotation} degrees")
            page.set_rotation(90)  # Rotate by 90 degrees or based on your needs
    
    # Save the output PDF
    document.save(output_path)
    document.close()

# Main code to process the PDF
pdf_path = 'path/to/your/pdf/file'  # Replace with the path to your PDF file
output_path = 'path/to/output/file'  # Replace with the desired output path

rotate_pdf_pages(pdf_path, output_path)
