import spacy
from transformers import pipeline
import re

# Load the spaCy model to extract general entities
nlp = spacy.load("en_core_web_sm")

# Define a custom hardware dictionary
hardware_terms = [
    "server", "router", "firewall", "switch", "load balancer", "storage array",
    "backup system", "network appliance", "Dell", "Cisco", "HP", "IBM", "Juniper",
    "Fortinet", "Arista", "Nexus", "Rack", "Blade", "SAN", "NAS", "UPS", "Power Supply",
    "Ethernet", "Wi-Fi", "Modem", "Gateway", "APC", "NetApp", "Lenovo", "Supermicro"
]

# Function to extract hardware terms from text
def extract_hardware_terms(text):
    doc = nlp(text)
    extracted_hardware = []
    for token in doc:
        if token.text in hardware_terms:
            extracted_hardware.append(token.text)
    return list(set(extracted_hardware))

# Function to assign risk scores to hardware components
def assign_risk_scores(hardware_list):
    risk_scores = {
        "server": 10, "router": 8, "firewall": 9, "switch": 7, "load balancer": 6,
        "storage array": 8, "backup system": 9, "network appliance": 7, "Dell": 6,
        "Cisco": 9, "HP": 6, "IBM": 6, "Juniper": 8, "Fortinet": 9, "Arista": 7,
        "Nexus": 7, "Rack": 5, "Blade": 6, "SAN": 8, "NAS": 7, "UPS": 6,
        "Power Supply": 5, "Ethernet": 6, "Wi-Fi": 5, "Modem": 4, "Gateway": 4,
        "APC": 5, "NetApp": 8, "Lenovo": 6, "Supermicro": 7
    }
    
    risk_result = []
    for hardware in hardware_list:
        score = risk_scores.get(hardware, 5)  # Assign a default score of 5 if not found
        risk_result.append({"hardware": hardware, "score": score, "weighted_score": score * 10})
    
    return risk_result

# Function to calculate total score
def calculate_total_score(risk_result):
    total_score = sum(item["weighted_score"] for item in risk_result)
    return min(100, total_score)

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

            # Calculate total score
            total_score = calculate_total_score(risk_result)

            # Print individual hardware scores and the total score
            for hardware in risk_result:
                print(f"{hardware['hardware']}: {hardware['weighted_score']}")

            print(f"\nTotal Hardware Score: {total_score}/100")

            return total_score

    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return 0  # Return 0 if file not found
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0  # Return 0 if an error occurs

# Function to calculate average score over multiple iterations
def average_hardware_score(file_path, iterations=12):
    total_score_sum = 0
    for i in range(iterations):
        print(f"\n--- Iteration {i+1} ---")
        total_score_sum += process_hardware_file(file_path)
    
    average_score = total_score_sum / iterations
    print(f"\nAverage Hardware Score after {iterations} iterations: {average_score}/100")
    return average_score

# Specify the file path for Hardware.txt
hardware_file_path = "/home/user/Documents/Github/classified_output/Hardware.txt"  # Replace with correct path

# Run the average hardware score calculation
average_hardware_score(hardware_file_path, iterations=12)
