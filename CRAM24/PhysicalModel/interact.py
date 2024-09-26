# Import necessary libraries
import os
from unsloth import FastLanguageModel  # Import custom language model library
from transformers import AutoTokenizer  # Import tokenizer
import torch  # PyTorch for model operations

# Load the pre-trained model and tokenizer
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="lora_model",  # Use the path where your model is saved
    max_seq_length=2048,
    load_in_4bit=True,  # Load the model in 4-bit precision
)

# Preparing the model for inference
model = FastLanguageModel.for_inference(model)

# Function to generate text using the model
def generate_text(text):
    inputs = tokenizer(text, return_tensors="pt").to("cuda:0")  # Tokenize and move to GPU
    outputs = model.generate(**inputs, max_new_tokens=10, temperature=0.0)  # Limit to relevant tokens and make output deterministic
    response = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()  # Decode and clean output
    return response  # Return the generated text

# Interaction loop
print("Welcome to the interactive model! Type 'exit' to quit.")
while True:
    question = input("You: ")  # Get user input
    if question.lower() == "exit":
        break  # Exit the loop if the user types 'exit'
    
    answer = generate_text(question)  # Generate the answer using the model
    print(f"Model: {answer}")  # Print the model's answer
