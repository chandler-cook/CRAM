import re
import torch
import ollama
import os
from openai import OpenAI
import json
import time
import statistics  # To use the built-in mean function

# Helper function to read content from a file
def read_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Retrieving the most similar content from the document vault
def fetch_related_content(query, doc_embeddings, doc_texts, num_results=3):
    if doc_embeddings.nelement() == 0:
        return []
    
    query_embedding = ollama.embeddings(model='mxbai-embed-large', prompt=query)["embedding"]
    similarity_scores = torch.cosine_similarity(torch.tensor(query_embedding).unsqueeze(0), doc_embeddings)
    top_doc_indices = torch.topk(similarity_scores, k=min(num_results, len(similarity_scores)))[1].tolist()
    return [doc_texts[idx].strip() for idx in top_doc_indices]

# The function to extract the number from AI response
def extract_number_from_response(response):
    match = re.search(r'\*\*(\d+)\*\*', response)
    if match:
        return int(match.group(1))
    
    match_plain_number = re.search(r'\b\d+\b', response)
    if match_plain_number:
        return int(match_plain_number.group(0))
    
    return None

# This is the main function to handle user interactions and get AI responses
def engage_with_ollama(user_input, base_prompt, doc_embeddings, doc_texts, ai_model):
    def get_scores(runs):
        scores = []
        for i in range(runs):
            # Adding delay to prevent resource issues from affecting the outputs
            time.sleep(1)

            # Reset the chat log for each independent run
            chat_log = []  # Clear chat log at the beginning of each run

            # Always build the full prompt with a new clean base and user input
            full_prompt = f"{base_prompt} {user_input}"
            chat_log.append({"role": "user", "content": full_prompt})

            # Create messages anew, no history from previous queries
            messages = [
                {"role": "system", "content": base_prompt},
                *chat_log
            ]

            response = client.chat.completions.create(
                model=ai_model,
                messages=messages,
                max_tokens=2000,
            )

            # Extract the response content
            ai_response = response.choices[0].message.content
            
            # Extract the numerical score from AI response
            extracted_number = extract_number_from_response(ai_response)

            print(extracted_number)

            if extracted_number:
                scores.append(extracted_number)

        return scores

    # New function to calculate the average of the scores
    def calculate_average(scores):
        if scores:
            # Calculate and return the average
            average_score = statistics.mean(scores)

            # If the average score is greater than 99, set it to 100
            if average_score > 99:
                average_score = 100

            return round(average_score, 2)
        else:
            return None

    # Perform initial 15 independent runs and collect the scores
    scores = get_scores(15)

    # Calculate the average score
    final_score = calculate_average(scores)

    # Return the valid final score
    return round(final_score)

# Localrag function to read from 'User-Input.txt', process input, and return score
def localrag(file_path, physical_vault_path):
    
    user_input = read_file_content(file_path)
    base_prompt = "Analyze where this text contains physical policy and score this system based on cyber resilience, and only give a numerical score. Use the related text as part of your judgement. No text or explanation."
    
    vault_texts = []
    if os.path.exists(physical_vault_path):
        with open(physical_vault_path, "r", encoding='utf-8') as vault_file:
            vault_texts = vault_file.readlines()
    
    embeddings_list = []
    for text in vault_texts:
        embedding_response = ollama.embeddings(model='mxbai-embed-large', prompt=text)
        embeddings_list.append(embedding_response["embedding"])
    
    embeddings_tensor = torch.tensor(embeddings_list)
    return engage_with_ollama(user_input, base_prompt, embeddings_tensor, vault_texts, "llama3")

# Initializing the LOCAL Ollama API client
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='llama3'
)

# Load and process document contents from the vault
vault_texts = []
if os.path.exists("vault.txt"):
    with open("vault.txt", "r", encoding='utf-8') as vault_file:
        vault_texts = vault_file.readlines()

# Generate embeddings for document contents
embeddings_list = []
for text in vault_texts:
    embedding_response = ollama.embeddings(model='mxbai-embed-large', prompt=text)
    embeddings_list.append(embedding_response["embedding"])

embeddings_tensor = torch.tensor(embeddings_list)