# Required Libraries
import spacy
from transformers import pipeline
import re

# Load the spaCy model to extract general entities
nlp = spacy.load("en_core_web_sm")

# Define a custom hardware dictionary (Updated based on real-world data)
hardware_terms = [
    "server", "router", "firewall", "switch", "load balancer", "storage array",
    "backup system", "network appliance", "Dell", "Cisco", "HP", "IBM", "Juniper", 
    "Fortinet", "Arista", "Nexus", "Rack", "Blade", "SAN", "NAS", "UPS", "Power Supply"
]

# Adjusted Risk Scores Based on Real-World Data
risk_scores = {
    "server": 9,
    "router": 8,
    "firewall": 9,
    "switch": 7,
    "load balancer": 8,
    "storage array": 7,
    "backup system": 8,
    "network appliance": 7,
    "Dell": 7,
    "Cisco": 9,
    "HP": 7,
    "IBM": 8,
    "Juniper": 9,
    "Fortinet": 9,
    "Arista": 7,
    "Nexus": 8,
    "Rack": 4,
    "Blade": 6,
    "SAN": 7,
    "NAS": 7,
    "UPS": 4,
    "Power Supply": 4
}

# Maximum possible score (sum of all scores in risk_scores)
MAX_SCORE = sum(risk_scores.values())

# Function to extract hardware terms from text
def extract_hardware_terms(text):
    doc = nlp(text)
    extracted_hardware = set()

    # Search for hardware terms in the text
    for token in doc:
        if token.text in hardware_terms:
            extracted_hardware.add(token.text)
    
    return list(extracted_hardware)

# Function to assign risk scores to extracted hardware
def assign_risk_scores(extracted_hardware):
    risk_result = []
    
    # Assign scores from the dictionary
    for hardware in extracted_hardware:
        score = risk_scores.get(hardware, 1)  # Default score 1 if not found
        risk_result.append({"hardware": hardware, "score": score})
    
    return risk_result

# Function to calculate total hardware score out of 100
def calculate_total_score(risk_result):
    total_score = sum([item['score'] for item in risk_result])

    # Normalize the total score to a 100-point scale
    normalized_score = (total_score / MAX_SCORE) * 100
    return min(normalized_score, 100)  # Ensure it doesn't exceed 100

# Function to process the hardware file and calculate the total score
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

            # Calculate total score
            total_score = calculate_total_score(risk_result)

            # Print individual hardware scores and the total score
            for hardware in risk_result:
                print(f"{hardware['hardware']}: {hardware['score']}")

            print(f"\nTotal Hardware Score: {total_score}/100")

    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
hardware_file_path = 'path_to_your_hardware.txt'  # Replace with your actual path
process_hardware_file(hardware_file_path)
