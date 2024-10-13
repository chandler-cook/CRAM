import fitz  # PyMuPDF
from io import BytesIO
import os
from PIL import Image
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import camelot
import tempfile
import glob
from transformers import pipeline
from datasets import Dataset
import re
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Function to extract text from a PDF
def extract_text(pdf_file):

    document = fitz.open(stream=pdf_file, filetype="pdf")
    all_text = ""
    
    for page_num, page in enumerate(document, start=1):
        # Extract text from the page using PyMuPDF
        page_text = page.get_text("text")
        all_text += f"\n\nPage {page_num} Text:\n{page_text}"
    
    document.close()
    return all_text

# Function to extract and save images from a PDF
def extract_images(pdf_file):
    
    document = fitz.open(stream=pdf_file, filetype="pdf")
    image_data = []
    
    for page_num in range(len(document)):
        page = document[page_num]
        image_list = page.get_images(full=True)
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = document.extract_image(xref)
            image_bytes = base_image["image"]

            image_data.append(BytesIO(image_bytes))
    
    document.close()
    return image_data

# Function to extract tables from PDF using Camelot and save them as CSV files
def extract_tables(output_path, pdf_file):
    
    # Create a temporary file to save the PDF content
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
        temp_pdf.write(pdf_file)  # Write PDF content to temp file
        temp_pdf_path = temp_pdf.name  # Get the file path
    
    # Use Camelot to read tables from the PDF file
    tables = camelot.read_pdf(temp_pdf_path, pages='all', flavor='lattice')
    
    # Save each table to a CSV file in the output directory
    for i, table in enumerate(tables):
        csv_filename = f"table_{i + 1}.csv"
        csv_path = os.path.join(output_path, csv_filename)
        table.to_csv(csv_path)
        print(f"Table {i + 1} saved as CSV at {csv_path}")
    
    # Remove the temporary PDF file
    os.remove(temp_pdf_path)

# Function to generate detailed descriptions for each image using CogVLM2
def cogvlm2_description(image_bytes, DEVICE, TORCH_TYPE, tokenizer, model):
    
    raw_image = Image.open(BytesIO(image_bytes)).convert("RGB")
    
    # Construct the prompt for the CogVLM2 model
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
        response = response.split("<|end_of_text|>")[0]  # Remove the end-of-text token

    # Clear CUDA memory to prevent potential memory backup
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()
    
    return response

def classify_text(classified_path, text_data, classifier, labels):
    # Split the text data into lines and filter out empty lines
    text_data = text_data.split('\n')
    text_data = [paragraph.strip() for paragraph in text_data if paragraph.strip()]

    # Create a dataset object for more efficient processing
    dataset = Dataset.from_dict({"text": text_data})

    # Function to classify a single text
    def classify_batch(batch):
        results = classifier(batch["text"], labels)
        batch["classification"] = [result["labels"][0] for result in results]
        return batch

    # Apply the classification function to the dataset
    classified_dataset = dataset.map(classify_batch, batched=True, batch_size=8)

    # Create dictionaries to store classified text
    classified_text = {
        "Software": [],
        "Hardware": [],
        "Physical": []
    }

    # Distribute classified text into corresponding categories
    for item in classified_dataset:
        classified_text[item["classification"]].append(item["text"])

    for label, content in classified_text.items():
        output_file_path = f"{classified_path}/{label}.txt"
        with open(output_file_path, "w", encoding="utf-8") as output_file:
            output_file.writelines(content)
    
    print(f"Text has been classified and saved into separate files in the {classified_path} folder.")

# Unified function to read, clean, summarize, and save text
def clean_text(file_path, DEVICE, tokenizer, model):
    
    physical_path = os.path.join(file_path, 'Physical.txt')
    
    # Read the content of the file
    with open(physical_path, "r", encoding="utf-8") as file:
        text_data = file.read()

    # Split text into chunks for processing
    text_chunks = [text_data[i:i+1024] for i in range(0, len(text_data), 1024)]
    summarized_text = ""
    
    # Summarize each chunk
    for chunk in text_chunks:
        inputs = tokenizer(chunk, return_tensors="pt", truncation=True, padding="longest", max_length=1024).to(DEVICE)
        summary_ids = model.generate(inputs["input_ids"], max_length=150, min_length=30, length_penalty=2.0, num_beams=4, early_stopping=True)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        summarized_text += summary + "\n"

    # Prepare the file name and path
    base_name = os.path.basename(physical_path)
    cleaned_file_path = os.path.join(file_path, f"cleaned_{base_name}")
    
    # Write the summarized text to the output file
    with open(cleaned_file_path, "w", encoding="utf-8") as file:
        file.write(summarized_text)
    
    print(f"Cleaned and summarized text has been saved to '{cleaned_file_path}'.")

# Function to extract CVEs from a CSV file
def extract_cves (csv_dir, output_file):
    
    # Find all CSV files in the directory
    csv_files = glob.glob(os.path.join(csv_dir, '*.csv'))
    
    # Process each CSV file
    for file_path in csv_files:
        try:
            df = pd.read_csv(file_path)
            
            # Convert DataFrame to a single string for searching
            csv_content = df.to_string(index=False, header=False)
            
            # Regular expression to match 'CVE-' followed by numbers and hyphens
            cve_matches = re.findall(r'(CVE-\d{4}-\d+)', csv_content)
            
            # Write each match to the output file
            with open(output_file, 'a') as outfile:  # Append mode to consolidate results across files
                for match in cve_matches:
                    outfile.write(match + '\n')
                    print(f"Extracted {match} from {file_path}")  # Optional: Print to console
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")