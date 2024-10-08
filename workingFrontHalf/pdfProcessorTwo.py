import fitz  # PyMuPDF
import io
import os
from PIL import Image
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import camelot
import os
from transformers import pipeline
import torch
from datasets import Dataset
import os
import re
import pandas as pd

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
        # Extract text from the page using PyMuPDF
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

# Function to extract tables from PDF using Camelot and save them as CSV files
def extract_tables_from_pdf(pdf_path, output_dir='CSVfromTables'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')  # 'stream' flavor works well for most tables
    
    for i, table in enumerate(tables):
        csv_filename = f"table_{i + 1}.csv"
        csv_path = os.path.join(output_dir, csv_filename)
        table.to_csv(csv_path)
        print(f"Table {i + 1} saved as CSV at {csv_path}")

# Function to generate detailed descriptions for each image using CogVLM2
def cogvlm2_description(image_path):
    raw_image = Image.open(image_path).convert("RGB")
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
    
    # Step 3: Extract tables from the PDF and save them as CSV
    extract_tables_from_pdf(pdf_path)
    print("Tables Extracted and Saved as CSV files.")

    # Step 4: Generate detailed descriptions for each image using CogVLM2
    image_descriptions = []
    for image_path in image_paths:
        description = cogvlm2_description(image_path)
        image_descriptions.append(description)
    
    # Combine text, table, and image descriptions into one final output
    final_text = extracted_text
    for idx, description in enumerate(image_descriptions):
        final_text += f"\n\n[Image {idx + 1}]:\n{description}\n"
    
    # Save the final output to a text file
    output_file = "final_output_with_text_images_tables_cogvlm2.txt"
    with open(output_file, "w") as f:
        f.write(final_text)
    print(f"Final output saved to '{output_file}'")

# Replace 'systemOne.pdf' with your actual PDF file path
pdf_path = '/home/user/Documents/Github/systemOne.pdf'
process_pdf_with_cogvlm2(pdf_path)




# Initialize the Zero-Shot Classification model
device = 0 if torch.cuda.is_available() else -1  # 0 for GPU, -1 for CPU
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=device)

# Define the labels for classification
labels = ["Software", "Hardware", "Physical"]

# Read the .txt file content
def read_txt_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.readlines()

# Classify text into categories and save into separate files
def classify_and_save_text(file_path, output_dir="classified_output"):
    text_data = read_txt_file(file_path)
    
    # Filter out empty lines
    text_data = [paragraph.strip() for paragraph in text_data if paragraph.strip()]

    # Create a dataset object for more efficient processing
    dataset = Dataset.from_dict({"text": text_data})

    # Function to classify a single text
    def classify_text(batch):
        results = classifier(batch["text"], labels)
        batch["classification"] = [result["labels"][0] for result in results]
        return batch

    # Apply the classification function to the dataset
    classified_dataset = dataset.map(classify_text, batched=True, batch_size=8)

    # Create dictionaries to store classified text
    classified_text = {
        "Software": [],
        "Hardware": [],
        "Physical": []
    }

    # Distribute classified text into corresponding categories
    for item in classified_dataset:
        classified_text[item["classification"]].append(item["text"])

    # Write classified text to separate files
    for label, content in classified_text.items():
        output_file_path = f"{output_dir}/{label}.txt"
        os.makedirs(output_dir, exist_ok=True)  # Create directory if it doesn't exist
        with open(output_file_path, "w", encoding="utf-8") as output_file:
            output_file.writelines(content)

    print(f"Text has been classified and saved into separate files in the {output_dir} folder.")

# Call the function with the updated .txt file path
txt_file_path = "/home/user/Documents/Github/final_output_with_text_images_tables_cogvlm2.txt"
classify_and_save_text(txt_file_path)






# Define the summarization model path
MODEL_PATH = "facebook/bart-large-cnn"

# Setup device based on CUDA availability
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
TORCH_TYPE = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.get_device_capability()[0] >= 8 else torch.float16

# Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH, torch_dtype=TORCH_TYPE).to(DEVICE).eval()

# Function to clean up and summarize the text
def clean_up_text(text_data):
    # Split text into chunks to avoid input size issues
    text_chunks = [text_data[i:i+1024] for i in range(0, len(text_data), 1024)]
    
    summarized_text = ""
    
    for chunk in text_chunks:
        inputs = tokenizer(chunk, return_tensors="pt", truncation=True, padding="longest", max_length=1024).to(DEVICE)
        summary_ids = model.generate(inputs["input_ids"], max_length=150, min_length=30, length_penalty=2.0, num_beams=4, early_stopping=True)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        summarized_text += summary + "\n"

    return summarized_text

# Function to read the text from a file
def read_txt_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

# Function to process and clean the Physical.txt file
def process_and_clean_physical_file(file_path, output_dir="cleaned_output"):
    # Read the content of the file
    text_data = read_txt_file(file_path)

    # Clean and summarize the text
    cleaned_text = clean_up_text(text_data)

    # Write the cleaned text to a new file
    base_name = os.path.basename(file_path)
    cleaned_file_path = os.path.join(output_dir, f"cleaned_{base_name}")
    os.makedirs(output_dir, exist_ok=True)
    
    with open(cleaned_file_path, "w", encoding="utf-8") as file:
        file.write(cleaned_text)
    
    print(f"Cleaned and summarized text has been saved to '{cleaned_file_path}'.")

# Specify the file path for Physical.txt
physical_file_path = os.path.join("classified_output", "Physical.txt")

# Call the function to process and clean the Physical.txt file
process_and_clean_physical_file(physical_file_path)

# Function to extract CVEs from a CSV file
def extract_cve_from_csv(file_path, output_file):
    try:
        df = pd.read_csv(file_path)
        
        # Convert the DataFrame to a single string for searching
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

# Function to process all CSV files in a directory
def process_all_csv_files(directory, output_file):
    try:
        csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
        
        # Clear the output file before appending results
        with open(output_file, 'w') as f:
            f.write('')
        
        for csv_file in csv_files:
            file_path = os.path.join(directory, csv_file)
            extract_cve_from_csv(file_path, output_file)
    except Exception as e:
        print(f"Error processing directory {directory}: {e}")

# Example usage
csv_directory = 'home/user/documents/Github/CSVfromTables'  # Directory containing the CSV files
output_file_path = 'CVEfromCSVOutput.txt'  # Output file to store extracted CVEs

process_all_csv_files(csv_directory, output_file_path)
