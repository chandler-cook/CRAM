#pip install spacy transformers
#python -m spacy download en_core_web_sm


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
    "Ethernet", "Wi-Fi", "wireless access point", "AP", "modem", "gateway", "firewall",
    "CPU", "GPU", "motherboard", "PCIe", "SSD", "HDD"
]

# Load Hugging Face's zero-shot classification pipeline
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Define the labels for classification
labels = ["High Risk", "Medium Risk", "Low Risk"]

# Function to extract hardware terms using regex and spaCy
def extract_hardware_info(text):
    doc = nlp(text)
    extracted_terms = set()

    # Use spaCy to extract named entities
    for ent in doc.ents:
        if ent.label_ in ["PRODUCT", "ORG", "FAC", "GPE"]:
            extracted_terms.add(ent.text)

    # Use custom dictionary matching for hardware terms
    for term in hardware_terms:
        pattern = re.compile(r"\b{}\b".format(re.escape(term)), re.IGNORECASE)
        matches = pattern.findall(text)
        extracted_terms.update(matches)
    
    return list(extracted_terms)

# Function to classify hardware risk
def classify_hardware_risk(hardware_term):
    hypothesis_template = f"This hardware is a {{}}."
    results = classifier(hardware_term, [hypothesis_template.format(label) for label in labels])
    return results

# Main function to process the hardware file and assign risk scores
def process_hardware_file(file_path):
    with open(file_path, "r") as file:
        text = file.read()

    # Step 1: Extract hardware terms from the file using both spaCy and dictionary matching
    hardware_terms = extract_hardware_info(text)
    print(f"Extracted Hardware: {hardware_terms}")

    # Step 2: Classify risk for each hardware entity
    hardware_risk_data = []
    for hardware in hardware_terms:
        risk_result = classify_hardware_risk(hardware)
        highest_risk = max(risk_result, key=lambda x: x['score'])
        
        hardware_risk_data.append({
            "Hardware": hardware,
            "Risk_Category": highest_risk['label'],
            "Confidence_Score": highest_risk['score']
        })

    # Print results
    for item in hardware_risk_data:
        print(f"Hardware: {item['Hardware']}, Risk Category: {item['Risk_Category']}, Confidence: {item['Confidence_Score']:.2f}")

# Example: Call the function with the path to your hardware.txt file
file_path = "hardware.txt"
process_hardware_file(file_path)
