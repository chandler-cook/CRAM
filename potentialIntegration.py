import fitz  # PyMuPDF
import io
from PIL import Image
import base64
import requests
import torch
from transformers import pipeline, BitsAndBytesConfig

# Function to convert PDF to text and base64-encoded images
def pdf_convert(file):
    text = ""
    images = []

    with fitz.open(file) as doc:
        for page_num, page in enumerate(doc, start=1):
            # Extract text from the page
            text += page.get_text()
            
            # Loop over images in the current page
            for img_index, img in enumerate(page.get_images(full=True)):
                # Extracts the image data using xref (cross-reference ID)
                xref = img[0]
                base_image = doc.extract_image(xref)
                
                # Extract image bytes and file extension
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Use Pillow to open the image
                image = Image.open(io.BytesIO(image_bytes))
                
                # Create a filename for the image
                image_filename = f"image_page{page_num}_{img_index}.{image_ext}"
                
                # Create a buffer in memory
                buffer = io.BytesIO()
                
                # Save the image in memory
                image.save(buffer, format=image.format or "PNG")
                
                # Encode the image to base64
                image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                # Append the base64-encoded image to the image list
                images.append(image_base64)

    return text, images

# Function to generate detailed descriptions using LLaVA model
def llava_description(image_base64):
    # Define the LLaVA endpoint or load model locally if configured
    # Here, we'll assume a local LLaVA model setup using a pipeline
    
    # Create a payload for API request
    payload = {
        "model": "llava",
        "prompt": "Explain this image in detail",
        "images": [image_base64]
    }
    
    # Example endpoint if using a web service (replace with your actual endpoint)
    # response = requests.post("http://localhost:8000/llava", json=payload)
    # return response.json()["description"]
    
    # If using LLaVA locally, configure and use the model directly
    model_id = "llava-hf/llava-1.5-7b-hf"
    quantization_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)
    model = pipeline("image-to-text", model=model_id, model_kwargs={"quantization_config": quantization_config})
    
    # Decode base64 to PIL image
    image_data = base64.b64decode(image_base64)
    image = Image.open(io.BytesIO(image_data)).convert("RGB")
    
    # Generate detailed description
    result = model({"image": image, "prompt": payload["prompt"]})
    return result[0]

# Process PDF and use LLaVA for image descriptions
def process_pdf_with_llava(pdf_path):
    # Extract text and base64 images from the PDF
    text, images = pdf_convert(pdf_path)
    
    # Initialize list to hold image descriptions
    image_descriptions = []
    
    # Generate LLaVA descriptions for each image
    for img_base64 in images:
        description = llava_description(img_base64)
        image_descriptions.append(description)
    
    # Combine text and image descriptions
    final_text = text
    for idx, description in enumerate(image_descriptions):
        final_text += f"\n\n[Image {idx + 1}]:\n{description}\n"
    
    # Save the final output to a file
    with open("final_output_with_llava.txt", "w") as f:
        f.write(final_text)
    print(f"Final text saved to 'final_output_with_llava.txt'")

# Replace 'your_file.pdf' with the path to your PDF file
pdf_path = 'CRAM Challenge System Under Evaluation.pdf'
process_pdf_with_llava(pdf_path)
