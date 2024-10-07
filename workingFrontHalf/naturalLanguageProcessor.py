import os
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

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

