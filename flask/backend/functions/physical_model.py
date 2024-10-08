import re
import torch
import ollama
import os
from openai import OpenAI
import argparse
import json
import time


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

# Rephrasing the user query based on the conversation history
def refine_query(user_input_str, chat_history, ai_model):
    user_query = json.loads(user_input_str)["Query"]
    recent_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history[-2:]])
    rephrase_prompt = f"""Refine the following query by adding necessary context from the conversation history:

    Conversation History:
    {recent_history}

    Original query: [{user_query}]
    
    Refined query:
    """
    
    response = client.chat.completions.create(
        model=ai_model,
        messages=[{"role": "system", "content": rephrase_prompt}],
        max_tokens=200,
        n=1,
        temperature=0.1,
    )
    
    return json.dumps({"Rewritten Query": response.choices[0].message.content.strip()})

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
def engage_with_ollama(user_input, base_prompt, doc_embeddings, doc_texts, ai_model, chat_log):
    full_prompt = f"{base_prompt} {user_input}"
    chat_log.append({"role": "user", "content": full_prompt})

    scores = []
    
    for i in range(15):
        messages = [
            {"role": "system", "content": base_prompt},
            *chat_log
        ]
        
        response = client.chat.completions.create(
            model=ai_model,
            messages=messages,
            max_tokens=2000,
        )
        
        ai_response = response.choices[0].message.content
        
        extracted_number = extract_number_from_response(ai_response)
        if extracted_number:
            scores.append(extracted_number)
        

    if scores:
        average_score = sum(scores) / len(scores)

        return round(average_score)
    

    return None

# Localrag function to read from file, process input, and return score. This is called in the main.py to interact with with the rest of the backend
def localrag(file_path):
    user_input = read_file_content(file_path)
    base_prompt = "Score this system based on cyber resilience, and only give a numerical score. No text or explanation."
    
    vault_texts = []
    if os.path.exists("vault.txt"):
        with open("vault.txt", "r", encoding='utf-8') as vault_file:
            vault_texts = vault_file.readlines()
    
    embeddings_list = []
    for text in vault_texts:
        embedding_response = ollama.embeddings(model='mxbai-embed-large', prompt=text)
        embeddings_list.append(embedding_response["embedding"])
    
    embeddings_tensor = torch.tensor(embeddings_list)
    return engage_with_ollama(user_input, base_prompt, embeddings_tensor, vault_texts, "llama3", [])

# Parsing command-line arguments for model configuration
parser = argparse.ArgumentParser(description="Interactive AI Chat")
parser.add_argument("--model", default="llama3", help="Specify the Ollama model (default: llama3)")
args = parser.parse_args()

# Initializing the LOCAL Ollama API client
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='llama3'
)

# Loading document contents from the vault. This is where the RAG implementation occurs
vault_texts = []
if os.path.exists("vault.txt"):
    with open("vault.txt", "r", encoding='utf-8') as vault_file:
        vault_texts = vault_file.readlines()

# Generating embeddings for document contents
embeddings_list = []
for text in vault_texts:
    embedding_response = ollama.embeddings(model='mxbai-embed-large', prompt=text)
    embeddings_list.append(embedding_response["embedding"])

embeddings_tensor = torch.tensor(embeddings_list)
#print("Document embeddings tensor created successfully:")
#print(embeddings_tensor)

# This is the base prompt for scoring in order to ensure a numerical response from the AI
base_prompt = "Score this system based on cyber resilience, and only give a numerical score. No text or explanation."

# Start of the conversation loop
chat_log = []
initial_system_message = "You are a knowledgeable assistant that excels at finding relevant context from the provided documents."

