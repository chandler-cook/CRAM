import spacy
from transformers import pipeline
import re

# Load the spaCy model to extract general entities
nlp = spacy.load("en_core_web_sm")

# Define a custom hardware dictionary
hardware_terms = [
    "server", "router", "firewall", "switch", "load balancer", "storage array",
    "backup system", "network appliance", "Dell", "Cisco", "HP", "IBM", "Juniper",
    "Fortinet", "Arista", "Nexus", "Rack", "Blade", "SAN", "NAS", "UPS", "Power Supply"
]

# Adjusting the weight based on hardware criticality
hardware_weights = {
    "server": 1.5,  # Servers are critical, higher weight
    "switch": 1.1,  # Important, but slightly lower than server
    "firewall": 1.4,  # Firewalls play a crucial security role
    "router": 1.2,  # Routers are vital but slightly less than firewalls
    "SAN": 1.1,  # Storage Area Networks are important
    "UPS": 1.0,  # Power supply is important
    "Rack": 0.8,  # Racks are infrastructural
    "Cisco": 1.2,  # Cisco products
    "Dell": 1.0,  # Dell, balanced
    "Ethernet": 0.9,  # Lower priority than switches and routers
    "HP": 1.0,  # Balanced weight for common hardware
    "Power Supply": 1.1,  # Power supply units are important
    "Blade": 1.0,  # Blades
    "Arista": 1.0,  # Networking vendor, balanced
    "Juniper": 1.2,  # Networking vendor, slightly higher weight
}

# Function to extract hardware terms from text
def extract_hardware_terms(text):
    doc = nlp(text)
    extracted_terms = []
    for token in doc:
        if token.text.lower() in hardware_terms:
            extracted_terms.append(token.text)
    return extracted_terms

# Function to process hardware file and calculate risk score
def process_hardware_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    # Extract hardware terms from the text
    extracted_terms = extract_hardware_terms(text)
    deduplicated_hardware_terms = list(set(extracted_terms))  # Remove duplicates
    print(f"\nExtracted hardware terms (deduplicated): {deduplicated_hardware_terms}\n")

    # Calculate risk score based on hardware terms
    base_risk_score = 5
    hardware_scores = []

    for term in deduplicated_hardware_terms:
        score = hardware_weights.get(term.lower(), 1.0) * base_risk_score  # Use 1.0 if no specific weight is defined
        weighted_score = score  # Removed multiplier to avoid exaggeration
        hardware_scores.append({"hardware": term, "score": score, "weighted_score": weighted_score})

    total_score = sum(item["weighted_score"] for item in hardware_scores)
    
    # Cap the final score at 100
    capped_score = min(total_score, 100)
    print(f"Risk results: {hardware_scores}\n")
    print(f"Total score (capped at 100): {capped_score}")
    
    return capped_score

# Function to average hardware resiliency score over multiple iterations
def average_hardware_score(file_path, iterations=1):
    total_score_sum = 0
    for i in range(iterations):
        print(f"\n--- Iteration {i + 1} ---")
        total_score_sum += process_hardware_file(file_path)
    final_score = total_score_sum / iterations
    print(f"\nFinal Hardware Resiliency Score (average): {final_score}/100")

# Define the file path for the hardware file
hardware_file_path = "/home/user/Documents/Github/classified_output/Hardware.txt"

# Run the hardware scoring process
average_hardware_score(hardware_file_path, iterations=1)
