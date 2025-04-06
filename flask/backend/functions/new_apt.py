import re
import torch
import ollama
import os
import json
import time
from openai import OpenAI

# Helper function to read content from a file
def read_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Function to extract the number from AI response
def extract_number_from_response(response):
    match = re.search(r'\*\*(\d+)\*\*', response)
    if match:
        return int(match.group(1))
    
    match_plain_number = re.search(r'\b\d+\b', response)
    if match_plain_number:
        return int(match_plain_number.group(0))
    
    return None

# Function to extract the category (hardware, software, physical) from the AI response
def extract_category_from_response(response):
    categories = ['hardware', 'software', 'physical']
    for category in categories:
        if category in response.lower():
            return category
    return None

# This is the main function to handle user interactions and get AI responses
def engage_with_ollama(user_input, base_prompt, doc_embeddings, doc_texts, ai_model):
    def get_category_and_extremity():
        # Prepare the prompt for Ollama with both category and extremity requests
        prompt = f"{base_prompt} {user_input} Please categorize the attack and provide a severity score from 1 to 10."
        
        # Create the chat log with the user input
        chat_log = [{"role": "user", "content": prompt}]
        
        # Build the full message with system prompt and chat log
        messages = [{"role": "system", "content": base_prompt}, *chat_log]
        
        # Call the model to get the AI response
        response = client.chat.completions.create(
            model=ai_model,
            messages=messages,
            max_tokens=2000,
        )
        
        # Extract the response content
        ai_response = response.choices[0].message.content
        
        # Extract the category from the AI response
        category = extract_category_from_response(ai_response)
        
        # Extract the extremity score from the AI response
        extremity = extract_number_from_response(ai_response)
        
        return category, extremity

    # Get the category and extremity score from the AI
    category, extremity = get_category_and_extremity()

    # If no valid extremity score or category, print a message
    if not category or not extremity:
        return None, None

    # Return the valid category and extremity score
    return category, extremity

# Function to process the input and return attack type and extremity score
def upgrade_Physical(prompt1, path_to_rag):
    
    user_input = f"{prompt1}"
    base_prompt = "What type of attack vector does this belong to between hardware, physical, and software."
    
    vault_texts = []
    if os.path.exists(path_to_rag):
        with open(path_to_rag, "r", encoding='utf-8') as vault_file:
            vault_texts = vault_file.readlines()
    
    embeddings_list = []
    for text in vault_texts:
        embedding_response = ollama.embeddings(model='mxbai-embed-large', prompt=text)
        embeddings_list.append(embedding_response["embedding"])
    
    # Convert embeddings to tensor
    embeddings_tensor = torch.tensor(embeddings_list)

    # Get the category and score from the Ollama model
    category, extremity = engage_with_ollama(user_input, base_prompt, embeddings_tensor, vault_texts, "llama3")

    # Return the result in "attack_type, score" format
    if category and extremity:
        return f"{category}, {extremity}"
    else:
        return "Could not determine attack type or score"

# Initializing the LOCAL Ollama API client
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='llama3'
)


# Helper function to read content from a file
def read_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Function to extract the number from AI response
def extract_number_from_response(response):
    match = re.search(r'\*\*(\d+)\*\*', response)
    if match:
        return int(match.group(1))
    
    match_plain_number = re.search(r'\b\d+\b', response)
    if match_plain_number:
        return int(match_plain_number.group(0))
    
    return None

# Function to extract the category (hardware, software, physical) from the AI response
def extract_category_from_response(response):
    categories = ['hardware', 'software', 'physical']
    for category in categories:
        if category in response.lower():
            return category
    return None

# This is the main function to handle user interactions and get AI responses
def engage_with_ollama(user_input, base_prompt, doc_embeddings, doc_texts, ai_model):
    def get_category_and_extremity():
        # Prepare the prompt for Ollama with both category and extremity requests
        prompt = f"{base_prompt} {user_input} Please categorize the attack and provide a severity score from 1 to 10."
        
        # Create the chat log with the user input
        chat_log = [{"role": "user", "content": prompt}]
        
        # Build the full message with system prompt and chat log
        messages = [{"role": "system", "content": base_prompt}, *chat_log]
        
        # Call the model to get the AI response
        response = client.chat.completions.create(
            model=ai_model,
            messages=messages,
            max_tokens=2000,
        )
        
        # Extract the response content
        ai_response = response.choices[0].message.content
        
        # Extract the category from the AI response
        category = extract_category_from_response(ai_response)
        
        # Extract the extremity score from the AI response
        extremity = extract_number_from_response(ai_response)
        
        return category, extremity

    # Get the category and extremity score from the AI
    category, extremity = get_category_and_extremity()

    # If no valid extremity score or category, print a message
    if not category or not extremity:
        return None, None

    # Return the valid category and extremity score
    return category, extremity

# Function to process the input and return attack type and extremity score
def New_APT(apt_db, apt_name, apt_behavior, path_to_rag):
    
    apt_file = f"{apt_db}{apt_name}-Profile.txt"
    
    user_input = f"{apt_behavior}"
    base_prompt = "What type of attack vector does this belong to between hardware, physical, or software."
    
    vault_texts = []
    if os.path.exists(path_to_rag):
        with open(path_to_rag, "r", encoding='utf-8') as vault_file:
            vault_texts = vault_file.readlines()
    
    embeddings_list = []
    for text in vault_texts:
        embedding_response = ollama.embeddings(model='mxbai-embed-large', prompt=text)
        embeddings_list.append(embedding_response["embedding"])
    
    # Convert embeddings to tensor
    embeddings_tensor = torch.tensor(embeddings_list)

    # Get the category and score from the Ollama model
    category, extremity = engage_with_ollama(user_input, base_prompt, embeddings_tensor, vault_texts, "llama3")

    with open(apt_file, 'w') as file:
        file.write(f"{category.capitalize()}: {extremity}")

# Initializing the LOCAL Ollama API client
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='llama3'
)