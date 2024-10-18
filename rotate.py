# pip install pymupdf pillow pytesseract pdfplumber

import fitz  # PyMuPDF
from PIL import Image
import io
import pytesseract

# Function to detect whether the page is rotated (basic OCR-based detection)
def is_page_rotated(page_image):
    """
    This function uses pytesseract to detect text orientation. If the text appears
    to be sideways, the function returns True, indicating the page needs to be rotated.
    """
    # Convert PIL image to grayscale
    gray_image = page_image.convert("L")
    
    # Use pytesseract to detect orientation and rotation angle
    ocr_result = pytesseract.image_to_osd(gray_image)
    
    # Parse the rotation angle from the OCR result
    rotation_angle = int(ocr_result.split("\n")[1].split(":")[1].strip())

    # If the detected rotation is 90 or 270 degrees, the page is sideways and needs rotation
    if rotation_angle in [90, 270]:
        return True
    return False

# Function to rotate pages in the PDF
def rotate_pdf_pages(pdf_path, output_path):
    # Open the PDF document
    document = fitz.open(pdf_path)
    
    for page_num in range(len(document)):
        page = document[page_num]
        pix = page.get_pixmap()  # Render the page as an image
        
        # Convert to a PIL image
        img = Image.open(io.BytesIO(pix.tobytes()))
        
        # Check if the page is rotated
        if is_page_rotated(img):
            print(f"Rotating page {page_num + 1}")
            page.set_rotation(90)  # Rotate the page 90 degrees counter-clockwise
        
    # Save the new PDF with rotated pages
    document.save(output_path)
    document.close()
    print(f"Rotated PDF saved as {output_path}")

# Define the input PDF and output PDF paths
pdf_path = "/path/to/your/input.pdf"
output_path = "/path/to/your/output_rotated.pdf"

# Call the function to rotate pages and save the output
rotate_pdf_pages(pdf_path, output_path)

