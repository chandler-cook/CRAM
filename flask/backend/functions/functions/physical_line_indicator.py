import re
import ollama
import os
import time

# Function to engage with the llama model using a hardcoded prompt and retry mechanism
def engage_with_llama(text, model_name, retries=3):
    base_prompt = "Does this text pertain to a company's specific laid out physical policy? Be strict, and do not answer yes to any paragraph with strange characters. Only answer yes or no."
    full_prompt = f"{base_prompt}\n\n{text}"

    for attempt in range(retries):
        try:
            # Sending the request to the model
            response = ollama.chat(
                model=model_name,
                messages=[{"role": "system", "content": full_prompt}]
            )
            # Return the response text, ensuring it's stripped and lowercased
            return response['message']['content'].strip().lower()
        except ollama._types.ResponseError as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt < retries - 1:
                time.sleep(2)  # Wait before retrying
            else:
                raise e  # Re-raise after final attempt

# This function checks if the text is a piece of physical policy
def is_physical_policy(text, model_name):
    response_text = engage_with_llama(text, model_name)
    return "yes" in response_text

# Function to check if a line contains hardware-related terms or unwanted characters
def contains_hardware_or_unwanted_terms(line):
    hardware_terms = ["hardware", "device", "model", "server", "laptop", "router", "switch", "firmware"]
    return any(term in line.lower() for term in hardware_terms) or "|" in line or "---" in line

# Function to remove lines with hardware-related terms or unwanted characters from the file
def remove_unwanted_lines(output_file_path):
    temp_file_path = "temp_output.txt"  # Temporary file to store filtered content
    with open(output_file_path, 'r', encoding='utf-8') as output_file, open(temp_file_path, 'w', encoding='utf-8') as temp_file:
        for line in output_file:
            if not contains_hardware_or_unwanted_terms(line):  # Write the line to temp if it doesn't contain unwanted terms
                temp_file.write(line)
    # Replace the original file with the filtered temp file
    os.replace(temp_file_path, output_file_path)

# Helper function to split large text into smaller chunks to avoid exceeding token limits
def split_text_into_chunks(text, max_tokens=1024):
    words = text.split()
    for i in range(0, len(words), max_tokens):
        yield ' '.join(words[i:i + max_tokens])

# The main function to process the input file and write the filtered paragraphs to the output file
def process_input_file(input_file_path, output_file_path, model_name, max_chunk_size=1024):
    # Read the entire file content at once
    with open(input_file_path, 'r', encoding='utf-8') as input_file:
        content = input_file.read()

    # Split content into paragraphs (assuming paragraphs are separated by two newlines)
    paragraphs = content.split('\n\n')

    # Open the output file to write the processed paragraphs
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        for paragraph in paragraphs:
            paragraph = paragraph.strip()  # Remove leading/trailing whitespace

            if paragraph:  # Check if the paragraph is not empty
                # Split large paragraphs into smaller chunks to avoid exceeding model limits
                for chunk in split_text_into_chunks(paragraph, max_chunk_size):
                    # Check if the chunk pertains to a physical policy
                    if is_physical_policy(chunk, model_name):
                        output_file.write(paragraph + "\n\n")  # Write the paragraph to the output file
    
    # Optionally, remove unwanted lines (hardware-related) from the output file
    remove_unwanted_lines(output_file_path)