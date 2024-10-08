import spacy
import re

# Load the spaCy model to extract general entities
nlp = spacy.load("en_core_web_sm")

# Define a custom hardware dictionary
hardware_terms = [
    "server", "router", "firewall", "switch", "load balancer", "storage array",
    "backup system", "network appliance", "Dell", "Cisco", "HP", "IBM", "Juniper",
    "Fortinet", "Arista", "Nexus", "Rack", "Blade", "SAN", "NAS", "UPS", "Power Supply",
    "Ethernet Switch", "Layer 2 Switch", "Layer 3 Switch", "Meraki", "PowerVault",
    "Uninterruptible Power Supply (UPS)", "Cisco Firepower", "Patch Panel", "RHEL",
    "PowerEdge R750", "PowerVault ME5024", "Cisco Catalyst 2960-X", "MS425-32",
    "SMT3000RM2UC", "N052-048-1U", "Tripp Lite", "RedHat Enterprise Linux",
    "Workstation", "Rugged Latitude Extreme Laptop", "Precision 5820", "Bulk Data Storage Rack",
    "Server Rack", "Boundary Defense", "Uninterruptible Power Supply", "Miscellaneous Components"
]

# Cap for the score to ensure it doesn't go below 0
def cap_score(score):
    return max(0, score)

# Subtract points based on vulnerabilities
def calculate_risk_penalty(hardware):
    # Penalty points per hardware type based on risk factor
    risk_penalty = {
        "server": 10, "router": 15, "firewall": 10, "switch": 15, "load balancer": 5,
        "storage array": 10, "SAN": 8, "NAS": 10, "UPS": 7, "Cisco": 12, "Dell": 10, 
        "PowerEdge": 12, "Ethernet": 7, "Patch Panel": 5, "Tripp Lite": 5, "Power Supply": 8,
        "RHEL": 12, "Blade": 5, "Rack": 7
    }
    
    # Return penalty points for the hardware, or a default value
    return risk_penalty.get(hardware, 5)  # Default penalty of 5

# Process the hardware and calculate final score
def process_hardware_file(file_path):
    try:
        with open(file_path, 'r') as infile:
            text = infile.read()
            # Extract hardware terms from text using spaCy and custom terms
            doc = nlp(text)
            extracted_hardware = [ent.text for ent in doc.ents if ent.text in hardware_terms]
            deduped_hardware = list(set(extracted_hardware))  # Remove duplicates

            print(f"Extracted hardware terms (deduplicated): {deduped_hardware}")

            # Start with a perfect score of 100
            total_score = 100
            risk_result = []

            # Subtract penalties for each hardware term
            for hardware in deduped_hardware:
                penalty = calculate_risk_penalty(hardware)
                total_score = cap_score(total_score - penalty)  # Subtract the penalty
                risk_result.append({"hardware": hardware, "penalty": penalty})

            print(f"Risk results: {risk_result}")
            print(f"Total score after applying penalties: {total_score}")

            return total_score
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
