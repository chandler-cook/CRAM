
------------------------------------------------------------

1. Imports and Setup
python
Copy code
import fitz  # PyMuPDF
import io
from PIL import Image
import base64
import requests
import torch
from transformers import pipeline, BitsAndBytesConfig
import camelot


Explanation:

fitz (PyMuPDF): Used for handling PDFs, extracting text, and images.
io: Used for managing byte streams, particularly for image handling.
PIL (Pillow): Used for manipulating and processing images.
base64: Encodes images in base64 format for compatibility with API requests or direct embedding.
requests: Used for making API calls (if needed).
torch and transformers: Required for loading and using the LLaVA model.
camelot: Specifically used for extracting tables from PDFs.
Review:

All necessary libraries are included for text, image, and table extraction, as well as for the LLaVA model.
If using a local setup without API calls, requests can be omitted.
Ensure that all required dependencies (camelot-py[cv], transformers, etc.) are installed properly.

-----------------------------------------------------------------

2. Text Extraction from PDF

def extract_text_from_pdf(pdf_path):
    document = fitz.open(pdf_path)
    all_text = ""
    
    for page_num, page in enumerate(document, start=1):
        page_text = page.get_text("text")
        all_text += f"\n\nPage {page_num} Text:\n{page_text}"
    
    document.close()
    return all_text

Explanation:

Opens the PDF using PyMuPDF (fitz) and iterates through each page.
Extracts text using the get_text("text") method, which works well for basic text extraction.
Concatenates text with page numbers for clarity.
Review:

Pros: Efficient and straightforward for extracting plain text.
Cons: This approach may miss structured data like tables or complex text layouts. For these, a more sophisticated extraction like OCR or using get_text("blocks") might be better.
Improvement: Consider using OCR libraries like Tesseract for more accurate extraction if needed.

------------------------------------------------------------------------

3. Image Extraction from PDF

def extract_images_from_pdf(pdf_path, output_dir="extracted_images"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    document = fitz.open(pdf_path)
    image_paths = []
    
    for page_num in range(len(document)):
        page = document[page_num]
        image_list = page.get_images(full=True)
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = document.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_filename = f"image_page{page_num + 1}_{img_index}.{image_ext}"
            image_path = os.path.join(output_dir, image_filename)
            
            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)
            image_paths.append(image_path)
    
    document.close()
    return image_paths

Explanation:

Iterates through each page of the PDF to find and extract images.
Saves extracted images to a specified directory and returns their file paths.
Review:

Pros: Efficient for extracting embedded images in the PDF.
Cons: Images that are not directly embedded but are part of the page rendering (e.g., vector graphics or diagrams) may not be captured.
Improvement: You could combine this with pdf2image for rendering entire pages as images if 
needed.


------------------------------------------------------------------------

4. Table Extraction Using Camelot

def extract_tables_from_pdf(pdf_path, output_format='text'):
    tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')  # 'stream' works well for most tables
    table_texts = []
    
    for i, table in enumerate(tables):
        if output_format == 'text':
            table_texts.append(f"Table {i + 1}:\n{table.df.to_string(index=False, header=False)}\n")
        elif output_format == 'csv':
            table.to_csv(f"table_{i + 1}.csv")
    
    return table_texts

Explanation:

Uses Camelot to extract tables using the 'stream' flavor, which works well for tables with clear boundaries.
Converts tables to text or CSV format based on the output_format parameter.
Review:

Pros: Camelot is powerful for extracting well-defined tables.
Cons: May not work well with complex tables or poorly scanned documents.
Improvement: For complex tables, consider using tabula-py or combining Camelot's 'lattice' method with manual verification.


----------------------------------------------------------------------

5. Generating Image Descriptions Using LLaVA

def llava_description(image_path, model):
    raw_image = Image.open(image_path).convert("RGB")
    result = model({
        "image": raw_image, 
        "prompt": "Describe this image in detail."
    })
    return result[0]

Explanation:

Takes an image path and uses the LLaVA model to generate a detailed description.
Passes the image along with a prompt to the model and returns the description.
Review:

Pros: Straightforward and integrates well with the image extraction function.
Cons: Depends on the quality of the model and the prompt for generating accurate descriptions.
Improvement: You could experiment with different prompts or fine-tune the model for specific descriptions.


----------------------------------------------------------------------

6. Setting Up the LLaVA Model

def setup_llava_model():
    quantization_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)
    model_id = "llava-hf/llava-1.5-7b-hf"
    model = pipeline("image-to-text", model=model_id, model_kwargs={"quantization_config": quantization_config})
    return model

Explanation:

Configures the LLaVA model for image-to-text generation.
Uses quantization to reduce memory usage, making it possible to run on less powerful hardware.
Review:

Pros: Efficient setup with quantization for lower memory footprint.
Cons: Reduced precision may affect the quality of generated descriptions.
Improvement: If performance is an issue, use a larger model or tweak quantization parameters.


----------------------------------------------------------------------

7. Main Function to Process the PDF

def process_pdf_with_llava(pdf_path):
    # Step 1: Extract text from the PDF
    extracted_text = extract_text_from_pdf(pdf_path)
    print("Text Extracted from PDF:")
    print(extracted_text)
    
    # Step 2: Extract images from the PDF
    image_paths = extract_images_from_pdf(pdf_path)
    print("Images Extracted from PDF (Paths):")
    print(image_paths)
    
    # Step 3: Extract tables from the PDF
    extracted_tables = extract_tables_from_pdf(pdf_path)
    print("Tables Extracted from PDF:")
    print(extracted_tables)

    # Step 4: Setup LLaVA model for image descriptions
    model = setup_llava_model()

    # Step 5: Generate detailed descriptions for each image using LLaVA
    image_descriptions = []
    for image_path in image_paths:
        description = llava_description(image_path, model)
        image_descriptions.append(description)
    
    # Combine text, table, and image descriptions into one final output
    final_text = extracted_text
    for idx, table in enumerate(extracted_tables):
        final_text += f"\n\n[Table {idx + 1}]\n{table}\n"
    for idx, description in enumerate(image_descriptions):
        final_text += f"\n\n[Image {idx + 1}]:\n{description}\n"
    
    # Save the final output to a text file
    output_file = "final_output_with_text_images_tables.txt"
    with open(output_file, "w") as f:
        f.write(final_text)
    print(f"Final output saved to '{output_file}'")

Explanation:

Combines all the extraction functions to process the PDF and integrate text, images, and tables.
Saves the output in a single text file.


-----------------------------------------------------------------------

Review:

Pros: Integrates all elements seamlessly, providing a comprehensive text output.
Cons: For large PDFs, this can be slow and memory-intensive.
Improvement: Consider adding parallel processing for large PDFs or optimizing image descriptions with batch processing.