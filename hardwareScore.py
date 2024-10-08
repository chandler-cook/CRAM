
import spacy
from transformers import pipeline
import re

# Load the spaCy model to extract general entities
nlp = spacy.load("en_core_web_sm")


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

# Adjusting the weight based on hardware criticality
hardware_weights = {
    "server": 1.5,  # Servers are critical, higher weight
    "switch": 1.2,  # Important, but slightly lower than server
    "firewall": 1.4,  # Firewalls play a crucial security role
    "router": 1.3,  # Routers are vital but slightly less than firewalls
    "SAN": 1.3,  # Storage Area Networks are essential
    "UPS": 1.0,  # Power supply is important but foundational
    "Rack": 0.8,  # Racks are infrastructural but not critical to security
    "Cisco": 1.2,  # Cisco products, often high-priority
    "Dell": 1.0,  # Dell, common but balanced
    "Ethernet": 0.9,  # Lower priority than switches and routers
    "HP": 1.0,  # Balanced weight for common hardware
    "Power Supply": 1.1,  # Power supply units can impact overall stability
    "Blade": 1.1,  # Blades typically run important services
    "Arista": 1.0,  # Networking vendor like Cisco, balanced
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
        weighted_score = score * 10  # Adjust as needed
        hardware_scores.append({"hardware": term, "score": score, "weighted_score": weighted_score})

    total_score = sum(item["weighted_score"] for item in hardware_scores)
    print(f"Risk results: {hardware_scores}\n")
    print(f"Total score: {total_score}")
    
    return total_score

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
