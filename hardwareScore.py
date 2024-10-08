# Required Libraries
import spacy
from transformers import pipeline
import re

# Load the spaCy model to extract general entities
nlp = spacy.load("en_core_web_sm")

# Define a custom hardware dictionary (You can expand this)
hardware_terms = [
    "server", "router", "firewall", "switch", "load balancer", "storage array",
    "backup system", "network appliance", "Dell", "Cisco", "HP", "IBM", "Juniper", 
    "Fortinet", "Arista", "Nexus", "Rack", "Blade", "SAN", "NAS", "UPS", "Power Supply"
]

# Function to extract hardware terms
def extract_hardware_terms(text):
    doc = nlp(text)
    extracted_hardware = set()

    # Search for hardware terms in the text
    for token in doc:
        if token.text in hardware_terms:
            extracted_hardware.add(token.text)
    
    return list(extracted_hardware)

# Dummy risk scoring dictionary (for simplicity, assume it's pre-defined)
risk_scores = {
    "server": 5,
    "router": 7,
    "firewall": 9,
    "switch": 6,
    "Dell": 4,
    "Cisco": 8
}

# Function to assign risk scores to extracted hardware
def assign_risk_scores(extracted_hardware):
    risk_result = []
    
    # Assign scores from the dictionary
    for hardware in extracted_hardware:
        score = risk_scores.get(hardware, 1)  # Default score 1 if not found
        risk_result.append({"hardware": hardware, "score": score})
    
    return risk_result

# Function to find the highest risk hardware
def find_highest_risk(risk_result):
    if isinstance(risk_result, str):
        # In case risk_result is a string, return a default value
        return "No valid risk data"
    
    print(f"Risk Results: {risk_result}")  # Debugging output

    try:
        highest_risk = max(risk_result, key=lambda x: x.get('score', 0))
        return highest_risk
    except TypeError as e:
        print(f"Error: {e}")
        return None

# Function to process the hardware file
def process_hardware_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            print(f"Extracted text from {file_path}...")

            # Extract hardware terms
            extracted_hardware = extract_hardware_terms(text)
            print(f"Extracted Hardware: {extracted_hardware}")

            # Assign risk scores
            risk_result = assign_risk_scores(extracted_hardware)

            # Find highest risk hardware
            highest_risk = find_highest_risk(risk_result)

            if highest_risk:
                print(f"The highest risk hardware is: {highest_risk['hardware']} with a score of {highest_risk['score']}")
            else:
                print("No valid hardware risks found.")
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
hardware_file_path = 'path_to_your_hardware.txt'  # Replace with your actual path
process_hardware_file(hardware_file_path)
