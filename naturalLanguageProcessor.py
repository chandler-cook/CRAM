import os
from transformers import pipeline
import torch

# Set device to use GPU (CUDA) if available
device = 0 if torch.cuda.is_available() else -1  # GPU if available, otherwise CPU

# Load the BART summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=device)

# Function to read the Physical.txt file
def read_txt_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

# Function to split text into chunks within the model's max token length
def split_into_chunks(text, max_tokens=1024):
    sentences = text.split(". ")
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        token_length = len(summarizer.tokenizer.tokenize(sentence))
        if current_length + token_length > max_tokens:
            chunks.append(". ".join(current_chunk) + ".")
            current_chunk = [sentence]
            current_length = token_length
        else:
            current_chunk.append(sentence)
            current_length += token_length
    
    if current_chunk:
        chunks.append(". ".join(current_chunk) + ".")
    
    return chunks

# Function to process and clean the Physical.txt file
def process_and_clean_physical_file(file_path, output_dir="classified_output"):
    text_data = read_txt_file(file_path)

    # Split text into smaller chunks
    text_chunks = split_into_chunks(text_data)

    # Clean and summarize each chunk
    cleaned_text = []
    for chunk in text_chunks:
        summarized = summarizer(chunk, max_length=150, min_length=50, do_sample=False)
        cleaned_text.append(summarized[0]["summary_text"])

    # Save the cleaned text into a new file
    output_file_path = os.path.join(output_dir, "Physical_cleaned.txt")
    os.makedirs(output_dir, exist_ok=True)
    
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write("\n".join(cleaned_text))
    
    print(f"Physical text has been cleaned and saved to {output_file_path}")

# Specify the file path for Physical.txt
physical_file_path = os.path.join("classified_output", "Physical.txt")

# Call the function to process and clean the Physical.txt file
process_and_clean_physical_file(physical_file_path)

# Run the main function
if __name__ == "__main__":
    main()
