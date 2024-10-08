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

# Adjusted Risk Scores Based on Real-World Data with Weighting for Criticality
risk_scores = {
    "server": {"base_score": 9, "weight": 1.5},  # Higher weight due to criticality
    "router": {"base_score": 8, "weight": 1.4},
    "firewall": {"base_score": 9, "weight": 1.5},
    "switch": {"base_score": 7, "weight": 1.2},
    "load balancer": {"base_score": 8, "weight": 1.3},
    "storage array": {"base_score": 7, "weight": 1.1},
    "backup system": {"base_score": 8, "weight": 1.3},
    "network appliance": {"base_score": 7, "weight": 1.1},
    "Dell": {"base_score": 7, "weight": 1.2},
    "Cisco": {"base_score": 9, "weight": 1.4},
    "HP": {"base_score": 7, "weight": 1.2},
    "IBM": {"base_score": 8, "weight": 1.3},
    "Juniper": {"base_score": 9, "weight": 1.4},
    "Fortinet": {"base_score": 9, "weight": 1.4},
    "Arista": {"base_score": 7, "weight": 1.2},
    "Nexus": {"base_score": 8, "weight": 1.3},
    "Rack": {"base_score": 4, "weight": 0.8},
    "Blade": {"base_score": 6, "weight": 1.1},
    "SAN": {"base_score": 7, "weight": 1.2},
    "NAS": {"base_score": 7, "weight": 1.2},
    "UPS": {"base_score": 4, "weight": 0.8},
    "Power Supply": {"base_score": 4, "weight": 0.8}
}

# Maximum possible score with weighted terms
MAX_SCORE = sum([v["base_score"] * v["weight"] for v in risk_scores.values()])

# Function to extract hardware terms from text
def extract_hardware_terms(text):
    doc = nlp(text)
    extracted_hardware = set()

    # Search for hardware terms in the text
    for token in doc:
        if token.text in hardware_terms:
            extracted_hardware.add(token.text)
    
    return list(extracted_hardware)

# Function to assign weighted risk scores to extracted hardware
def assign_risk_scores(extracted_hardware):
    risk_result = []
    
    # Assign scores from the dictionary
    for hardware in extracted_hardware:
        score_info = risk_scores.get(hardware, {"base_score": 1, "weight": 1})  # Default score if not found
        weighted_score = score_info["base_score"] * score_info["weight"]
        risk_result.append({"hardware": hardware, "weighted_score": weighted_score})
    
    return risk_result

# Function to calculate total hardware score out of 100
def calculate_total_score(risk_result):
    total_weighted_score = sum([item['weighted_score'] for item in risk_result])

    # Normalize the total score to a 100-point scale
    normalized_score = (total_weighted_score / MAX_SCORE) * 100
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
                print(f"{hardware['hardware']}: {hardware['weighted_score']}")

            print(f"\nTotal Hardware Score: {total_score}/100")

            return total_score

    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0  # Return 0 if an error occurs

# Function to run the hardware score calculation multiple times and average the score
def average_hardware_score(file_path, iterations=12):
    total_score_sum = 0

    for i in range(iterations):
        print(f"\n--- Iteration {i + 1} ---")
        total_score_sum += process_hardware_file(file_path)
    
    # Calculate the average score
    average_score = total_score_sum / iterations
    print(f"\n--- Final Average Hardware Score (over {iterations} iterations): {average_score:.2f}/100 ---")

# Example usage
hardware_file_path = 'path_to_your_hardware.txt'  # Replace with your actual path
average_hardware_score(hardware_file_path, iterations=12)
