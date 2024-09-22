import fitz
import io
from PIL import Image
import base64
import requests

def pdf_convert(file):
    
    text = ""
    images = []

    with fitz.open(file) as doc:
        for page_num, page in enumerate(doc, start=1):
            
            # Extract text
            text += page.get_text()

            # Loops over images on current page
            for img_index, img in enumerate(page.get_images(full=True)):
                
                # cross-reference ID, uniquely identifies image in PDF
                xref = img[0]
                
                # Extracts image data from PDF using xref
                base_image = doc.extract_image(xref)
                
                # Extracts bytes and file extension of image
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Uses Pillow to open image
                image = Image.open(io.BytesIO(image_bytes))

                # Creates filename for image
                image_filename = f"image_page{page_num}_{img_index}.{image_ext}"

                # Creates buffer in memory
                buffer = io.BytesIO()

                # Saves image in memory
                image.save(buffer, format=image.format or "PNG")

                # Encodes to base64
                image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

                # Appends base64-encoded image to image list
                images.append(image_base64)

    return text, images

def llava_description(image_base64):
    
    # Create payload for API request
    payload = {
        "model": "llava",
        "prompt": "Explain this image in detail",
        "images": [image_base64]
    }

text, images = pdf_convert('CRAM Challenge System Under Evaluation.pdf')
#print(text)
#print(images)