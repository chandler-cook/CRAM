import spacy
from transformers import pipeline
import re

# Load the spaCy model to extract general entities
nlp = spacy.load("en_core_web_sm")

# Define a custom hardware dictionary with stricter weighting
hardware_terms = [
    "server", "router", "firewall", "switch", "load balancer", "storage array", 
    "backup system", "network appliance", "Dell", "Cisco", "HP", "IBM", "Juniper", 
    "Fortinet", "Arista", "Nexus", "Rack", "Blade", "SAN", "NAS", "UPS", "Power Supply"
]

# Define an initial risk score based on real-world data and adjust scoring
hardware_risk_scores = {
    "server": 90,
    "router": 80,
    "firewall": 70,
    "switch": 65,
    "load balancer": 75,
    "storage array": 60,
    "backup system": 60,
    "network appliance": 85,
    "Dell": 90,
    "Cisco": 95,
    "HP": 88,
    "IBM": 80,
    "Juniper": 80,
    "Fortinet": 75,
    "Arista": 75,
    "Nexus": 80,
    "Rack": 50,
    "Blade": 60,
    "SAN": 70,
    "NAS": 70,
    "UPS": 50,
    "Power Supply": 40
}

# Adjust risk score calculation dynamically based on extracted hardware components
def calculate_risk_score(hardware_list):
    total_score = 0
    for hardware in hardware_list:
        # If the hardware is recognized, add its risk score
        if hardware in hardware_risk_scores:
            total_score += hardware_risk_scores[hardware]
    return total_score

# Process the hardware.txt file and extract hardware components
def process_hardware_file(file_path):
    with open(file_path, "r") as file:
        text = file.read()
    
    # Use spaCy to extract hardware-related terms
    doc = nlp(text)
    hardware_mentions = []

    for token in doc:
        if token.text.lower() in hardware_terms:
            hardware_mentions.append(token.text)

    # Deduplicate the hardware mentions
    hardware_mentions = list(set(hardware_mentions))
    print(f"Extracted hardware terms (deduplicated): {hardware_mentions}")

    # Calculate the total risk score
    total_score = calculate_risk_score(hardware_mentions)

    # Normalize the score to a range out of 100
    max_score_possible = len(hardware_terms) * 100
    final_score = (total_score / max_score_possible) * 100

    return final_score

# Average the hardware resiliency score across multiple iterations
def average_hardware_score(file_path, iterations=1):
    total_score_sum = 0

    for i in range(iterations):
        print(f"\n--- Iteration {i+1} ---")
        total_score_sum += process_hardware_file(file_path)

    average_score = total_score_sum / iterations
    return average_score

# Main function to run the hardware score calculation
if __name__ == "__main__":
    hardware_file_path = "/home/user/Documents/Github/classified_output/Hardware.txt"
    final_score = average_hardware_score(hardware_file_path, iterations=1)
    print(f"\nFinal Hardware Resiliency Score: {final_score}/100")
