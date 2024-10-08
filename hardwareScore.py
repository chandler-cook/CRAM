# Adjust the scoring script to improve the score calculation
import spacy
from transformers import pipeline
import re

# Load the spaCy model to extract general entities
nlp = spacy.load("en_core_web_sm")

# Define a custom hardware dictionary
hardware_terms = [
    # Network Devices
    "server", "router", "firewall", "switch", "load balancer", "storage array",
    "backup system", "network appliance", "Dell", "Cisco", "HP", "IBM", "Juniper",
    "Fortinet", "Arista", "Nexus", "Rack", "Blade", "SAN", "NAS", "UPS", "Power Supply",
    "Ethernet Switch", "Layer 2 Switch", "Layer 3 Switch", "Meraki", "PowerVault",
    "Uninterruptible Power Supply (UPS)", "Cisco Firepower", "Patch Panel", "RHEL",
    
    # Specific Hardware Models
    "PowerEdge R750", "PowerVault ME5024", "Cisco Catalyst 2960-X", "MS425-32",
    "SMT3000RM2UC", "N052-048-1U", "Tripp Lite", "RedHat Enterprise Linux",
    
    # Additional Items
    "Workstation", "Rugged Latitude Extreme Laptop", "Precision 5820", "Bulk Data Storage Rack",
    "Server Rack", "Boundary Defense", "Uninterruptible Power Supply", "Miscellaneous Components",
    
    # Common Servers and Racks
    "Server Rack", "Boundary Defense and System Administrator Rack", "Test Laptop",
    "Engineering Workstation", "Server Rack SR1", "Server Rack SR2", "Server Rack SR3", 
    "Server Rack SR4", "Server Rack SR5", "Server Rack SR6", "Server Rack SR7",
    "Server Rack SR8", "Server Rack SR9", "Server Rack SR10", "Server Rack SR11",
    "Server Rack SR12", "Patch Panel", "Rack Mounted Monitor", "Cybersecurity Capability and Tools"
]

# Cap for the score to avoid going beyond 100
def cap_score(score):
    if score > 100:
        return 100
    elif score < 0:
        return 0
    return score

# Calculate weighted score per hardware based on risks
def calculate_risk_score(hardware):
    # Base score per hardware
    base_risk_score = {
        "server": 7, "router": 8, "firewall": 6, "switch": 7, "load balancer": 6,
        "storage array": 5, "SAN": 7, "NAS": 6, "UPS": 6, "Cisco": 8, "Dell": 9, 
        "PowerEdge": 8, "Ethernet": 6, "Patch Panel": 4, "Tripp Lite": 4, "Power Supply": 5,
        "RHEL": 8, "Blade": 5, "Rack": 5
    }
    return base_risk_score.get(hardware, 5) * 10  # Adjust weight calculation for hardware vulnerability

# Process the hardware and calculate total score
def process_hardware_file(file_path):
    try:
        with open(file_path, 'r') as infile:
            text = infile.read()
            # Extract hardware terms from text using spaCy and custom terms
            doc = nlp(text)
            extracted_hardware = [ent.text for ent in doc.ents if ent.text in hardware_terms]
            deduped_hardware = list(set(extracted_hardware))  # Remove duplicates

            print(f"Extracted hardware terms (deduplicated): {deduped_hardware}")

            # Calculate risk scores
            total_score = 0
            risk_result = []
            for hardware in deduped_hardware:
                score = calculate_risk_score(hardware)
                weighted_score = cap_score(score)  # Apply the score cap here
                risk_result.append({"hardware": hardware, "score": score, "weighted_score": weighted_score})
                total_score += weighted_score

            print(f"Risk results: {risk_result}")
            print(f"Total score: {total_score}")

            # Cap total score at 100
            final_score = cap_score(total_score)
            return final_score
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None

# Example of averaging score over iterations
def average_hardware_score(file_path, iterations=1):
    total_score_sum = 0
    for i in range(iterations):
        print(f"\n--- Iteration {i + 1} ---")
        total_score_sum += process_hardware_file(file_path)

    average_score = total_score_sum / iterations if iterations > 0 else 0
    print(f"\nFinal Hardware Resiliency Score (average): {cap_score(average_score)}/100")

# Example usage
hardware_file_path = '/home/user/Documents/Github/classified_output/Hardware.txt'  # Replace with actual path
average_hardware_score(hardware_file_path, iterations=1)  # Run once for the final score
