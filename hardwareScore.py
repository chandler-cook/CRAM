# Import necessary libraries
import spacy
from transformers import pipeline
import re

# Load the spaCy model for entity extraction and Hugging Face sentiment analysis pipeline
nlp = spacy.load("en_core_web_sm")
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# Define a custom hardware dictionary (expandable)
hardware_terms = [
    "server", "router", "firewall", "switch", "load balancer", "storage array",
    "backup system", "network appliance", "Dell", "Cisco", "HP", "IBM", "Juniper",
    "Fortinet", "Arista", "Nexus", "Rack", "Blade", "SAN", "NAS", "UPS", "Power Supply"
]

# Function to extract hardware terms and evaluate their context using sentiment analysis
def extract_and_score_hardware(file_path):
    with open(file_path, 'r') as file:
        text = file.read()

    # Extracting sentences and terms
    doc = nlp(text)
    extracted_hardware = []
    hardware_contexts = {}

    for sent in doc.sents:
        sentence_text = sent.text.strip()
        for hardware in hardware_terms:
            if hardware.lower() in sentence_text.lower():
                extracted_hardware.append(hardware)
                if hardware not in hardware_contexts:
                    hardware_contexts[hardware] = []
                hardware_contexts[hardware].append(sentence_text)

    # Deduplicate the extracted hardware terms
    extracted_hardware = list(set(extracted_hardware))
    
    # Analyzing the sentiment around each hardware context
    hardware_scores = {}
    for hardware, contexts in hardware_contexts.items():
        total_score = 0
        count = 0
        for context in contexts:
            # Get sentiment for each sentence
            sentiment_result = sentiment_analyzer(context)
            sentiment = sentiment_result[0]['label']
            score = sentiment_result[0]['score']

            # Adjust risk score based on sentiment
            if sentiment == 'NEGATIVE':
                risk_score = 100 * score  # Negative sentiment is high risk, keep it strong
            elif sentiment == 'POSITIVE':
                risk_score = 80 * (1 - score)  # Lower the impact of positive sentiment on risk
            else:
                risk_score = 70  # Keep neutral sentiment moderate-risk

            total_score += risk_score
            count += 1

        # Calculate average risk score for the hardware term
        if count > 0:
            hardware_scores[hardware] = total_score / count

    # Output the hardware and their risk scores
    print("Extracted hardware and calculated risk scores:")
    for hardware, score in hardware_scores.items():
        print(f"{hardware}: {score:.2f}")

    # Calculate total score as an average
    if len(hardware_scores) > 0:
        total_score = sum(hardware_scores.values()) / len(hardware_scores)
    else:
        total_score = 0

    # Apply a final scaling to make the score closer to the desired range
    final_score = total_score * 0.75  # Adjust this scaling factor to calibrate scores
    print(f"\nFinal Hardware Resiliency Score (average): {final_score:.2f}/100")
    return final_score

# File path to hardware.txt
file_path = "hardware.txt"

# Call the function to process the file and calculate hardware risk score
extract_and_score_hardware(file_path)
