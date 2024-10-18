# pip install pytesseract fitz Pillow
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

# Function to detect if a page's content is rotated based on Tesseract's OSD (Orientation and Script Detection)
def is_page_rotated(page):
    # Render page to image
    pix = page.get_pixmap()
    img_data = pix.tobytes("png")
    
    # Convert image data to PIL image
    img = Image.open(io.BytesIO(img_data))
    
    # Use Tesseract to detect orientation (OSD mode)
    ocr_result = pytesseract.image_to_osd(img)
    
    # Check for rotation angle in OSD result
    rotation_angle = int(ocr_result.split("\n")[2].split(":")[1].strip())
    return rotation_angle != 0, rotation_angle

# Function to rotate pages based on Tesseract's detected orientation
def rotate_pdf_pages(pdf_path, output_path):
    # Open the PDF
    document = fitz.open(pdf_path)
    
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        
        # Check if the page content is rotated
        rotated, angle = is_page_rotated(page)
        
        if rotated:
            print(f"Rotating page {page_num + 1} by {angle} degrees")
            page.set_rotation(angle)  # Rotate by the detected angle
            
    # Save the rotated PDF
    document.save(output_path)
    document.close()

# Main code to process the PDF
pdf_path = 'path/to/your/pdf/file'  # Replace with the path to your PDF file
output_path = 'path/to/output/file'  # Replace with the desired output path

rotate_pdf_pages(pdf_path, output_path)
