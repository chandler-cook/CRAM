# pip install pytesseract fitz Pillow
import fitz  # PyMuPDF

# Function to check if a page's content should be rotated based on its aspect ratio
def is_page_rotated(page):
    pix = page.get_pixmap()
    
    # Calculate aspect ratio (width / height)
    aspect_ratio = pix.width / pix.height
    
    # If width is greater than height, it likely needs rotation
    return aspect_ratio > 1.0

# Function to rotate pages if needed based on aspect ratio
def rotate_pdf_pages(pdf_path, output_path):
    document = fitz.open(pdf_path)
    
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        
        # Check if the page content is rotated
        if is_page_rotated(page):
            print(f"Rotating page {page_num + 1}")
            page.set_rotation(90)  # Rotate page by 90 degrees
            
    # Save the rotated PDF
    document.save(output_path)
    document.close()

# Main code to process the PDF
pdf_path = 'path/to/your/pdf/file'  # Replace with the path to your PDF file
output_path = 'path/to/output/file'  # Replace with the desired output path

rotate_pdf_pages(pdf_path, output_path)
