# Import necessary libraries
import os
import re
from transformers import pipeline

# Function to read text from a .txt file
def read_txt_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()  # read as a single string instead of line by line

# Function to split the long text into smaller chunks based on punctuation
def split_text_into_chunks(text, chunk_size=400):
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)  # Split on period, question mark, etc.
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    
    if current_chunk:  # Add any remaining text in the final chunk
        chunks.append(current_chunk.strip())
    
    return chunks

# Function to clean up text using a summarization model
def clean_up_text(text_data):
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", device=-1)
    
    cleaned_text = []
    for chunk in text_data:
        if len(chunk.strip()) > 0:
            summarized = summarizer(chunk, max_length=50, min_length=30, do_sample=False)
            cleaned_text.append(summarized[0]['summary_text'] + "\n")
    
    return cleaned_text

# Function to clean and save physical file
def process_and_clean_physical_file(file_path, output_dir="classified_output"):
    # Read the entire text from the physical file
    text_data = read_txt_file(file_path)
    
    # Split the text into manageable chunks
    text_chunks = split_text_into_chunks(text_data)
    
    # Clean up the text
    cleaned_text = clean_up_text(text_chunks)
    
    # Create output directory if not exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Define output path for the cleaned physical file
    output_file_path = os.path.join(output_dir, "Physical_cleaned.txt")
    
    # Write cleaned text to the output file
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.writelines(cleaned_text)
    
    print(f"Cleaned Physical file has been saved to: {output_file_path}")

# Main function to process the physical file
def main():
    # File path for the classified physical file
    physical_file_path = os.path.join("classified_output", "Physical.txt")
    
    # Clean and save the physical file
    process_and_clean_physical_file(physical_file_path)

# Run the main function
if __name__ == "__main__":
    main()
