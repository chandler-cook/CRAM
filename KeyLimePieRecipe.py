# pip install fitz pdf2image pillow camelot-py[cv] transformers torch PyPDF2==2.10.0 torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu118

import torch
from PIL import Image
from transformers import AutoModelForCausalLM, AutoTokenizer
import fitz  # PyMuPDF
import os
import camelot

# Define model path
MODEL_PATH = "THUDM/cogvlm2-llama3-chat-19B"

# Setup device based on CUDA availability (no Triton dependency)
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
TORCH_TYPE = torch.float16 if torch.cuda.is_available() else torch.float32

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, torch_dtype=TORCH_TYPE, trust_remote_code=True).to(DEVICE).eval()

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    document = fitz.open(pdf_path)
    all_text = ""
    for page_num, page in enumerate(document, start=1):
        page_text = page.get_text("text")
        all_text += f"\n\nPage {page_num} Text:\n{page_text}"
    document.close()
    return all_text

# Function to extract and save images from a PDF
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

# Function to extract tables from PDF using Camelot
def extract_tables_from_pdf(pdf_path, output_format='text'):
    tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
    table_texts = []
    for i, table in enumerate(tables):
        if output_format == 'text':
            table_texts.append(f"Table {i + 1}:\n{table.df.to_string(index=False, header=False)}\n")
        elif output_format == 'csv':
            table.to_csv(f"table_{i + 1}.csv")
    return table_texts

# Function to generate detailed descriptions for each image using CogVLM2
def cogvlm2_description(image_path):
    raw_image = Image.open(image_path).convert("RGB")
    input_by_model = model.build_conversation_input_ids(
        tokenizer,
        query="Describe this image in detail.",
        history=[],
        images=[raw_image],
        template_version='chat'
    )

    inputs = {
        'input_ids': input_by_model['input_ids'].unsqueeze(0).to(DEVICE),
        'token_type_ids': input_by_model['token_type_ids'].unsqueeze(0).to(DEVICE),
        'attention_mask': input_by_model['attention_mask'].unsqueeze(0).to(DEVICE),
        'images': [[input_by_model['images'][0].to(DEVICE).to(TORCH_TYPE)]],
    }

    gen_kwargs = {
        "max_new_tokens": 2048,
        "pad_token_id": 128002,
    }

    with torch.no_grad():
        outputs = model.generate(**inputs, **gen_kwargs)
        outputs = outputs[:, inputs['input_ids'].shape[1]:]
        response = tokenizer.decode(outputs[0])
        response = response.split("<|end_of_text|>")[0]
    
    return response

# Main function to process the PDF and integrate text, tables, and CogVLM2 image descriptions
def process_pdf_with_cogvlm2(pdf_path):
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

    # Step 4: Generate detailed descriptions for each image using CogVLM2
    image_descriptions = []
    for image_path in image_paths:
        description = cogvlm2_description(image_path)
        image_descriptions.append(description)
    
    # Combine text, table, and image descriptions into one final output
    final_text = extracted_text
    for idx, table in enumerate(extracted_tables):
        final_text += f"\n\n[Table {idx + 1}]\n{table}\n"
    for idx, description in enumerate(image_descriptions):
        final_text += f"\n\n[Image {idx + 1}]:\n{description}\n"
    
    # Save the final output to a text file
    output_file = "final_output_with_text_images_tables_cogvlm2.txt"
    with open(output_file, "w") as f:
        f.write(final_text)
    print(f"Final output saved to '{output_file}'")

# Replace 'systemOne.pdf' with your actual PDF file path
pdf_path = 'C:/Users/Mitchell/Documents/GitHub/CRAM/systemOne.pdf'
process_pdf_with_cogvlm2(pdf_path)
