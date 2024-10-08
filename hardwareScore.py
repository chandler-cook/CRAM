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

# Cap for the score to avoid going beyond 100
def cap_score(score):
    return max(0, min(score, 100))

# Calculate weighted score per hardware based on risks
def calculate_risk_score(hardware):
    # Adjusted base score per hardware type
    base_risk_score = {
        "server": 30, "router": 25, "firewall": 20, "switch": 25, "load balancer": 15,
        "storage array": 20, "SAN": 20, "NAS": 20, "UPS": 15, "Cisco": 30, "Dell": 25, 
        "PowerEdge": 30, "Ethernet": 20, "Patch Panel": 10, "Tripp Lite": 10, "Power Supply": 15,
        "RHEL": 30, "Blade": 10, "Rack": 10
    }
    
    # Multiply by a risk factor (e.g., based on importance or known vulnerabilities)
    risk_factor = 1.5  # You can adjust this to make the model more or less sensitive
    
    # Apply a more conservative multiplier
    risk_score = base_risk_score.get(hardware, 10) * risk_factor
    return cap_score(risk_score)

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
                weighted_score = cap_score(score)  # Apply the score cap
                risk_result.append({"hardware": hardware, "score": score, "weighted_score": weighted_score})
                total_score += weighted_score

            print(f"Risk results: {risk_result}")
            print(f"Total score before capping: {total_score}")

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
