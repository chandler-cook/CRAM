import os
from transformers import pipeline
import torch

# Initialize the Summarization model for cleaning up the text
device = 0 if torch.cuda.is_available() else -1  # 0 for GPU, -1 for CPU
summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=device)

# Read the .txt file content
def read_txt_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.readlines()

# Write the cleaned-up text back to a file
def write_cleaned_file(content, output_path):
    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write("\n".join(content))

# Clean up the text using the summarization model
def clean_up_text(text):
    # Summarize or clean each paragraph
    cleaned_text = []
    for paragraph in text:
        if len(paragraph.strip()) > 10:  # Avoid short lines
            summarized = summarizer(paragraph.strip(), max_length=100, min_length=30, do_sample=False)
            cleaned_text.append(summarized[0]['summary_text'])
    return cleaned_text

# Process and clean the text files
def process_and_clean_text(file_path, output_dir="classified_output"):
    # Read the text data
    text_data = read_txt_file(file_path)
    
    # Filter out empty lines
    text_data = [paragraph.strip() for paragraph in text_data if paragraph.strip()]

    # Clean up the text
    cleaned_text = clean_up_text(text_data)

    # Save cleaned text to a new file
    base_name = os.path.basename(file_path)
    output_file_path = os.path.join(output_dir, f"cleaned_{base_name}")
    os.makedirs(output_dir, exist_ok=True)
    
    write_cleaned_file(cleaned_text, output_file_path)
    print(f"Cleaned text saved to {output_file_path}")

# Main function to process the three classified files
def main():
    classified_output_dir = "/home/user/Documents/Github/classified_output"  # Adjust this path based on your setup
    
    hardware_file_path = os.path.join(classified_output_dir, "Hardware.txt")
    software_file_path = os.path.join(classified_output_dir, "Software.txt")
    physical_file_path = os.path.join(classified_output_dir, "Physical.txt")

    # Process and clean each file
    process_and_clean_text(hardware_file_path)
    process_and_clean_text(software_file_path)
    process_and_clean_text(physical_file_path)

if __name__ == "__main__":
    main()

