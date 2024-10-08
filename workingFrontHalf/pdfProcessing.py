# Combined Python Script from COGwithCSVtables.py, CVEfromCSV.py, sorter.py, naturalLanguageProcessor.py

# --- Content from COGwithCSVtables.py ---
import fitz  # PyMuPDF
import io
import os
from PIL import Image
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import camelot

# Define model path
MODEL_PATH = "THUDM/cogvlm2-llama3-chat-19B"

# Setup device based on CUDA availability
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
TORCH_TYPE = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.get_device_capability()[0] >= 8 else torch.float16

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
    tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')  # 'stream' works well for most tables
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
        response = response.split("<|end_of_text|>")[0]  # Remove the end-of-text token
    
    return response

# --- Content from sorter.py ---
import os
from transformers import pipeline
import torch
from datasets import Dataset

device = 0 if torch.cuda.is_available() else -1
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=device)

labels = ["Software", "Hardware", "Physical"]

def read_txt_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.readlines()

def classify_and_save_text(file_path, output_dir="classified_output"):
    text_data = read_txt_file(file_path)
    text_data = [paragraph.strip() for paragraph in text_data if paragraph.strip()]

    dataset = Dataset.from_dict({"text": text_data})

    def classify_text(batch):
        results = classifier(batch["text"], labels)
        batch["classification"] = [result["labels"][0] for result in results]
        return batch

    classified_dataset = dataset.map(classify_text, batched=True, batch_size=8)

    classified_text = {"Software": [], "Hardware": [], "Physical": []}

    for item in classified_dataset:
        classified_text[item["classification"]].append(item["text"])

    for label, content in classified_text.items():
        output_file_path = f"{output_dir}/{label}.txt"
        os.makedirs(output_dir, exist_ok=True)
        with open(output_file_path, "w", encoding="utf-8") as output_file:
            output_file.writelines(content)

# --- Content from CVEfromCSV.py ---
import pandas as pd
import re

def extract_cves_from_csv(csv_file):
    cve_pattern = r'C &#8203;:contentReference[oaicite:0]{index=0}&#8203;
# --- Content from CVEfromCSV.py continued ---

def extract_cves_from_csv(csv_file):
    cve_pattern = r'CVE-\d{4}-\d+'
    df = pd.read_csv(csv_file)
    cve_list = []

    for col in df.columns:
        matches = df[col].astype(str).apply(lambda x: re.findall(cve_pattern, x))
        matches = [item for sublist in matches for item in sublist if item]  # Flatten the list and filter
        cve_list.extend(matches)

    return list(set(cve_list))  # Return unique CVEs

def process_all_csv_files(directory, output_file):
    with open(output_file, 'w') as outfile:
        for filename in os.listdir(directory):
            if filename.endswith('.csv'):
                csv_path = os.path.join(directory, filename)
                cves = extract_cves_from_csv(csv_path)
                if cves:
                    outfile.write(f'CVEs from {filename}:\n')
                    for cve in cves:
                        outfile.write(f'{cve}\n')
                    outfile.write('\n')

# --- Content from naturalLanguageProcessor.py ---
from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def process_and_clean_physical_file(file_path, output_dir="cleaned_output"):
    with open(file_path, 'r', encoding='utf-8') as file:
        text_data = file.readlines()

    paragraphs = [line.strip() for line in text_data if line.strip()]
    
    summarized_paragraphs = []
    for paragraph in paragraphs:
        summarized = summarizer(paragraph.strip(), max_length=150, min_length=80, do_sample=False)
        summarized_paragraphs.append(summarized[0]['summary_text'])

    output_file_path = f"{output_dir}/cleaned_Physical.txt"
    os.makedirs(output_dir, exist_ok=True)
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        for summary in summarized_paragraphs:
            output_file.write(summary + "\n")

# --- Main script (Panoptes.py) ---

def main():

     # Step 1: Run the CogVLM2 for image descriptions and extract tables and text
    print("Running COGwithCSVtables.py...")
    COGwithCSVtables.process_pdf_with_cogvlm2('/path/to/your/pdf/file')  # Replace with your PDF path

  

    # Step 2: Sort the Software, Hardware, and Physical files
    print("Running sorter.py...")
    txt_file_path = 'final_output_with_text_images_tables_cogvlm2.txt'
    classify_and_save_text(txt_file_path)


    # Step 3: Run the natural language processor to clean the Physical.txt
    print("Running naturalLanguageProcessor.py...")
    physical_file_path = 'classified_output/Physical.txt'
    process_and_clean_physical_file(physical_file_path)

    # Step 4: Pull CVEs from the CSV tables using the CVEfromCSV.py script
    print("Running CVEfromCSV.py...")
    csv_directory = 'CSVfromTables'
    output_file_path = 'CVEfromCSVOutput.txt'
    process_all_csv_files(csv_directory, output_file_path)

if __name__ == "__main__":
    main()
