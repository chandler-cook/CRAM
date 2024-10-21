import torch
import ollama
import os
import argparse

# Helper function to read content from a file
def read_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Retrieving the most relevant content from the document vault using embeddings
def fetch_related_content(query, doc_embeddings, doc_texts, num_results=3):
    if doc_embeddings.nelement() == 0:
        return []
    
    # Generate the embedding for the query
    query_embedding = ollama.embeddings(model='mxbai-embed-large', prompt=query)["embedding"]
    
    # Calculate similarity scores between the query embedding and document embeddings
    similarity_scores = torch.cosine_similarity(torch.tensor(query_embedding).unsqueeze(0), doc_embeddings)
    
    # Get the indices of the top matching documents
    top_doc_indices = torch.topk(similarity_scores, k=min(num_results, len(similarity_scores)))[1].tolist()
    
    # Return the most relevant document texts
    return [doc_texts[idx].strip() for idx in top_doc_indices]

# Function to engage with the llama model using the improved prompt and RAG
import time

def engage_with_llama_rag(text, model_name, doc_embeddings, doc_texts, retries=3):
    base_prompt = (
        "Analyze the following text and provide suggestions to improve the physical policies. "
        "There are physical policies present, and the lines likely begin with a letter or number. "
        "Also, DO NOT mention things that pertain to the text formatting, only the physical policy."
    )

    related_content = fetch_related_content(text, doc_embeddings, doc_texts)
    related_content_text = "\n".join(related_content)
    full_prompt = f"{base_prompt}\n\nUser Input:\n{text}\n\nRelevant Context from Vault:\n{related_content_text}"

    for attempt in range(retries):
        try:
            # Sending the request to the model
            response = ollama.chat(model=model_name, messages=[{"role": "system", "content": full_prompt}])
            return response['message']['content'].strip()
        except ollama._types.ResponseError as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt < retries - 1:
                time.sleep(2)  # Wait before retrying
            else:
                raise e  # Re-raise after final attempt


# Function to remove unwanted lines from the final output
def remove_lines(output_file_path):
    temp_file_path = "temp_output.txt"  # Temporary file to store filtered content
    
    # Open output.txt and a temporary file to write the filtered content
    with open(output_file_path, 'r', encoding='utf-8') as output_file, open(temp_file_path, 'w', encoding='utf-8') as temp_file:
        for line in output_file:
            if "|" not in line and "---" not in line:  # Filtering out lines with unwanted characters
                temp_file.write(line)
    
    # Replace the original output.txt with the filtered temp file
    os.replace(temp_file_path, output_file_path)

# Function to remove all instances of double asterisks (**) from the suggestions file
def remove_double_asterisks(file_path):
    temp_file_path = "temp_suggestions.txt"  # Temporary file to store cleaned content

    # Read the suggestions.txt file and write cleaned content to temp file
    with open(file_path, 'r', encoding='utf-8') as file, open(temp_file_path, 'w', encoding='utf-8') as temp_file:
        for line in file:
            cleaned_line = line.replace("**", "")  # Remove all double asterisks without deleting lines
            temp_file.write(cleaned_line)
    
    # Replace the original suggestions.txt with the cleaned temp file
    os.replace(temp_file_path, file_path)

# Main function to process the file and provide suggestions using RAG
def process_file(input_file_path, output_file_path, model_name, rag_file_path):
    # Load and process document contents from the RAG file (vault)
    vault_texts = []
    if os.path.exists(rag_file_path):
        with open(rag_file_path, "r", encoding='utf-8') as vault_file:
            vault_texts = vault_file.readlines()

    # Generate embeddings for document contents
    embeddings_list = []
    for text in vault_texts:
        embedding_response = ollama.embeddings(model='mxbai-embed-large', prompt=text)
        embeddings_list.append(embedding_response["embedding"])

    # Convert the embeddings list into a tensor
    embeddings_tensor = torch.tensor(embeddings_list)

    # Read the entire content of the input file
    with open(input_file_path, 'r', encoding='utf-8') as input_file:
        full_text = input_file.read()

    # Engage with the model to analyze the whole text for physical policies and suggestions using RAG
    suggestions = engage_with_llama_rag(full_text, model_name, embeddings_tensor, vault_texts)
    
    # Write the suggestions to the output file
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(f"Suggestions and Identified Physical Policies:\n\n{suggestions}\n")
